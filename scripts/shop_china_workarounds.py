"""
EQ12 SOURCING AGENT: FILTER BYPASS & NO-MOQ MODE
Uses alternative keywords and search parameters to find single-unit items and bypass brand filters.
"""
import webbrowser
import time

def shop_china_workarounds():
    print("🕵️ Launching EQ12 Sourcing Agent (Stealth Mode)...")
    
    # STRATEGY 1: KEYWORD MASQUERADING
    # Instead of "Nike", we search for the specific fabric style ("Tech Fleece") or generic "Designer" terms.
    # This often bypasses the "Brand Name" blocklist while finding the exact same factory items.
    
    # AliExpress: "Tech Fleece Joggers" (The specific style name, often unblocked)
    ali_tech_fleece = "https://www.aliexpress.com/wholesale?catId=0&initiative_id=SB_20251206&SearchText=tech+fleece+joggers+men"
    
    # DHGate: "Designer Sports Pants" (Sellers use 'Designer' to hide logos in thumbnails)
    dhgate_designer = "https://www.dhgate.com/wholesale/search.do?act=search&sus=&searchkey=designer+sports+pants+men"

    # STRATEGY 2: MOQ (MINIMUM ORDER QUANTITY) BYPASS
    # We force Alibaba to show items with "Min Order: 1 Piece"
    
    # Alibaba: "Tech Fleece" + MOQ=1 Filter
    # Note: 'moqt=1' is the parameter for Minimum Order Quantity = 1
    alibaba_no_moq = "https://www.alibaba.com/trade/search?fsb=y&IndexArea=product_en&CatId=&SearchText=tech+fleece+joggers&Moqt=1"

    # STRATEGY 3: THE "HIDDEN LINK" METHOD
    # Sellers post generic items on AliExpress but share the "Real" catalog on Reddit/Yupoo.
    # We search Reddit for the latest "Hidden Link" spreadsheets.
    reddit_hidden = "https://www.google.com/search?q=site%3Areddit.com+aliexpress+nike+joggers+hidden+link+spreadsheet+2025"

    # STRATEGY 4: YUPOO CATALOGS (The "Source" Visual Search)
    # Yupoo is where factories post unedited photos. You find the code here, then buy on Ali/DHGate.
    yupoo_search = "https://www.google.com/search?q=site%3Ayupoo.com+nike+tech+fleece+joggers"

    urls = [ali_tech_fleece, dhgate_designer, alibaba_no_moq, reddit_hidden, yupoo_search]

    for url in urls:
        print(f"Opening: {url}")
        webbrowser.open(url)
        time.sleep(1)

    print("✅ Workarounds deployed.")
    print("1. AliExpress/DHGate: Look for items with NO LOGO in the picture but 'Swoosh' in the reviews.")
    print("2. Alibaba: The 'Moqt=1' filter is active.")
    print("3. Reddit/Yupoo: Use these to find the 'Secret Codes' to search on AliExpress.")

if __name__ == "__main__":
    shop_china_workarounds()
