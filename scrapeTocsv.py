from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from colorama import Fore, Style
import os
import time
import pandas as pd
from bs4 import BeautifulSoup
import pprint
pp = pprint.PrettyPrinter(indent=4)

# [DEBUG SELECTOR]
# WRITE = False
WRITE = True


def debug(argument: str, clearOnNew: bool = True):
    if WRITE:
        if os.path.exists("debug.txt"):
            if(clearOnNew):
                with open('debug.txt', 'w', encoding="utf-8") as debug:
                    debug.truncate(0)
                    debug.write(str(argument))
            else:
                with open('debug.txt', 'a', encoding="utf-8") as debug:
                    debug.write(str(argument))
            debug.close()


def convertToCsv(data):
    df = pd.DataFrame(data=data)
    df.to_csv('history_of_ferrari.csv', sep=',', header=True, index=False)
    print(f"{Fore.GREEN}"+"Successfully converted to csv."+f"{Style.RESET_ALL}")


data = dict()


def addToData(row, data=data):
    for spec in data:
        if spec not in row:
            data[spec].append(None)

    if "model" not in data:
        rowCount = 0

    else:
        rowCount = len(data["model"])

    for spec in row:
        if spec not in data:
            data[spec] = (rowCount) * [None]
        data[spec].append(row[spec])


skiplist = ["166 MM"]  # cdn unable to deliver jpgs
skipSkipList = False

history_home_url = 'https://www.ferrari.com/en-EN/auto/'
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
driver = webdriver.Chrome(chrome_options=options)
driver.get(history_home_url + 'past-model')
time.sleep(3)
page_source = driver.page_source

souped_History_home = BeautifulSoup(page_source, 'html.parser')
historySections = souped_History_home.find_all(
    'div', class_='PastModels__section__2TwZvTPv')

# [Print to text controls]
allowAll = True
stop = 0
condition = 5

for year in historySections:
    souped_year = BeautifulSoup(str(year), 'html.parser')
    yearOf = souped_year.find(
        'h2', class_='PastModels__sectionYear__33cNPh9I').get_text()
    modelsByYear = souped_year.find_all('a')
    for model in modelsByYear:
        row = dict()
        model_url = model.get('href')
        name_plate = BeautifulSoup(str(model), 'html.parser')
        name_parts = name_plate.find(
            'span', class_="PastModels__text__2qL1mq9T")
        name_parts = BeautifulSoup(str(name_parts), 'html.parser')
        name_parts = name_parts.findAll('span')
        model_name = name_parts[1].text
        model_type = name_parts[2].text
        if model_name in skiplist and skipSkipList:
            continue
        row["model"] = model_name
        row["year"] = yearOf
        print(f"{Fore.GREEN}"+yearOf + " - " + model_name+f"{Style.RESET_ALL}")
        driver.get(history_home_url + model_url)
        model_source = driver.page_source
        souped_model = BeautifulSoup(model_source, 'html.parser')
        available = souped_model.find('div', class_='main')
        if available:
            print(f"{Fore.RED}Model page not available{Style.RESET_ALL}")
            continue
        trivia = souped_model.find(
            'div', class_='Intro__text__2JBv1kY9')
        if trivia is None:
            trivia = souped_model.find(
                'div', class_='Editorial__desc__20EN5mi7').get_text()
        else:
            trivia = trivia.get_text()
        if trivia is None:
            trivia = ""
        model_speclist = souped_model.find(
            'div', class_='TechSpecs__list__1_NWtTPS')
        if stop == condition and not allowAll:
            exit()
        else:
            row["trivia"] = trivia
            for speclist_property in model_speclist:
                if "note" in speclist_property:
                    continue
                souped_spec = BeautifulSoup(
                    str(speclist_property), 'html.parser')
                sectionName = souped_spec.find(
                    'div', class_='Accordion__title--body-alt__3AKQP6Lg').get_text()
                specs = [spec.get_text()
                         for spec in souped_spec.findAll('strong')]
                specs_values = [spec_val.get_text(" ") for spec_val in souped_spec.findAll(
                    'span', class_="TechSpecs__value__1wW_OIzf")]
                spec_list = zip(specs, specs_values)
                for spec, value in spec_list:
                    spec = spec.replace(" km/h", "").replace(" m", "")
                    while(spec.find("  ") != -1):
                        spec = spec.replace(
                            "***", " ").replace("**", " ").replace("*", " ").replace("  ", " ")
                    spec = spec.lstrip().rstrip()
                    if spec.lower()[0:4] == "note":
                        continue
                    row[spec.lower()] = value.strip()
        addToData(row)
        stop += 1

convertToCsv(data)
pp.pprint(data)
debug(data, False)
debug(data.keys(), False)
driver.quit()
