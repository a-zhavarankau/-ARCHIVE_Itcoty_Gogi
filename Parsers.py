import re

from flask import Flask
import requests, random, time
from bs4 import BeautifulSoup as bs
from bs4 import NavigableString, Comment
from pprint import pprint

app = Flask(__name__)




def prepare_search_input(query_input):
        if len(query_input) != 0:
            search_query = query_input
        else:
            return "Please enter keyword"
        url_add = "".join([f"%20{i}" if len(search_query) > 1 else i for i in search_query]).strip("%20")
        return url_add


def create_search_url_glassdoor():
    query_input = input("\nGlassdoor.com\nEnter keywords by space here: ").split()
    url_add = prepare_search_input(query_input)
    search_url = "https://www.glassdoor.com/Job/jobs.htm?sc.keyword=" + url_add
    return search_url


def is_exists_glassdoor(item):            # Checking if any field (Position, Salary, Location) exists
    try:
        result = item.text
    except AttributeError:
        result = "N/A"
    return result


def get_descr_glassdoor(link, headers):    # Getting description walking string by strings
    vac_req = requests.get(url=link, headers=headers)
    vac_soup = bs(vac_req.text, "lxml")
    big_div = vac_soup.find("div", class_="ecgq1xb4")
    if big_div == None:
        return f"Description not specified"

    # from bs4 import NavigableString, Comment          # ===== Must try this =====
    # print
    # ''.join(unicode(child) for child in hit.children
    #         if isinstance(child, NavigableString) and not isinstance(child, Comment))


    descr_raw = ""
    for i in big_div.descendants:
        if isinstance(i, str):
            if str(i.previous_element.name) == "li":  # set(tag.name for tag in BeautifulSoup(html_cal, 'html.parser').find_all())
                descr_raw += f"\u30FB{i.strip('Â').strip()}\n"
            else:
                descr_raw += f"{i.strip('Â').strip()}\n"
    descr_fine = "\n".join([stng.rstrip() for stng in descr_raw.splitlines() if stng.strip()])
    return descr_fine


def parsing_glassdoor():
    search_url = create_search_url_glassdoor()
    print(f"\nSearch link is: {search_url}\n")
    headers = {
        "Accept": "image/avif,image/webp,*/*",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/94.0.4606.81 Safari/537.36"
    }

    req = requests.get(url=search_url, headers=headers)
    soup = bs(req.text, "lxml")

    pages_by_url = soup.find("div", {"data-test": "page-x-of-y"}).text.split()[-1]  # Getting max quantity of pages
    last_page_by_url = search_url + "&p=" + pages_by_url  # by searching request
    print("Last page by request is: ", last_page_by_url, "\n")

    page_num = 0
    all_id = []
    for i in range(int(pages_by_url)):
        search_url_one_page = search_url + "&p=" + str(page_num)
        req = requests.get(url=search_url_one_page, headers=headers)
        soup = bs(req.text, "lxml")

        all_vacs_per_page = soup.find_all("li", class_="react-job-listing")

        # for i, vac in enumerate(all_vacs_per_page):                                     # Output all vacancy's positions
        #     print(i + 1, vac.find("a", {"data-test": "job-link"}).find("span").text,    # and locations (to find error)
        #           vac.find("span", {"class": "css-1buaf54"}).text)                      # This list not equal as in a browser
        # print()

        count = page_num*30
        for vac in all_vacs_per_page:                                                   # Output vacancy information0
            pos = is_exists_glassdoor(vac.find("a", {"data-test": "job-link"}).find("span"))                # Position
            sal = is_exists_glassdoor(vac.find("span", {"data-test": "detailSalary"}))                      # Salary
            comp = is_exists_glassdoor(vac.find("div", {"class": "flex-nowrap"}).find_previous_sibling())   # Company
            loc = is_exists_glassdoor(vac.find("span", {"class": "css-1buaf54"}))                           # Location
            vac_id = vac.get("data-id")                                                                  # Vacancy ID
            linkv = "https://www.glassdoor.com" + vac.find("a", {"data-test": "job-link"}).get("href")   # Link
            descr = get_descr_glassdoor(linkv, headers)

            count += 1
            print(f' {count}\n Position: {pos}\n Salary: {sal}\n Company: {comp}\n Location: {loc}\n '
                  f'ID: {vac_id}\n Link: {linkv}\n Description: \n{descr}\n')

            # time.sleep(random.randrange(1, 3))
            all_id.append(vac_id) if vac_id not in all_id else print("This vacancy already exists")

        page_num += 1

    print("All vacancies from Glassdoor.com are presented")




