# Future Roadmap: n8n + ChatGPT Automation

**Status**: DEFERRED (Phase 2)
**Priority**: Low (Until Betting Engine V1 is live)

## Concept
Combine n8n (workflow automation) with ChatGPT (reasoning) to handle complex, multi-step logic that doesn't require custom Python code.

## Potential Workflows (Post-V1)

### 1. Deal-Alert Engine
- **Trigger**: API poll (Housing/Travel/Hemp).
- **Process**: GPT filters for "Good Deals".
- **Action**: Telegram alert.

### 2. Content Funnel (Hemp/CBD)
- **Trigger**: New product drop.
- **Process**: GPT writes blog/social copy.
- **Action**: Post to CMS.

### 3. Travel Concierge
- **Trigger**: User request.
- **Process**: Scrape flight/hotel -> GPT itinerary.
- **Action**: Email user.

### 4. Lead Qualification
- **Trigger**: New CRM entry.
- **Process**: GPT scores lead.
- **Action**: Route to sales/nurture.

### 5. Dashboarding
- **Trigger**: Weekly schedule.
- **Process**: Aggregate stats -> GPT summary.
- **Action**: Slack report.

## Why Deferred?
- **Constraint**: "No new infra/tools until V1 runs daily."
- **Focus**: Betting Engine V1 (Python) is the current priority.
