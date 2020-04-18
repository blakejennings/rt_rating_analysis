import requests
from bs4 import BeautifulSoup
import json
import time
from math import ceil

# Gets results for one page, can specify streaming service, page and max score
page = requests.get("https://www.rottentomatoes.com/api/private/v2.0/browse?maxTomato=100&services=netflix_iw&sortBy=release&type=dvd-streaming-all&page=2")
# Loads the json in
rt_json = json.loads(page.content)
for x in rt_json['results']:
	# Gets rating
	print(x['tomatoScore'])

services = ['amazon', 'itunes', 'netflix_iw', 'vudu', 'amazon_prime', 'fandango_now']
for service in services:
	print(service + " RESULTS =======================")
	url = "https://www.rottentomatoes.com/api/private/v2.0/browse?maxTomato=100&services=" \
		+ service + "&sortBy=release&type=dvd-streaming-all&page=1"
	page = requests.get(url)
	# Loads the json in
	rt_json = json.loads(page.content)
	# Get number of pages to process
	print(str(ceil(rt_json['counts']['total']/rt_json['counts']['count'])) + " pages")
	pages = ceil(rt_json['counts']['total']/rt_json['counts']['count'])
	for i in range(1, pages + 1):
		time.sleep(.2)
		url = "https://www.rottentomatoes.com/api/private/v2.0/browse?maxTomato=100&services=" \
		+ service + "&sortBy=release&type=dvd-streaming-all&page=" + str(i)
		page = requests.get(url)
		# Loads the json in
		rt_json = json.loads(page.content)
		for x in rt_json['results']:
			# Gets rating
			for whatever in x:
				try:
					print(x['theaterReleaseDate'])
				except:
					print(x['dvdReleaseDate'])
			#break
		break
	break
			