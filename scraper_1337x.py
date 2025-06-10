from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
from bs4 import BeautifulSoup
import logging
import os

BASE_URL = "https://www.1337x.to"
PROXY = os.getenv("HTTP_PROXY")  # Set your proxy URL in the environment variable

# Updated User-Agent
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def search_1337x(query):
    try:
        logging.debug(f"Starting Playwright browser for query: {query}")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)  # Run in non-headless mode to help bypass Cloudflare
            context = browser.new_context(
                user_agent=HEADERS["User-Agent"],
                viewport={"width": 1280, "height": 800},
                locale="en-US",
                timezone_id="America/Chicago"
            )
            page = context.new_page()
            stealth_sync(page)  # Apply stealth to evade bot detection

            url = f"{BASE_URL}/search/{query}/1/"
            page.goto(url)

            logging.debug("Waiting for CloudFlare challenge to complete...")
            try:
                page.wait_for_load_state("networkidle", timeout=60000)  # Wait for network to be idle
                page.wait_for_selector(".table-list tbody tr", timeout=60000)  # Wait for the selector
            except Exception as e:
                logging.error(f"Timeout while waiting for page to load: {e}")
                logging.debug(f"Page content for debugging: {page.content()[:1000]}")  # Log first 1000 characters of page content
                browser.close()
                return []

            soup = BeautifulSoup(page.content(), "html.parser")
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
                    magnet_link = get_magnet_link(link, page)

                    # Append the data as a tuple
                    results.append((title, seeders, leechers, magnet_link, link))

            logging.debug(f"Parsed {len(results)} results from the response.")
            browser.close()
            return results
    except Exception as e:
        logging.error(f"Error during search_1337x: {e}", exc_info=True)
        return []

def get_magnet_link(torrent_url, page=None):
    try:
        logging.debug(f"Fetching magnet link from URL: {torrent_url}")
        page.goto(torrent_url)

        logging.debug("Waiting for magnet link to load...")
        page.wait_for_selector("a[href^='magnet:?xt=']")

        soup = BeautifulSoup(page.content(), "html.parser")
        magnet_tag = soup.select_one("a[href^='magnet:?xt=']")
        if magnet_tag:
            logging.debug("Magnet link found.")
            return magnet_tag['href']
        logging.warning("Magnet link not found.")
        return None
    except Exception as e:
        logging.error(f"Error during get_magnet_link: {e}", exc_info=True)
        return None
