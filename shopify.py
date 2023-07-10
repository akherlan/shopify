#!/usr/bin/env python3

import crawler
import scraper
import asyncio
import argparse
import time
import re


async def main(command, fin, fout):
    start = time.time()
    if command == "crawl":
        if not re.findall("^https?://(www)?.+", fin):
            print("input must be URL e.g. https://enji.co.id")
        else:
            await crawler.scrape_product_url(url=fin, fileout=fout, all_product=True)
            print(f"---------- {time.time() - start} seconds ----------")
    elif command == "scrape":
        await scraper.get_data(fileout=fout, filein=fin)
        print(f"---------- {time.time() - start} seconds ----------")
    else:
        print("must be 'crawl' or 'scrape'")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Scraping product from Shopify powered website"
    )
    parser.add_argument("fileout", help="output path for result")
    parser.add_argument("-c", "--command", help="crawl, scrape")
    parser.add_argument("-i", "--input", help="website, path containing links")
    args = parser.parse_args()
    asyncio.run(main(command=args.command, fin=args.input, fout=args.fileout))