def create_search_url_dev():
    query_input = input("\nDev.by\nEnter keywords by space here: ").split()
    url_add = prepare_search_input(query_input)
    search_url = f'https://jobs.dev.by/?&filter%5Bsearch%5D={url_add}'
    return search_url


def is_exists_dev(item):            # Checking if any field in vacancy exists
    try:
        result = item.next_element.text
    except AttributeError:
        result = "N/A"
    return result


def get_descr_dev(bs):    # Getting description walking string by strings
    descr_raw = bs.find("div", class_="text")
    if descr_raw == None:
        return f"Description not specified"
    descr_edited = ""
    for i in descr_raw.descendants:
        if isinstance(i, str):
            # regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
            # url = re.findall(regex, str(i.previous_sibling))      # ===== Checking if URL in the text ===== #
            # if url:
            #     descr_edited += f"{i.strip()} {url}\n"
            if str(i.previous_element.name) == "li":
                descr_edited += f"\n\u30FB{i.strip()}"
            else:
                descr_edited += f"{i.strip()}\n"
    descr_fine = "\n".join([stng.rstrip() for stng in descr_edited.splitlines() if stng.strip()])
    return descr_fine


def parsing_dev():
    search_url = create_search_url_dev()
    print(f"\nSearch link is: {search_url}\n")
    headers = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/95.0.4638.54 Safari/537.36 Edg/95.0.1020.30"
            }

    req = requests.get(url=search_url, headers=headers)
    page = bs(req.text, "lxml")
    all_vacs = page.findAll("div", class_="vacancies-list-item")    # All vacancies as bs's elements

    vac_num = 1
    for vac in all_vacs:
        premium_vac_banner = vac.find("a", class_="button--link")
        email_vac_service = vac.find("div", class_="vacancies-item-banner")
        if not (premium_vac_banner or email_vac_service):
            link = "https://jobs.dev.by" + vac.find("a", class_="vacancies-list-item__link_block").get("href")
            vac_req = requests.get(url=link, headers=headers)
            vac_bs = bs(vac_req.text, "lxml")
            pos = is_exists_dev(vac_bs.find("h1", class_="title"))
            spec = is_exists_dev(vac_bs.find(text="Специализация: "))
            level = is_exists_dev(vac_bs.find(text="Уровень: "))
            expir = is_exists_dev(vac_bs.find(text="Опыт: "))
            english = is_exists_dev(vac_bs.find(text="Уровень английского: "))
            salary = is_exists_dev(vac_bs.find(text="Зарплата: "))
            loc = is_exists_dev(vac_bs.find(text="Город: "))
            sched = is_exists_dev(vac_bs.find(text="Режим работы: "))
            cows = is_exists_dev(vac_bs.find(text="Размер команды: "))
            comp_size = is_exists_dev(vac_bs.find(text="Размер компании: "))
            remote = is_exists_dev(vac_bs.find(text="Возможна удалённая работа: "))
            skills_in_tags = vac_bs.find_all("div", class_="vacancy__tags__item")
            skills = ", ".join([i.next_element.text for i in skills_in_tags if skills_in_tags])
            descr = get_descr_dev(vac_bs)

            print(f"{vac_num}/{len(all_vacs)-2}\nPosition: {pos}\nSpecialization: {spec}\nLevel: {level}"
                  f"\nExpirience: {expir}\nEnglish level: {english}\nSalary: {salary}\nLocation: {loc}"
                  f"\nSchedule: {sched}\nCo-workers: {cows}\nCompany size: {comp_size}\nRemote: {remote}"
                  f"\nSkills: {skills}\nDescription: {descr}\nLink: {link}\n")
            vac_num += 1
            # time.sleep(random.randrange(1, 3))

    print("All vacancies from Dev.by are presented")


# parsing_glassdoor()
# parsing_dev()


@app.route('/')
def hello_world():
    pass

if __name__ == '__main__':
    app.run()