import requests
from bs4 import BeautifulSoup

host = "https://www.blinkist.com"
headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"}
free_daily = requests.get("https://www.blinkist.com/en/nc/daily", headers=headers)
html = BeautifulSoup(free_daily.content, 'html.parser')

headline = html.find("h3", class_="daily-book__headline").get_text()
author = html.find(class_="daily-book__author")

link = html.find("a", class_="cta cta--play daily-book__cta").get('href')
slug = link.split("/")[-1]

article = requests.get(host + link, headers=headers)

soup = BeautifulSoup(article.content, 'html.parser')

chapters = soup.find_all('div', class_='chapter')

with open(slug + ".md", 'a') as f:
    for chapter in chapters:
        heading = chapter.find('h1').get_text()
        f.write('#' + heading + '\n')

        content = chapter.find_all(class_="chapter__content")
        for paragraph in content:
            f.write(paragraph.text + '\n')

        f.write('\n')