import requests
from bs4 import BeautifulSoup
import notify2
import json
import sched, time
from datetime import datetime

QUERY = "osnabrueck/wohnung-wüste"
NUM_PAGES = 3
JSON_FILE_NAME = "known_entries.json"
INTERVAL = 5

try:
    jsonFile = open(JSON_FILE_NAME, "r")
    known_entries = json.load(jsonFile)
    jsonFile.close()
except:
    known_entries = []

notify2.init("ebay listener")


s = sched.scheduler(time.time, time.sleep)
def scrape():
    print(datetime.now().strftime("%H:%M:%S"), "looking for new ads ...")

    new_cnt = 0

    for page in range(NUM_PAGES):
        URL = f"https://www.ebay-kleinanzeigen.de/s-seite:{page + 1}/{QUERY}/k0"
        # print(URL)

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36 Edg/84.0.522.59',}
        response = requests.get(url=URL, headers=headers)

        page = BeautifulSoup(response.content, "html.parser")
        content = page.find("ul", id="srchrslt-adtable")


        ads = content.find_all("li")
        for ad in ads:
            ad_link = ad.find("a", class_="ellipsis")
            if ad_link != None:
                if "https://www.ebay-kleinanzeigen.de" + ad_link["href"] not in known_entries:
                    # filter searches and just show offers
                    search = False
                    for tag in ad.find("span", class_="simpletag"):
                        if tag.get_text() == "Gesuch":
                            search = True
                    if search:
                        continue

                    price = ad.find("p", class_="aditem-main--middle--price")

                    print("------------------------------")
                    print(f"{ad_link.get_text()}:")
                    if price != None:
                        print(price.get_text().replace(" ", ""))
                    print()
                    print("https://www.ebay-kleinanzeigen.de" + ad_link["href"])
                    print("------------------------------")

                    n = notify2.Notification("New Ebay Ad",
                                            f"{ad_link.get_text()}")
                    n.set_urgency(notify2.URGENCY_CRITICAL)
                    n.set_timeout(notify2.EXPIRES_NEVER)
                    n.show()

                    known_entries.append("https://www.ebay-kleinanzeigen.de" + ad_link["href"])
                    new_cnt += 1
        
    jsonFile = open(JSON_FILE_NAME, "w")
    jsonFile.write(json.dumps(known_entries, indent=4))
    jsonFile.close()

    print(f"found {new_cnt} new ads")
    print(f"{len(known_entries)} in total yet")
    print()

    s.enter(60 * INTERVAL, 1, scrape)

s.enter(0, 1, scrape)
s.run()