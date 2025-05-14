from scraper import clean_team_name, get_game_logs, combine_game_logs, read_teams
from rank import TeamRanker
import argparse
import os
import time


def main():
    # Set up command line arguments
    parser = argparse.ArgumentParser(description='Scrape and rank college basketball teams')
    parser.add_argument('--teams-file', default='teams.txt',
                      help='Path to file containing team names (default: teams.txt)')
    parser.add_argument('--year', type=int, default=2025,
                      help='Year to scrape data for (default: 2025)')
    args = parser.parse_args()
    
    # Read teams from file
    try:
        teams = read_teams(args.teams_file)
        print(f"Loaded {len(teams)} teams from {args.teams_file}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return
    
    # Create results directory if it doesn't exist
    os.makedirs("results", exist_ok=True)
    
    # Scrape game logs for each team
    completed = []
    for team in teams:
        low_team = team.strip().lower().replace(" ", "-")  # Fix spaces in URLs
        get_game_logs(low_team, args.year, completed)
        completed.append(low_team)
        time.sleep(10)
    
    # Combine all game logs
    combine_game_logs()
    
    # Initialize ranker and get rankings
    ranker = TeamRanker()
    rankings = ranker.get_ranks(normalize=True)
    print("\nTeam Rankings:")
    for team, rank in rankings:
        print(f"{team}: {rank:.6f}")

if __name__ == "__main__":
    main() 