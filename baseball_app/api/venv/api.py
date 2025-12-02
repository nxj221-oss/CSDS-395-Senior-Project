import time
from flask import Flask
import pandas as pd

app = Flask(__name__)

def formatLevel(row):
  list = str(row.team).replace('.csv', '').split('-')
  return list.pop(len(list)-1)

def formatTeamName(x):
  if str(x).endswith('.csv'):
    return str(x).replace('.csv', '').replace('MLB', '').replace('AAA', '').replace('AA', '').replace('A+', '').replace('A', '').replace('Rookie', '').replace('-', ' ').title()
  return x

@app.route('/api/playerData')
def get_player_data():
   # get data
   df = pd.read_csv('../algorithm_output/all_players_sorted.csv')

   # format team column and add level column
   df['level'] = df.apply(lambda row: formatLevel(row), axis = 1)
   df = df.map(lambda x: formatTeamName(x))

   # handle duplicate players --> average metrics into one entry weighted based off AB(at bats)
   duplicates = df[df.duplicated(subset='Player')]
   df = df.drop_duplicates(subset='Player')
   for r in df.itertuples():
    if duplicates['Player'].str.contains(r.Player).any():
      for d in duplicates.itertuples():
        if d.Player == r.Player:
          dweight = d.AB/(d.AB + r.AB)
          rweight = r.AB/(d.AB + r.AB)
          # average the metrics
          df.at[r.Index, 'combined'] = ((d.combined*dweight) + (r.combined*rweight))
          df.at[r.Index, 'perf'] = ((d.perf*dweight) + (r.perf*rweight))
          df.at[r.Index, 'use'] = ((d.use*dweight) + (r.use*rweight))
          # format AB (adding the at bats will allow more than just one duplicate to be successfully averaged)
          df.at[r.Index, 'AB'] = d.AB + r.AB
          # format level
          if d.level != r.level:
            df.at[r.Index, 'level'] = d.level + " / " + r.level
          # format team names if there are multiple
          if d.team != r.team:
            df.at[r.Index, 'team'] = d.team + " / " + r.team

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