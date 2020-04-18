import cfscrape
import re
from bs4 import BeautifulSoup
import json
import time
import csv
import math
import datetime
from dateutil.parser import parse

def get_rt_json(scraper, page):
    url = "https://www.rottentomatoes.com/api/private/v2.0/browse?minTomato=0&maxTomato=100&services=amazon%3Bhbo_go%3Bitunes%3Bnetflix_iw%3Bvudu%3Bamazon_prime%3Bfandango_now&certified&sortBy=tomato&type=dvd-streaming-all&page=" \
        + str(page)
    return json.loads(scraper.get(url).content)

# Returns a list of all urls from Rotten Tomatoes
def get_urls():
    scraper = cfscrape.create_scraper()
    url = "https://www.rottentomatoes.com/api/private/v2.0/browse?minTomato=0&maxTomato=100&services=amazon%3Bhbo_go%3Bitunes%3Bnetflix_iw%3Bvudu%3Bamazon_prime%3Bfandango_now&certified&sortBy=tomato&type=dvd-streaming-all&page=1"
    rt_json = json.loads(scraper.get(url).content)
    num_pages = math.ceil(rt_json['counts']['total']/rt_json['counts']['count'])
    # num_pages = 3 # Testing
    url_list = []
    lost = 0
    for page in range(2, num_pages):
        print("processing page " + str(page) + "/" + str(num_pages) + " **** " + str(lost) + "/" + str(num_pages) + " lost")
        for movie in rt_json['results']:
            url_list.append(movie['url'])

        # Try twice to get the page, otherwise continue
        try:
            rt_json = get_rt_json(scraper, page)
        except:
            try:
                rt_json = get_rt_json(scraper, page)
            except:
                lost += 1
                continue

    return url_list


# Returns a list of movie info for a specified url, empty list if significant error
# [title, tomatometer, audience score, release date, runtime, rating, genre, cast, studio, director]
# If value not 'available' use math.nan
def get_movie_info(url):
    # Get page
    scraper = cfscrape.create_scraper()
    full_url = "https://www.rottentomatoes.com" + url
    html = scraper.get(full_url).text
    soup = BeautifulSoup(html, 'html.parser')

    # Get title
    title_meta = soup.find("meta",  property="og:title")
    title = title_meta['content']

    # Get Tomato Score and Audience Score
    rating_box = soup.find("section", {"class":"mop-ratings-wrap__row"})
    tomato = rating_box.find("span", {"class" : "mop-ratings-wrap__percentage"}).text.strip()
    audience = rating_box.find("div", {"class" : "mop-ratings-wrap__half audience-score"}).find("span", {"class" : "mop-ratings-wrap__percentage"}).text.strip()
    tomato_score = ''.join([i for i in tomato if i.isdigit()])
    audience_score = ''.join([i for i in audience if i.isdigit()])

    # Get Cast
    cast_area = soup.find("div", {"class":"castSection"})
    names = cast_area.find_all("div",{"class":"media-body"})
    cast_list = [' '.join((name.find("span").text).split()) for name in names]

    # Get Rating, Genre, Director(s), Release Date, Runtime, Studio
    info = soup.find("div",{"class":"media-body"})
    elements = info.find_all("li", {"class":"meta-row clearfix"})
    infodict = {}
    for x in elements:
        for y in x.find_all("div", {"class":"meta-value"}):
            time = y.find("time")
            if time is not None:
                infodict[x.div.text] = time.get("datetime")
            else:
                infodict[x.div.text] = y.text.strip()
    
    # Clean up whitespace in genre, director
    infodict['Genre: '] = ' '.join(infodict['Genre: '].split())
    infodict['Directed By: '] = ' '.join(infodict['Directed By: '].split())

    # Remove unecessary info in rating
    infodict['Rating: '] = re.sub(r'\([^)]*\)', '', infodict['Rating: '])

    # Isolate numbers in runtime
    infodict['Runtime: '] = ''.join([i for i in infodict['Runtime: '] if i.isdigit()])

    # Determine release date
    release_date = math.nan
    if 'In Theaters: ' in infodict:
        release_date = parse(infodict['In Theaters: '])
    elif 'On Disc/Streaming: ' in infodict:
        release_date = parse(infodict['On Disc/Streaming: '])

    # Final list of values
    ret_list = [title,
                tomato_score,
                audience_score,
                release_date,
                infodict['Runtime: '],
                infodict['Rating: '],
                infodict['Genre: '].split(', '),
                cast_list,
                infodict['Studio: '],
                infodict['Directed By: '].split(', ')]
    return ret_list



# MAIN FUNCTION ===============================================================

urls = get_urls()

with open('scores/all_scores.csv','w') as result_file:
    wr = csv.writer(result_file)
    wr.writerow(['title', 'tomato_score', 'audience_score', 'release_date', 'runtime', 'rating', 'genre', 'cast', 'studio', 'director'])
    lost = 0
    total = 0
    for url in urls:
        print("processing ..." + url + " **** lost pages: " + str(lost) + "/" + str(total))
        # Try to get movie info
        try:
            total += 1
            info = get_movie_info(url)
        # If page doesn't load, just skip it
        except:
            lost += 1
            continue    
        wr.writerow(info)