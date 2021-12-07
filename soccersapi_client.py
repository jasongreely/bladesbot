import yaml
import requests
import json

# temp load config for testing, @TODO move to main and pass through
config = yaml.load(open('config.yaml'), Loader=yaml.BaseLoader)
base_uri = '%s%s/' % (config['soccersapi_baseuri'], config['soccersapi_version'])
auth_params = {'user': config['soccersapi_user'], 'token': config['soccersapi_token_dev']}

leagues_uri = '%sleagues/' % base_uri
fixtures_uri = '%sfixtures/' % base_uri
venues_uri = '%svenues/' % base_uri


def request(uri, params):
    response = requests.get(uri, params=params)
    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        print(response.status_code)


# get all leagues configured for the account
def get_leagues():
    params = {**auth_params, **{'t': 'list'}}
    return request(leagues_uri, params)


# get league by ID
def get_league(league_id):
    params = {**auth_params, **{'t': 'info', 'id': league_id}}
    return request(leagues_uri, params)


# get standings for current season of a league
def get_standings(season_id):
    params = {**auth_params, **{'t': 'standings', 'season_id': season_id}}
    return request(leagues_uri, params)


# get current standings for a league by ID
def get_league_standings_by_id(league_id):
    league = get_league(league_id)
    if league['data'] and league['data']['id_current_season']:
        return get_standings(league['data']['id_current_season'])


# get previous and next fixtures for team
def get_next_last_fixtures(team_id):
    params = {**auth_params, **{'t': 'last_next', 'team_id': team_id}}
    return request(fixtures_uri, params)


# get match by ID
def get_match_by_id(match_id):
    params = {**auth_params, **{'t': 'info', 'id': match_id}}
    return request(fixtures_uri, params)


# get matches for today
def get_today_fixtures(team_id):
    next_last = get_next_last_fixtures(team_id)
    if next_last['data']['current']:
        match = next_last['data']['current'][0]
        return get_match_by_id(match['id'])


def get_match_lineups(match_id):
    params = {**auth_params, **{'t': 'match_lineups', 'id': match_id}}
    return request(fixtures_uri, params)


def get_match_events(match_id):
    params = {**auth_params, **{'t': 'match_events', 'id': match_id}}
    return request(fixtures_uri, params)


def get_venue(venue_id):
    params = {**auth_params, **{'t': 'info', 'id': venue_id}}
    return request(venues_uri, params)

