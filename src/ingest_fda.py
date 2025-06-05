import pandas as pd
import asyncio
from playwright.async_api import async_playwright

FDA_URL = "https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm?event=report.page"

async def fetch_fda_report():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(FDA_URL, timeout=60000)

        await page.wait_for_selector("h4", timeout=15000)

        # Evaluate in page context
        results = await page.evaluate("""
        () => {
            const data = [];
            const headers = document.querySelectorAll("h4");
            headers.forEach(header => {
                const date = header.innerText.trim();
                let wrapper = header.nextElementSibling;
                while (wrapper && !wrapper.querySelector("table")) {
                    wrapper = wrapper.nextElementSibling;
                }
                const table = wrapper?.querySelector("table");
                if (!table) return;

                const rows = table.querySelectorAll("tbody tr");
                rows.forEach(row => {
                    const cells = Array.from(row.querySelectorAll("td")).map(td => {
                        return td.textContent.trim().replace(/\\n/g, " ").replace(/\\s+/g, " ");
                    });
                    if (cells.length) {
                        data.push([date, ...cells]);
                    }
                });
            });
            return data;
        }
        """)

        if results:
            df = pd.DataFrame(results, columns=[
                "Approval Date", "Drug Name & App #", "Active Ingredient",
                "Dosage Form/Route", "Submission", "Company",
                "Submission Classification", "Submission Status"
            ])
            df.to_csv("data/raw/fda_approvals.csv", index=False)
            print(f"✅ Saved {len(df)} rows to data/raw/fda_approvals.csv")
        else:
            print("❌ No data extracted.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(fetch_fda_report())
