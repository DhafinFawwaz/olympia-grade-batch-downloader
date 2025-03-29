import requests
from bs4 import BeautifulSoup
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm


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

def process_row(row, HEADERS, COOKIES):
    tds = row.find_all("td")
    for td in tds:
        if td.get("id", "").startswith("mod-quiz-report-overview-report_") and td.get("id", "").endswith("_c2"):
            links = td.find_all("a")
            if len(links) >= 2:
                name = links[0].get_text(strip=True)
                href = links[1].get("href")
                attachments = fetch_attachments(href, HEADERS, COOKIES)
                return (name, href, attachments)
    return None

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

    rows = tbody.find_all("tr")
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(process_row, row, HEADERS, COOKIES): row for row in rows}
        
        progress_bar = tqdm(total=len(futures), desc="Fetching data", unit="row")
        
        for future in as_completed(futures):
            result = future.result()
            if result:
                results.append(result)
            progress_bar.update(1)

        progress_bar.close()

    return results

def save_to_json_file(data, folder):
    with open(folder+".json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def download_file(file_name, file_url, student_folder, HEADERS, COOKIES):
    file_path = os.path.join(student_folder, file_name)
    try:
        response = requests.get(file_url, headers=HEADERS, cookies=COOKIES)
        response.raise_for_status()
        
        with open(file_path, "wb") as f:
            f.write(response.content)

        return True
    except Exception as e:
        print(f"Error downloading {file_name} from {file_url}: {e}")
        return False
    
def save_student_data(data, base_folder, HEADERS, COOKIES):
    os.makedirs(base_folder, exist_ok=True)
    
    total_files = sum(len(attachments) for _, _, attachments in data)  # Count total files
    progress_bar = tqdm(total=total_files, desc="Downloading files", unit="file")

    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_file = {}

        for name, href, attachments in data:
            student_folder = os.path.join(base_folder, name.replace(" ", "_"))
            os.makedirs(student_folder, exist_ok=True)

            href_file = os.path.join(student_folder, "href.txt")
            with open(href_file, "w", encoding="utf-8") as f:
                f.write(href)

            for file_name, file_url in attachments:
                future = executor.submit(download_file, file_name, file_url, student_folder, HEADERS, COOKIES)
                future_to_file[future] = file_name

        for future in as_completed(future_to_file):
            future.result()
            progress_bar.update(1)

    progress_bar.close()

