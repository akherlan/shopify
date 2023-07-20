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
    for item in html.css("a"):
        collection = item.attributes.get("href")
        try:
            is_catalog = collection.split("/")[1] == "collections"
        except:
            is_catalog = False
        link = urljoin(url, collection)
        if is_catalog and link not in catalog:
            catalog.append(link)
    return catalog


def parse_catalog(response):
    for item in HTMLParser(response.text).css("a"):
        product_link = item.attributes.get("href")
        try:
            product_split = product_link.split("/")
            is_product = (
                product_split[1] == "collections" and product_split[3] == "products"
            )
        except:
            is_product = False
        if is_product:
            yield urljoin(str(response.url), product_link)


def get_pagination(response):
    html = HTMLParser(response.text)
    navigations = html.css("div[class*=agination] a")
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
        product_urls = []
        async for item in fetch_product(url, all_product):
            if item not in product_urls:
                f.write(item + "\n")
                product_urls.append(item)
                print(item)


if __name__ == "__main__":
    pass

