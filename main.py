from scrapper import get_names_and_links, to_json, save_student_data
import argparse
import json

COOKIES = json.load(open("cookies.json"))
HEADERS = {}

parser = argparse.ArgumentParser()
parser.add_argument("folder", type=str, help="Folder to save the data")
parser.add_argument("url", type=str, help="URL to scrape")
args = parser.parse_args()
url = args.url
folder = args.folder

data = get_names_and_links(url, HEADERS, COOKIES)
to_json(data)
save_student_data(data, folder, HEADERS, COOKIES)
