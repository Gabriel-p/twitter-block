# twitter-block

Blocks all the followers of a given Twitter account

Usage:

    $ python twitter_block.py AccountName

The script expect the keys and tokens in a separate 'KEY_TOKEN.txt' file.
Requires the [Tweepy](https://www.tweepy.org/) library.

The process is divided into four steps:

1. Download IDs already blocked by the issuing account
2. Download IDs for 'AccountName' (the one whose followers we are blocking)
3. Remove IDs for accounts that were already blocked, or that I follow, or that follow me, or accounts that were manually white-listed
4. Block the remaining accounts

* The IDs are downloaded in blocks of 5000 per minute (~80-90 accounts/sec).
* The blocking step is the slowest (~2 accounts/sec). The script
allows to stop the process at any time and re-start it later on, using the
files that were generated. If you want to run the process from scratch, just
delete these files.