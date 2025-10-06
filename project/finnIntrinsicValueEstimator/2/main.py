    import requests
from bs4 import BeautifulSoup
import time
import re

# Base URL for the search
base_url = "https://hjem.no/list"
params = {
    "locationBottomRightLat": "60.34309013609257",
    "locationBottomRightLng": "5.442352294921876",
    "locationTopLeftLat": "60.46144960413299",
    "locationTopLeftLng": "5.182800292968751",
    "zoomLevel": "12",
    "mapCentroid": "60.402323675432804",  # Note: duplicated in original, keeping first
    "bedroomMin": "2",
    "askingPriceMin": "1000000",
    "askingPriceMax": "8700000",
    "totalPriceMin": "1950000",
    "totalPriceMax": "7000000",
}

# Headers to mimic a browser
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}


def get_property_links(session, page=1):
    """
    Fetch property links from a single page.
    Adjust the CSS selector based on actual site structure (inspect element on hjem.no).
    Common selectors: 'article a[href*="/bolig/"]', '.listing-item a', etc.
    """
    params_copy = params.copy()
    if page > 1:
        params_copy["page"] = page  # Assuming pagination uses ?page=N

    response = session.get(base_url, params=params_copy, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # TODO: Inspect the page source and update this selector
    # For example, if listings are in <article> tags with links:
    listing_links = []
    for link in soup.find_all(
        "a", href=re.compile(r"/bolig/\d+")
    ):  # Adjust regex to match property URLs, e.g., /bolig/12345
        href = link.get("href")
        if href and not href.startswith("http"):
            full_url = "https://hjem.no" + href
        else:
            full_url = href
        if full_url not in listing_links:
            listing_links.append(full_url)

    # Check if there are more pages (adjust based on pagination element)
    has_next = bool(
        soup.find("a", text=re.compile(r"Neste|Next", re.I))
    )  # Or check total count

    return listing_links, has_next


def scrape_all_links():
    all_links = []
    session = requests.Session()
    page = 1
    max_pages = 10  # Safety limit, since ~99 results, likely 4-5 pages

    while page <= max_pages:
        print(f"Scraping page {page}...")
        links, has_next = get_property_links(session, page)
        all_links.extend(links)
        print(
            f"Found {len(links)} links on page {page}. Total so far: {len(all_links)}"
        )

        if not links or not has_next:
            break

        page += 1
        time.sleep(1)  # Be polite, delay between requests

    session.close()
    return all_links


if __name__ == "__main__":
    links = scrape_all_links()
    print(f"\nTotal property links scraped: {len(links)}")
    for i, link in enumerate(links, 1):
        print(f"{i}. {link}")

    # Optionally save to file
    with open("property_links.txt", "w") as f:
        for link in links:
            f.write(link + "\n")
    print("\nLinks saved to 'property_links.txt'")
