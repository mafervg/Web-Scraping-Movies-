import numpy as np
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import re

chrome_driver_path = "C:\Development\chromedriver.exe"
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service)

URL = 'https://en.wikipedia.org/wiki/'
df = pd.read_csv('50 best films of 2022.csv')
titles = df['movie_title'].values.tolist()
# print(titles)
# titles = ['Jackass_Forever', 'Turning Red', 'Happening']

movies_info_list = []
def urlify(s):

    # Remove all non-word characters (everything except numbers and letters)
    s = re.sub(r"[^\w\s]", '', s)

    # Replace all runs of whitespace with a single dash
    s = re.sub(r"\s+", '_', s)

    return s

driver.get(URL)
time.sleep(1)
for title in titles[::-1]:

    wiki_search = driver.find_element(By.NAME, 'search')
    wiki_search.send_keys(f"{title} film 2022")
    button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="searchform"]/div/button')))
    button.click()
    time.sleep(1)
    try:
        movie_url = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mw-content-text"]/div[3]/div[2]/ul/li[1]/table/tbody/tr/td[2]/div[1]/a'))).click()
    except:
        movie_url = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="mw-content-text"]/div[4]/div[2]/ul/li[1]/table/tbody/tr/td[2]/div[1]/a'))).click()

    driver.switch_to.window(driver.window_handles[0])
    current_url = driver.current_url
    time.sleep(1)

    response = requests.get(current_url)
    wikipedia_page = response.text

    soup = BeautifulSoup(wikipedia_page, 'html.parser')
    table_info = soup.find("table", class_="infobox vevent")
    # print(table_info.prettify())

    all_labels = table_info.findAll("th", class_="infobox-label")
    all_info = table_info.findAll("td", class_="infobox-data")

    label = [urlify(l.text) for l in all_labels]
    info = [i.text.strip().replace("\n", ",").encode('ascii', 'ignore').decode() for i in all_info]
    info_clean = [re.sub(r'\[\d+\]', '', i) for i in info]

    movie_dict = {title: {lab: inf for lab, inf in zip(label, info_clean)}}
    movies_info_list.append(movie_dict)
    print(movie_dict)


dataframe_list = []
for dic in movies_info_list:
    df = pd.DataFrame.from_dict(dic, orient='index')
    dataframe_list.append(df)

df1 = pd.concat(dataframe_list)
df1.to_csv('movies_info.csv')
print(df1)



driver.quit()