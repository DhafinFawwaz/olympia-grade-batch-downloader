import requests
from bs4 import BeautifulSoup
import requests
from bs4 import BeautifulSoup
import requests
from bs4 import BeautifulSoup
import json
import os


def fetch_attachments(url, HEADERS, COOKIES):
    response = requests.get(url, headers=HEADERS, cookies=COOKIES)
    soup = BeautifulSoup(response.text, "html.parser")

    attachments = []
    count = 1
    for div in soup.find_all("div", class_="attachments"):
        for a in div.find_all("a", recursive=True):
            text = a.get_text(strip=True)
            href = a.get("href")
            if text and href:
                attachments.append((str(count) + ". " + text, href))
            else:
                attachments.append((None, None))
        count += 1
    return attachments

def get_names_and_links(url, HEADERS, COOKIES):
    response = requests.get(url, headers=HEADERS, cookies=COOKIES)
    soup = BeautifulSoup(response.text, "html.parser")

    results = []

    table = soup.find("table", id="attempts")
    if not table:
        return results

    tbody = table.find("tbody")
    if not tbody:
        return results

    count = 0
    for row in tbody.find_all("tr"):
        if count == 1: break
        count += 1
        tds = row.find_all("td")
        for td in tds:
            if td.get("id", "").startswith("mod-quiz-report-overview-report_") and td.get("id", "").endswith("_c2"):
                links = td.find_all("a")
                if len(links) >= 2:
                    name = links[0].get_text(strip=True)
                    href = links[1].get("href")
                    attachment_data = fetch_attachments(href, HEADERS, COOKIES)
                    results.append((name, href, attachment_data))
                    print((name, href, attachment_data))

    return results

def to_json(data):
    return json.dumps(data, indent=4)

def save_student_data(data, base_folder, HEADERS, COOKIES):
    os.makedirs(base_folder, exist_ok=True)

    for name, href, attachments in data:
        student_folder = os.path.join(base_folder, name.replace(" ", "_"))
        os.makedirs(student_folder, exist_ok=True)
        href_file = os.path.join(student_folder, "href.txt")
        with open(href_file, "w", encoding="utf-8") as f:
            f.write(href)

        for file_name, file_url in attachments:
            file_path = os.path.join(student_folder, file_name)
            try:
                response = requests.get(file_url, headers=HEADERS, cookies=COOKIES)
                response.raise_for_status()
                
                with open(file_path, "wb") as f:
                    f.write(response.content)
                
                print(f"Downloaded: {file_name} -> {file_path}")
            except Exception as e:
                print(f"Failed to download {file_name}: {e}")

