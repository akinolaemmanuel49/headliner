from datetime import datetime, timedelta
import json
from pathlib import Path
from typing import Dict, List, Optional, TypedDict

from bs4 import BeautifulSoup
import requests


class Headline(TypedDict):
    text: str
    link: Optional[str]


class Response(TypedDict):
    network: str
    timestamp: datetime
    headlines: List[Headline]


def get_cached_data() -> Dict[str, Dict]:
    """Load the cached headlines and their timestamps from the file."""
    FILE_PATH = Path("aggregator/static/aggregator/data/headliner.json")
    if FILE_PATH.exists():
        with open(FILE_PATH, "r") as file:
            return json.load(file)
    return {}


def save_cache(data: Dict[str, Dict]):
    """Save the updated headlines and timestamps to the cache."""
    FILE_PATH = Path("aggregator/static/aggregator/data/headliner.json")
    with open(FILE_PATH, "w") as file:
        json.dump(data, file, indent=4)


def headlines(sources: List[Response]) -> Dict[str, List[Headline]]:
    """
    Aggregate headlines from multiple sources.

    Args:
        sources (List[Response]): List of responses from different sources, each containing a network name and its headlines.

    Returns:
        Dict[str, List[Headline]]: Dictionary mapping network names to their list of headlines.
    """
    REFRESH_INTERVAL = timedelta(minutes=30)

    # Load the current cache
    cached_data = get_cached_data()

    aggregated_headlines = {}

    # Aggregate headlines, check timestamps for each source
    for source in sources:
        network = source["network"]
        timestamp = datetime.fromisoformat(source["timestamp"])
        
        # If the data for this network exists and is fresh, use the cached headlines
        if network in cached_data:
            cached_timestamp = datetime.fromisoformat(cached_data[network]["timestamp"])
            if datetime.now() - cached_timestamp < REFRESH_INTERVAL:
                # Use cached headlines
                aggregated_headlines[network] = cached_data[network]["headlines"]
                continue

        # If data is not cached or outdated, fetch new headlines
        network_headlines = source["headlines"]
        aggregated_headlines[network] = network_headlines

        # Save this data to the cache
        cached_data[network] = {
            "timestamp": datetime.now().isoformat(),
            "headlines": network_headlines
        }

    # Save the updated cache
    save_cache(cached_data)

    return aggregated_headlines


def bbcnews_headlines() -> Response:
    """Fetch the latest headlines from BBC News."""
    url = "https://www.bbc.com/"
    FILE_PATH = Path("aggregator/static/aggregator/data/bbc_headlines.json")
    
    # Check if there's cached data for BBC News
    if FILE_PATH.exists():
        with open(FILE_PATH, "r") as file:
            data = json.load(file)
        cached_timestamp = datetime.fromisoformat(data["timestamp"])
        if datetime.now() - cached_timestamp < timedelta(minutes=30):
            # Return cached headlines if data is recent
            return {
                "network": "BBC News",
                "timestamp": data["timestamp"],
                "headlines": data["headlines"]
            }

    # Otherwise, scrape new headlines
    req = requests.get(url)
    soup = BeautifulSoup(req.text, "html.parser")
    
    extracted_headlines = []
    headlines = soup.find_all("h2", {"data-testid": "card-headline"})

    for headline in headlines:
        headline_text = headline.get_text(strip=True)
        if headline_text == "":
            continue
        parent_link = headline.find_parent("a")
        headline_link = parent_link["href"] if parent_link else None
        if headline_link:
            full_link = (
                f"https://www.bbc.com{headline_link}"
                if headline_link.startswith("/")
                else headline_link
            )
        extracted_headlines.append({"text": headline_text, "link": full_link})

    # Save the new headlines to cache
    data = {
        "timestamp": datetime.now().isoformat(),
        "headlines": extracted_headlines
    }
    with open(FILE_PATH, "w") as file:
        json.dump(data, file, indent=4)

    return {
        "network": "BBC News",
        "timestamp": data["timestamp"],
        "headlines": extracted_headlines
    }


def nbcnews_headlines() -> Response:
    """Fetch the latest headlines from NBC News."""
    url = "https://www.nbcnews.com/"
    FILE_PATH = Path("aggregator/static/aggregator/data/nbc_headlines.json")

    # Check if there's cached data for NBC News
    if FILE_PATH.exists():
        with open(FILE_PATH, "r") as file:
            data = json.load(file)
        cached_timestamp = datetime.fromisoformat(data["timestamp"])
        if datetime.now() - cached_timestamp < timedelta(minutes=30):
            # Return cached headlines if data is recent
            return {
                "network": "NBC News",
                "timestamp": data["timestamp"],
                "headlines": data["headlines"]
            }

    # Otherwise, scrape new headlines
    req = requests.get(url)
    soup = BeautifulSoup(req.text, "html.parser")

    headlines = soup.find_all("h2", class_="multistoryline__headline")
    extracted_headlines = []

    for headline in headlines:
        headline_text = headline.get_text(strip=True)
        if headline_text == "":
            continue
        if headline.a:
            headline_link = headline.a["href"]
            full_link = (
                f"https://www.nbcnews.com{headline_link}"
                if headline_link.startswith("/")
                else headline_link
            )
        else:
            full_link = None

        extracted_headlines.append({"text": headline_text, "link": full_link})

    # Save the new headlines to cache
    data = {
        "timestamp": datetime.now().isoformat(),
        "headlines": extracted_headlines
    }
    with open(FILE_PATH, "w") as file:
        json.dump(data, file, indent=4)

    return {
        "network": "NBC News",
        "timestamp": data["timestamp"],
        "headlines": extracted_headlines
    }
