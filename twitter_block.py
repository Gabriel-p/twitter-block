
import sys
from os.path import isfile
import tweepy
import time


# API Key
consumer_key = "xxxxxx"
# API key secret
consumer_secret = "xxxxxx"
# Make sure to generate these using Read & Write permissions
access_token = "xxxxxx"
access_token_secret = "xxxxxx"


def main():
    """
    Usage:

    $ python twitter_block.py AccountName

    The process is divided into 4 steps:

    1. Download IDs already blocked by the issuing account
    2. Download IDs for 'AccountName' (the one whose followers we are blocking)
       Creates the "AccountName_IDs.txt" file (for account 'AccountName')
    3. Remove IDs for those accounts that were already blocked
    4. Block remaining accounts

    * The IDs are downloaded 5000 per minute (~80-90 accounts/sec).
    * The bocking step is the slowest (~2 accounts/sec). Thus the script
    allows to stop the process at any time and re-start it later on using the
    file generated. If you want to run the process from scratch, just
    delete this file.

    Sources:
    https://stackoverflow.com/q/31000178/1391441
    https://stackoverflow.com/a/17490816/1391441

    """

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

    # # Request user names
    # if requestNames:
    #     out_name = out_name.replace('IDs', 'names')
    #     users = usersRequest(api, followerids, out_name)
    # # Read names of followers to block
    # with open(out_name, "r") as f:
    #     users = f.read().split()

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


# def usersRequest(api, followerids, out_name):
#     """
#     Make lookup requests for ids 100 at a time.
#     """
#     def chunks(lst, n=100):
#         """Yield successive n-sized chunks from lst."""
#         for i in range(0, len(lst), n):
#             yield lst[i:i + n]

#     with open(out_name, "w") as f:
#         f.write('')

#     Nt = len(followerids)
#     print("Requesting {} user screen names...".format(Nt))
#     for i, chunk in enumerate(chunks(followerids)):
#         users_names = api.lookup_users(user_ids=chunk)
#         if i % 100 == 0:
#             print("{} ({:.2f}%)".format(i, 100 * (i * 100) / Nt))

#         with open(out_name, "a") as f:
#             for _ in users_names:
#                 f.write(_.screen_name + '\n')


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
