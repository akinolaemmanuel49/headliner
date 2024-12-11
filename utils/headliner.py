from typing import Dict, List, Optional, TypedDict

from bs4 import BeautifulSoup
import requests


class Headline(TypedDict):
    text: str
    link: Optional[str]


class Response(TypedDict):
    network: str
    headlines: Headline


def headlines(sources: List[Response]) -> Dict[str, List[Headline]]:
    """
    Aggregate headlines from multiple sources.

    Args:
        sources (List[Response]): List of responses from different sources, each containing a network name and its headlines.

    Returns:
        Dict[str, List[Headline]]: Dictionary mapping network names to their list of headlines.
    """
    aggregated_headlines = {}

    for source in sources:
        network = source["network"]
        network_headlines = source["headlines"]

        # Add to the aggregated dictionary
        if network not in aggregated_headlines:
            aggregated_headlines[network] = []

        aggregated_headlines[network].extend(network_headlines)

    return aggregated_headlines


def bbcnews_headlines() -> Response:
    url = "https://www.bbc.com/"
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

    return {"network": "BBC News", "headlines": extracted_headlines}


def nbcnews_headlines() -> Response:
    url = "https://www.nbcnews.com/"
    req = requests.get(url)

    soup = BeautifulSoup(req.text, "html.parser")

    headlines = soup.find_all("h2", class_="multistoryline__headline")
    extracted_headlines = []

    for headline in headlines:
        # Extract and clean the text
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

    return {"network": "NBC News", "headlines": extracted_headlines}
