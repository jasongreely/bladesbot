import yaml
import requests

# temp load config for testing, @TODO move to main and pass through
config = yaml.load(open('config.yaml'), Loader=yaml.BaseLoader)
base_uri = '%s%s/' % (config['soccersapi_baseuri'], config['soccersapi_version'])
auth_params = {'user': config['soccersapi_user'], 'token': config['soccersapi_token_dev']}

leagues_uri = '%sleagues/' % base_uri


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
