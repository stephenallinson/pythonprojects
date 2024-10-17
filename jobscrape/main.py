from bs4 import BeautifulSoup
import cloudscraper
import time

scraper = cloudscraper.create_scraper()  # create cloudscraper instance


# Define the search paramaeters
def search_params(search_title, search_location):
    job_title = search_title.replace(" ", "+").lower()
    location = search_location.lower()
    url = "https://ca.indeed.com/jobs?q=" + job_title + "&l=" + location

    print(url)

    return url


def page_data(url):
    html = scraper.get(url)  # scrape URL
    soup = BeautifulSoup(html.text, "html.parser")  # parse the URL
    print(soup.find("title"))
    return soup  # return HTML


def job_data(parse_soup, topic, location):
    titles = []
    companies = []
    posting_url = []

    for i in parse_soup.find_all(
        "span", attrs={"id": lambda e: e.startswith("jobTitle") if e else False}
    ):
        titles.append(i.get_text())
    for i in parse_soup.find_all(
        "a", attrs={"class": lambda e: e.startswith("jcs") if e else False}
    ):
        posting_url.append("https://ca.indeed.com" + i.get("href"))
    for i in parse_soup.find_all(
        "span",
        attrs={"data-testid": lambda e: e.startswith("company-name") if e else False},
    ):
        if not i:
            companies.append("No Company Found")
        else:
            companies.append(i.get_text())

    markdown_location = f"/home/stephen/Documents/JCA Personal/Stephen/Jobs/Job Scrape/{str(time.strftime("%Y%m%d"))}.md"

    if len(titles) > 1:
        with open(markdown_location, "a") as file:
            print(f"Searching for jobs listed {topic} in {location}")
            file.write(f"# RESULTS FOR {topic} IN {location}\n\n")
            for i in range(len(titles)):
                print(f"- Found: {titles[i]} at {companies[i]}")
                file.write(
                    "- ["
                    + titles[i]
                    + "]("
                    + posting_url[i]
                    + ") at "
                    + companies[i]
                    + "\n\n"
                )
        return True
    else:
        return False


# Put Job Title and Location as a tuple
search = [
    ("Information Technology", "Winnipeg"),
    ("Information Technology Manager", "Winnipeg"),
    ("IT", "Winnipeg"),
]


success = False
while not success:
    for topic, location in search:
        text = search_params(topic, location)
        jobs = page_data(text)
        result = job_data(jobs, topic, location)
        if not result:
            time.sleep(1)
            print(f"Did not find any results matching: {topic} in {location}\n")
            success = False
        else:
            print(f"Found results matching: {topic} in {location}\n")
            success = True
