import httpx
import asyncio
import logging
import json
from random import randint
from urllib.parse import urljoin
from selectolax.parser import HTMLParser


logging.basicConfig(
    # filename="logs",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def parse_product(response):
    html = HTMLParser(response.text)
    try:
        product = html.css_first("script[type='application/ld+json']").text()
        product = json.loads(product, strict=False)
        description = extract_description(html)
        if description is not None:
            product.update({"description": description})
    except Exception as e:
        logging.error(f"{str(e)} {str(response.url)}", exc_info=True)
    finally:
        yield product


def extract_description(html):
    try:
        description = html.css_first("div.Rte").html
    except Exception as e:
        description = None
        logging.error(str(e))
    finally:
        return description


async def get_product(urlpath: str, timeout: int = 60):
    async with httpx.AsyncClient(timeout=httpx.Timeout(timeout)) as session:
        with open(urlpath) as fin:
            links = [link.strip() for link in fin.readlines()]
        requests = [session.get(link) for link in links]
        for task in asyncio.as_completed(requests):
            response = await task
            await asyncio.sleep(randint(0, 5))
            for product in parse_product(response):
                # logging.info(f"GET {str(response.url)}")
                yield product

async def get_data(fileout, filein):
    with open(fileout, "w") as f:
        data = []
        async for product in get_product(filein):
            data.append(product)
        json.dump(data, f)


if __name__ == "__main__":
    pass
