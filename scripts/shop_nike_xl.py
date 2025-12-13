"""
EQ12 DEAL HUNTER: Nike Joggers (Size XL)
Opens the best market feeds sorted by LOWEST PRICE.
"""
import webbrowser
import time

def shop_nike_xl():
    print("🚀 Launching EQ12 Deal Hunter for Nike Joggers (XL)...")
    
    # 1. Google Shopping (Aggregator) - Sorted by Price (Low to High)
    # tbs=vw:g,mr:1,price:1,ppr_min:20 (Filter junk under $20),cat:208 (Pants)
    google_url = "https://www.google.com/search?q=nike+joggers+men+size+xl&tbm=shop&tbs=vw:g,mr:1,price:1,ppr_min:20,cat:208&sxsrf=ALiCzsZ"
    
    # 2. Dick's Sporting Goods - Sort: Price Low to High
    dicks_url = "https://www.dickssportinggoods.com/search/SearchDisplay?searchTerm=nike%20joggers%20men&storeId=15108&catalogId=12301&langId=-1&sType=SimpleSearch&resultCatEntryType=2&showResultsPage=true&fromPage=Search&searchSource=Q&pageView=grid&beginIndex=0&DSG_Size=XL&orderBy=3"

    # 3. Kohl's - Sort: Price Low-High
    kohls_url = "https://www.kohls.com/catalog/mens-nike-joggers-sweatpants-bottoms-clothing.jsp?CN=Gender:Mens+Brand:Nike+Silhouette:Joggers+Category:Sweatpants+Category:Bottoms+Category:Clothing+Size:XL&S=4"

    # 4. Nike.com - Sale Section (XL)
    nike_url = "https://www.nike.com/w/mens-sale-joggers-sweatpants-3ya77z6p6bezn5w?sort=priceAsc"

    # 5. Amazon - Prime, 4 Stars+, Price Low to High
    amazon_url = "https://www.amazon.com/s?k=nike+joggers+men+xl&i=fashion-mens-clothing&rh=n%3A7141123011%2Cp_89%3ANike%2Cp_72%3A2661618011&s=price-asc-rank"

    urls = [google_url, dicks_url, kohls_url, nike_url, amazon_url]

    for url in urls:
        print(f"Opening: {url}")
        webbrowser.open(url)
        time.sleep(1)

    print("✅ All markets opened. Check your browser tabs.")

if __name__ == "__main__":
    shop_nike_xl()
