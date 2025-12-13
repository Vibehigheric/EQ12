"""
EQ12 REP FINDER BOT
Automates the "Hidden Link" and "Secret Code" discovery process.
Searches Reddit Spreadsheets, Yupoo Catalogs, and Rep Archives.
"""
import webbrowser
import urllib.parse
import sys
import time

def find_reps(query):
    encoded_query = urllib.parse.quote(query)
    
    print(f"🕵️  EQ12 REP FINDER: Hunting for '{query}'...")
    print("----------------------------------------------------")
    
    # 1. Reddit Spreadsheet Search (The Gold Mine)
    # Searches for Google Sheets shared on Rep subreddits containing the item.
    # These spreadsheets usually contain the "Secret Code" and the direct AliExpress link.
    reddit_sheets = f"https://www.google.com/search?q=site%3Areddit.com+%22google.com%2Fspreadsheets%22+%22{encoded_query}%22+aliexpress"
    
    # 2. Yupoo Image Search (The Source Catalog)
    # Factories upload real photos to Yupoo. The album title often contains the code.
    yupoo = f"https://www.google.com/search?q=site%3Ayupoo.com+%22{encoded_query}%22"
    
    # 3. RepArchive (Dedicated Search Engine)
    # A tool that indexes these hidden items.
    reparchive = f"https://reparchive.com/search?q={encoded_query}&s=taobao" # Taobao/Weidian focus, but good for codes
    
    # 4. TikTok "Hidden Link" Search (Visual Proof)
    # TikTokers often post videos of the item with the code in the comments.
    tiktok = f"https://www.tiktok.com/search?q={encoded_query}%20hidden%20link%20code"

    # 5. AliExpress "Code" Search (Direct Attempt)
    # Sometimes searching "Brand + Code" works if you guess the code format, 
    # but here we search for pages discussing the codes.
    ali_code_search = f"https://www.google.com/search?q=aliexpress+hidden+link+code+%22{encoded_query}%22"

    urls = [reddit_sheets, yupoo, reparchive, tiktok, ali_code_search]
    
    for i, url in enumerate(urls):
        print(f"[{i+1}/5] Opening Search Vector...")
        webbrowser.open(url)
        time.sleep(1)

    print("\n✅ BOT EXECUTION COMPLETE.")
    print("----------------------------------------------------")
    print("👉 STRATEGY GUIDE:")
    print("1. REDDIT TABS: Look for 'Spreadsheet' links. Open them (Google Sheets).")
    print("   - Ctrl+F in the sheet for your item.")
    print("   - Click the 'AliExpress' link in that row.")
    print("2. YUPOO TABS: Look for an album with the photo you want.")
    print("   - The title might say something like '9982' or 'NK-Jogger'.")
    print("   - Search that code on AliExpress.")
    print("3. TIKTOK: Look for videos showing the item. The code is usually in the video overlay.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        user_query = " ".join(sys.argv[1:])
    else:
        print("Enter the item you want to find (e.g., 'Nike Tech Fleece', 'Rolex Submariner'):")
        user_query = input("> ")
    
    if user_query:
        find_reps(user_query)
