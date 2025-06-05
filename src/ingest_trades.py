import requests
import pandas as pd

def fetch_capitol_trades(pages=5):
    base_url = "https://www.capitoltrades.com/api/trades"
    all_trades = []

    for page in range(1, pages + 1):
        url = f"{base_url}?page={page}"
        resp = requests.get(url)
        if resp.status_code != 200:
            print(f"Error on page {page}")
            continue
        data = resp.json()["data"]
        for trade in data:
            all_trades.append({
                "politician": trade["politician"],
                "transaction_date": trade["transactionDate"],
                "ticker": trade["ticker"],
                "asset_type": trade["assetType"],
                "amount": trade["amount"],
                "type": trade["type"],
                "disclosure_date": trade["disclosureDate"],
                "chamber": trade["chamber"]
            })

    df = pd.DataFrame(all_trades)
    df.to_csv("data/raw/politician_trades.csv", index=False)
    print(f"Saved {len(df)} trades to data/raw/politician_trades.csv")

if __name__ == "__main__":
    fetch_capitol_trades()
