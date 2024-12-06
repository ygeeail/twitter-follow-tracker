import tweepy
import os
import csv
import json

# Authenticate with Twitter API
API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")

auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

# Twitter list details
list_owner = "soundb0x"  # Replace with your username
list_name = "Accounts to Track"       # Replace with your List name

# File to store previous followings
previous_followings_file = "previous_followings.json"
output_file = "new_followings.csv"

# Load previous followings from file
if os.path.exists(previous_followings_file):
    with open(previous_followings_file, "r") as file:
        previous_followings = json.load(file)
else:
    previous_followings = {}

# Fetch accounts from the Twitter List
list_id = api.get_list(screen_name=list_owner, slug=list_name).id
accounts_to_track = [(member.screen_name, member.name) for member in api.list_members(list_id=list_id)]

# Track new followings
new_followings = []

for account_screen_name, account_name in accounts_to_track:
    print(f"Checking account: {account_screen_name}")
    try:
        # Get the current followings
        current_followings = api.friends_ids(screen_name=account_screen_name)
        previous = set(previous_followings.get(account_screen_name, []))
        current = set(current_followings)

        # Find new followings
        new_ids = current - previous

        if new_ids:
            for user_id in new_ids:
                user = api.get_user(user_id=user_id)
                new_followings.append({
                    "Tracked Account Handle": f"@{account_screen_name}",
                    "Tracked Account Name": account_name,
                    "New Follow Handle": f"@{user.screen_name}",
                    "New Follow Name": user.name,
                    "Profile Description": user.description,
                    "Profile Link": f"https://twitter.com/{user.screen_name}"
                })

        # Save current followings for the next run
        previous_followings[account_screen_name] = list(current_followings)

    except Exception as e:
        print(f"Error with account {account_screen_name}: {e}")

# Save new followings to CSV
if new_followings:
    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "Tracked Account Handle",
            "Tracked Account Name",
            "New Follow Handle",
            "New Follow Name",
            "Profile Description",
            "Profile Link"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(new_followings)

    print(f"New followings saved to {output_file}")
else:
    print("No new followings found.")

# Save the updated followings data
with open(previous_followings_file, "w") as file:
    json.dump(previous_followings, file)
