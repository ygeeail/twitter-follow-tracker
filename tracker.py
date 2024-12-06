import tweepy
import csv
import os
import json
import time

# Replace these with your credentials
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

# Initialize Tweepy client
client = tweepy.Client(bearer_token=BEARER_TOKEN)

# File to save previous data
DATA_FILE = "tracked_followings.json"

# List ID for your Twitter List
TRACKED_LIST_ID = "1864974579615306005"  # Replace with your List ID


# Function to get following for a user
def get_following(user_id):
    following = []
    paginator = tweepy.Paginator(client.get_users_following, id=user_id, max_results=500)
    for page in paginator:
        if page.data:
            following.extend(page.data)
        time.sleep(1)  # Stagger requests to avoid hitting rate limits
    return following


# Function to fetch tracked accounts from the Twitter List
def get_tracked_accounts_from_list(list_id):
    tracked_accounts = []
    paginator = tweepy.Paginator(client.get_list_members, id=list_id, max_results=100)
    for page in paginator:
        if page.data:
            tracked_accounts.extend(page.data)
        time.sleep(1)  # Stagger requests
    return tracked_accounts


# Function to load previously saved followings
def load_previous_followings():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return {}


# Function to save the current followings
def save_current_followings(data):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


# Function to save new follows to a CSV
def save_new_follows_to_csv(tracked_user, new_follows):
    with open("new_follows.csv", "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        for user in new_follows:
            writer.writerow([
                tracked_user.username,
                tracked_user.name,
                user.username,
                user.name,
                user.description,
                f"https://twitter.com/{user.username}"
            ])


# Main function
def main():
    # Load previously saved data
    previous_followings = load_previous_followings()

    # Fetch tracked accounts from the Twitter List
    tracked_accounts = get_tracked_accounts_from_list(TRACKED_LIST_ID)

    # Current followings data
    current_followings = {}

    # Check followings for each tracked account
    for tracked_account in tracked_accounts:
        print(f"Fetching followings for {tracked_account.username}...")
        following = get_following(tracked_account.id)

        # Store current followings
        current_followings[tracked_account.username] = [user.id for user in following]

        # Compare with previous followings to find new follows
        previous = set(previous_followings.get(tracked_account.username, []))
        current = set(user.id for user in following)
        new_follow_ids = current - previous

        # Get details of new follows
        new_follows = [user for user in following if user.id in new_follow_ids]

        # Save new follows to CSV
        save_new_follows_to_csv(tracked_account, new_follows)

        # Stagger requests
        time.sleep(10)  # Adjust sleep as needed

    # Save the current followings for the next run
    save_current_followings(current_followings)


if __name__ == "__main__":
    main()
