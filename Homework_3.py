from pymongo import MongoClient
from pymongo import errors
from pprint import pprint
import json

path = '/Users/svetlanaskobeltcyna/PycharmProjects/Data_collection_methods/lesson2/'
with open(path + 'vacancy_data.json') as f:
    data = json.load(f)

#1) Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию,
# записывающую собранные вакансии в созданную БД (без датафрейма)

def insert_data(data):
    for doc in data:
        insert_unique_data(doc)


#2) Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введенной суммы.
# Поиск по двум полям (мин и макс зарплату)

def find_vac_by_amount(amount):
    for vac in hh_vacancy.find({'$or': [{'Min_compensation': {'$gt': amount}}, {'Min_compensation': {'$gt': amount}}]}):
        pprint(vac)


# 3) Написать функцию, которая будет добавлять в вашу базу данных только новые вакансии с сайта

def insert_unique_data(doc):
    try:
        hh_vacancy.insert_one(doc)
    except errors.DuplicateKeyError:
        pass


client = MongoClient('localhost',27017)
db = client['vacancys_db']

hh_vacancy = db.hh

insert_data(data)
find_vac_by_amount(100000)

print(db.hh.count())








