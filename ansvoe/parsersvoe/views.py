import array
import sqlite3

import requests
from django.http import HttpResponse
from xml.dom.minidom import parse, parseString


def index(request):
    url = 'https://feed-p.topnlab.ru//export/database/bDFtR0ZyWE9adHBvdUwvSQ,,/feed.xml'
    download_xml(url)
    return HttpResponse('<h2>Парсинг</h2>')


def download_xml(url):
    fileName = 'svoe-xml.xml'
    r = requests.get(url, allow_redirects=True)
    open(fileName, "wb").write(r.content)
    parser_xml(fileName)


def parser_xml(fileName):
    dom = parse(fileName)
    elements = dom.getElementsByTagName("offer")


    for node in elements:
        ids = node.getAttribute("internal-id")
        for child in node.childNodes:
            if child.tagName == 'rooms':
                rooms = child.firstChild.data
        insert_db(ids, rooms)


def insert_db(ids, rooms):
    try:
        sqlite_connection = sqlite3.connect('db.sqlite3')
        cursor = sqlite_connection.cursor()
        print("Подключен к SQLite")

        sqlite_insert_query = """INSERT INTO parsersvoe_apartments(id_crm, rooms) VALUES (?,?);"""
        data_tuple = [(ids, rooms)]
        cursor.executemany(sqlite_insert_query, data_tuple)
        sqlite_connection.commit()
        print("Запись успешно вставлена в таблицу parsersvoe_apartments ", cursor.rowcount)
        sqlite_connection.commit()

        cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)

    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")
