import pandas as pd 
import requests 
from bs4 import BeautifulSoup
from sqlite3 import connect
import itertools
import numpy as np

def get_redirect_url(url, year):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    # find dropdown class
    dropdown = soup.find_all(lambda tag: tag.name == 'div' and 
                               tag.get('class') == ['dropdown'])[0]

    # find bp3-menu div that is a child of that class
    menu = dropdown.find_all(lambda tag: tag.name == 'div' and 
                               tag.get('class') == ['bp3-menu'])[0]

    # got to (2023 - date)th a class="bp3-menu-item" and copy href
    years = menu.find_all(class_='bp3-menu-item')
    cur_year_href = years[2023 - year]['href']
    new_url = f'https://sofifa.com{cur_year_href}'
    return new_url

def get_roster(url, year):
    url = get_redirect_url(url, year)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    table = soup.find_all(lambda tag: tag.name == 'table')[0]
    starting_rows = table.find_all('tr', class_='starting')
    subs_rows = table.find_all('tr', class_='sub')
    starters, subs = list(), list()
    for i, group in enumerate(itertools.chain([starting_rows, subs_rows])):
        for player in group:
            # get player_fifa_api_id
            name_tag = player.find('td', class_='col-name')
            fifa_api_id = name_tag.find('a')['href'].split('/')[2]
            if i == 0:
                starters.append(fifa_api_id)
            else:
                subs.append(fifa_api_id)
    return starters, subs

def scrape():
    URL = 'https://sofifa.com/team/'
    conn = connect('./database/database.sqlite')
    matches_df = pd.read_sql('SELECT * FROM Match', conn)
    teams_df = pd.read_sql('SELECT * FROM Team', conn)
    teams_df = teams_df[teams_df['team_fifa_api_id'].notna()]
    res_rows = []
    max_subs = 0
    for idx, row in matches_df.iterrows():
        if idx % 1000 == 0:
            print(idx)
        home_api_id = row['home_team_api_id']
        away_api_id = row['away_team_api_id']
        match_year = row['date'].split('-')[0]
        # print(home_api_id, away_api_id)
        home_fifa_api_id, away_fifa_api_id = None, None
        if (len(teams_df[teams_df['team_api_id'] == home_api_id]) > 0):
            rows = teams_df[teams_df['team_api_id'] == home_api_id]
            home_fifa_api_id = rows['team_fifa_api_id'].iloc[0].astype('int')
        if (len(teams_df[teams_df['team_api_id'] == away_api_id]) > 0):
            rows = teams_df[teams_df['team_api_id'] == away_api_id]
            away_fifa_api_id = rows['team_fifa_api_id'].iloc[0].astype('int')
        

        if home_fifa_api_id != None and away_fifa_api_id != None:
            # go to sofifa and scrape roster
            home_url = URL + str(home_fifa_api_id)
            away_url = URL + str(away_fifa_api_id)
            home_starter, home_sub = get_roster(home_url, int(match_year))
            away_starter, away_sub = get_roster(away_url, int(match_year))
            max_subs = max(max_subs, max(len(home_sub), len(away_sub)))
            home_row = [row['id'], 1] + home_starter + home_sub 
            away_row = [row['id'], 0] + away_starter + away_sub
            res_rows.append(home_row)
            res_rows.append(away_row)
            # if idx > 5: break
    df = pd.DataFrame(res_rows)
    start_cols = [f'starting_{i}' for i in range(1, 12)]
    num_cols = len(df.columns)
    sub_cols = [f'sub_{i}' for i in range(1, num_cols - 12)]
    df.columns = ['id', 'home'] + start_cols + sub_cols
    # print(df.head())
    df.to_csv('match_players.csv', index=False)


if __name__ == '__main__':
    scrape()
    # get_roster('https://sofifa.com//team/1', 2008)