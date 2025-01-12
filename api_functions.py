# find_user
def get_collection_username(username):
    url = "https://boardgamegeek.com/xmlapi2/collection"
    for _ in range(10):
        params = {
            "username": username,
            "stats": 1,       # Include statistics like ratings
            "subtype": "boardgame"  # Optional: Fetch only board games
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return parse_collection_etree(response.content, username)


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
