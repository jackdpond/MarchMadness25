import pandas as pd
import time
import os
from bs4 import BeautifulSoup
import requests
from io import StringIO
import re

def clean_team_name(name):
    """Remove ranking in parentheses anywhere in the team name and format it correctly."""
    name = name.strip()
    name = re.sub(r'\s*\(\d+\)', '', name)  # Remove any ranking (e.g., "Duke (3)" -> "Duke")
    name = name.replace('\xa0', ' ')  # Fix non-breaking spaces
    return name.lower().replace(" ", "-")  # Convert to lowercase and replace spaces with hyphens


def get_game_logs(team, year, completed):
    """Scrape game logs for a given team and year."""
    url = f"https://www.sports-reference.com/cbb/schools/{team}/men/{year}-schedule.html"
    print(url)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to get data for {team} {year}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the game logs table
    table = soup.find('table', {'id': 'schedule'})
    if not table:
        print(f"No schedule found for {team} {year}")
        return None

    # Read the table into a DataFrame using StringIO to avoid deprecation warning
    df = pd.read_html(StringIO(str(table)))[0]
    
    # Drop unnecessary rows and columns
    df = df.dropna(subset=['Date'])  # Remove empty rows
    df = df[['Opponent', 'Tm','Opp']]  # Keep relevant columns
    df.columns = ['opponent', 'team_score', 'opp_score']

    # Convert scores to numeric
    df['team_score'] = pd.to_numeric(df['team_score'], errors='coerce')
    df['opp_score'] = pd.to_numeric(df['opp_score'], errors='coerce')

    # Clean opponent names
    df['opponent'] = df['opponent'].apply(clean_team_name)
    team_name = clean_team_name(team.capitalize())  # Ensure proper format for comparison

    # Create winner and loser columns
    df['winner'] = df.apply(lambda row: team_name if row['team_score'] > row['opp_score'] else row['opponent'], axis=1)
    df['loser'] = df.apply(lambda row: row['opponent'] if row['team_score'] > row['opp_score'] else team_name, axis=1)

    # Now apply clean_team_name() to clean all names properly
    df['winner'] = df['winner'].apply(clean_team_name)
    df['loser'] = df['loser'].apply(clean_team_name)

    # Keep only winner and loser columns
    df = df[['winner', 'loser']]

    df = df[~df['winner'].isin(completed)]
    df = df[~df['loser'].isin(completed)]

    df.to_csv(f'results/{team}_{year}.csv', index=False)

def combine_game_logs():
    """Combine all individual team CSV files into one master file."""
    directory = "results"
    csv_files = [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith(".csv")]
    
    df_list = [pd.read_csv(file) for file in csv_files]
    combined_df = pd.concat(df_list, ignore_index=True)
    
    # Exclude rows containing 'opponent'
    combined_df = combined_df[~combined_df['winner'].str.contains('opponent', case=False, na=False)]
    combined_df = combined_df[~combined_df['loser'].str.contains('opponent', case=False, na=False)]
    
    combined_df.to_csv("results/all_games.csv", index=False)
    print(f"Combined {len(csv_files)} CSV files into 'all_games.csv'.")

def read_teams(teams_file):
    """Read team names from file and clean them."""
    if not os.path.exists(teams_file):
        raise FileNotFoundError(f"Teams file not found: {teams_file}")
    
    with open(teams_file, 'r') as f:
        teams = [line.strip() for line in f if line.strip()]
    
    # Clean team names for URL formatting
    return [clean_team_name(team) for team in teams]