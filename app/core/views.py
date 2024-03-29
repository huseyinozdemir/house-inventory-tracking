import requests

from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.template import loader

API_HOST = 'http://app:8000/api/'
API_TOKEN_URL = 'user/token/'
API_BUILDING_URL = 'building/buildings/'
API_FLAT_URL = 'building/flats/'
API_ROOM_URL = 'building/rooms/'
API_FIXTURE_URL = 'building/fixtures/'

HEADER_NO_AUTH = {
    'Allow': "Content-Type",
    'Content-Type': "application/json",
    'Vary': "Accept"
}

def __delete(token, url, method="DELETE"):
    headers = {
        'Authorization': 'Token ' + token,
    }

    response = requests.request(
        method, url=url, headers=headers
    )

    if not response:
        return 'logout'

    res = 'Success'

    return res


def __save(token, url, val=None, method="POST"):
    headers = {
        'Authorization': 'Token ' + token,
    }

    response = requests.request(
        method, url=url, data=val, headers=headers
    )

    if not response:
        return 'logout'

    res = 'Success'

    return res

def __source(token, url):
    headers = {
        'Authorization': 'Token ' + token,
    }
    response = requests.request(
        "GET", url=url, headers=headers
    )

    if not response:
        return redirect(logout)

    res = response.json()

    return res

def __total(token, modul='building'):
    res = {}
    if modul == 'flat':
        obj = __source(token, API_HOST+API_FLAT_URL)
    elif modul == 'room':
        obj = __source(token, API_HOST+API_ROOM_URL)
    elif modul == 'fixture':
        obj = __source(token, API_HOST+API_FIXTURE_URL)
    else:
        obj = __source(token, API_HOST+API_BUILDING_URL)
    total = len(obj)
    sum_price = 0
    for item in obj:
        if 'total_price' in item.keys():
            if type(item['total_price']) != type(1):
                if item['total_price']['total'] is not None:
                    sum_price += float(item['total_price']['total'])

    res['total'] =  total
    res['sum_price'] = str(sum_price)
    return res

@csrf_protect
def index(request):
    token = request.session['token'] if 'token' in request.session.keys() else ''
    if token != '': return redirect(dashboard)
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    if (username.strip() != '') and (password.strip() != ''):
        params = {
            'email': username,
            'password': password,
        }
        response = requests.request(
            "POST", url=API_HOST+API_TOKEN_URL, data=params
        )
        if response:
            res = response.json()
            if res['token'] is not None:
                token = res['token']
                request.session['token'] = token
                return redirect(dashboard)
    context = {}
    return render(request, 'login.html', context)

def dashboard(request):
    token = request.session['token'] if 'token' in request.session.keys() else ''
    if token == '': return redirect(index)

    total_building = __total(token, 'building')
    total_flat = __total(token, 'flat')
    total_room = __total(token, 'room')
    total_fixture = __total(token, 'fixture')

    context = {
        'building_total' : total_building['total'],
        'building_sum' : total_building['sum_price'],
        'flat_total' : total_flat['total'],
        'room_total' : total_room['total'],
        'fixture_total' : total_fixture['total'],
    }
    return render(request, 'dashboard.html', context)

def buildings(request):
    token = request.session['token'] if 'token' in request.session.keys() else ''
    if token == '': return redirect(index)

    obj = __source(token, API_HOST+API_BUILDING_URL)

    context = {
        'title' : 'Buildings',
        'edit_action' : '/building',
        'rows' : obj,
    }
    return render(request, 'lists.html', context)

def flats(request):
    token = request.session['token'] if 'token' in request.session.keys() else ''
    if token == '': return redirect(index)

    obj = __source(token, API_HOST+API_FLAT_URL)

    context = {
        'title' : 'Flats',
        'edit_action' : '/flat',
        'rows' : obj,
    }
    return render(request, 'lists.html', context)

def rooms(request):
    token = request.session['token'] if 'token' in request.session.keys() else ''
    if token == '': return redirect(index)

    url = API_HOST+API_ROOM_URL
    url_building = API_HOST+API_BUILDING_URL
    url_flat = API_HOST+API_FLAT_URL

    obj = __source(token, url)

    buildings = __source(token, url_building)
    flats = __source(token, url_flat)

    for itm in obj:
        for flat in flats:
            if itm['flat_id'] == flat['id']:
                itm['building_id'] = flat['building_id']

    for itm in obj:
        for building in buildings:
            if itm['building_id'] == building['id']:
                itm['building_name'] = building['name']

    context = {
        'title' : 'Rooms',
        'edit_action' : '/room',
        'rows' : obj,
        #'rows' : flats,
    }
    return render(request, 'lists.html', context)

