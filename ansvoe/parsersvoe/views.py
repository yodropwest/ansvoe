import sqlite3
import requests
from django.http import HttpResponse
from xml.dom.minidom import parse


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
            if child.nodeType == 1:

                if child.tagName == 'area':
                    for area in child.childNodes:
                        if area.tagName == 'value':
                            area_total = area.firstChild.data

                if child.tagName == 'price':
                    for price in child.childNodes:
                        if price.tagName == 'value':
                            price_apart = price.firstChild.data

                if child.tagName == 'living-space':
                    for area in child.childNodes:
                        if area.tagName == 'value':
                            area_living = area.firstChild.data

                if child.tagName == 'kitchen-space':
                    for area in child.childNodes:
                        if area.tagName == 'value':
                            area_kitchen = area.firstChild.data

                if child.tagName == 'floor':
                    floor = child.firstChild.data

                if child.tagName == 'floors-total':
                    floor_total = child.firstChild.data

                if child.tagName == 'building-type':
                    building = child.firstChild.data

                if child.tagName == 'bathroom-unit':
                    bathroom = child.firstChild.data

                if child.tagName == 'balcony':
                    balcony = child.firstChild.data

                if child.tagName == 'built-year':
                    build_year = child.firstChild.data
                else:
                    build_year = 'null'

                if child.tagName == 'description':
                    description = child.firstChild.data

                if child.tagName == 'property-type':
                    property_type = child.firstChild.data

                if child.tagName == 'rooms':
                    rooms = child.firstChild.data

                if child.tagName == 'location':
                    for location in child.childNodes:
                        if location.tagName == 'house':
                            if location.firstChild.nodeType == 3:
                                house = location.firstChild.data
                        if location.tagName == 'street':
                            if location.firstChild.nodeType == 3:
                                street = location.firstChild.data


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
