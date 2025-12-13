"""
EQ12 SOURCING AGENT: Direct-from-China Market Search
Opens Alibaba, AliExpress, and DHGate to find 'the source' or wholesale options.
"""
import webbrowser
import time

def shop_china_direct():
    print("🌏 Launching EQ12 Sourcing Agent (China Direct)...")
    
    # 1. Alibaba (Wholesale/Factory Source)
    # Note: "Nike" searches may be filtered. Searching for "branded joggers" or specific style codes is often needed.
    alibaba_url = "https://www.alibaba.com/trade/search?fsb=y&IndexArea=product_en&CatId=&SearchText=nike+joggers+men"
    
    # 2. AliExpress (Consumer Direct)
    aliexpress_url = "https://www.aliexpress.com/wholesale?catId=0&initiative_id=SB_20251206&SearchText=nike+joggers+men"

    # 3. DHGate (Known for 'Replica' or 'Grey Market' goods)
    dhgate_url = "https://www.dhgate.com/wholesale/search.do?act=search&sus=&searchkey=nike+joggers+men"

    # 4. Made-in-China (Another factory source)
    mic_url = "https://www.made-in-china.com/productdirectory.do?word=nike+joggers+men&subaction=hunt&style=b&mode=and&code=0&comProvince=nolimit&order=0&isOpenCorrection=1"

    urls = [alibaba_url, aliexpress_url, dhgate_url, mic_url]

    for url in urls:
        print(f"Opening: {url}")
        webbrowser.open(url)
        time.sleep(1)

    print("✅ Sourcing markets opened. WARNING: Verify authenticity carefully on these platforms.")

if __name__ == "__main__":
    shop_china_direct()
