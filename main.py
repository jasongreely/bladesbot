import reddit_client
import soccersapi_client
import yaml
import time

config = yaml.load(open('config.yaml'), Loader=yaml.FullLoader)

team_id = config['reddit_sub_team_id']
match_status_finished = config['soccersapi_match_status_finished']

match = soccersapi_client.get_today_fixtures(team_id)
match_status = match['data']['status']

if match and match_status not in match_status_finished:
    reddit = reddit_client.auth()
    match_post = reddit_client.match_submission(reddit)

    time.sleep(60)

    while match_status not in match_status_finished:
        match = soccersapi_client.get_today_fixtures(team_id)
        match_status = match['data']['status']

        if match_status not in match_status_finished:
            reddit_client.match_thread_update(reddit, match, match_post)

        time.sleep(60)
