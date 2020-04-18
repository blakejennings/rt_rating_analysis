import requests
import json
import time
import csv
from math import ceil

def get_rt_json(service, page):
    # Sleep for a bit, just in case going too fast means they find out
    # I didn't pay $60,000 for their API
    # time.sleep(5)
    # Build URL from service and page
    url = "https://www.rottentomatoes.com/api/private/v2.0/browse?maxTomato=100&services=" \
        + service + "&sortBy=tomato&type=dvd-streaming-all&page=" + str(page)
    response = requests.get(url)
    # print(response.content)
    # Parse into JSON and return
    return json.loads(response.content)

services = ['amazon', 'itunes', 'netflix_iw', 'vudu', 'amazon_prime']
for service in services:
    # Write results to csv
    with open('scores/' + service + '.csv','w') as result_file:
        wr = csv.writer(result_file)
        print(service + " START")
        lost = 0
        # Get first page JSON
        rt_json = get_rt_json(service, 1)
        # Determine how many pages need to be processed
        num_pages = ceil(rt_json['counts']['total']/rt_json['counts']['count'])
        # Load each page of results
        for i in range(1, num_pages + 1):
            print(str(i) + "/" + str(num_pages) + " " + str(lost) + " lost")

            # Load page JSON
            try:
                rt_json = get_rt_json(service, i)
            # If load fails, just skip it
            except json.decoder.JSONDecodeError:
                lost += 1
                continue

            for x in rt_json['results']:
                # Write rating to csv
                wr.writerow([x['tomatoScore']])