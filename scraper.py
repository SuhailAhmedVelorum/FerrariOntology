from bs4 import BeautifulSoup
import requests
import os
import time
from colorama import Fore, Style
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# [DEBUG SELECTOR]
WRITE = False
# WRITE = True


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
condition = 1

for year in historySections:
    souped_year = BeautifulSoup(str(year), 'html.parser')
    yearOf = souped_year.find(
        'h2', class_='PastModels__sectionYear__33cNPh9I').get_text()
    modelsByYear = souped_year.find_all('a')
    for model in modelsByYear:
        model_url = model.get('href')
        name_plate = BeautifulSoup(str(model), 'html.parser')
        name_parts = name_plate.find(
            'span', class_="PastModels__text__2qL1mq9T")
        name_parts = BeautifulSoup(str(name_parts), 'html.parser')
        name_parts = name_parts.findAll('span')
        model_name = name_parts[1].text
        model_type = name_parts[2].text
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
            debug('\n\t<!-- Ferrari ' + model_name +
                  ' -->\n\n', clearOnNew=False)
            debug('** Model Section starts **\n', clearOnNew=False)
            debug('model:Ferrari ' + model_name + '\n', clearOnNew=False)
            sectionCount = 0
            debug('\t<owl:NamedIndividual rdf:about="http://www.semanticweb.org/nope/ontologies/2021/11/history-of-ferraris#Ferrari_' +
                  model_name.replace(" ", "_").lstrip().rstrip()+'">\n', clearOnNew=False)
            debug('\t\t<rdfs:label xml:lang="en">' + 'Ferrari '+model_name +
                  '</rdfs:label>\n\t\t<rdfs:subClassOf rdf:resource="http://www.semanticweb.org/nope/ontologies/2021/11/history-of-ferraris#car"/>\n', clearOnNew=False)
            debug('\t\t<rdf:type rdf:resource="http://www.semanticweb.org/nope/ontologies/2021/11/history-of-ferraris#' +
                  model_type.lower().replace(" ", "_")+'"/>\n', clearOnNew=False)
            debug("\t\t<has_trivia>" + trivia +
                  "</has_trivia>\n", clearOnNew=False)

            # [added]
            debug('trivia:' + trivia + "\n", clearOnNew=False)
            # * ENDED

            for speclist_property in model_speclist:
                souped_spec = BeautifulSoup(
                    str(speclist_property), 'html.parser')
                sectionName = souped_spec.find(
                    'div', class_='Accordion__title--body-alt__3AKQP6Lg').get_text()
                if sectionName.lower().replace(" ", "_").lstrip().rstrip() == "notes":
                    continue
                sectionStart = "<has_" + \
                    sectionName.lower().replace(" ", "_").lstrip().rstrip()+">"
                sectionEnd = "</has_" + \
                    sectionName.lower().replace(" ", "_").lstrip().rstrip()+">"
                debug("\t\t"+sectionStart +
                      "\n", clearOnNew=False)
                sectionCount += 1
                specs = [spec.get_text()
                         for spec in souped_spec.findAll('strong')]
                specs_values = [spec_val.get_text(" ") for spec_val in souped_spec.findAll(
                    'span', class_="TechSpecs__value__1wW_OIzf")]
                spec_list = zip(specs, specs_values)
                for spec, value in spec_list:
                    spec = spec.replace(" km/h", "").replace(" m", "")
                    while(spec.find("  ") != -1):
                        spec = spec.replace("  ", " ")
                    spec = spec.lstrip().rstrip()
                    if spec.lower()[0:4] == "note":
                        continue
                    specstart = "\t\t\t<has_" + spec.lower().replace(" ", "_") + ">"
                    specend = "</has_" + spec.lower().replace(" ", "_") + ">"
                    debug(specstart + value.strip() +
                          specend + "\n", clearOnNew=False)
                    # [new]
                    debug(spec.lower() + ":" + value.strip() +
                          "\n", clearOnNew=False)
                    # * ended
                debug("\t\t"+sectionEnd +
                      "\n", clearOnNew=False)
                sectionCount += 1
            debug("\t</owl:NamedIndividual>\n", clearOnNew=False)
        stop += 1

driver.quit()
