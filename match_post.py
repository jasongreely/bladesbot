import soccersapi_client
import yaml

event_types = yaml.load(open('event_types.yaml'), Loader=yaml.FullLoader)


def build_player_name(player):
    first_name = player['player']['firstname'].split[' '][0]
    name = '%s %s' % (first_name, player['player']['lastname'])
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
    if events:
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


def build_starting_xi(match):
    home_team = match['teams']['home']['name']
    away_team = match['teams']['away']['name']

    header = '|**%s**|\#|Position|**%s**|\#|Position|' % (home_team, away_team)
    table = [header, '|:-|:--:|:--:|:-|:--:|:--:|']

    lineups = soccersapi_client.get_match_lineups(match['id'])['data']
    if lineups:
        home_squad = lineups['home']['squad']
        away_squad = lineups['away']['squad']

        for x in range(len(home_squad)):
            home_player = home_squad[x]
            away_player = away_squad[x]

            table_row = '%s|%s|%s|%s|%s|%s' % (
                build_player_name(home_player), home_player['number'], home_player['position'],
                build_player_name(away_player), away_player['number'], away_player['position'])
            table.append(table_row)

        return '\n'.join(table)


class MatchPost:
    def __init__(self, match, date, time, venue, events, starting_xi, reddit_post, persist):
        self.match = match
        self.date = date
        self.time = time
        self.venue = venue
        self.events = events
        self.starting_xi = starting_xi
        self.reddit_post = reddit_post
        self.persist = persist

    def set_match(self, match):
        self.set_date(match['time']['date'])
        self.set_time(match['time']['time'])

        venue_data = soccersapi_client.get_venue(match['venue_id'])
        if venue_data:
            self.set_venue(venue_data['data'])

        self.set_starting_xi(build_starting_xi(match))
        self.set_events(match)

    def set_date(self, date):
        self.date = date

    def set_time(self, time):
        self.time = time

    def set_venue(self, venue):
        self.venue = venue

    def set_events(self, events):
        if events:
            self.events = events
        else:
            self.events = None

    def set_starting_xi(self, starting_xi):
        if starting_xi:
            self.starting_xi = starting_xi
            self.persist = True
        else:
            self.starting_xi = None

    def get_persist(self):
        return self.persist

    def set_reddit_post(self, reddit_post):
        self.reddit_post = reddit_post

    def get_reddit_post(self):
        return self.reddit_post

    def to_post(self):
        post = []

        match_date = '**Date:** %s\n\n' % self.date
        post.append(match_date)

        match_time = '**Time:** %s\n\n' % self.time
        post.append(match_time)

        venue_text = "**Location:** %s - %s, %s  \n" % (self.venue['name'], self.venue['city'],
                                                        self.venue['country']['name'])
        post.append(venue_text)

        if self.starting_xi:
            post.append('###Starting XI:')
            post.append(self.starting_xi)

        if self.events:
            post.append('###Match Events:')
            post.append(self.events)

        if not self.starting_xi and not self.events:
            post.append("Match data not yet available")

        post.append('\n')
        post.append('^(match thread updates every minute)')

        return '\n'.join(post)
