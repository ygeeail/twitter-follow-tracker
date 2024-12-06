import tweepy
import os

# Authenticate with Twitter API
API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")

auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

# Fetch accounts from a Twitter List
list_owner = "your_twitter_username"  # Replace with your username
list_name = "Accounts to Track"       # Replace with your List name
list_id = api.get_list(screen_name=list_owner, slug=list_name).id
accounts_to_track = [member.screen_name for member in api.list_members(list_id=list_id)]

print("Tracking accounts:", accounts_to_track)

# Monitor followings of each account
for account in accounts_to_track:
    try:
        following = api.friends_ids(screen_name=account)
        print(f"{account} is following {len(following)} accounts.")
        # Add logic to save or compare results here
    except Exception as e:
        print(f"Error with {account}: {e}")
