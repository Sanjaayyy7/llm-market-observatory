import {defineConfig} from "@playwright/test";

const desktop = {viewport: {width: 1280, height: 800}};

export default defineConfig({
  testDir: "tests",
  outputDir: "test-results",
  reporter: [["list"]],
  webServer: {
    stdout: "ignore",
    stderr: "ignore",
    // stdlib http.server with a bigger listen backlog (default 5 resets connections under page load)
    command: `uv run python -c "import functools as f, http.server as h; h.ThreadingHTTPServer.request_queue_size = 128; h.test(f.partial(h.SimpleHTTPRequestHandler, directory='dist'), h.ThreadingHTTPServer, port=4173, bind='127.0.0.1')"`,
    url: "http://127.0.0.1:4173/index.html",
    reuseExistingServer: false
  },
  use: {baseURL: "http://127.0.0.1:4173"},
  projects: [
    {name: "desktop", use: desktop},
    {name: "mobile", use: {viewport: {width: 375, height: 812}}},
    {name: "desktop-dark", use: {...desktop, colorScheme: "dark"}}
  ]
});
