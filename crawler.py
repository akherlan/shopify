import httpx
import asyncio
from urllib.parse import urljoin
from random import randint
from selectolax.parser import HTMLParser


async def fetch_catalog(url, session):
    url = urljoin(url, "products")
    response = await session.get(url)
    html = HTMLParser(response.text)
    catalog = []
    for item in html.css("a.CollectionItem"):
        collection = item.attributes.get("href")
        catalog.append(urljoin(url, collection))
    return catalog


def parse_catalog(response):
    for item in HTMLParser(response.text).css("h2 > a"):
        yield urljoin(str(response.url), item.attributes.get("href"))


def get_pagination(response):
    html = HTMLParser(response.text)
    navigations = html.css("div.Pagination__Nav a")
    if navigations is not None:
        page_nav = [nav.text(strip=True) for nav in navigations]
        if len(page_nav) >= 2 and int(page_nav[-2]) >= 2:
            return [
                str(response.url) + f"?page={page}"
                for page in range(2, int(page_nav[-2]) + 1)
            ]
        else:
            return []
    else:
        return []


async def fetch_product(url, all_product=False, timeout=60):
    async with httpx.AsyncClient(timeout=httpx.Timeout(timeout)) as session:
        catalog = await fetch_catalog(url, session)
        responses = [session.get(item_catalog) for item_catalog in catalog]
        for task in asyncio.as_completed(responses):
            response = await task
            await asyncio.sleep(randint(0, 2))
            for product in parse_catalog(response):
                yield product
            if all_product:
                other_pages = [session.get(page) for page in get_pagination(response)]
                for task in asyncio.as_completed(other_pages):
                    resp = await task
                    for product in parse_catalog(resp):
                        yield product


async def scrape_product_url(url: str, fileout: str, all_product: bool = False):
    with open(fileout, "a") as f:
        async for item in fetch_product(url, all_product):
            f.write(item + "\n")
            print(item)


if __name__ == "__main__":
    pass
