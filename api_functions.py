# find_user
import xml.etree.ElementTree as ET
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
RATE_LIMIT_DELAY = 2.0  # seconds between requests, adjust as needed


def get_collection_username(username):
    url = "https://boardgamegeek.com/xmlapi2/collection"
    for _ in range(10):
        time.sleep(RATE_LIMIT_DELAY)
        params = {
            "username": username,
            "stats": 1,       # Include statistics like ratings
            "subtype": "boardgame"  # Optional: Fetch only board games
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return parse_collection_etree(response.content, username)
        else:
            print(response.status_code)


def parse_collection_etree(xml_content, username):
    """
    Parse the XML content using ElementTree and extract rated games.

    Args:
        xml_content (bytes): The XML content from the response.

    Returns:
        list of dict: A list of dictionaries containing game details and ratings.
    """
    root = ET.fromstring(xml_content)
    rated_games = []

    for item in root.findall('item'):
        game_id = item.get('objectid')
        # Extract rating
        rating_tag = item.find("stats/rating")
        if rating_tag is not None:
            try:
                rating = float(rating_tag.get('value'))
                rated_games.append({
                    "game_id": game_id,
                    "rating": rating,
                    "username": username
                })
            except ValueError:
                continue

    return rated_games


def fetch_all_collections_parallel(usernames, max_workers=5):
    """
    Given a list of usernames, fetch their collections in parallel
    using a ThreadPoolExecutor.
    """
    results = []  # This will store all the dictionaries

    # Create a thread pool with a certain number of workers
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit a future for each username
        future_to_user = {
            executor.submit(get_collection_username, user): user
            for user in usernames
        }

        # As each future completes, gather the results
        for future in as_completed(future_to_user):
            user = future_to_user[future]  # get the username for reference
            try:
                data = future.result()  # This should be the list of rated games
                # Append data (list of dicts) to our results list
                results.extend(data)
                # print(f"User {user} worked!")
            except Exception as exc:
                print(f"User {user} generated an exception: {exc}")

    return results
