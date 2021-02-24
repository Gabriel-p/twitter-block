
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
    api, accountvar = APIAccount()
    print("\nAccount whose followers to block: '{}'".format(accountvar))

    # Read manually white-listed IDs
    try:
        with open("whitelist.txt", "r") as f:
            whitelistIDs = f.read().split()
        whitelistIDs = [int(_) for _ in whitelistIDs]
    except FileNotFoundError:
        whitelistIDs = []

    # Fetch my followers
    followers_fname = "my_followers.txt"
    myfollowersIDs = IDsRequest(
        None, api.followers_ids, followers_fname, False)
    print("{} followers of my account".format(len(myfollowersIDs)))

    # Fetch accounts I follow
    followed_fname = "my_followed.txt"
    myfollowedIDs = IDsRequest(None, api.friends_ids, followed_fname, False)
    print("{} accounts followed by me".format(len(myfollowedIDs)))

    # Fetch accounts already blocked (to speed up the process)
    blocked_fname = "blocked_IDs.txt"
    if not isfile(blocked_fname):
        IDsRequest(None, api.blocks_ids, blocked_fname)
    with open(blocked_fname, "r") as f:
        blockedIDs = f.read().split()
    blockedIDs = [int(_) for _ in blockedIDs]
    print("{} accounts already blocked".format(len(blockedIDs)))

    # Request all the follower IDs for 'accountvar'
    out_name = "{}_IDs.txt".format(accountvar)
    if not isfile(out_name):
        IDsRequest(accountvar, api.followers_ids, out_name)
    with open(out_name, "r") as f:
        followerids = f.read().split()
    followerids = [int(_) for _ in followerids]
    print("{} IDs requested".format(len(followerids)))

    # Remove whitelisted IDs
    followerids = list(set(followerids) - set(whitelistIDs))
    # Remove accounts that I follow or that follow me
    followerids = list(set(followerids) - set(myfollowersIDs))
    followerids = list(set(followerids) - set(myfollowedIDs))
    print("{} non whitelist or follow accounts".format(len(followerids)))
    # Remove accounts that were already blocked
    followerids = list(set(followerids) - set(blockedIDs))
    print("{} non-blocked accounts".format(len(followerids)))

    # Block non-blocked accounts
    userBlock(api, followerids, blocked_fname)


def APIAccount():
    """
    Define API call and name of account whose followers to block.
    """
    # Read keys & tokens
    config = configparser.ConfigParser()
    config.read("KEY_TOKEN.txt")
    consumer_key = config.get("api_token", "consumer_key")
    consumer_secret = config.get("api_token", "consumer_secret")
    access_token = config.get("api_token", "access_token")
    access_token_secret = config.get("api_token", "access_token_secret")

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    # Make sure you have set wait_on_rate_limit to True while connecting
    # through Tweepy
    api = tweepy.API(
        auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    # Passed as argument
    accountvar = sys.argv[1].lower()

    return api, accountvar


def IDsRequest(accountvar, api_call, out_name, write=True, sec_sleep=60):
    """
    Store blocked accounts from the issuing account or follower ids from
    'accountvar'.
    """
    print("Requesting IDs...")
    listIDs = []
    for page in tweepy.Cursor(
            api_call, screen_name=accountvar).pages():
        if write:
            with open(out_name, "a") as f:
                for _ in page:
                    f.write(str(_) + '\n')
        else:
            listIDs += [int(_) for _ in page]

        if len(page) % 5000 == 0:
            print("5000 IDs requested. Sleeping for {} seconds...".format(
                sec_sleep))
            time.sleep(sec_sleep)

    return listIDs


def userBlock(api, users, blocked_fname):
    """
    Block all users in 'users' list
    """
    print("Blocking users...")
    Nt = len(users)
    start = time.time()

    j, _5perc = 0, (5. * Nt) / 100.

    with open(blocked_fname, "a") as f:
        for i, user in enumerate(users):
            try:
                api.create_block(user)
                f.write(str(user) + '\n')
            except tweepy.TweepError:
                # print("Error: {}".format(user))
                continue

            if i > _5perc * j:
                j += 1
                # time used so far
                tt = time.time() - start
                # estimation of total time
                t_tot = Nt * tt / (i + 1)
                # estimation of time remaining
                t_rem = t_tot - tt
                txt = "Blocked: {} ({:.2f}%) | Time remaining: {:.1f} min"
                print(txt.format(i, 100 * i / Nt, t_rem / 60.))


if __name__ == '__main__':
    main()
