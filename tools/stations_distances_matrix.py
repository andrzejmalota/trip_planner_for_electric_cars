import json
from calculate_distance import calculate_distance

with open('tools/stations_coords.json') as f:
    stations = json.load(f)

id = 0
stations_id = {}
for key in stations.keys():
    stations_id[key] = id
    id = id + 1

with open('tools/stations_id.json', 'w') as ff:
    json.dump(stations_id, ff)

# stations_array = {'matrix': [[0]*(len(stations.keys())) for i in range(len(stations.keys()))]}
# routes_array = {'matrix': [[0] * (len(stations.keys())) for i in range(len(stations.keys()))]}

keys = list(stations.keys())

# for i in range(len(keys)):
#     print(i)
#     for j in range(len(keys)):
#         stations_array['matrix'][i][j] = -1
#
# with open('tools/stations_distances_matrix.json', 'w') as fp:
#     json.dump(stations_array, fp)

with open('tools/stations_distances_matrix.json') as fff:
    stations_array = json.load(fff)

with open('tools/stations_routes_matrix.json') as fff:
    routes_array = json.load(fff)

for i in range(150, 403):
    print(i)
    for j in range(i, len(keys)):
        try:

            x = calculate_distance([stations[keys[i]]['lat'], stations[keys[i]]['lng']],
                                   [stations[keys[j]]['lat'], stations[keys[j]]['lng']])
            stations_array['matrix'][i][j] = x[0]

            routes_array['matrix'][i][j] = x[1]



        except TimeoutError:
            print('directions err')

    with open('tools/stations_distances_matrix.json', 'w') as fp:
        json.dump(stations_array, fp)

    with open('tools/stations_routes_matrix.json', 'w') as file:
        json.dump(routes_array, file)
