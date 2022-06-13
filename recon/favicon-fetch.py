from cgi import print_environ_usage
import re
import string
import sys
import os
import requests
import bs4
import shodan
import codecs
import mmh3
from dotenv import load_dotenv
import urllib.parse as url_parse


def fetch_favicon(api, hash):
    query = f"http.favicon.hash:{hash}"
    print(f"Searching for: https://www.shodan.io/search?query={url_parse.quote(query)}")
    try:
        results = api.search(f"http.favicon.hash:{hash}")

        print("Results found: {}".format(results["total"]))
        for result in results["matches"]:
            print("IP: {}".format(result["ip_str"]))
            print(result["data"])
            print("")
    except shodan.APIError as e:
        print("Error: {}".format(e))


def get_favicon(url: string):
    response = requests.get(url)
    if response.status_code != 200:
        exit()

    soup = bs4.BeautifulSoup(response.text, "html.parser")
    for link in soup.find_all("link"):
        if "icon" in link.get("rel"):
            favicon_url = link.get("href")

    favicon_content = requests.get(favicon_url).content
    favicon_base64 = codecs.encode(favicon_content, "base64")
    favicon_hash = abs(mmh3.hash(favicon_base64))
    return favicon_hash


def main():
    load_dotenv()
    SHODAN_API_KEY = os.getenv("SHODAN_API_KEY")
    api = shodan.Shodan(SHODAN_API_KEY)

    url = sys.argv[1]
    favicon_hash = get_favicon(url)
    fetch_favicon(api, favicon_hash)


def usage():
    print(
        f"""
        usage: 
            python3 {sys.argv[0]} <URL>
        examples:
            python3 {sys.argv[0]} https://apple.com
            python3 {sys.argv[0]} http://example.com
    """
    )
    exit(1)


if __name__ == "__main__":
    for arg in sys.argv:
        if arg in ["-h", "--help", "-help", "help"]:
            usage()

    if len(sys.argv) == 2:
        main()
    else:
        usage()
