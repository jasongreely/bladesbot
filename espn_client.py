from html.parser import HTMLParser
from bs4 import BeautifulSoup
import yaml
import requests
from datetime import date

config = yaml.load(open('config.yaml'), Loader=yaml.BaseLoader)
team_id = config["espn_team_id"]

fixtures_url = config["espn_fixtures_url"]


def get_today_fixture_id():
    today = date.today().strftime('%a, %b %d')
    fixtures_url = "https://www.espn.com/soccer/team/fixtures/_/id/%s/sheffield-united" % team_id
    request = requests.get(fixtures_url)
    soup = BeautifulSoup(request.text, features="html.parser")
    first_result = soup.find("div", {"class": "matchTeams"})
    if first_result.text == today:
        tds = first_result.find_parent('td').find_next_siblings('td')
        for td in tds:
            span = td.find('span')
            if span:
                anchors = span.find_all('a')
                if anchors:
                    for a in anchors:
                        if a['href'].find('gameId') != -1:
                            return a['href'].split('/')[-1]


def get_match(match_id):
    match_url = "https://www.espn.com/soccer/match/_/gameId/%s" % match_id
    request = requests.get(match_url)
    return BeautifulSoup(request.text, features="html.parser")


def get_info(match):
    info = match.find('article', {'class': 'soccer-game-information'})
    return info


def get_venue(match):
    info = get_info(match)
    venue = info.find('li', {'class': 'venue'}).find('div').text
    venue = venue.split(': ')[-1]
    address = info.find('div', {'class': 'address'}).find('span').text
    return '%s - %s' % (venue, address)


def get_starting_xi(match_id):
    lineup_url = 'https://www.espn.com/soccer/lineups?gameId=%s' % match_id
    request = requests.get(lineup_url)
    soup = BeautifulSoup(request.text, features='html.parser')
    lineups = soup.find('div', {'data-module': 'lineups'}).find_all('div', {'class': 'content-tab'})
    for lineup in lineups:
        rows = lineup.find_all('tr')
        for row in rows:
            #@TODO finish this
            data = row.find_all('span', {'class': 'name'})
            player = '%s %s' % (data[0], data[1])
            print(player)
        print(row)
    return len(lineups)


def get_subs(match):
    return


def get_score(match):
    return


def get_summary(match):
    return


