
import sys
import configparser
from os.path import isfile
import tweepy
import time


def main():
    """
    Usage:

    $ python twitter_block.py AccountName

    The script expect the keys and tokens in a separate 'KEY_TOKEN.txt' file.

    Sources:
    https://stackoverflow.com/q/31000178/1391441
    https://stackoverflow.com/a/17490816/1391441

    """
    # Read keys & tokens
    config = configparser.ConfigParser()
    config.read("KEY_TOKEN.txt")
    consumer_key = config.get("api_token", "consumer_key")
    consumer_secret = config.get("api_token", "consumer_secret")
    access_token = config.get("api_token", "access_token")
    access_token_secret = config.get("api_token", "access_token_secret")

    # Passed as argument
    accountvar = sys.argv[1]

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    # Make sure you have set wait_on_rate_limit to True while connecting
    # through Tweepy
    api = tweepy.API(
        auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    print("\nAccount whose followers to block: '{}'".format(accountvar))

    # Fetch accounts already blocked by the issuing account (to speed up the
    # process)
    blockedIDs = IDsRequest(None, api.blocks_ids)
    print("{} accounts blocked".format(len(blockedIDs)))

    # Request all the follower IDs for 'accountvar'
    out_name = "{}_IDs.txt".format(accountvar)
    # If the IDs file is not present, create it
    if not isfile(out_name):
        IDsRequest(accountvar, api.followers_ids, out_name)
    # Read IDs of followers to block
    with open(out_name, "r") as f:
        followerids = f.read().split()
    followerids = [int(_) for _ in followerids]
    print("{} IDs requested".format(len(followerids)))

    # Remove accounts already blocked
    followerids = list(set(followerids) - set(blockedIDs))
    print("Non-blocked accounts: {}".format(len(followerids)))

    # Blocking
    userBlock(api, followerids)


def IDsRequest(accountvar, api_call, out_name=None, sec_sleep=60):
    """
    Store follower ids from 'accountvar'.
    """
    txt = 'blocked' if out_name is None else accountvar
    print("Requesting {} IDs...".format(txt))
    IDs = []
    for page in tweepy.Cursor(
            api_call, screen_name=accountvar).pages():
        if out_name is None:
            IDs.extend([int(_) for _ in page])
        else:
            with open(out_name, "a") as f:
                for _ in page:
                    f.write(str(_) + '\n')

        if len(page) % 5000 == 0:
            print("5000 IDs requested. Sleeping for {} seconds...".format(
                sec_sleep))
            time.sleep(sec_sleep)

    return IDs


def userBlock(api, users):
    """
    Block all users in 'users' list
    """
    print("Blocking users...")
    Nt = len(users)
    start = time.time()

    for i, user in enumerate(users):
        try:
            api.create_block(user)
        except tweepy.TweepError:
            print("Error: {}".format(user))
            continue

        if i % int(Nt / 1000) == 0:
            # time used so far
            tt = time.time() - start
            # estimation of total time
            t_tot = Nt * tt / (i + 1)
            # estimation of time remaining
            t_rem = t_tot - tt
            print("Blocked: {} ({:.2f}%) | Remaining: {:.1f} min".format(
                i, 100 * i / Nt, t_rem / 60.))


if __name__ == '__main__':
    main()
