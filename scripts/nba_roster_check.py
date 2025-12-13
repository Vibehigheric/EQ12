import pandas as pd
from nba_api.stats.endpoints import commonteamroster
from nba_api.stats.static import teams

# Team IDs
ATL_ID = 1610612737
DET_ID = 1610612765

def get_and_print_roster(team_id, team_name):
    print(f"\n=== {team_name} Roster (12/12/2025) ===")
    try:
        # Try fetching for the 2025-26 season
        roster = commonteamroster.CommonTeamRoster(team_id=team_id, season='2025-26').common_team_roster.get_data_frame()
        
        if roster.empty:
             # Fallback to default (current)
             roster = commonteamroster.CommonTeamRoster(team_id=team_id).common_team_roster.get_data_frame()

        if roster.empty:
            print("No roster data found.")
            return

        # Select relevant columns
        display_roster = roster[['PLAYER', 'NUM', 'POSITION', 'HEIGHT', 'WEIGHT', 'AGE', 'SCHOOL']]
        print(display_roster.to_string(index=False))
        
    except Exception as e:
        print(f"Error fetching roster: {e}")

def main():
    print("Fetching Rosters for ATL vs DET...")
    get_and_print_roster(ATL_ID, "Atlanta Hawks")
    get_and_print_roster(DET_ID, "Detroit Pistons")

if __name__ == "__main__":
    main()
