import yaml
import requests

# temp load config for testing, @TODO move to main and pass through
config = yaml.load(open('config.yaml'), Loader=yaml.FullLoader)
base_uri = '%s%s/' % (config['soccersapi_baseuri'], config['soccersapi_version'])

# test API call
uri = '%sleagues/' % base_uri
params = {'user': config['soccersapi_user'], 'token': config['soccersapi_token_dev'], 't': 'list'}
response = requests.get(uri, params=params)

print(response.json())

