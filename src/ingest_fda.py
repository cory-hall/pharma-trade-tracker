import pandas as pd
import asyncio
from playwright.async_api import async_playwright

async def fetch_fda_data(month="June", year="2025"):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Set to True if stable
        page = await browser.new_page()

        url = "https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm?event=report.page"
        await page.goto(url, timeout=60000)

        # Select "All Approvals and Tentative Approvals by Month"
        await page.check('input[value="1"]')

        # Select month/year
        await page.select_option('select[name="month"]', label=month)
        await page.select_option('select[name="year"]', label=year)

        # Click "Search"
        await page.click('input[value="Search"]')

        # Wait for results table or any date header
        await page.wait_for_selector("h3", timeout=15000)

        # Get all h3 date headers
        headers = await page.locator("h3").all()

        all_rows = []

        for header in headers:
            date_text = await header.inner_text()
            # Use XPath to find the next <table> after this <h3>
            table = await header.evaluate_handle("""
                el => {
                    let next = el.nextElementSibling;
                    while (next && next.tagName !== 'TABLE') {
                        next = next.nextElementSibling;
                    }
                    return next;
                }
            """)
            if not table:
                continue
            rows = await table.query_selector_all("tbody tr")

            for row in rows:
                cols = await row.query_selector_all("td")
                values = [await col.inner_text() for col in cols]
                if values:
                    all_rows.append([date_text] + values)

        await browser.close()

        if all_rows:
            df = pd.DataFrame(all_rows, columns=[
                "Approval Date", "Drug & Application", "Active Ingredient",
                "Dosage Form/Route", "Submission", "Company",
                "Submission Classification", "Submission Status"
            ])
            df.to_csv("data/raw/fda_approvals.csv", index=False)
            print(f"✅ Saved {len(df)} rows to data/raw/fda_approvals.csv")
        else:
            print("❌ No data extracted.")

if __name__ == "__main__":
    asyncio.run(fetch_fda_data())
