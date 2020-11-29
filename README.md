# twitter-block

Block all followers of a given Twitter account

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