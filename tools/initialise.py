import random
import googlemaps
import json
import math
from tools.calculate_distance import calculate_distance
import sys


def show():
    print("INITIALISE")


def radius(firstLat, firstLng, secondLat, secondLng):
    r = math.sqrt((secondLat - firstLat) ** 2 + (secondLng - firstLng) ** 2)
    return r


def findStations(startLat, startLng, endLat, endLng, small_r=1.5):
    with open('tools/stations_coords.json') as f:
        stations = json.load(f)

    big_r = small_r + 0.5

    available_stations = {}
    if endLat >= startLat and endLng >= startLng:
        for item in stations.keys():
            r = radius(startLat, startLng, stations[item]['lat'], stations[item]['lng'])
            if stations[item]['lat'] >= startLat and stations[item]['lng'] >= startLng:
                if r < big_r:
                    available_stations[item] = stations[item]
            else:
                if r < small_r:
                    available_stations[item] = stations[item]
    elif endLat < startLat and endLng > startLng:
        for item in stations.keys():
            r = radius(startLat, startLng, stations[item]['lat'], stations[item]['lng'])
            if stations[item]['lat'] < startLat and stations[item]['lng'] > startLng:
                if r < big_r:
                    available_stations[item] = stations[item]
            else:
                if r < small_r:
                    available_stations[item] = stations[item]
    elif endLat <= startLat and endLng <= startLng:
        for item in stations.keys():
            r = radius(startLat, startLng, stations[item]['lat'], stations[item]['lng'])
            if stations[item]['lat'] <= startLat and stations[item]['lng'] <= startLng:
                if r < big_r:
                    available_stations[item] = stations[item]
            else:
                if r < small_r:
                    available_stations[item] = stations[item]
    elif endLat > startLat and endLng < startLng:
        for item in stations.keys():
            r = radius(startLat, startLng, stations[item]['lat'], stations[item]['lng'])
            if stations[item]['lat'] > startLat and stations[item]['lng'] < startLng:
                if r < big_r:
                    available_stations[item] = stations[item]
            else:
                if r < small_r:
                    available_stations[item] = stations[item]
    return available_stations


def generatePoints(start_coords, end_coords, number_of_stations):
    if number_of_stations != 0:
        segment_lat = (end_coords[0] - start_coords[0]) / number_of_stations
        segment_lng = (end_coords[1] - start_coords[1]) / number_of_stations
    tab = []
    for x in range(0, number_of_stations + 1):
        tab.append([start_coords[0] + segment_lat * x, start_coords[1] + segment_lng * x])
    return tab


def generatePoints2(start_coords, end_coords, number_of_stations, starting_soc):
    path = calculate_distance(start_coords, end_coords, 90)[1]
    if number_of_stations > 0:
        # print('path', len(path))
        # print('il stacji', number_of_stations)
        # print('skok',int((len(path) / (number_of_stations + 1))))
        path = path[0:len(path):int((len(path) / (number_of_stations + 1)))]
    elif number_of_stations == 0:
        path = path[0] + path[len(path) - 1]
    if starting_soc > 70:
        if path[len(path) - 1] == [end_coords[1], end_coords[0]]:
            path = path[1:len(path) - 1]
    else:
        path = path[0:len(path) - 1]


    for p in range(len(path)):
        path[p] = [path[p][1], path[p][0]]
    #
    # print("il stacji", number_of_stations)
    # print('dl path', len(path))
    # path += end_coords

    return path


# def get_initial_parameters():
#     gmaps = googlemaps.Client(key='AIzaSyCdd036WGl2HpBmwhygwqGjn2YgMNSyfC8')
#     print("Enter starting location")
#     start = input()
#     print("Enter destination")
#     end = input()
#     print("Enter starting state of charge")
#     starting_soc = int(input())
#
#     try:
#         start_coords = [gmaps.geocode(start)[0]['geometry']['location']['lat'],
#                         gmaps.geocode(start)[0]['geometry']['location']['lng']]
#     except:
#         print('Wrong entry point')
#
#     try:
#         end_coords = [gmaps.geocode(end)[0]['geometry']['location']['lat'],
#                       gmaps.geocode(end)[0]['geometry']['location']['lng']]
#         print(end_coords)
#     except:
#         print('Wrong destination')
#
#     return [start_coords, end_coords, starting_soc]


def get_initial_parameters1(start, end, starting_soc):
    gmaps = googlemaps.Client(key='AIzaSyAJw4KZ8df094Qsqk3YS2kUIpNWjLLb5MI')
    start_coords = []
    end_coords = []
    try:
        start_coords = [gmaps.geocode(start)[0]['geometry']['location']['lat'],
                        gmaps.geocode(start)[0]['geometry']['location']['lng']]
    except TimeoutError or TypeError:
        print('Wrong entry point')

    try:
        end_coords = [gmaps.geocode(end)[0]['geometry']['location']['lat'],
                      gmaps.geocode(end)[0]['geometry']['location']['lng']]
        print(end_coords)
    except TimeoutError or TypeError:
        print('Wrong destination')
    print(start_coords, end_coords)
    if start_coords == [] or end_coords == []:
        sys.exit('Wrong points')
    return [start_coords, end_coords, starting_soc]



def initialise(coords):
    with open("tools/parameters.json") as f:
        parameters = json.load(f)

    if 'generation_size' in parameters['config1'].keys():
        generation_size = parameters['config1']['generation_size']
    else:
        generation_size = parameters['default']['generation_size']

    start_coords = coords[0]
    end_coords = coords[1]
    solution = []
    solutions = []
    max_range = 350  # range in km
    # TODO
    # ogarnac przlicznik minut katawych (wspolrzedne) na km
    min_speed = 60
    max_speed = 100
    average_speed = 70
    max_charging_time = 50
    # number_of_stations = math.ceil(radius(start_coords[0], start_coords[1], end_coords[0], end_coords[1]) / max_range)
    number_of_stations = math.ceil((calculate_distance(start_coords, end_coords)[0]) / 1000 / max_range)
    print('DISTANCE = ', calculate_distance(start_coords, end_coords)[0] / 1000)

    # zmienic zeby nie losowalo tych samych ladowarek, np lista uzytych ladowek ktore beda usuwane z available_stations
    # Glowna petla
    for j in range(generation_size):
        solution = []
        # tworzymy np. 50 rozw z czego jaksa ilosc jest tworzona dla n ladowarek
        number_of_stations_temp = 0
        number_of_stations_temp = number_of_stations + random.randint(0, math.ceil(number_of_stations / 5))
        center_points = generatePoints2(start_coords, end_coords, number_of_stations_temp, coords[2])
        used_stations = []
        if number_of_stations_temp > 0:
            for i in range(len(center_points)):
                available_stations = findStations(center_points[i][0], center_points[i][1], end_coords[0],
                                                  end_coords[1])

                # when circles with available stations overlap
                for station in used_stations:
                    available_stations.pop(station, None)


                if len(list(available_stations)) != 0:

                    drawn_station = random.choice(list(available_stations))
                    available_stations.pop(drawn_station, None)
                    solution.append(
                        [random.randint(min_speed, max_speed), drawn_station, random.randint(10, max_charging_time)])
                    used_stations.append(drawn_station)
                elif len(list(available_stations)) == 0:
                    print('no available stations')

        solution.append([random.randint(min_speed, max_speed), end_coords, 0])

        solutions.append(solution)

    return solutions
