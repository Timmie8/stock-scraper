from playwright.sync_api import sync_playwright
import pandas as pd
import time

tickers = ["AMT", "BHVN", "CCI", "CRTO", "EAF", "HSAI", "KC", "KN", 
           "QMCO", "RDN", "RHI", "RITM", "RNG", "SBAC", "SIGI", "SKHY", "XPEV", "ZLAB"]

results = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)  # True = onzichtbaar, False = zie de browser
    page = browser.new_page()

    for t in tickers:
        print(f"Bezig met {t}...")

        # --- yRobot ---
        try:
            page.goto(f"https://yrobot.us/chart/{t}", wait_until="networkidle", timeout=30000)
            time.sleep(2)
            text = page.inner_text("body")
            
            # Probeer de score te vinden
            yrobot_score = "niet gevonden"
            for line in text.split("\n")[:30]:
                if any(x in line for x in ["Buy", "Sell", "Hold", "Bullish", "Bearish"]):
                    if any(c.isdigit() for c in line):
                        yrobot_score = line.strip()
                        break
        except Exception as e:
            yrobot_score = f"Fout: {e}"

        # --- Vunelix ---
        vunelix_data = "niet gevonden"
        for exchange in ["NASDAQ", "NYSE"]:
            try:
                page.goto(f"https://vunelix.com/symbols/{exchange}-{t}", wait_until="networkidle", timeout=20000)
                time.sleep(2)
                
                # Cookies accepteren als die er zijn
                try:
                    page.click("text=Accept", timeout=2000)
                except:
                    pass

                text = page.inner_text("body")
                if "Trading Signals" in text:
                    # Haal het relevante stuk eruit
                    start = text.find("Trading Signals")
                    vunelix_data = text[start:start+300].replace("\n", " | ")
                    break
            except:
                continue

        results.append({
            "Ticker": t,
            "yRobot": yrobot_score,
            "Vunelix": vunelix_data
        })

    browser.close()

# Maak een mooie tabel
df = pd.DataFrame(results)
print("\n=== RESULTAAT ===")
print(df.to_string())

# Sla op als Excel
df.to_excel("stock_scores.xlsx", index=False)
print("\nBestand opgeslagen als: stock_scores.xlsx")
