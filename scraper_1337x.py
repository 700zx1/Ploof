import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.1337x.to"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def search_1337x(query):
    url = f"{BASE_URL}/search/{query}/1/"
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")
    results = []

    for row in soup.select(".table-list tbody tr"):
        name_tag = row.select_one("td.name a:nth-of-type(2)")
        seeders_tag = row.select_one("td.seeds")
        leechers_tag = row.select_one("td.leeches")

        if name_tag and seeders_tag and leechers_tag:
            title = name_tag.text.strip()
            link = BASE_URL + name_tag['href']
            seeders = int(seeders_tag.text.strip())
            leechers = int(leechers_tag.text.strip())

            # Get the magnet link
            magnet_link = get_magnet_link(link)

            # Append the data as a tuple
            results.append((title, seeders, leechers, magnet_link, link))

    return results

def get_magnet_link(torrent_url):
    response = requests.get(torrent_url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")
    magnet_tag = soup.select_one("a[href^='magnet:?xt=']")
    if magnet_tag:
        return magnet_tag['href']
    return None
