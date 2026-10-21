import { defineConfig, devices } from "@playwright/test";
export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  workers: 1,
  timeout: 60000,
  expect: { timeout: 10000 },
  reporter: "list",
  use: {
    baseURL: "http://127.0.0.1:13000",
    actionTimeout: 15000,
    trace: "retain-on-failure",
    launchOptions: {
      executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH,
    },
  },
  projects: [
    {
      name: "chromium",
      use: {
        ...devices["Desktop Chrome"],
        viewport: { width: 1440, height: 1000 },
      },
    },
  ],
  webServer: [
    {
      command:
        "cd ../backend && UI_E2E_ENABLED=1 PYTHONPATH=. ../.venv/bin/python tests/ui_server.py",
      url: "http://127.0.0.1:18000/health",
      reuseExistingServer: false,
      timeout: 30000,
    },
    {
      command: process.env.UI_E2E_PRODUCTION === "1" ? "npm run start -- --port 13000" : "npm run dev -- --port 13000",
      url: "http://127.0.0.1:13000",
      env: {
        BACKEND_URL: "http://127.0.0.1:18000",
        NEXT_PUBLIC_EMAIL_DELIVERY_ENABLED: "false",
        NEXT_TELEMETRY_DISABLED: "1",
      },
      reuseExistingServer: false,
      timeout: 60000,
    },
  ],
});
