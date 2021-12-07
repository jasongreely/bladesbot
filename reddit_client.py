import praw
import yaml
import time
import soccersapi_client

config = yaml.load(open('config.yaml'), Loader=yaml.FullLoader)
event_types = yaml.load(open('event_types.yaml'), Loader=yaml.FullLoader)

sidebar_league_id = config['soccersapi_sidebar_league_id']
sub_team_name = config['reddit_sub_team_name']
sub_team_id = config['reddit_sub_team_id']
subreddit_name = config['reddit_subreddit_name']
sidebar_standings_widget_name = config['reddit_sidebar_standings_widget_name']
match_thread_flair_id = config['reddit_submission_flair_match_thread']
results_thread_flair_id = config['reddit_submission_flair_results_thread']


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


def match_submission(reddit, match):
    match = match['data']
    if match:
        home_team = match['teams']['home']['name']
        away_team = match['teams']['away']['name']

        title = "Match Thread: %s vs. %s" % (home_team, away_team)
        self_text = build_match_thread_body(match)
        flair_text = "Match Thread"

        return reddit.subreddit(subreddit_name).submit(title, selftext=self_text, flair_text=flair_text,
                                                flair_id=match_thread_flair_id)


def match_results_submission(reddit, match):
    if match:
        home_team = match['teams']['home']['name']
        away_team = match['teams']['away']['name']

        title = "Match Results: %s vs. %s" % (home_team, away_team)
        self_text = build_match_thread_body(match)
        flair_text = "Match Results"

        return reddit.subreddit(subreddit_name).submit(title, selftext=self_text, flair_text=flair_text,
                                                flair_id=results_thread_flair_id)


def match_thread_update(match, post):
    match = match['data']
    self_text = build_match_thread_body(match)
    return post.edit(self_text)


def build_match_thread_body(match):
    post = []

    match_date = '**Date:** %s\n\n' % match['time']['date']
    post.append(match_date)

    match_time = '**Time:** %s\n\n' % match['time']['time']
    post.append(match_time)

    venue = soccersapi_client.get_venue(match['venue_id'])['data']
    venue_text = "**Location:** %s - %s, %s  \n" % (venue['name'], venue['city'], venue['country']['name'])
    post.append(venue_text)

    post.append('###Starting XI:')
    starting_xi = build_starting_xi(match)
    post.append(starting_xi)

    post.append('###Match Events:')
    events = build_events_table(match, match['teams']['home']['id'])
    post.append(events)

    return '\n'.join(post)


def build_starting_xi(match):
    home_team = match['teams']['home']['name']
    away_team = match['teams']['away']['name']

    header = '|**%s**|\#|Position|**%s**|\#|Position|' % (home_team, away_team)
    table = [header, '|:-|:--:|:--:|:-|:--:|:--:|']

    lineups = soccersapi_client.get_match_lineups(match['id'])['data']
    home_squad = lineups['home']['squad']
    away_squad = lineups['away']['squad']

    for x in range(len(home_squad)):
        home_player = home_squad[x]
        away_player = away_squad[x]

        table_row = '%s|%s|%s|%s|%s|%s' % (build_player_name(home_player), home_player['number'], home_player['position'],
                                           build_player_name(away_player), away_player['number'], away_player['position'])
        table.append(table_row)

    return '\n'.join(table)


def build_player_name(player):
    name = '%s %s' % (player['player']['firstname'], player['player']['lastname'])
    if player['captain']:
        name += ' (C)'
    return name


def get_player_last_name(name):
    if name and ',' in name:
        return name.split(',')[0]
    else:
        return name


def build_events_table(match, home_team_id):
    home_team = match['teams']['home']['name']
    away_team = match['teams']['away']['name']

    header = '|**%s**|Time|**%s**|' % (home_team, away_team)
    table = [header, '|:--:|:--:|:--:|']

    events = soccersapi_client.get_match_events(match['id'])
    for event in events['data']:
        event_type = event['type'].replace(' ', '')
        if event_type == 'backfrominjury':
            continue

        team_id = event['team_id']
        minute = '%s\'' % event['minute']
        player = get_player_last_name(event['player_name'])
        related_player = event['related_player_name']
        if related_player:
            related_player = get_player_last_name(related_player)

        event_message = '%s: %s' % (event_types[event_type], player)

        if event_type == 'goal':
            if event['own_goal']:
                event_message += ' OG'
            elif event['penalty']:
                event_message += ' PEN'
            event_message = "***%s***" % event_message
        elif event_type == 'substitution':
            event_message += ' <> %s' % related_player
        if str(team_id) == str(home_team_id):
            table_row = '|%s|%s||' % (event_message, minute)
            table.append(table_row)
        else:
            table_row = '||%s|%s|' % (minute, event_message)
            table.append(table_row)
    return '\n'.join(table)

