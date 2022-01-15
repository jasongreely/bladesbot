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

