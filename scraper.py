import httpx
import asyncio

from random import randint
from urllib.parse import urljoin
from selectolax.parser import HTMLParser

import logging
import json
import os
import re


logging.basicConfig(
    # filename="log.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def parse_product(response):
    html = HTMLParser(response.text)
    try:
        json_obj = html.css("script[type='application/json']")
        if len(json_obj) >= 2:
            product = json_obj[1]
        elif html.css_matches("link[type='application/json+oembed']"):
            json_obj = list(
                filter(lambda node: node.css_matches("script[id*=product]"), json_obj)
            )
            product = json_obj[0] if len(json_obj) > 0 else None
        else:
            product = html.css_first("script[type='application/ld+json']")
        if product:
            product = product.text(strip=True)
            product = json.loads(product, strict=False)
    except Exception as e:
        logging.info("title: {}".format(html.css_first("title").text(strip=True)))
        logging.error(f"{str(e)} {str(response.url)}", exc_info=True)
        product = None
    finally:
        yield product


async def get_product(urlpath: str, timeout: int = 60):
    async with httpx.AsyncClient(timeout=httpx.Timeout(timeout)) as session:
        with open(urlpath) as fin:
            links = [link.strip() for link in fin.readlines()]
        requests = [session.get(link) for link in links]
        for task in asyncio.as_completed(requests):
            response = await task
            await asyncio.sleep(randint(0, 5))
            for product in parse_product(response):
                yield product


async def get_data(fileout, filein):
    if re.findall("/", fileout):
        directory = fileout.replace(fileout.split("/")[-1], "")
        if not os.path.exists(directory):
            os.makedirs(directory)
    with open(fileout, "w") as f:
        data = []
        async for product in get_product(filein):
            data.append(product)
        json.dump(data, f)


if __name__ == "__main__":
    pass
