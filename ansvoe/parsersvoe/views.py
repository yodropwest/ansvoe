import urllib
import xml.etree.ElementTree as ET
import urllib.request

from django.http import HttpResponse


def index(request):
    url = 'https://feed-p.topnlab.ru//export/database/bDFtR0ZyWE9adHBvdUwvSQ,,/feed.xml'
    response = urllib.request.urlopen(url).read()
    tree = ET.fromstring(response)

    for child in tree:
        print(child.attrib)

    return HttpResponse('<h2>Парсинг</h2>')
