import tweepy
import os
import csv
import json

# Authenticate with Twitter API v1.1 (for list management)
API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")

# Authenticate with Twitter API v2 (for fetching followers)
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

# Initialize v1.1 authentication for lists
auth = tweepy.OAuth1UserHandler(consumer_key=API_KEY,
                                consumer_secret=API_SECRET,
                                access_token=ACCESS_TOKEN,
                                access_token_secret=ACCESS_SECRET)

api = tweepy.API(auth, wait_on_rate_limit=True)

# Initialize v2 authentication
client = tweepy.Client(bearer_token=BEARER_TOKEN)

# Twitter list details
list_owner = "soundb0x"  # Replace with the username of the list owner
list_name = "Accounts to Track"       # Replace with your list name

# File to store previous followers
previous_followers_file = "previous_followers.json"
output_file = "new_followers.csv"

# Load previous followers from file
if os.path.exists(previous_followers_file):
    with open(previous_followers_file, "r") as file:
        previous_followers = json.load(file)
else:
    previous_followers = {}

# Fetch the list ID using v1.1
try:
    list_id = api.get_list(screen_name=list_owner, slug=list_name).id
    print(f"List ID: {list_id}")
except tweepy.errors.Forbidden as e:
    print("Error: Access to the list denied. Check your API access permissions.")
    print(str(e))

# Fetch current followers (using v2 endpoint)
def get_followers(user_id):
    followers = []
    response = client.get_users_followers(id=user_id, max_results=10000)  # Adjust max_results as needed
    if response.data:
        followers = [user.id for user in response.data]
    return followers

# Track new followers for the list members
new_followers = []
for user_id in previous_followers.get("tracked_accounts", []):
    current_followers = get_followers(user_id)

    # Compare previous followers with current followers
    previous = set(previous_followers.get(str(user_id), []))
    current = set(current_followers)

    new_ids = current - previous

    if new_ids:
        for user_id in new_ids:
            user = client.get_user(id=user_id)
            new_followers.append({
                "Tracked Account Handle": f"@{user.data['username']}",
                "Tracked Account Name": user.data['name'],
                "New Follow Handle": f"@{user.data['username']}",
                "New Follow Name": user.data['name'],
                "Profile Description": user.data['description'],
                "Profile Link": f"https://twitter.com/{user.data['username']}"
            })

# Stagger the requests to avoid hitting rate limits (sleep for 5 seconds between requests)
time.sleep(5)  # Adjust sleep time as needed
  
# Save new followers to CSV
if new_followers:
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
        writer.writerows(new_followers)

    print(f"New followers saved to {output_file}")
else:
    print("No new followers found.")

# Save the updated followers data
with open(previous_followers_file, "w") as file:
    json.dump(previous_followers, file)
