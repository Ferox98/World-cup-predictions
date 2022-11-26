import pandas as pd 
import requests 
from bs4 import BeautifulSoup
from sqlite3 import connect
import itertools
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import math 

groups = {
    'A': ['Qatar', 'Ecuador', 'Senegal', 'Netherlands'],
    'B': ['England', 'Iran', 'USA', 'Wales'],
    'C': ['Argentina', 'Saudi Arabia', 'Mexico', 'Poland'],
    'D': ['France', 'Australia', 'Denmark', 'Tunisia'],
    'E': ['Germany', 'Japan', 'Costa Rica', 'Spain'],
    'F': ['Belgium', 'Canada', 'Morocco', 'Croatia'],
    'G': ['Brazil', 'Cameroon', 'Serbia', 'Switzerland'],
    'H': ['Ghana', 'South Korea', 'Portugal', 'Uruguay']
}

team_urls = {
    'Qatar': 'https://sofifa.com/team/111527/qatar/',
    'Netherlands': 'https://sofifa.com/team/105035/netherlands/',
    'England': 'https://sofifa.com/team/1318/england/',
    'USA': 'https://sofifa.com/team/1387/united-states/',
    'Wales': 'https://sofifa.com/team/1367/wales/',
    'Argentina': 'https://sofifa.com/team/1369/argentina/',
    'Mexico': 'https://sofifa.com/team/1386/mexico/',
    'Poland': 'https://sofifa.com/team/1353/poland/',
    'France': 'https://sofifa.com/team/1335/france/',
    'Australia': 'https://sofifa.com/team/1415/australia/',
    'Denmark': 'https://sofifa.com/team/1331/denmark/',
    'Germany': 'https://sofifa.com/team/1337/germany/',
    'Spain': 'https://sofifa.com/team/1362/spain/',
    'Belgium': 'https://sofifa.com/team/1325/belgium/',
    'Canada': 'https://sofifa.com/team/111455/canada/',
    'Morocco': 'https://sofifa.com/team/111111/morocco/', 
    'Croatia': 'https://sofifa.com/team/1328/croatia/',
    'Brazil': 'https://sofifa.com/team/1370/brazil/', 
    'Ghana': 'https://sofifa.com/team/111462/ghana/',
    'Portugal': 'https://sofifa.com/team/1354/portugal/'
}


def init():
    team_id = dict()
    id_to_string = dict()
    cur_id = 0
    global groups
    for group in groups:
        for team in groups[group]:
            team_id[team] = cur_id
            id_to_string[cur_id] = team
            cur_id += 1
    return team_id, id_to_string
210040

def scrape_world_cup_team_rosters():
    global team_urls
    res = []
    team_id, id_to_string = init()
    print(team_id)
    for url in team_urls:
        # get team starting lineup 
        roster = get_roster(team_urls[url])
        team = [url] + [team_id[url]] + roster 
        res.append(team)
    cols = ['Country', 'CountryID'] + [f'player_{i}' for i in range(1, 12)]
    df = pd.DataFrame(res, columns=cols)
    df.to_csv('wc_team_rosters.csv', index=False)

def get_player_stats():
    roster_df = pd.read_csv('wc_team_rosters.csv')
    unique_ids = pd.unique(roster_df.iloc[:, 2:].values.ravel())
    rows, stats = [], ['player_id', 'Overall', 'Potential'] 
    for count, id in enumerate(unique_ids):
        url = f'https://sofifa.com/player/{id}'
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        block_quarters = soup.find_all(lambda tag: tag.name == 'div' and 
                                        tag.get('class') == ['block-quarter'])
        # block quarters 1 and 2 are Overall and Potential
        overall = block_quarters[0].find_all(lambda tag: tag.name == 'span')[0].text 
        potential = block_quarters[1].find_all(lambda tag: tag.name == 'span')[0].text 
        player_stats = [id, overall, potential]
        for i in range(len(block_quarters) - 2, len(block_quarters) - 9, -1):

            block_quarter = block_quarters[i]
            stat_list = block_quarter.find_all(lambda tag: tag.name == 'li')
            for j in range(len(stat_list)):
                spans = stat_list[j].find_all(lambda tag: tag.name == 'span')
                stat_val = spans[0].text
                stat_name = spans[1].text
                if count == 0:
                    stats.append(stat_name)
                cur_idx = len(player_stats)
                if stats[cur_idx] == stat_name:
                    player_stats.append(stat_val)
                else:
                    player_stats.append(None)
        rows.append(player_stats)
        # break
    # print(stats)
    # print(rows[0])
    df = pd.DataFrame(rows, columns=stats)
    df.to_csv('wc_player_stats.csv', index=False)

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

def get_roster(url):
    # url = get_redirect_url(url, year)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    table = soup.find_all(lambda tag: tag.name == 'table')[0]
    starting_rows = table.find_all('tr', class_='starting')
    starters = []
    
    for i in range(len(starting_rows)):
        # get player_fifa_api_id
        name_tag = starting_rows[i].find('td', class_='col-name')
        fifa_api_id = name_tag.find('a')['href'].split('/')[2]
        starters.append(fifa_api_id)
    
    return starters

# def modify():
#     df = pd.read_csv('wc_team_rosters.csv')
#     df['group_id'] = df.apply(lambda x: math.ceil((int(x.loc['CountryID']) + 1) / 4), axis=1)
#     df.to_csv('wc_team_rosters.csv')
if __name__ == '__main__':
    # scrape_world_cup_team_rosters()
    get_player_stats()
    # get_roster('https://sofifa.com//team/1', 2008)
    # modify()