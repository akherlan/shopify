import json
import argparse
from rich import print


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pretty print JSON")
    parser.add_argument("file", help="input path JSON")
    args = parser.parse_args()
    with open(args.file) as f:
        data = json.load(args.file)
        print(data)
