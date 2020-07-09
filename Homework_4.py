# 1)Написать приложение, которое собирает основные новости с сайтов news.mail.ru, lenta.ru, yandex.news
# Для парсинга использовать xpath. Структура данных должна содержать:
# название источника,
# наименование новости,
# ссылку на новость,
# дата публикации


from pprint import pprint
from lxml import html
import requests
from pymongo import MongoClient
from datetime import datetime
import re

today = datetime.today()
header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36',
          'Accept':'*/*'}

def remove_extra_char(text):
    text = re.sub(r'[\xa0]', " ", text)
    return  text

def request_to_mail_ru():
    response = requests.get('https://news.mail.ru/society/', headers=header)
    dom = html.fromstring(response.text)
    news = []

    news_block = dom.xpath("//div[@class='newsitem newsitem_height_fixed js-ago-wrapper js-pgng_item']")

    for item in news_block:
        new_info = {}

        name = item.xpath(".//span[@class='newsitem__title-inner']/text()")[0]
        new_info['name'] = remove_extra_char(name)
        link = item.xpath(".//a[@class='newsitem__title link-holder']/@href")[0]
        new_info['link'] = link
        date = dom.xpath("//span[@class='newsitem__param js-ago']/@datetime")
        if len(date) == 0:
            new_info['date'] = str(today.date())
        else:
            new_info['date'] = str(datetime.fromisoformat(date[0]).date())
        #new_info['date'] = str(datetime.fromisoformat(date).date())

        response = requests.get(link, headers=header)
        dom = html.fromstring(response.text)

        new_info['source_name'] = dom.xpath("//span[@class='note']/*/span[@class='link__text']/text()")[0]


        news.append(new_info)
    return news


def request_to_lenta_ru():
    response = requests.get('https://lenta.ru/', headers=header)
    dom = html.fromstring(response.text)
    news = []

    news_block = dom.xpath("//div[@class='b-yellow-box__wrap']/div[@class='item']")

    for item in news_block:
        new_info = {}

        new_info['source_name'] = 'lenta.ru'
        name = item.xpath(".//a/text()")[0]
        new_info['name'] = remove_extra_char(name)
        link = 'https://lenta.ru/' + item.xpath(".//a/@href")[0]
        new_info['link'] = link

        response = requests.get(link, headers=header)
        dom = html.fromstring(response.text)

        date = dom.xpath("//div[@class='b-topic__info']/time[@class='g-date']/@datetime")
        if len(date) == 0:
            new_info['date'] = str(today.date())
        else:
            new_info['date'] = str(datetime.fromisoformat(date[0]).date())

        news.append(new_info)
    return news


def request_to_yandex_news():
    response = requests.get('https://yandex.ru/news/rubric/society', headers=header)
    dom = html.fromstring(response.text)
    news = []

    name = dom.xpath("//a[@class='link link_theme_black i-bem']/text()")
    link = dom.xpath("//a[@class='link link_theme_black i-bem']/@href")
    sourse_date = dom.xpath("//div[@class='story__date']/text()")
    sourse = []
    dates = []
    for i in range(len(sourse_date)):
        sourse.append(' '.join(re.findall('[a-zA-ZА-Яа-я]+', sourse_date[i])))
        date = remove_extra_char(sourse_date[i])
        #time = re.findall(r'\S+$', text)

        if 'вчера' in date:
            date = today.replace(day=today.day - 1).date()
        else:
            date = str(today.date())

        dates.append(date)

    data = zip(name, link, sourse, dates)

    for item in list(data):
        new_info = {}

        new_info['name'] = item[0]
        new_info['link'] = 'https://yandex.ru' + item[1]
        new_info['source_name'] = item[2]
        new_info['date'] = item[3]

        news.append(new_info)

    return news

# 2)Сложить все новости в БД

def insert_data(data):
    news_db.news.insert_many(data)

client = MongoClient('localhost',27017)
news_db = client['news_db']

data = request_to_mail_ru() + request_to_lenta_ru() + request_to_yandex_news()

pprint(data)

insert_data(data)
print(news_db.news.count_documents({}))
