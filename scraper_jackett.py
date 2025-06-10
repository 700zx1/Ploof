from dotenv import load_dotenv
import os
import requests
import xml.etree.ElementTree as ET
import logging
import json

# Load environment variables from .env file
load_dotenv()

# Use environment variables directly
JACKETT_URL = os.getenv("JACKETT_URL", "http://localhost:9117/api/v2.0/indexers/all/results/torznab/api")
JACKETT_API_KEY = os.getenv("JACKETT_API_KEY", "")

def search_jackett(query):
    """
    Search Jackett/Prowlarr Torznab API for torrents.
    Returns a list of (title, seeders, leechers, magnet_link, url) tuples.
    """
    if not JACKETT_URL or not JACKETT_API_KEY:
        logging.error("Jackett URL or API key not set in config.json")
        return []

    params = {
        "apikey": JACKETT_API_KEY,
        "t": "search",
        "q": query
    }
    try:
        response = requests.get(JACKETT_URL, params=params, timeout=30)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        results = []
        for item in root.findall("./channel/item"):
            title = item.findtext("title", default="N/A")
            link = item.findtext("link", default="")
            seeders = int(item.findtext("{http://torznab.com/schemas/2015/feed}seeders", default="0"))
            leechers = int(item.findtext("{http://torznab.com/schemas/2015/feed}peers", default="0"))
            magnet_link = ""
            for enclosure in item.findall("enclosure"):
                url = enclosure.attrib.get("url", "")
                if url.startswith("magnet:?"):
                    magnet_link = url
                    break
            # Fallback: look for magnet in links
            if not magnet_link:
                for link_tag in item.findall("link"):
                    if link_tag.text and link_tag.text.startswith("magnet:?"):
                        magnet_link = link_tag.text
                        break
            results.append((title, seeders, leechers, magnet_link, link))
        logging.debug(f"Jackett returned {len(results)} results for query '{query}'")
        return results
    except Exception as e:
        logging.error(f"Error searching Jackett: {e}", exc_info=True)
        return []