def fixtures(request):
    token = request.session['token'] if 'token' in request.session.keys() else ''
    if token == '': return redirect(index)

    url = API_HOST+API_FIXTURE_URL
    url_building = API_HOST+API_BUILDING_URL
    url_flat = API_HOST+API_FLAT_URL
    url_room = API_HOST+API_ROOM_URL

    obj = __source(token, url)
    buildings = __source(token, url_building)
    flats = __source(token, url_flat)
    rooms = __source(token, url_room)

    for itm in obj:
        for room in rooms:
            if itm['room_id'] == room['id']:
                itm['flat_id'] = room['flat_id']

    for itm in obj:
        for flat in flats:
            if itm['flat_id'] == flat['id']:
                itm['building_id'] = flat['building_id']
                itm['flat_name'] = flat['name']

    for itm in obj:
        for building in buildings:
            if itm['building_id'] == building['id']:
                itm['building_name'] = building['name']


    context = {
        'title' : 'Fixtures',
        'edit_action' : '/fixture',
        'rows' : obj,
    }
    return render(request, 'lists.html', context)


def __buildingId(request, Tag):
    token = request.session['token'] if 'token' in request.session.keys() else ''
    if token == '': return redirect(index)

    url = API_HOST+API_BUILDING_URL+str(Tag)+'/'

    info = ''
    if request.POST:
        val = {
            'name' : request.POST.get('name', ''),
        }
        res = __save(token, url, val, "PUT")
        if res == 'logout':
            return redirect(logout)
        info = res

    row = __source(token, url)
    context = {
        'title': 'Item',
        'row': row,
        'info': info,
    }
    return render(request, 'item_building.html', context)


def __buildingNew(request, Tag):
    token = request.session['token'] if 'token' in request.session.keys() else ''
    if token == '': return redirect(index)
    url = API_HOST+API_BUILDING_URL

    info = ''
    if request.POST:
        val = {
            'name' : request.POST.get('name', ''),
        }
        res = __save(token, url, val, "POST")
        if res == 'logout':
            return redirect(logout)
        return redirect(buildings)

    context = {
        'title': 'Item',
        'info': '',
    }
    return render(request, 'item_building.html', context)

@csrf_protect
def building(request, Tag):
    if Tag == 'new':
        return __buildingNew(request, Tag)

    return __buildingId(request, Tag)

def buildingDel(request, Tag):
    token = request.session['token'] if 'token' in request.session.keys() else ''
    if token == '': return redirect(index)
    url = API_HOST+API_BUILDING_URL+Tag

    info = ''
    if request.GET:
        res = __delete(token, url, "DELETE")
        if res == 'logout':
            return redirect(logout)
    return redirect(buildings)

def __flatId(request, Tag):
    token = request.session['token'] if 'token' in request.session.keys() else ''
    if token == '': return redirect(index)

    url = API_HOST+API_FLAT_URL+str(Tag)+'/'
    url_building = API_HOST+API_BUILDING_URL

    info = ''
    if request.POST:
        val = {
            'name' : request.POST.get('name', ''),
            'building_id' : request.POST.get('building_id', ''),
        }
        res = __save(token, url, val, "PUT")
        if res == 'logout':
            return redirect(logout)
        info = res

    row = __source(token, url)
    buildings = __source(token, url_building)
    context = {
        'title': 'Item',
        'row': row,
        'buildings': buildings,
        'info': info,
    }
    return render(request, 'item_flat.html', context)


def __flatNew(request, Tag):
    token = request.session['token'] if 'token' in request.session.keys() else ''
    if token == '': return redirect(index)
    url = API_HOST+API_FLAT_URL
    url_building = API_HOST+API_BUILDING_URL

    info = ''
    if request.POST:
        val = {
            'name' : request.POST.get('name', ''),
            'building_id' : request.POST.get('building_id', ''),
        }
        res = __save(token, url, val, "POST")
        if res == 'logout':
            return redirect(logout)
        return redirect(flats)


    buildings = __source(token, url_building)
    context = {
        'title': 'Item',
        'info': '',
        'buildings': buildings,
    }
    return render(request, 'item_flat.html', context)


@csrf_protect
def flat(request, Tag):
    if Tag == 'new':
        return __flatNew(request, Tag)

    return __flatId(request, Tag)

def flatDel(request, Tag):
    token = request.session['token'] if 'token' in request.session.keys() else ''
    if token == '': return redirect(index)
    url = API_HOST+API_FLAT_URL+Tag

    if request.GET:
        res = __delete(token, url, "DELETE")
        if res == 'logout':
            return redirect(logout)
    return redirect(flats)

def __roomId(request, Tag):
    token = request.session['token'] if 'token' in request.session.keys() else ''
    if token == '': return redirect(index)

    url = API_HOST+API_ROOM_URL+str(Tag)+'/'
    url_building = API_HOST+API_BUILDING_URL
    url_flat = API_HOST+API_FLAT_URL

    info = ''
    if request.POST:
        val = {
            'name' : request.POST.get('name', ''),
            'flat_id' : request.POST.get('flat_id', ''),
        }
        res = __save(token, url, val, "PUT")
        if res == 'logout':
            return redirect(logout)
        info = res

    row = __source(token, url)
    buildings = __source(token, url_building)
    flats = __source(token, url_flat)

    for flat in flats:
        flat['name'] = [building['name'] for building in buildings if building['id'] == flat['building_id']][0] + ' -> ' + flat['name']

    context = {
        'title': 'Item',
        'row': row,
        'flats': flats,
        'info': info,
    }
    return render(request, 'item_room.html', context)


