import googlemaps
import math

def decode_polyline(polyline_str):
    index, lat, lng = 0, 0, 0
    coordinates = []
    changes = {'latitude': 0, 'longitude': 0}

    while index < len(polyline_str):
        for unit in ['latitude', 'longitude']:
            shift, result = 0, 0

            while True:
                byte = ord(polyline_str[index]) - 63
                index += 1
                result |= (byte & 0x1f) << shift
                shift += 5
                if not byte >= 0x20:
                    break

            if (result & 1):
                changes[unit] = ~(result >> 1)
            else:
                changes[unit] = (result >> 1)

        lat += changes['latitude']
        lng += changes['longitude']

        coordinates.append((lng / 100000.0, lat / 100000.0))

    return coordinates


gmaps = googlemaps.Client(key='AIzaSyAJw4KZ8df094Qsqk3YS2kUIpNWjLLb5MI')  # Moj klucz


# gmaps = googlemaps.Client(key='AIzaSyCnGkahFIYva7I8WiWUP_Q1F3x5VhvQgHU')  # klucz Michala


def calculate_distance(start, end, points_density=2):
    # print(directions_result)
    final_route = []
    counter = 0
    points = 0
    distance = 0
    decoded_route_list = []

    try:
        directions_result = gmaps.directions((start[0], start[1]), (end[0], end[1]), mode="driving")
        for ii in directions_result[0]['legs'][0]['steps']:
            points += len(decode_polyline((ii['polyline']['points'])))
            final_route += decode_polyline((ii['polyline']['points']))

        for k in directions_result[0]['legs'][0]['steps']:
            distance += k['distance']['value']

        decoded_route_list = [list(elem) for elem in final_route]
        decoded_route_list = decoded_route_list[:points:math.ceil(points / points_density)]
        decoded_route_list.remove(decoded_route_list[len(decoded_route_list) - 1])
        decoded_route_list.append([end[1], end[0]])
        # print('sceizka: ',decoded_route_list)

    except:
        print('CANT FIND ROUTE, possible wrong start or destination')

    return [distance, decoded_route_list]
