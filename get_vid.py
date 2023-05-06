# Selenium tools to scrape BaseballSavant
from selenium import webdriver
from bs4 import BeautifulSoup
import time, os
import requests

# Multi-result searches concatenated by '%7C'
result_dict = {'called_strike': 'called%5C.%5C.strike',
               'ball': 'ball',
               'blocked_ball': 'blocked%5C.%5C.ball',
               'foul': 'foul',
               'foul_bunt': 'foul%5C.%5C.bunt',
               'bunt_foul_tip': 'bunt%5C.%5C.foul%5C.%5C.tip',
               'foul_pitchout': 'foul%5C.%5C.pitchout',
               'pitchout': 'pitchout',
               'hit_by_pitch': 'hit%5C.%5C.by%5C.%5C.pitch',
               'intent_ball': 'intent%5C.%5C.ball',
               'hit_into_play': 'hit%5C.%5C.into%5C.%5C.play',
               'missed_bunt': 'missed%5C.%5C.bunt',
               'foul_tip': 'foul%5C.%5C.tip',
               'swinging_pitchout': 'swinging%5C.%5C.pitchout',
               'swinging_strike': 'swinging%5C.%5C.strike',
               'swinging_strike_blocked': 'swinging%5C.%5C.strike%5C.%5C.blocked'} #Need to investigate other results

def init_driver():
    chromedriver = '/Applications/chromedriver'
    os.environ['webdriver.chrome.driver'] = chromedriver
    driver = webdriver.Chrome(chromedriver)
    return driver

def get_search_url(pitcher = '', batter = '', date = '', inning = '', balls = '', strikes = '', result = ''):
    """Takes statcast search parameters and gives the url for the search results."""
    url = 'https://baseballsavant.mlb.com/statcast_search?'
    url += f'hfPTM=&hfPT=&hfAB=&hfGT=R%7C&hfPR={result_dict[result]}%7C&hfZ=&hfStadium=&hfBBL=&hf'
    url += f'NewZones=&hfPull=&hfC={balls}{strikes}%7C&hfSea=2023%7C&hfSit=&player_type=pitcher&hfOuts=&hfOpponent=&pitcher_throws=&batter_stands=&hfSA=&game_date_gt={date}&game_date_lt={date}&hfMo=&hfTeam=&home_road=&hfRO=&position=&hfInfield=&hfOutfield=&hfInn={inning}%7C&hfBBT=&'
    url += f'batters_lookup%5B%5D={batter}&hfFlag=&pitchers_lookup%5B%5D={pitcher}'
    url += '&metric_1=&group_by=name&min_pitches=0&min_results=0&min_pas=0&sort_col=pitches&player_event_sort=api_p_release_speed&sort_order=desc#results'
    return url

def get_vid_from_url(url: str, driver, filename = 'highlight.mp4'):
    """Takes in a url as a string and uses Selenium to download the video, returning the filename. Retrieves first video in results"""
    pass

    driver.get(url)
    time.sleep(3)
    driver.find_element_by_class_name('player_name').click()
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.get('https://baseballsavant.mlb.com' + soup.find('div', {'id':'search-results'}).find('a')['href'])
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    source_url = soup.find('video', {'id':'sporty'}).find('source')['src']

    r = requests.get(source_url, stream = True)
    if r.ok:
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024 * 8):
                if chunk:
                    f.write(chunk)
                    f.flush()
                    os.fsync(f.fileno())

    return filename

def get_vids_from_urls(urls: list, driver):
    """Takes in multiple urls and uses Selenium to download the videos, returning the list of filenames."""
    output = []
    for i, url in enumerate(urls):
        output.append(get_vid_from_url(url, driver, f'highlight{i}.mp4'))
    return output
