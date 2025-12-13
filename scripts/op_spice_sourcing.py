"""
OPERATION SPICE ROUTE: STEP 1 (SOURCING)
Finds packaging suppliers for the seasoning business.
"""
import webbrowser
import time

def run_sourcing():
    print("🌶️  Executing Operation Spice Route: Step 1 (Packaging Sourcing)...")
    
    # 1. Mylar Bags (The "Volume" Packaging)
    # Search for "Stand up pouch", "Matte black", "Custom print"
    # Alibaba is best for this.
    mylar_url = "https://www.alibaba.com/trade/search?fsb=y&IndexArea=product_en&CatId=&SearchText=custom+printed+stand+up+pouch+seasoning+matte+black&Moqt=500"
    
    # 2. Glass Jars (The "Premium" Packaging)
    # Search for "Square spice jars", "Grinder tops"
    glass_url = "https://www.alibaba.com/trade/search?fsb=y&IndexArea=product_en&CatId=&SearchText=square+glass+spice+jars+4oz+wholesale"
    
    # 3. Labels (If buying blank bags/jars)
    # Sticker Mule or Alibaba
    label_url = "https://www.alibaba.com/trade/search?fsb=y&IndexArea=product_en&CatId=&SearchText=custom+roll+labels+for+spice+jars"

    # 4. Co-Packers (The "Hands-Off" Option)
    # Factories that mix AND pack for you.
    copacker_url = "https://www.google.com/search?q=private+label+spice+blends+usa+low+moq"

    urls = [mylar_url, glass_url, label_url, copacker_url]

    for url in urls:
        print(f"Opening: {url}")
        webbrowser.open(url)
        time.sleep(1)

    print("✅ Sourcing tabs opened. Look for:")
    print("   - MOQ < 1000 for starting out.")
    print("   - 'Trade Assurance' suppliers on Alibaba.")

if __name__ == "__main__":
    run_sourcing()
