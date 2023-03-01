from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup

chrome_driver_path = "C:\Development\chromedriver.exe"
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service)

URL = 'https://www.imdb.com/?ref_=nv_home'

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

df = pd.read_csv('50 best films of 2022.csv')
titles = df['movie_title'].values.tolist()

movies_info = []

driver.get(URL)
driver.maximize_window()
time.sleep(1)
for title in titles[::-1]:
    IMDb_search = driver.find_element(By.NAME, 'q')
    IMDb_search.send_keys(title)
    button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'suggestion-search-button')))
    button.click()
    time.sleep(1)

    # Wait until the container is loaded
    # container = driver.find_element(By.CLASS_NAME, 'ipc-page-section')
    container = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'ipc-page-section')))
    first_result = container.find_element(By.XPATH, '//*[@id="__next"]/main/div[2]/div[3]/section/div/div[1]/section[2]/div[2]/ul/li[1]/div[2]/div/a')
    driver.execute_script("arguments[0].click();", first_result)
    time.sleep(1)

    # Wait until the page is loaded
    driver.switch_to.window(driver.window_handles[0])
    current_url = driver.current_url
    time.sleep(1)

    # Wait until the page content is loaded
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, 'h1')))

    response = requests.get(current_url, headers=HEADERS)
    imdb_page = response.content
    soup = BeautifulSoup(imdb_page, 'html.parser')

    # Find Movie Title
    movie_title = soup.find('h1').text.strip()

    # Find Year
    # general_info = soup.find('div', {'class': 'sc-eda143c4-0'})
    # general_container = general_info.find_next('ul')
    # general_tags = general_container.find_all('a')
    # year_rate = [g.text.strip() for g in general_tags]

    #  Find Genres
    genres_container = soup.find('div', {'class': 'ipc-chip-list__scroller'})
    genres = [genre.text.strip() for genre in genres_container.findAll('span', {'class': 'ipc-chip__text'})]

    # Find Director
    director_tag = soup.find('div', class_='ipc-metadata-list-item__content-container')
    director_link = director_tag.find('a')['href']
    director_name = director_tag.find('a').text.strip()

    # Find the Writers
    try:
        writers_tag = soup.find('a', text='Writers')
        writers_container = writers_tag.find_next('ul')
        writers = writers_container.find_all('a')
        writers_names = [w.text.strip() for w in writers]
    except:
        writers_tag = soup.find('button', text=['Writer', 'Writers'])
        if writers_tag:
            writers_container = writers_tag.find_next('ul')
            writers = writers_container.find_all('a')
            writers_names = [w.text.strip() for w in writers]
        else:
            writers_names = ''

    # Find the Stars
    try:
        stars_tag = soup.find('a', text='Stars')
        stars_container = stars_tag.find_next('ul')
        stars = stars_container.find_all('a')
        stars_names = [s.text.strip() for s in stars]
    except:
        stars_names = ''

    # Find the metascore
    metascore = soup.find('span', {'class': 'score-meta'}).text.strip()

    # Find the imdb rating
    imdb_rating = soup.find('span', {'class': 'sc-e457ee34-1'}).text.strip()

    # Go to director's page
    driver.get(f"https://www.imdb.com{director_link}")
    time.sleep(1)

    # Scrape Director's Info
    director_page = driver.page_source
    director_soup = BeautifulSoup(director_page, 'html.parser')

    # Get Image_URL
    try:
        director_image_element = director_soup.find('img', {'class': 'ipc-image'})
        director_image_url = director_image_element['src']
    except:
        director_image_url = 'NaN'

    # Get Birthday and Country
    try:
        born_element = director_soup.find('li', {'data-testid': 'nm_pd_bl'})
        birthdate = born_element.find_all('a')[0].text.strip()
        birthyear = born_element.find_all('a')[1].text.strip()
        birthplace = born_element.find_all('a')[2].text.strip()

    except:
        born_element = director_soup.find('li', {'data-testid': 'nm_pd_bl'})
        birthdate = 'NaN'
        birthyear = 'NaN'
        birthplace = 'NaN'

        if born_element:
            born_links = born_element.find_all('a')
            if len(born_links) >= 1:
                birthyear = born_links[0].text.strip()
            if len(born_links) >= 2:
                birthplace = born_links[1].text.strip()
            if len(born_links) >= 3:
                birthdate = born_links[2].text.strip()

    movie_dict = {
        'movie_title': movie_title,
        # 'year': year_rate[0] if len(year_rate) > 0 else 'NaN',
        # 'rate': year_rate[1] if len(year_rate) > 1 else 'NaN',
        'genres': genres,
        'director_name': director_name,
        'director_birthdate': birthdate,
        'director_birthyear': birthyear,
        'director_birthplace': birthplace,
        'director_img_url': director_image_url,
        'writers': writers_names,
        'stars': stars_names,
        'metascore': metascore,
        'imdb_rating': imdb_rating
    }

    # append the dictionary to the list of movies
    movies_info.append(movie_dict)
    print(movie_dict)

# print(movies_info)

df1 = pd.DataFrame(movies_info)
df1.to_csv('new_imdb_info.csv')
print(df1)