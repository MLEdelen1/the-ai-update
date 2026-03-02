#!/usr/bin/env python3
import json

def get_target_communities():
    return {
        "Reddit": ["r/ArtificialInteligence", "r/SmallBusiness", "r/SideHustle"],
        "LinkedIn": ["AI for Business Group", "Entrepreneur Hub"],
        "Forums": ["IndieHackers", "ProductHunt Discussions"]
    }

def generate_distribution_strategy(topic):
    return f"Strategy for {topic}: Post summary to Reddit, Thread to X, Link to LinkedIn."

if __name__ == "__main__":
    communities = get_target_communities()
    print(f"Targeting {sum(len(v) for v in communities.values())} external growth channels.")
