# 📅 EQ12 Edge Kiosk Rotation — Import Instructions

## 🚀 Quick Setup

Import all three rotation schedules into Windows Task Scheduler:

```powershell
# Import all three XML schedules at once
schtasks /create /xml "C:\EQ12\edge_kiosk_parlay_morning.xml" /tn "EQ12_EdgeKiosk_Parlay_Morning"
schtasks /create /xml "C:\EQ12\edge_kiosk_deals_afternoon.xml" /tn "EQ12_EdgeKiosk_Deals_Afternoon"
schtasks /create /xml "C:\EQ12\edge_kiosk_sales_evening.xml" /tn "EQ12_EdgeKiosk_Sales_Evening"
```

**Or import manually:**
1. Open Task Scheduler → `Action > Import Task...`
2. Import each XML file
3. Update the ngrok URL in each task if needed

---

## ⏰ Rotation Schedule

| **Time** | **Dashboard** | **Focus** |
|----------|---------------|-----------|
| **6:00 AM - 12:00 PM** | `/tv/parlay` | Morning betting analysis |
| **12:00 PM - 6:00 PM** | `/tv/deals` | Afternoon travel/sales |
| **6:00 PM - 12:00 AM** | `/tv/sales` | Evening revenue tracking |

---

## 🔧 Customization

### Change URLs
Edit each XML and replace `http://localhost:8080/tv/parlay` with your ngrok URL:
```
https://xxxx.ngrok-free.app/tv/parlay
```

### Change Schedule
Modify `<StartBoundary>` times:
- Morning: `2025-01-01T06:00:00` (6 AM)
- Afternoon: `2025-01-01T12:00:00` (12 PM)
- Evening: `2025-01-01T18:00:00` (6 PM)

### Test Manual Launch
```powershell
# Test each dashboard manually
schtasks /run /tn "EQ12_EdgeKiosk_Parlay_Morning"
schtasks /run /tn "EQ12_EdgeKiosk_Deals_Afternoon"
schtasks /run /tn "EQ12_EdgeKiosk_Sales_Evening"
```

---

## ✅ Result
Your EQ12 will now automatically rotate through **parlay → deals → sales** dashboards throughout the day in full-screen Edge kiosk mode.

Perfect for:**
- Multi-monitor wallboard setups
- Automated daily dashboards
- Hands-free Apple TV-style command center
