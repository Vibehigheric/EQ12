import requests
import json

api_key = "ODDS_API_KEY_PLACEHOLDER"
url = f"https://api.the-odds-api.com/v4/sports/americanfootball_nfl/scores/?daysFrom=3&apiKey={api_key}"

response = requests.get(url)
print(json.dumps(response.json(), indent=2))
