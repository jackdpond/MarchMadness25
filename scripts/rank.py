import pandas as pd
import networkx as nx
import scipy as sp
import matplotlib.pyplot as plt

class TeamRanker:
    def __init__(self, games_file="results/all_games.csv"):
        """Initialize the ranker with game data and compute PageRank values."""
        # Read the game data
        self.df = pd.read_csv(games_file)
        
        # Create a directed graph
        self.G = nx.DiGraph()
        
        # Add edges based on game outcomes
        for _, row in self.df.iterrows():
            winner = row['winner']
            loser = row['loser']
            if pd.notna(winner) and pd.notna(loser):
                self.G.add_edge(loser, winner)
        
        # Compute PageRank
        self.ranks = nx.pagerank(self.G)
    
    def get_ranks(self, normalize=False):
        """Get sorted list of teams by PageRank value.
        
        Args:
            normalize (bool): If True, scales scores so highest is 1 and lowest is 0
        """
        ranks = sorted(self.ranks.items(), key=lambda x: x[1], reverse=True)
        if normalize:
            min_rank = ranks[-1][1]
            max_rank = ranks[0][1]
            range_rank = max_rank - min_rank
            ranks = [(team, (score - min_rank) / range_rank) for team, score in ranks]
        return ranks
    
    def versus(self, team1, team2):
        """Compare two teams based on their PageRank values."""
        team1_rank = self.ranks.get(team1, 0)
        team2_rank = self.ranks.get(team2, 0)
        
        if team1_rank > team2_rank:
            return team1
        else:
            return team2
    
    def get_rank(self, team):
        """Get the PageRank value for a specific team."""
        return self.ranks.get(team, 0)
        
    def save_graph(self, output_file="graph.png"):
        """Save a visualization of the game graph.
        
        Args:
            output_file (str): Path to save the graph image
        """
        plt.figure(figsize=(8, 8))
        nx.draw(self.G, node_color='green', 
                edge_color='black', node_size=1, width=0.5)
        plt.title("Regular Season 2025 Results", fontsize=20)          # Title (larger font)
        plt.suptitle("An edge represents a game, and points to the winner", fontsize=12)   # Subheading above the title
        
        # Save the image
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()  # Close the figure to free memory 