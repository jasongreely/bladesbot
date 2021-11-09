import praw
import yaml
import time
import soccersapi_client

# temp load config for testing, @TODO move to main and pass through
config = yaml.load(open('config.yaml'), Loader=yaml.FullLoader)
sidebar_league_id = config['soccersapi_sidebar_league_id']
sub_team_name = config['reddit_sub_team_name']
subreddit_name = config['reddit_subreddit_name']
sidebar_standings_widget_name = config['reddit_sidebar_standings_widget_name']


def auth():
    return praw.Reddit(
        client_id=config['reddit_id_dev'],
        client_secret=config['reddit_secret_dev'],
        user_agent='blades_bot_dev%s' % time.time(),
        username=config['reddit_user'],
        password=config['reddit_password']
    )


def build_sidebar_standings():
    table = ['\#|Team|PTS|W|D|L', ':--:|:--:|:--:|:--:|:--:|:--:']
    standings = soccersapi_client.get_league_standings_by_id(sidebar_league_id)
    if standings['data']['standings']:
        for team in standings['data']['standings']:
            team_overall = team['overall']
            table_row = '%s|%s|%s|%s|%s|%s' % (team_overall['position'], team['team_name'], team_overall['points'], team_overall['won'], team_overall['draw'], team_overall['lost'])
            if team['team_name'] == sub_team_name:
                cells = table_row.split('|')
                formatted_row = []
                for cell in cells:
                    formatted_row.append('**%s**' % cell)
                table_row = '|'.join(formatted_row)
            table.append(table_row)
    return '\n'.join(table)


def update_sidebar_standings(reddit):
    widgets = reddit.subreddit(subreddit_name).widgets
    for widget in widgets.sidebar:
        if widget.shortName == sidebar_standings_widget_name:
            widget.mod.update(text=build_sidebar_standings())


reddit = auth()
