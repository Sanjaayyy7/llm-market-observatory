import {test, expect} from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import {readFileSync} from "node:fs";

const pages = ["index.html", "prices.html", "adoption.html", "methods.html"];

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
  // G5 kill (DECISIONS "G5 kill action"): Home carries no market number in v1.0
  const headline = await page.locator("[data-testid=headline]").innerText();
  expect(headline).toContain("no market estimate");
  expect(headline).not.toMatch(/\d+(\.\d+)?%/);
  expect(await page.locator("main").innerText()).not.toMatch(/\d+(\.\d+)?%/);
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

test("adoption: renders the exported verdict, paths and matched placebo", async ({page}, info) => {
  const study = JSON.parse(readFileSync(new URL("../src/data/event_study.json", import.meta.url), "utf8"));
  await page.goto("index.html");
  // Pages serves the clean URL; the stdlib test server does not, so assert the link and load the built file.
  await expect(page.getByRole("main").getByRole("link", {name: "Adoption", exact: true})).toHaveAttribute("href", "./adoption");
  await page.goto("adoption.html");
  await expect(page.getByTestId("adoption-verdict")).toHaveText(study.verdict);
  await expect(page.getByRole("link", {name: "Pre-registration"})).toHaveAttribute("href", `https://github.com/Sanjaayyy7/llm-market-observatory/commit/${study.prereg_commit}`);

  const paths = page.getByTestId("event-paths");
  await expect(paths.locator('line[aria-label="First cut"]')).toHaveCount(1);
  await expect(paths.locator('path[aria-label$="date path"]')).toHaveCount(study.events.length);
  await expect(page.locator("tbody tr")).toHaveCount(study.events.length);

  const events = study.events.filter((event) => event.ratio != null && event.placebo_share_le != null);
  const hist = page.getByTestId("placebo-histogram");
  const index = events.findLastIndex((event) => event.sdk_group !== events[0].sdk_group);
  const event = events[index];
  const picker = page.getByLabel("Compare cut event");
  await expect(picker.locator("option")).toHaveCount(events.length);
  const firstDomain = await hist.evaluate((chart) => chart.scale("x").domain);
  await picker.selectOption({index});
  await expect(hist).toHaveAttribute("aria-label", new RegExp(`${event.sdk_group}.*${RegExp.escape(event.ratio.toFixed(2))}×`));
  await expect(hist.locator('line[aria-label="Selected cut ratio"]')).toHaveCount(1);
  expect(await hist.evaluate((chart) => chart.scale("x").domain)).not.toEqual(firstDomain);
  await expect(page.getByRole("link", {name: `${event.ratio.toFixed(2)}×`, exact: true}).first()).toHaveAttribute("href", "./methods#adoption");
  for (const cut of study.verified_missed_cuts) {
    await expect(page.getByTestId("adoption-limits")).toContainText(`${cut.model} (${cut.date})`);
  }
  await page.screenshot({path: `test-results/adoption-${info.project.name}.png`, fullPage: true});
});
