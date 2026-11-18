import {test, expect} from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

const pages = ["index.html", "prices.html", "methods.html"];

for (const page of pages) {
  test.describe(page, () => {
    test("loads without console or page errors", async ({page: p}) => {
      const errors = [];
      p.on("console", (m) => m.type() === "error" && errors.push(m.text()));
      p.on("pageerror", (e) => errors.push(String(e)));
      await p.goto(page);
      await p.waitForLoadState("networkidle");
      expect(errors).toEqual([]);
    });

    test("axe color-contrast has 0 violations", async ({page: p}) => {
      await p.goto(page);
      await p.waitForLoadState("networkidle");
      const {violations} = await new AxeBuilder({page: p}).withRules(["color-contrast"]).analyze();
      const msg = violations
        .flatMap((v) => v.nodes.map((n) => `${n.target} ${n.any.map((a) => a.message).join("; ")}`))
        .join("\n");
      expect(violations, msg).toEqual([]);
    });

    test("no horizontal overflow (<= 375 at mobile)", async ({page: p}) => {
      await p.goto(page);
      await p.waitForLoadState("networkidle");
      expect(await p.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(p.viewportSize().width);
    });
  });
}

test("home: question, headline and stamp fit above the fold", async ({page}, info) => {
  await page.goto("index.html");
  await page.waitForLoadState("networkidle");
  const height = page.viewportSize().height;
  for (const id of ["question", "headline", "stamp"]) {
    const box = await page.locator(`[data-testid=${id}]`).boundingBox();
    expect(box, id).not.toBeNull();
    expect(box.y + box.height, id).toBeLessThanOrEqual(height);
  }
  await page.screenshot({path: `test-results/home-${info.project.name}.png`, fullPage: true});
});

test("methods: km-chart is a labelled svg", async ({page}) => {
  await page.goto("methods.html");
  const chart = page.locator("[data-testid=km-chart]");
  await expect(chart).toBeVisible();
  // Plot returns the <svg> itself with the testid, or a figure wrapping it
  expect(await chart.evaluate((el) => el.matches("svg") || el.querySelector("svg") !== null)).toBe(true);
  expect(((await chart.getAttribute("aria-label")) ?? "").trim()).not.toBe("");
});
