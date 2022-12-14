#!/bin python3.11

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import pyperclip

import sys
import webbrowser
import platform

from functions import messages

def get_link():
    link = pyperclip.paste()
    while 'www.imdb.com/title/' not in link:
        messages.message('error', 1.2, 'error_link')
        input()
        link = pyperclip.paste()
    return link

def web_driver():
    link = get_link()
    if platform.system() == 'Windows':
        service = Service('C:\Program Files (x86)\chromedriver.exe')
        driver = webdriver.Chrome(service=service)
        driver.minimize_window()
        driver.get(link)

    if platform.system() == 'Linux':
        service = Service('/home/zsandark/_DEV/Support/Chrome_driver/chromedriver')
        driver = webdriver.Chrome(service=service)
        driver.minimize_window()
        driver.get(link)

#### DECIDER
    try:
        element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((
                By.CSS_SELECTOR, '.sc-8c396aa2-0 > li:nth-child(1)'))
        )                       
        
        decider_read = driver.find_element(
        By.CSS_SELECTOR, '.sc-8c396aa2-0 > li:nth-child(1)').text      
    except:
            messages.message('error', 2, 'error_decider')
            driver.quit()
            sys.exit()

    decider = None
    if len(decider_read) == 4:        # 1992 - year -> Movie, Short Film
        decider = 'movie'
    if 'Series' in decider_read:      # TV Series, TV Mini Series
        decider = 'series'
    if decider == None:               # TV Movie, TV Special
        decider = 'tv_movie'

### MOVIE TITLE
    try:
            element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                    By.CSS_SELECTOR, '.sc-b73cd867-0'))
            )                       
            
            titleRead = driver.find_element(
            By.CSS_SELECTOR, '.sc-b73cd867-0').text
    except:
            messages.message('error', 2, 'error_movie_title')
            driver.quit()
            sys.exit()

### YEAR OF RELEASE
    if decider == 'movie':
        index = 1
    else:
        index = 2  # series, tv_movie
    try:
        yearRead = driver.find_element(
        By.CSS_SELECTOR, f'.sc-8c396aa2-0 > li:nth-child({index}) > a:nth-child(1)').text
                    
    except:
            messages.message('error', 2, 'error_year')

### DIRECTOR(S)
    directors = []
    if decider in ['movie', 'tv_movie']:    # series do not have directors on the front page
        try:    
                for counter in range(1,4):
                        directors = directors +[driver.find_element(
                        By.CSS_SELECTOR, f'.sc-fa02f843-0 > ul:nth-child(1) > li:nth-child(1) > div:nth-child(2) > ul:nth-child(1) > li:nth-child({counter}) > a:nth-child(1)').text]
        except:
                pass # most of the time the movies have only 1 director -> would trigger an error message / not help to identify, if there is a valid error

### STAR(S)
    stars = []
    if decider in ['movie', 'tv_movie']:
        index_s = 3
    else:
        index_s = 2
    try:    
            for counter in range(1,4):
                    stars = stars + [driver.find_element(
                    By.CSS_SELECTOR, f'.sc-fa02f843-0 > ul:nth-child(1) > li:nth-child({index_s}) > div:nth-child(2) > ul:nth-child(1) > li:nth-child({counter}) > a:nth-child(1)').text]
    except:
            messages.message('error', 2, 'error_stars') # would be triggered if the movie has less than 3 stars (not common)
            

### GENRE(S)
    genres= []
    try:    
            for counter in range(1,4):
                    genres = genres + [driver.find_element(
            By.CSS_SELECTOR, f'a.sc-16ede01-3:nth-child({counter}) > span:nth-child(1)').text]

    except:
            pass # would be triggered if the movie has less than 3 genres

### LENGTH VALUE
    if decider == 'movie':  # format: 1992 15 1h 35m 
        index_l_1 = 2
        index_l_2 = 3
        
    else:                   # format: TV Series 2011???2019 18 57m
        index_l_1 = 3
        index_l_2 = 4
    try:
            # taking the 2nd item(1h 33m) from "2022 1h 33m"
            movieLengthSum = driver.find_element(
            By.CSS_SELECTOR, f'.sc-8c396aa2-0 > li:nth-child({index_l_1}) > a:nth-child(1)').text

            # if the movie has classification(pg-13): "2022 pg-13 1h 33m" taking the 3rd item
            if 'h' not in list(movieLengthSum) or 'm' not in list(movieLengthSum):
                    movieLengthSum = driver.find_element(
                    By.CSS_SELECTOR, f'.sc-8c396aa2-0 > li:nth-child({index_l_2})').text
    except:
            movieLengthSum = None
            messages.message('error', 2, 'error_length')

### VALUATE AND TRANSFORM THE LENGTH VALUE(S)
    lengthHour = None
    lengthMinute = None
    # JUST ONE ITEM LENGTH VALUE, LIKE 45m OR 2h
    if len(str(movieLengthSum).split()) == 1:
            if 'h' in list(str(movieLengthSum)):
                    lengthHour = str(movieLengthSum).strip('hm')    # removing the "h" or "m" values, i know, in this scenario, just 'h' should be fine
            if 'm' in list(str(movieLengthSum)):
                    lengthMinute = str(movieLengthSum).strip('hm')

    # TWO ITEMS LENGTH VALUES, LIKE 2h 32m
    if len(str(movieLengthSum).split()) == 2:
            lengthList = str(movieLengthSum).split()
            lengthHour = lengthList[0].strip('hm')
            lengthMinute = lengthList[1].strip('hm')

### POSTER IMAGE
    try:
            poster = driver.find_element(By.CSS_SELECTOR, '.ipc-media--poster-l > img:nth-child(1)')
            posterLink = poster.get_attribute('srcset')
            posterLink_list = posterLink.split() # making a list devided by the space(link(1st in the list) size, link(3rd) size, link(5th) size)       
            webbrowser.open(posterLink_list[0])     # small
            # webbrowser.open(posterLink_list[2])   # medium
            # webbrowser.open(posterLink_list[4])   # larger

    except:
            messages.message('error', 2, 'error_poster')

    return titleRead, yearRead, directors, stars, genres, lengthHour, lengthMinute