def __roomNew(request, Tag):
    token = request.session['token'] if 'token' in request.session.keys() else ''
    if token == '': return redirect(index)
    url = API_HOST+API_ROOM_URL
    url_building = API_HOST+API_BUILDING_URL
    url_flat = API_HOST+API_FLAT_URL

    info = ''
    if request.POST:
        val = {
            'name' : request.POST.get('name', ''),
            'flat_id' : request.POST.get('flat_id', ''),
        }
        res = __save(token, url, val, "POST")
        if res == 'logout':
            return redirect(logout)
        return redirect(rooms)


    buildings = __source(token, url_building)
    flats = __source(token, url_flat)

    for flat in flats:
        flat['name'] = [building['name'] for building in buildings if building['id'] == flat['building_id']][0] + ' -> ' + flat['name']

    context = {
        'title': 'Item',
        'info': '',
        'flats': flats,
    }
    return render(request, 'item_room.html', context)


@csrf_protect
def room(request, Tag):
    if Tag == 'new':
        return __roomNew(request, Tag)

    return __roomId(request, Tag)

def roomDel(request, Tag):
    token = request.session['token'] if 'token' in request.session.keys() else ''
    if token == '': return redirect(index)
    url = API_HOST+API_ROOM_URL+Tag

    if request.GET:
        res = __delete(token, url, "DELETE")
        if res == 'logout':
            return redirect(logout)
    return redirect(rooms)

def __fixtureId(request, Tag):
    token = request.session['token'] if 'token' in request.session.keys() else ''
    if token == '': return redirect(index)

    url = API_HOST+API_FIXTURE_URL+str(Tag)+'/'
    url_building = API_HOST+API_BUILDING_URL
    url_flat = API_HOST+API_FLAT_URL
    url_room = API_HOST+API_ROOM_URL

    info = ''
    if request.POST:
        val = {
            'name' : request.POST.get('name', ''),
            'room_id' : request.POST.get('room_id', ''),
            'price_value' : request.POST.get('price_value', ''),
        }
        res = __save(token, url, val, "PUT")
        if res == 'logout':
            return redirect(logout)
        info = res

    row = __source(token, url)
    buildings = __source(token, url_building)
    flats = __source(token, url_flat)
    rooms = __source(token, url_room)

    for room in rooms:
        for flat in flats:
            if flat['id'] == room['flat_id']:
                room['name'] = flat['name'] + ' -> ' + room['name']
                room['building_id'] = flat['building_id']

    for room in rooms:
        for building in buildings:
            if building['id'] == room['building_id']:
                room['name'] = building['name'] + ' -> ' + room['name']

    context = {
        'title': 'Item',
        'row': row,
        'rooms': rooms,
        'info': info,
    }
    return render(request, 'item_fixture.html', context)


def __fixtureNew(request, Tag):
    token = request.session['token'] if 'token' in request.session.keys() else ''
    if token == '': return redirect(index)

    url = API_HOST+API_FIXTURE_URL
    url_building = API_HOST+API_BUILDING_URL
    url_flat = API_HOST+API_FLAT_URL
    url_room = API_HOST+API_ROOM_URL

    info = ''
    if request.POST:
        val = {
            'name' : request.POST.get('name', ''),
            'room_id' : request.POST.get('room_id', ''),
            'price_value' : request.POST.get('price_value', ''),
        }
        res = __save(token, url, val, "POST")
        if res == 'logout':
            return redirect(logout)
        return redirect(fixtures)


    buildings = __source(token, url_building)
    flats = __source(token, url_flat)
    rooms = __source(token, url_room)

    for room in rooms:
        for flat in flats:
            if flat['id'] == room['flat_id']:
                room['name'] = flat['name'] + ' -> ' + room['name']
                room['building_id'] = flat['building_id']

    for room in rooms:
        for building in buildings:
            if building['id'] == room['building_id']:
                room['name'] = building['name'] + ' -> ' + room['name']


    context = {
        'title': 'Item',
        'info': '',
        'rooms': rooms,
    }
    return render(request, 'item_fixture.html', context)

@csrf_protect
def fixture(request, Tag):
    if Tag == 'new':
        return __fixtureNew(request, Tag)

    return __fixtureId(request, Tag)

def fixtureDel(request, Tag):
    token = request.session['token'] if 'token' in request.session.keys() else ''
    if token == '': return redirect(index)
    url = API_HOST+API_FIXTURE_URL+Tag

    if request.GET:
        res = __delete(token, url, "DELETE")
        if res == 'logout':
            return redirect(logout)
    return redirect(fixtures)

def logout(request):
    request.session['token'] = ''
    return redirect(index)
