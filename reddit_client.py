import praw
import yaml
import time

# temp load config for testing, @TODO move to main and pass through
config = yaml.load(open('config.yaml'), Loader=yaml.FullLoader)


def auth():
    return praw.Reddit(
        client_id=config['reddit_id_dev'],
        client_secret=config['reddit_secret_dev'],
        user_agent='blades_bot_dev%s' % time.time(),
        username=config['reddit_user'],
        password=config['reddit_password']
    )


reddit = auth()
print(reddit.read_only)
