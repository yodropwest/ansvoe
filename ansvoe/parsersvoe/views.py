import os
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
    ids_array = []

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
                if child.tagName == 'main-image':
                    imageMain = child.firstChild.data
                if child.tagName == 'image':
                    image = child.firstChild.data
                    download_images(ids, image)

        ids_array.append(ids)
        data_tuple = [(ids, price_apart, area_total, area_living, area_kitchen, floor, floor_total, building, bathroom,
                       balcony, build_year, description, property_type, rooms, house, street)]
        query_execution(data_tuple, ids, price_apart, area_total, area_living, area_kitchen, floor, floor_total,
                        building, bathroom,
                        balcony, build_year, description, property_type, rooms, house, street)
    remove_sqlite_offers(ids_array)


def download_images(ids, images):
    url = images
    response = requests.get(url)
    if response.status_code == 200:
        file_name = url[url.rfind('/') + 1:]
        if os.path.exists("uploads/" + file_name + '.jpg'):
            print('Существует')
        else:
            with open("uploads/" + file_name + '.jpg', "wb") as file:
                file.write(response.content)
                print('Картинка успешно скачена')
                image_url = "uploads/" + file_name + '.jpg'
                data_tuple_image = [(ids, "uploads/" + file_name + '.jpg')]
                insert_images(data_tuple_image, ids, image_url)
    else:
        print('Ошибка: картинка не скачалась')


def insert_images(data_tuple_image, ids, image_url):
    try:
        sqlite_connection = sqlite3.connect('db.sqlite3')
        cursor = sqlite_connection.cursor()
        print("Подключен к SQLite image")

        sqlite_insert_query = """INSERT INTO
                       parsersvoe_apartmentsimage(id_crm_id, image)
                       VALUES (?,?)"""
        cursor.executemany(sqlite_insert_query, data_tuple_image)
        print('Успешно добавили картинку')
        sqlite_connection.commit()
        cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)

    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")


def query_execution(data_tuple, ids, price_apart, area_total, area_living, area_kitchen, floor, floor_total, building,
                    bathroom,
                    balcony, build_year, description, property_type, rooms, house, street):
    try:
        sqlite_connection = sqlite3.connect('db.sqlite3')
        cursor = sqlite_connection.cursor()
        print("Подключен к SQLite")

        sqlite_select_query = """select * from parsersvoe_apartments WHERE id_crm = ? """
        cursor.execute(sqlite_select_query, (ids,))
        records = cursor.fetchone()
        if records is None:
            sqlite_insert_query = """INSERT INTO
               parsersvoe_apartments(id_crm, price, area, area_living, area_kitchen, floor, floor_total, building, bathroom, balcony, build_year, description, property_type, rooms, house, street)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
            cursor.executemany(sqlite_insert_query, data_tuple)
        else:
            sqlite_update_query = """Update parsersvoe_apartments set price = ?, area = ?, area_living = ?, area_kitchen = ?, floor = ?, floor_total = ?, building = ?, bathroom = ?, balcony = ?, build_year = ?, description = ?, property_type = ?, rooms = ?, house = ?, street = ? where id_crm = ?"""
            data = [(price_apart, area_total, area_living, area_kitchen, floor, floor_total, building, bathroom,
                     balcony, build_year, description, property_type, rooms, house, street, ids)]
            cursor.executemany(sqlite_update_query, data)

        sqlite_connection.commit()
        cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)

    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")


def remove_sqlite_offers(ids_array):
    try:
        sqlite_connection = sqlite3.connect('db.sqlite3')
        cursor = sqlite_connection.cursor()
        print("Подключен к SQLite удаление")

        sqlite_select_ids = """select id_crm from parsersvoe_apartments"""
        cursor.execute(sqlite_select_ids)
        record = cursor.fetchall()
        new_list = []
        for item in record:
            new_list.append(''.join(list(item)))
        remove_offer = list(set(new_list) ^ set(ids_array))
        if remove_offer:
            for item_id in remove_offer:
                sqlite_update_query = """DELETE from parsersvoe_apartments where id_crm = ?"""
                cursor.execute(sqlite_update_query, (item_id,))
                print('Удаление успешно')
        else:
            print('Нет лишнего')

        sqlite_connection.commit()
        cursor.close()
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)

    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")
