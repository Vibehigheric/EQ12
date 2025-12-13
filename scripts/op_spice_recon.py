"""
OPERATION SPICE ROUTE: STEP 2 (RECON)
Opens competitor product pages to analyze negative reviews.
"""
import webbrowser
import time

def run_recon():
    print("🕵️  Executing Operation Spice Route: Step 2 (Competitor Recon)...")
    
    # 1. McCormick Taco Seasoning (The King to Dethrone)
    # Focus: Read 1-3 star reviews. Look for "Too salty", "MSG", "Bland".
    mccormick_url = "https://www.amazon.com/McCormick-Original-Taco-Seasoning-Mix/product-reviews/B0009P683C/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&filterByStar=critical&reviewerType=all_reviews&pageNumber=1"
    
    # 2. Blackstone Burger Seasoning (The Premium Rival)
    # Focus: Look for "Clumping", "Overpriced", "Artificial taste".
    blackstone_url = "https://www.amazon.com/Blackstone-1544-Seasoning-Classic-Burger/product-reviews/B079V1B6Z8/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&filterByStar=critical&reviewerType=all_reviews&pageNumber=1"
    
    # 3. Dan-O's Seasoning (The Viral Competitor)
    # Focus: See what people dislike about the "Low Sodium" trend.
    danos_url = "https://www.amazon.com/Dan-Os-Seasoning-Natural-Friendly-Purpose/product-reviews/B083C4P53F/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&filterByStar=critical&reviewerType=all_reviews&pageNumber=1"

    urls = [mccormick_url, blackstone_url, danos_url]

    for url in urls:
        print(f"Opening: {url}")
        webbrowser.open(url)
        time.sleep(1)

    print("✅ Recon tabs opened (Filtered to CRITICAL reviews).")
    print("👉 TASK: Copy recurring complaints into 'reports/spice_competitor_analysis.md'.")

if __name__ == "__main__":
    run_recon()
