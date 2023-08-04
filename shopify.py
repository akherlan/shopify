#!/usr/bin/env python3

from scraper import ShopifyScraper
import argparse
import time


def main(url, product_file=None, offers_file=None, timer=False):
    tic = time.perf_counter()
    shopify = ShopifyScraper(url)
    data = shopify.fetch()
    product, offers = shopify.transform(data)
    if product_file is not None:
        shopify.save(product, product_file)
        print(f"Saved product dataset to {product_file}")
    if offers_file is not None:
        shopify.save(offers, offers_file)
        print(f"Saved pricing data to {offers_file}")
    if timer:
        toc = time.perf_counter()
        print(f"---------- {toc - tic:.2f} seconds ----------")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Scraping product from a Shopify powered website"
    )
    parser.add_argument("url", help="Shopify website")
    parser.add_argument("-p", "--product", nargs="?", help="Product file output")
    parser.add_argument("-o", "--offers", nargs="?", help="Prices file output")
    parser.add_argument(
        "-t", "--timer", action="store_true", help="Show timer at the end"
    )
    args = parser.parse_args()
    main(
        url=args.url,
        product_file=args.product,
        offers_file=args.offers,
        timer=args.timer,
    )
