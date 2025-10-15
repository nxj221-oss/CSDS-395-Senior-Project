from bs4 import BeautifulSoup
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time, os


print("hello wsl! try 2")
chromedriver = "/usr/bin/chromedriver"
service = Service(chromedriver)


os.environ["webdriver.chrome.driver"] = chromedriver

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")



def get_csv_bbref(link_list):
    soup_list = []
    for i in link_list:
        driver = webdriver.Chrome(service=Service(chromedriver), options=options)
        driver.get(i)
        time.sleep(10)
        driver.execute_script("window.scrollTo(0, 1500);")
        print("scrolled")

        element = driver.find_element("xpath", '//*[@id="players_standard_batting_sh"]/div[2]/ul/li[1]')
        driver.execute_script("arguments[0].click();", element)
        print("clicked1")

        time.sleep(10)

        element = driver.find_element("xpath", '//*[@id="players_standard_batting_sh"]/div[2]/ul/li[1]/div/ul/li[3]/button')
        driver.execute_script("arguments[0].click();", element)
        print("clicked2")

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        crude = soup.find('pre', id = 'csv_players_standard_batting').text.split("\n")
        soup_list.append(crude)
    driver.quit()
    return soup_list


def clean_crude(csv):
    print("cleaning")
    no_blank = [] 
    for i in csv:
        for j in i:
            if j != '':
                no_blank.append(j)
        new_data_split = []
    for i in no_blank:
        new_line = pd.DataFrame(i.split(','))
        new_data_split.append(new_line)
    season_data = pd.concat(new_data_split, ignore_index = True, axis = 1).T
    header = season_data.iloc[0]
    season_data = season_data[1:]
    season_data.columns = header
    #season_data.drop(columns = ['Rk'], inplace = True)
    return season_data


bbref_list = ['https://www.baseball-reference.com/teams/WSN/2025.shtml']
raw_csv_data_list = get_csv_bbref(bbref_list)
clean_list = clean_crude(raw_csv_data_list)
#print(clean_list.head())