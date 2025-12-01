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

def collect_data(team, pos):
    base_url = "https://www.fangraphs.com/leaders/minor-league?pos={pos}&level=0&lg=2,4,5,6,7,8,9,10,11,14,12,13,15,16,17,18,30,32&stats=bat&qual=50&type=0&team={team}&season=2025&seasonEnd=2025&org=15&ind=0&splitTeam=false&players=&sort=23,1&pg=0";

    response = requests.get(base_url)
    response.raise_for_status()
    html = response.text

    soup = BeautifulSoup(html, "html.parser")
    
    section = soup.find("div", class_="table_fixed", )
    if not section:
        raise ValueError("could not find table")
    
    table = section.find_next("table")
    headers = [th.get_text(strip=True) for th in table.find_all("th")]
    print(headers)
    
    rows = []
    for tr in table.find_all("tr"):
        cells = tr.find_all("td")
        if cells:
            rows.append([cell.get_text(strip=True) for cell in cells])

    df = pd.DataFrame(rows, columns=headers)
    print(df.head())


collect_data("all")



