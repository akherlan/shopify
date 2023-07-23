#!/usr/bin/env python3

from scraper import ShopifyScraper
import argparse
import time


def main(url, product_file, offers_file):
    tic = time.perf_counter()

    shopify = ShopifyScraper(url)
    data = shopify.fetch()
    product, offers = shopify.transform(data)
    shopify.save(product, product_file)
    shopify.save(offers, offers_file)

    toc = time.perf_counter()
    print(f"---------- {toc - tic:.2f} seconds ----------")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Scraping product from a Shopify powered website"
    )
    parser.add_argument("url", help="Shopify website")
    parser.add_argument("-p", "--product", help="product file output")
    parser.add_argument("-o", "--offers", help="prices file output")
    args = parser.parse_args()
    main(url=args.url, product_file=args.product, offers_file=args.offers)
