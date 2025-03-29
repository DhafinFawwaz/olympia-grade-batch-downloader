# Olympia Batch Grades Downloader

## Getting Started
rename `cookies.example.json` to `cookies.json` and fill in your cookies.

## Quick Command
The url here is the url of a page that contains tables with grades. So currently you have to manually navigate to the page you want to download and copy the url from the address bar. Do it for all the pages.
```bash
python main.py page1 "https://olympia.id/mod/quiz/report.php?id=7239&mode=overview&attempts=enrolled_with&onlygraded&onlyregraded=0&slotmarks=1&page="
```

## Command
```bash
python main.py <downloaded folder> <url>
```