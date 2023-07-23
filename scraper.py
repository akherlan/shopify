import httpx
import json
import pandas as pd
from urllib.parse import urljoin
from datetime import datetime
import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class ShopifyScraper:
    def __init__(self, website, **kwargs):
        headers = {"user-agent": "httpx"}
        self.session = httpx.Client(timeout=30, headers=headers, **kwargs)
        self.website = website

    def fetch(self, limit=None):
        url = urljoin(self.website, "products.json")

        if limit is None:
            limit = 999999
            lim = 250
        elif limit > 250:
            lim = 250
        else:
            lim = limit

        p = 1
        last = False
        data = []

        while not last:
            par = {"limit": lim, "page": p}
            response = self.session.get(url, params=par)
            logging.info("GET page {}".format(str(p)))
            if response.status_code == 200:
                rawjson = response.json().get("products")
                data += rawjson
                last = bool(not len(rawjson)) or len(data) >= limit
                p += 1
            else:
                logging.error("bad response {}".format(response.status_code))
                return

        if len(data) > limit:
            data = data[:limit]
        logging.info("collect {} items from {}".format(len(data), self.website))
        return data

    def convert_date(self, string, fmt):
        return datetime.strptime(string, fmt)

    def transform(self, rawdata):
        acquisition_date = datetime.now()
        date_fmt = "%Y-%m-%dT%H:%M:%S%z"

        name = list(map(lambda item: item.get("title"), rawdata))
        description = list(map(lambda item: item.get("body_html"), rawdata))
        brand = list(map(lambda item: item.get("vendor"), rawdata))
        category = list(map(lambda item: item.get("product_type"), rawdata))
        date_release = list(
            map(
                lambda item: self.convert_date(item.get("published_at"), date_fmt),
                rawdata,
            )
        )
        slug = list(map(lambda item: item.get("handle"), rawdata))
        # images = list(map(lambda item: item.get("images"), rawdata))
        category = list(map(lambda item: item.get("product_type"), rawdata))
        tag = list(map(lambda item: item.get("tags"), rawdata))

        variants = list(map(lambda item: item.get("variants"), rawdata))
        collectible_product, collectible_offers = [], []

        for i, var in enumerate(variants):
            varid = list(map(lambda item: item.get("id"), var))
            sku = list(map(lambda item: item.get("sku"), var))
            # name = list(map(lambda item: item.get("name"), var))

            is_instock = list(map(lambda item: item.get("available"), var))
            price = list(map(lambda item: int(float(item.get("price"))), var))
            is_discount = list(
                map(lambda item: item.get("compare_at_price") != item.get("price"), var)
            )

            product = pd.DataFrame(
                list(
                    zip(
                        sku,
                        [name[i]] * len(sku),
                        [brand[i]] * len(sku),
                        [category[i]] * len(sku),
                        [date_release[i]] * len(sku),
                        [description[i]] * len(sku),
                        [slug[i]] * len(sku),
                    )
                ),
                columns=[
                    "sku",
                    "name",
                    "brand",
                    "category",
                    "date_release",
                    "description",
                    "slug",
                ],
            )
            collectible_product.append(product)

            offers = pd.DataFrame(
                list(
                    zip(
                        sku,
                        price,
                        ["IDR"] * len(sku),
                        is_instock,
                        [None] * len(sku),
                        [acquisition_date] * len(sku),
                    )
                ),
                columns=[
                    "sku",
                    "price",
                    "currency",
                    "is_instock",
                    "condition",
                    "last_updated",
                ],
            )
            collectible_offers.append(offers)

        product = pd.concat(collectible_product, ignore_index=True)
        offers = pd.concat(collectible_offers, ignore_index=True)
        return product, offers

    def save(self, dataset, fname):
        dataset.to_csv(fname, index=False)


if __name__ == "__main__":
    pass
