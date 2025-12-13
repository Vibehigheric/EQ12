import requests

# Check available markets
r = requests.get(
    "https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds",
    params={
        "apiKey": "8eb822610b7753d45f76dcac8230a7d1",
        "regions": "us",
        "markets": "h2h",
    },
)

print("Status:", r.status_code)
games = r.json()

if games:
    print("Sample game structure:")
    game = games[0]
    print(f"Game: {game.get('away_team')} @ {game.get('home_team')}")

    if "bookmakers" in game:
        print("Available markets:")
        for book in game["bookmakers"][:1]:  # Just check first bookmaker
            for market in book.get("markets", []):
                print(f"  - {market.get('key', 'unknown')}")

    # Try to get player props separately
    print("\nTrying player props...")
    try:
        r2 = requests.get(
            "https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds",
            params={
                "apiKey": "8eb822610b7753d45f76dcac8230a7d1",
                "regions": "us",
                "markets": "player_anytime_td",
            },
        )
        print(f"Player TD Status: {r2.status_code}")
        if r2.status_code == 200:
            print("Player TD props available!")
        else:
            print("Player TD error:", r2.text)
    except Exception as e:
        print("Error checking player props:", e)
else:
    print("No games found")
