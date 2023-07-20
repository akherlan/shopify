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
        product = html.css_first("script[type='application/ld+json']")
        logging.info("check point 1: {}".format(product))
        if product is not None:
            product = product.text(strip=True)
            logging.info("check point 2: {}".format(product))
        else:
            product = html.css_first("link[type='application/json+oembed']")
            logging.info("check point 3: {}".format(product))
            if product is not None:
                product_href = product.attributes.get("href")
                logging.info(f"product_href: {product_href}")
                product = httpx.get(product_href).text
                logging.info("check point 4: {}".format(product))
        if product:
            product = json.loads(product, strict=False)
            logging.info("check point 5: {}".format(product))
            description = extract_description(html)
            if description is not None:
                product.update({"description": description})
    except Exception as e:
        logging.info("title: {}".format(html.css_first("title").text(strip=True)))
        logging.error(f"{str(e)} {str(response.url)}", exc_info=True)
        product = None
    finally:
        yield product


def extract_description(html):
    try:
        description = html.css_first("div.Rte").html
    except Exception as e:
        # description = html.css_first("div#description")
        # if description:
        #     description = description.html
        # else:
        #     description = None
        #     logging.warning(str(e))
        description = None
        logging.warning(str(e))
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

