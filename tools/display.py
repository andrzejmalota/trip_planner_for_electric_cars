from mapbox import StaticStyle
from tools.calculate_distance import calculate_distance
import json
import copy

def find_best_solution(generation):
    cost = generation[0][len(generation[0]) - 1]
    best_solution = generation[0]
    for solution in generation:
        if solution[len(solution) - 1] < cost:
            cost = solution[len(solution) - 1]
            best_solution = solution
    return best_solution


#
# def generatePoints(start_coords, end_coords, number_of_stations):
#     if number_of_stations != 0:
#         segment_lat = (end_coords[0] - start_coords[0]) / number_of_stations
#         segment_lng = (end_coords[1] - start_coords[1]) / number_of_stations
#     tab = []
#     for x in range(0, number_of_stations + 1):
#         tab.append([start_coords[0] + segment_lat * x, start_coords[1] + segment_lng * x])
#     return tab


def generatePoints2(start_coords, end_coords, number_of_stations, starting_soc):
    path = calculate_distance(start_coords, end_coords, 90)[1]
    if number_of_stations > 0:
        print('path', len(path))
        print('il stacji', number_of_stations)
        print('skok', int((len(path) / (number_of_stations + 1))))
        path = path[0:len(path):int((len(path) / (number_of_stations + 1)))]
    elif number_of_stations == 0:
        path = path[0] + path[len(path) - 1]

    if starting_soc > 70:
        path = path[1:len(path) - 1]
    else:
        path = path[0:len(path) - 1]

    for p in range(len(path)):
        path[p] = [path[p][0], path[p][1]]
    return path



def test_line(generation, init_parameters):
    solution = find_best_solution(generation)
    print("test rozw", solution)
    # pts = generatePoints2([init_parameters[0][1],init_parameters[0][0]],[init_parameters[1][1],init_parameters[1][0]],len(solution) - 1 )
    pts = generatePoints2(init_parameters[0], init_parameters[1], len(solution) - 2, init_parameters[2])
    icons = []

    for i in range(len(pts)):
        icon_supercharger = {'type': 'Feature', 'properties': {"marker-symbol": i, },
                             'geometry': {'type': 'Point', 'coordinates': pts[i]}}
        icons.append(icon_supercharger)

    return icons


def create_path(solution, init_parameters):
    start_symbol = 'car'
    charger_symbol = 'fuel'
    end_symbol = 'marker'
    line_width = 5
    line_opacity = 0.8
    line_color = '#FF0000'
    path = []
    icons = []

    with open('tools/stations_coords.json') as f:
        stations_coords = json.load(f)

    with open('tools/stations_routes_matrix.json') as fff:
        routes_array = json.load(fff)

    with open('tools/stations_id.json') as fff:
        stations_id = json.load(fff)

    # create path, line from start to end through superchargers

    if len(solution) > 2:
        number_of_segments = len(solution) - 1
        path = calculate_distance(init_parameters[0],
                                  [stations_coords[solution[0][1]]['lat'], stations_coords[solution[0][1]]['lng']])[1]
        # path = path[:len(path):int(len(path))]

        for i in range(0, number_of_segments - 3):

            if routes_array['matrix'][stations_id[solution[i][1]]][stations_id[solution[i + 1][1]]] == 0:
                print('zzzero')
                print(routes_array['matrix'][stations_id[solution[i][1]]][stations_id[solution[i + 1][1]]])
                print(routes_array['matrix'][stations_id[solution[i + 1][1]]][stations_id[solution[i][1]]][::-1])
                segment = routes_array['matrix'][stations_id[solution[i + 1][1]]][stations_id[solution[i][1]]][::-1]
            else:
                segment = routes_array['matrix'][stations_id[solution[i][1]]][stations_id[solution[i + 1][1]]]

            # print(segment)
            start = segment[0]
            end = segment[len(segment) - 1]
            center = segment[int(len(segment) / 2)]
            # segment = segment[1:len(segment)-1:int(len(segment) / 2)]
            # segment.append(end)
            # segment.insert(0,start)
            seg = []
            seg.append(start)
            # seg.append(center)
            seg.append(end)

            print(seg)
            path = path + seg

        segment = calculate_distance([stations_coords[solution[len(solution) - 4][1]]['lat'],
                                      stations_coords[solution[len(solution) - 4][1]]['lng']],
                                     init_parameters[1], )[1]

        segment.append([init_parameters[1][1], init_parameters[1][0]])
        #segment = segment[:len(segment):int(len(segment))]
        path = path + segment

    if len(solution) == 2:
        path = calculate_distance(init_parameters[0], init_parameters[1])[1]

    print("PATH COORDS ", path)

    # for j in range(len(solution) - 1):

    generation = {'type': 'Feature', 'properties': {'name': 'Path', "marker-symbol": "monument"},
                  'geometry': {'type': 'LineString', 'coordinates': path}}
    if len(solution) < 13:
        icons.append(generation)

    # ---------------------------------------------------------------------------------
    # Create markers for start,end and superchargers

    coords = [init_parameters[0][1], init_parameters[0][0]]
    icon_start = {'type': 'Feature', 'properties': {"marker-symbol": start_symbol, "marker-color": "#FF0000"},
                  'geometry': {'type': 'Point', 'coordinates': coords}}
    icons.append(icon_start)

    if len(solution) > 1:
        for i in range(0, len(solution) - 3):
            charging_time = solution[i][2]
            coords = [stations_coords[solution[i][1]]['lng'],
                      stations_coords[solution[i][1]]['lat']]

            icon_supercharger = {'type': 'Feature', 'properties': {"marker-symbol": i + 1, },
                                 'geometry': {'type': 'Point', 'coordinates': coords}}

            print('SUPERCHARGER-', i, ': ', solution[i][1])
            icons.append(icon_supercharger)

    coords = [init_parameters[1][1], init_parameters[1][0]]

    icon_end = {'type': 'Feature', 'properties': {"marker-symbol": end_symbol, "marker-color": "#FF0000"},
                'geometry': {'type': 'Point', 'coordinates': coords}}

    icons.append(icon_end)
    return icons


