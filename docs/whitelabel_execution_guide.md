# 💼 EQ12 Whitelabel Execution Guide: "Selling the Bot"

**Objective**: Sell a custom, automated AI Betting Bot to an existing sports influencer for **$500 - $1,000 setup + $100/mo**.

---

## Phase 1: The Hunt (Prospecting)
**Target Audience**:
*   **Twitter/X Cappers**: Look for accounts with 1k-50k followers who post manual picks.
*   **Telegram Channel Owners**: Look for "VIP" channels that promise daily wins.
*   **Instagram Sports Pages**: Pages that post highlights but want to monetize via betting.

**Keywords to Search**:
*   "DM for VIP"
*   "Sports Picks"
*   "Betting Lock"
*   "Capper"

## Phase 2: The Bait (The "Godfather" Offer)
Do not ask for money. Offer value first.

**The Cold DM Script**:
> "Hey [Name], huge fan of your NFL picks.
>
> I’m a developer building AI automation for sports bettors. I just ran my 'Smart Money' engine on this week's slate and it flagged **[Team Name]** as a massive value play.
>
> I can set up a bot that auto-posts these kinds of AI insights directly to your VIP channel 24/7, so you don't have to stare at odds all day.
>
> Want me to send you a demo for this weekend's games? No cost."

## Phase 3: The Hook (The Demo)
When they say "Sure" or "How much?":

1.  **Run the Engine**: Use `python betting_engine_v1/src/gpt_analyzer.py` to get the latest picks.
2.  **Format the Output**: Make it look pretty (use the emojis from our n8n workflow).
3.  **Send it**: "Here is what the bot would have posted automatically at 10 AM today: [Insert Pick]. It saves you ~10 hours a week of research."

## Phase 4: The Close (The Deal)
**The Pitch**:
> "I can install this engine for you. It runs on my private server.
>
> **What you get:**
> 1. Custom AI Bot posting to your Telegram.
> 2. Your branding (e.g., 'The [Name] AI Algo').
> 3. 24/7 Uptime.
>
> **Price:** normally $1,500 setup, but I'll do it for **$500** if I can use you as a testimonial. Plus $100/mo for server costs."

## Phase 5: The Delivery (Technical Execution)
Once they pay:

1.  **Create a Telegram Bot**: Use `@BotFather` on Telegram to create a new bot (e.g., `@[Name]AlgoBot`). Get the Token.
2.  **Add to Channel**: Have the client add that bot to their Channel as an Admin.
3.  **Configure n8n**:
    *   Open `workflow_americanfootball_nfl_safe_lock.json` (or whatever sport they want).
    *   Update the `Telegram Alert` node with their **Chat ID** and **Bot Token**.
    *   Customize the text to say "⚡ [Client Name] AI Algo says:..."
4.  **Deploy**: Activate the workflow on your Lenovo Cluster.

**Result**: You now have a recurring revenue stream and a powerful testimonial.
