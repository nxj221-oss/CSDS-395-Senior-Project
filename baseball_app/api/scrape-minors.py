# New way to scrape for minor league data:
# visit the below site
# ensure params are set to batters, min PA/IP = 50, season start = 2025, season end = 2025, level = all
# league = all affiliated minor, minor league team = all
# position and MLB org will be looped through
# https://www.fangraphs.com/leaders/minor-league?pos=all&level=0&lg=2,4,5,6,7,8,9,10,11,14,12,13,15,16,17,18,30,32&stats=bat&qual=50&type=0&team=all&season=2025&seasonEnd=2025&org=15&ind=0&splitTeam=false&players=&sort=23,1&pg=0
# 
# goal: scrape table data for the following columns:
# Name, Age, PO, PA, AB, R, H, 2B, 3B, HR, RBI, BB, SO, SB, CS
#
# we will want to first find the table in html, then using a given position (eg "all" to test)
# we want to save that table as a pandas df, then adjust the columns so they are in the correct
# order (described above)
#
# we can parse html pretty easily using beautiful soup. it's well documented and chat knows it pretty good
# we will need to knit the tables together so that each team has one table with all positions instead of
# many tables with one position


import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
import sys

org_to_id = {
    "los-angeles-angels": 1,
    'baltimore-orioles': 2,
    'boston-red-sox': 3,
    'chicago-white-sox': 4,
    'cleveland-guardians': 5,
    'detroit-tigers': 6,
    'kansas-city-royals': 7,
    'minnesota-twins': 8,
    'new-york-yankees': 9,
    "the-athletics": 10,
    'seattle-mariners': 11,
    'tampa-bay-rays': 12,
    'texas-rangers': 13,
    'toronto-blue-jays': 14,
    'arizona-diamondbacks': 15,
    'atlanta-braves': 16,
    'chicago-cubs': 17,
    'cincinnati-reds': 18,
    'colorado-rockies': 19,
    'miami-marlins': 20,
    "houston-astros": 21,
    'los-angeles-dodgers': 22,
    'milwaukee-brewers': 23,
    'washington-nationals': 24,
    'new-york-mets': 25,
    'philadelphia-phillies': 26,
    'pittsburgh-pirates': 27,
    'st.-louis-cardinals': 28,
    'san-diego-padres': 29,
    'san-francisco-giants': 30,
}

def collect_data(team, pos):
    # AAA
    base_url = f"https://www.fangraphs.com/api/leaders/minor-league/data?pos={pos}&level=1&lg=2,4,5,6,7,8,9,10,11,14,12,13,15,16,17,18,30,32&stats=bat&qual=50&type=0&team=all&season=2025&seasonEnd=2025&org={org_to_id[team]}&ind=0&splitTeam=false"
    
    aaa = pd.read_json(base_url)
    aaa = aaa.filter(['PlayerName', 'Age', 'PO', 'PA', 'AB', 'R', 'H', '2B', '3B', 'HR', 'RBI', 'BB', 'SO', 'SB', 'CS'], axis=1)
    aaa = aaa.rename(columns={"PlayerName": "Name"})

    output_path = f"scraped_data/{team}-AAA.csv"
    aaa.to_csv(output_path, index=False)

    # AA
    base_url = f"https://www.fangraphs.com/api/leaders/minor-league/data?pos={pos}&level=2&lg=2,4,5,6,7,8,9,10,11,14,12,13,15,16,17,18,30,32&stats=bat&qual=50&type=0&team=all&season=2025&seasonEnd=2025&org={org_to_id[team]}&ind=0&splitTeam=false"
    
    aa = pd.read_json(base_url)
    aa = aa.filter(['PlayerName', 'Age', 'PO', 'PA', 'AB', 'R', 'H', '2B', '3B', 'HR', 'RBI', 'BB', 'SO', 'SB', 'CS'], axis=1)
    aa = aa.rename(columns={"PlayerName": "Name"})

    output_path = f"scraped_data/{team}-AA.csv"
    aa.to_csv(output_path, index=False)

    # A+
    base_url = f"https://www.fangraphs.com/api/leaders/minor-league/data?pos={pos}&level=3&lg=2,4,5,6,7,8,9,10,11,14,12,13,15,16,17,18,30,32&stats=bat&qual=50&type=0&team=all&season=2025&seasonEnd=2025&org={org_to_id[team]}&ind=0&splitTeam=false"
    
    ap = pd.read_json(base_url)
    ap = ap.filter(['PlayerName', 'Age', 'PO', 'PA', 'AB', 'R', 'H', '2B', '3B', 'HR', 'RBI', 'BB', 'SO', 'SB', 'CS'], axis=1)
    ap = ap.rename(columns={"PlayerName": "Name"})

    output_path = f"scraped_data/{team}-A+.csv"
    ap.to_csv(output_path, index=False)

    # A
    base_url = f"https://www.fangraphs.com/api/leaders/minor-league/data?pos={pos}&level=4&lg=2,4,5,6,7,8,9,10,11,14,12,13,15,16,17,18,30,32&stats=bat&qual=50&type=0&team=all&season=2025&seasonEnd=2025&org={org_to_id[team]}&ind=0&splitTeam=false"
    
    a = pd.read_json(base_url)
    a = a.filter(['PlayerName', 'Age', 'PO', 'PA', 'AB', 'R', 'H', '2B', '3B', 'HR', 'RBI', 'BB', 'SO', 'SB', 'CS'], axis=1)
    a = a.rename(columns={"PlayerName": "Name"})

    output_path = f"scraped_data/{team}-A.csv"
    a.to_csv(output_path, index=False)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python scrapeFangraphs.py [location-team] [position]")
        sys.exit(1)

    collect_data(sys.argv[1], sys.argv[2])