def display(best_solution, init_parameters, iteration):
    map_style = 'streets-v9'
    with open("tools/parameters.json") as f:
        parameters = json.load(f)

    if 'penalty_multiplier' in parameters['config1'].keys():
        penalty_multiplier = parameters['config1']['penalty_multiplier']
    else:
        penalty_multiplier = parameters['default']['penalty_multiplier']

    print('BEST SOLUTION : ', best_solution)
    icons = create_path(best_solution, init_parameters)
    #icons = test_line(generation, init_parameters)
    print("ICONS :", icons)

    map = StaticStyle(access_token=
                      'pk.eyJ1IjoiYW5kcmV3MTAxMSIsImEiOiJjamprcDVnOWE0YjBsM2t0ZThqa3Nvb3JsIn0.SKdRIieUwaw7Fbhke3jVMw')

    response = map.image(username='mapbox', style_id=map_style, features=icons, width=1279, height=700)

    string = 'Iteration: ' + str(iteration) + '\n' + str('Superchargers \n')
    for i in range(len(best_solution) - 3):
        segment_str = str(i + 1) + ': ' + str(best_solution[i][1]) + '\n' + 'Speed: ' + str(
            best_solution[i][0]) + ' km/h, charge: ' + str(best_solution[i][2]) + ' minutes'
        string += segment_str + '\n'
    string += 'Destination: speed: ' + str(best_solution[len(best_solution) - 3][0]) + ' km/h \n' + 'Total time :'
    time_hours = best_solution[len(best_solution) - 2] / 60
    time_minutes = best_solution[len(best_solution) - 2] % 60
    string += str(int(time_hours)) + ' hours,' + str(time_minutes) + ' minutes \n'
    str_time = str(best_solution[len(best_solution) - 2]) + ' | '
    k = best_solution[len(best_solution) - 2]
    for x in best_solution[len(best_solution) - 1]:
        if x > 0:
            k += penalty_multiplier * x
    str_function = str(int(k)) + ' | '

    string += 'Distance: ' + str(calculate_distance(init_parameters[0], init_parameters[1])[0] / 1000) + ' km \n'
    energy = best_solution[len(best_solution) - 1]
    en = []
    print(energy)
    for x in range(len(energy)):
        print(energy[x] * (-1))
        en.append(energy[x] * (-1))
    string_energy = str(en[::-1])
    print('energia', string_energy)

    return [response.content, string, string_energy, str_time, str_function]
