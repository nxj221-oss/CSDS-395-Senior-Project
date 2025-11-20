import time
from flask import Flask
import pandas as pd

app = Flask(__name__)

def formatTeamName(x):
  if str(x).endswith('.csv'):
    return str(x).replace('.csv', '').replace('-', ' ').title()
  return x

@app.route('/api/playerData')
def get_player_data():
   df = pd.read_csv('../aggregated_data/all_players_MLB_formatted.csv')
   df = df.rename(columns={"team.csv": "team"})
   df = df.map(lambda x: formatTeamName(x))
   return df.to_json(orient='records', lines=False)

@app.route('/api/time')
def get_current_time():
    return {'time': time.time()}

@app.route('/api/examplePlayerData')
def get_example_player_data():
    return [{
    'id': 1,
    'playerName': 'Konnor Griffin',
    'team': 'Pittsburg Pirates',
    'age': 19,
    'level': 'AA',
    'position': 'SS',
  },
  {
    'id': 2,
    'playerName': 'Kevin McGonigle',
    'team': 'Erie SeaWolves',
    'age': 21,
    'level': 'AA',
    'position': 'SS',
  },
  {
    'id': 3,
    'playerName': 'Leo De Vries',
    'team': 'Midland RockHounds',
    'age': 18,
    'level': 'AA',
    'position': 'SS',
  },
  {
    'id': 4,
    'playerName': 'Josue Briceño',
    'team': 'Erie SeaWolves',
    'age': 21,
    'level': 'AA',
    'position': '1B',
  },
  {
    'id': 5,
    'playerName': 'Travis Bazzana',
    'team': 'Columbus Clippers',
    'age': 23,
    'level': 'AAA',
    'position': '2B',
  },
  {
    'id': 6,
    'playerName': 'Alfredo Duno',
    'team': 'Daytona Tortugas',
    'age': 19,
    'level': 'A',
    'position': 'C',
  },
  {
    'id': 7,
    'playerName': 'Walker Jenkins',
    'team': 'St. Paul Saints',
    'age': 20,
    'level': 'AAA',
    'position': 'OF',
  },
  {
    'id': 8,
    'playerName': 'Eduardo Quintero',
    'team': 'Great Lakes Loons',
    'age': 20,
    'level': 'A+',
    'position': 'OF',
  }]