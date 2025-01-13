import asyncio
import aiohttp
from bs4 import BeautifulSoup


async def fetch_countries(session):
    """
    Asynchronously fetches the list of country options from boardgamegeek.com/users
    """
    url = "https://boardgamegeek.com/users"
    async with session.get(url) as response:
        response.raise_for_status()
        html = await response.text()

    soup = BeautifulSoup(html, 'html.parser')
    if country_select := soup.find(id='avatars-country'):
        return [
            option.get_text(strip=True)
            for option in country_select.find_all('option')
            if option.get_text(strip=True)
        ]
    else:
        return []


async def fetch_users_on_page(session, url):
    """
    Asynchronously fetch the list of users on a given page URL.
    """
    async with session.get(url) as response:
        response.raise_for_status()
        html = await response.text()

    soup = BeautifulSoup(html, 'html.parser')
    user_elements = soup.find_all(class_="username")

    return [
        user.get_text(strip=True).strip("()")
        for user in user_elements
    ]


def build_country_url(country, page_number=1):
    """
    Builds the users page URL for a given country and page number.
    (No async needed here since it's just string manipulation.)
    """
    page_suffix = f"/page/{page_number}" if page_number > 1 else ""
    return f"https://boardgamegeek.com/users{page_suffix}?country={country}&state=&city="


async def find_last_page(session, url):
    """
    Asynchronously find the last page number from a given URL.
    """
    async with session.get(url) as response:
        response.raise_for_status()
        html = await response.text()

    soup = BeautifulSoup(html, 'html.parser')
    if last_page_link := soup.find(title='last page'):
        return int(last_page_link.get_text(strip=True).strip("[]"))
    else:
        return 1  # fallback if "last page" does not exist


async def scrape_users():
    """
    Asynchronously scrapes all users for each country.
    Returns a (flat) list of all user names from all pages, or an empty list if none.
    """
    all_users = []

    async with aiohttp.ClientSession() as session:
        countries = await fetch_countries(session)

        tasks = []
        for country in countries[:2]:
            first_page_url = build_country_url(country, 1)
            last_page = await find_last_page(session, first_page_url)

            for page_num in range(1, last_page + 1):
                page_url = build_country_url(country, page_num)
                tasks.append(fetch_users_on_page(session, page_url))

        # Now gather all results concurrently
        results = await asyncio.gather(*tasks)

        # Flatten the list of lists into a single list
        for user_list in results:
            all_users.extend(user_list)

    return all_users


def main():
    return await scrape_users()
