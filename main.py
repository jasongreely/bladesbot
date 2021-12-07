import reddit_client
import soccersapi_client
import yaml
import time

config = yaml.load(open('config.yaml'), Loader=yaml.FullLoader)

team_id = config['reddit_sub_team_id']
match_status_finished = config['soccersapi_match_status_finished']

reddit = reddit_client.auth()

update_sidebar = False

if update_sidebar:
    print('Updating sidebar...')
    reddit_client.update_sidebar_standings(reddit)
    print('Sidebar updated.')

print('Checking for fixtures..')
match = soccersapi_client.get_today_fixtures(team_id)
if match:
    match_status = match['data']['status']
    match_id = match['data']['id']
    print('Match found: %s, %s' % (match_id, match['data']['status_name']))

    if match and match_status not in match_status_finished:
        print('Posting match thread..')
        match_post = reddit_client.match_submission(reddit, match)
        print('Thread posted.')

        time.sleep(60)

        while match_status not in match_status_finished:
            match = soccersapi_client.get_match_by_id(match_id)
            match_status = match['data']['status']
            print('Scheduled fixture status: %s' % match['data']['status_name'])

            if match_status not in match_status_finished:
                print('Editing match thread...')
                match_post = reddit_client.match_thread_update(match, match_post)
                print('Edited.')

            time.sleep(60)

print('End.')
