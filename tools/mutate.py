import random
from tools.initialise import findStations
from tools.calculate_distance import calculate_distance
import json
import copy

max_time = 99
min_time = 10
radius = 1

with open("tools/parameters.json") as f:
    parameters = json.load(f)

if 'min_speed' in parameters['config1'].keys():
    min_speed = parameters['config1']['min_speed']
else:
    min_speed = parameters['default']['min_speed']
if 'max_speed' in parameters['config1'].keys():
    max_speed = parameters['config1']['max_speed']
else:
    max_speed = parameters['default']['max_speed']
if 'mutation_multiplier' in parameters['config1'].keys():
    mutation_multiplier = parameters['config1']['mutation_multiplier']
else:
    mutation_multiplier = parameters['default']['mutation_multiplier']

with open('tools/stations_coords.json') as f:
    stations_coords = json.load(f)

with open('tools/stations_distances_matrix.json') as f:
    stations_distances = json.load(f)

with open('tools/stations_id.json') as ff:
    stations_id = json.load(ff)


def mutation(solutions, init_parameters):
    print("MUTATION")
    temp = copy.deepcopy(solutions)
    mutateNumberOfSuperchargers_set = []
    mutateSpeed_set = []
    mutateChargingTime_set = []
    mutateSupercharger_set = []
    mutate_supercharger_distance_set = []
    mutate_number_of_superchargers_distance_set = []
    mutate_number_of_superchargers_remove_distance_set = []
    mutate_supercharger_distance_too_close_set = []

    for i in range(len(solutions)):
        choice = i % 10
        if choice == 1 or choice == 5 or choice == 8:
            chosen = random.choice(temp)
            mutateSpeed_set.append(chosen)
            temp.remove(chosen)
        elif choice == 2 or choice == 6:
            chosen = random.choice(temp)
            mutateChargingTime_set.append(chosen)
            temp.remove(chosen)
        elif choice == 3 or choice == 7:
            chosen = random.choice(temp)
            mutate_supercharger_distance_set.append(chosen)
            temp.remove(chosen)
        elif choice == 9:
            chosen = random.choice(temp)
            mutate_supercharger_distance_too_close_set.append(chosen)
            temp.remove(chosen)
        elif choice == 4:
            chosen = random.choice(temp)
            mutate_number_of_superchargers_distance_set.append(chosen)
            temp.remove(chosen)
        elif choice == 0:
            chosen = random.choice(temp)
            mutate_number_of_superchargers_remove_distance_set.append(chosen)
            temp.remove(chosen)

    new_solutions = mutate_number_of_superchargers_remove_distance(mutate_number_of_superchargers_remove_distance_set,
                                                                   init_parameters) \
                    + mutateChargingTime(mutateChargingTime_set) \
                    + mutateSpeed(mutateSpeed_set) \
                    + mutate_supercharger_distance(mutate_supercharger_distance_set, init_parameters) \
                    + mutate_number_of_superchargers_distance(mutate_number_of_superchargers_distance_set,
                                                              init_parameters) \
                    + mutate_supercharger_distance_too_close(mutate_supercharger_distance_too_close_set,
                                                             init_parameters)

    return new_solutions


def mutateSpeed(solutions):
    new_solutions = copy.deepcopy(solutions)
    print('zmiana predkosci set')
    for solution in new_solutions:
        print(solution)

    # kaara > 0 -> zabraklo
    # kara < 0 -> nadwyzka enegrii
    for solution in new_solutions:
        for i in range(len(solution) - 2):
            if solution[len(solution) - 1][i] > 0:
                if int(solution[i][0] - (solution[len(solution) - 1][i] * mutation_multiplier)) <= min_speed:
                    offset = min_speed
                else:
                    offset = int(solution[i][0] - (solution[len(solution) - 1][i] * mutation_multiplier))
                solution[i][0] = random.randint(offset, solution[i][0])

            else:
                if int(solution[i][0] - (solution[len(solution) - 1][i] * mutation_multiplier)) >= max_speed:
                    offset = max_speed
                else:
                    offset = int(solution[i][0] - (solution[len(solution) - 1][i] * mutation_multiplier))
                solution[i][0] = random.randint(solution[i][0], offset)
    print('zmiana predkosci wynik')
    for solution in new_solutions:
        print(solution)
    return new_solutions


def mutateChargingTime(solutions):
    new_solutions = copy.deepcopy(solutions)
    print('zmiana czasu set')
    for solution in new_solutions:
        print(solution)

    # kaara > 0 -> zabraklo
    # kara < 0 -> nadwyzka enegrii
    for solution in new_solutions:
        for i in range(len(solution) - 3):
            if solution[len(solution) - 1][i + 1] > 0:
                if int(solution[i][2] + (solution[len(solution) - 1][i + 1] * mutation_multiplier)) >= max_time:
                    offset = max_time
                else:
                    offset = int(solution[i][2] + (solution[len(solution) - 1][i + 1] * mutation_multiplier))
                solution[i][2] = random.randint(solution[i][2], offset)

            else:
                if int(solution[i][2] + (solution[len(solution) - 1][i + 1] * mutation_multiplier)) <= min_time:
                    offset = min_time
                else:
                    offset = int(solution[i][2] + (solution[len(solution) - 1][i + 1] * mutation_multiplier))
                solution[i][2] = random.randint(offset, solution[i][2])
    print('zmiana czasu wynik')
    for solution in new_solutions:
        print(solution)
    return new_solutions


# zeby ladowarki byly rowno rozmieszczone
def mutate_supercharger_distance(solutions, init_parameters):
    new_solutions = copy.deepcopy(solutions)
    index_list = [0, 0]
    print('zmiana ladowarki dystans set')
    for solution in new_solutions:
        print(solution)

    for solution in new_solutions:
        if len(solution) > 3:
            max_distance = 0
            for i in range(len(solution) - 2):
                if i == 0:  # od pkt startowego do pierwszej ladowarki
                    distance = calculate_distance(init_parameters[0],
                                                  [stations_coords[solution[i + 1][1]]['lat'],
                                                   stations_coords[solution[i + 1][1]]['lng']])[0]
                    print("start-ladow")

                elif i == len(solution) - 3:  # od ostatniej ladowarki do pkt koncowego
                    distance = calculate_distance(init_parameters[1], [stations_coords[solution[i - 2][1]]['lat'],
                                                                       stations_coords[solution[i - 2][1]]['lng']])[0]
                    print('ladow-koniec')

                elif i > 0 and i < len(solution) - 4:  # od ladowarki do ladowarki
                    # print("pierwsza ladowarka ", stations_id[solution[i-1][1]])
                    # print("druga ladowarka ", stations_id[solution[i][1]])
                    # print('blad',stations_distances['matrix'][stations_id[solution[i - 1][1]]][stations_id[solution[i][1]]])
                    print('ladow-ladow')
                    if stations_distances['matrix'][stations_id[solution[i - 1][1]]][
                        stations_id[solution[i + 1][1]]] == -1:
                        distance = stations_distances['matrix'][stations_id[solution[i + 1][1]]][
                            stations_id[solution[i - 1][1]]]
                    else:
                        distance = stations_distances['matrix'][stations_id[solution[i - 1][1]]][
                            stations_id[solution[i + 1][1]]]
                if distance > max_distance:
                    max_distance = distance
                    index = i
                    index_list[1] = index_list[0]
                    index_list[0] = index

            index = random.randint(0, 1)
            index = index_list[index]
            print('index', index)
            print('sol', solution[index])
            # DISTANCE BEETWEN START AND FIRST SUPERCHARGER
            if index == 0:
                center = [
                    (init_parameters[0][0] + stations_coords[solution[index + 1][1]]["lat"]) / 2,
                    (init_parameters[0][1] + stations_coords[solution[index][1]]["lng"]) / 2]
                print('0')
            # DISTANCE BEETWEN LAST SUPERCHARGER AND END
            elif index == len(solution) - 3:
                center = [
                    (stations_coords[solution[index - 2][1]]["lat"] + init_parameters[1][0]) / 2,
                    (stations_coords[solution[index - 2][1]]["lng"] + init_parameters[1][1]) / 2]
                print('1')
            elif index == len(solution) - 4:
                center = [
                    (stations_coords[solution[index - 1][1]]["lat"] + init_parameters[1][0]) / 2,
                    (stations_coords[solution[index - 1][1]]["lng"] + init_parameters[1][1]) / 2]
                print('1 ostatnia ladow')
            # DISTANCE BEETWEN 2 SUPERCHARGERS
            else:
                center = [
                    (stations_coords[solution[index + 1][1]]["lat"] + stations_coords[solution[index - 1][1]][
                        "lat"]) / 2,
                    (stations_coords[solution[index + 1][1]]["lng"] + stations_coords[solution[index - 1][1]][
                        "lng"]) / 2]
                print('2')

            available_stations = findStations(center[0], center[1], init_parameters[1][0],
                                              init_parameters[1][1], radius)

            if len(available_stations) != 0:
                for i in range(len(solution) - 3):
                    available_stations.pop(solution[i][1], None)
                if len(available_stations) != 0:
                    drawn_station = random.choice(list(available_stations))

                    solution[index] = [100, drawn_station, 40]
        # calkowity czas i kary sie gdzies indziej potem zmieniaja czy to trzeba tutaj jeszcze uwzglednic?
        # nie trzeba, to i tak jest usuwane do rysowania

    print('zmiana ladowarki dystans wynik')
    for solution in new_solutions:
        print(solution)
    return new_solutions


# zeby ladowarki byly rowno rozmieszczone
def mutate_number_of_superchargers_distance(solutions, init_parameters):
    new_solutions = copy.deepcopy(solutions)
    print('dodawanie ladowarki dystans set')
    for solution in new_solutions:
        print(solution)

    for solution in new_solutions:
        if len(solution) > 3:
            max_distance = 0
            for i in range(len(solution) - 2):
                if i == 0:  # od pkt startowego do pierwszej ladowarki
                    distance = calculate_distance(init_parameters[0],
                                                  [stations_coords[solution[i][1]]['lat'],
                                                   stations_coords[solution[i][1]]['lng']])[0]

                elif i == len(solution) - 3:  # od ostatniej ladowarki do pkt koncowego
                    distance = calculate_distance(init_parameters[1], [stations_coords[solution[i - 1][1]]['lat'],
                                                                       stations_coords[solution[i - 1][1]]['lng']])[0]

                elif i > 0 and i < len(solution) - 3:  # od ladowarki do ladowarki
                    # print("pierwsza ladowarka ", stations_id[solution[i-1][1]])
                    # print("druga ladowarka ", stations_id[solution[i][1]])
                    # print('blad',stations_distances['matrix'][stations_id[solution[i - 1][1]]][stations_id[solution[i][1]]])
                    if stations_distances['matrix'][stations_id[solution[i - 1][1]]][stations_id[solution[i][1]]] == -1:
                        distance = stations_distances['matrix'][stations_id[solution[i][1]]][
                            stations_id[solution[i - 1][1]]]
                    else:
                        distance = stations_distances['matrix'][stations_id[solution[i - 1][1]]][
                            stations_id[solution[i][1]]]
                if distance > max_distance:
                    max_distance = distance
                    index = i
            print('index', index)
            print('sol', solution[index])
            # DISTANCE BEETWEN START AND FIRST SUPERCHARGER
            if index == 0:
                center = [
                    (init_parameters[0][0] + stations_coords[solution[index][1]]["lat"]) / 2,
                    (init_parameters[0][1] + stations_coords[solution[index][1]]["lng"]) / 2]
                print('0')
            # DISTANCE BEETWEN LAST SUPERCHARGER AND END
            elif index == len(solution) - 3:
                center = [
                    (stations_coords[solution[index - 1][1]]["lat"] + init_parameters[1][0]) / 2,
                    (stations_coords[solution[index - 1][1]]["lng"] + init_parameters[1][1]) / 2]
                print('1')
            # DISTANCE BEETWEN 2 SUPERCHARGERS
            else:
                center = [
                    (stations_coords[solution[index][1]]["lat"] + stations_coords[solution[index - 1][1]][
                        "lat"]) / 2,
                    (stations_coords[solution[index][1]]["lng"] + stations_coords[solution[index - 1][1]][
                        "lng"]) / 2]
                print('2')

            available_stations = findStations(center[0], center[1], init_parameters[1][0],
                                              init_parameters[1][1], radius)

            if len(available_stations) != 0:
                for i in range(len(solution) - 4):
                    available_stations.pop(solution[i][1], None)
                if len(available_stations) != 0:
                    drawn_station = random.choice(list(available_stations))

                    solution.insert(index, [100, drawn_station, 40])
        # calkowity czas i kary sie gdzies indziej potem zmieniaja czy to trzeba tutaj jeszcze uwzglednic?
        # nie trzeba, to i tak jest usuwane do rysowania

    print('dodawanie ladowarki dystans wynik')
    for solution in new_solutions:
        print(solution)
    return new_solutions


def mutate_supercharger_distance_too_close(solutions, init_parameters):
    new_solutions = copy.deepcopy(solutions)
    index_list = [0, 0]
    print('ladowarki za bisko dystans set')
    for solution in new_solutions:
        print(solution)

    for solution in new_solutions:
        if len(solution) > 3:
            max_distance = 0
            for i in range(len(solution) - 2):
                if i == 0:  # od pkt startowego do pierwszej ladowarki
                    distance = calculate_distance(init_parameters[0],
                                                  [stations_coords[solution[i][1]]['lat'],
                                                   stations_coords[solution[i][1]]['lng']])[0]
                    print('start-ladow')

                elif i == len(solution) - 3:  # od ostatniej ladowarki do pkt koncowego
                    distance = calculate_distance(init_parameters[1], [stations_coords[solution[i - 1][1]]['lat'],
                                                                       stations_coords[solution[i - 1][1]]['lng']])[0]
                    print('ladow-koniec')

                elif i > 0 and i < len(solution) - 3:  # od ladowarki do ladowarki
                    # print("pierwsza ladowarka ", stations_id[solution[i-1][1]])
                    # print("druga ladowarka ", stations_id[solution[i][1]])
                    # print('blad',stations_distances['matrix'][stations_id[solution[i - 1][1]]][stations_id[solution[i][1]]])
                    print('ladow-ladow')
                    if stations_distances['matrix'][stations_id[solution[i - 1][1]]][stations_id[solution[i][1]]] == -1:
                        distance = stations_distances['matrix'][stations_id[solution[i][1]]][
                            stations_id[solution[i - 1][1]]]
                    else:
                        distance = stations_distances['matrix'][stations_id[solution[i - 1][1]]][
                            stations_id[solution[i][1]]]
                if distance < max_distance:
                    max_distance = distance
                    index = i
                    index_list[1] = index_list[0]
                    index_list[0] = index

            index = random.randint(0, 1)
            index = index_list[index]
            print('index', index)
            print('sol', solution[index])
            # DISTANCE BEETWEN START AND FIRST SUPERCHARGER
            if index == 0:
                center = [
                    (init_parameters[0][0] + stations_coords[solution[index + 1][1]]["lat"]) / 2,
                    (init_parameters[0][1] + stations_coords[solution[index + 1][1]]["lng"]) / 2]
                print('0')
            # DISTANCE BEETWEN LAST SUPERCHARGER AND END
            elif index == len(solution) - 3:
                center = [
                    (stations_coords[solution[index - 2][1]]["lat"] + init_parameters[1][0]) / 2,
                    (stations_coords[solution[index - 2][1]]["lng"] + init_parameters[1][1]) / 2]
                print('1')
            elif index == len(solution) - 4:
                center = [
                    (stations_coords[solution[index - 1][1]]["lat"] + init_parameters[1][0]) / 2,
                    (stations_coords[solution[index - 1][1]]["lng"] + init_parameters[1][1]) / 2]
                print('1 ostatnia ladow')
            # DISTANCE BEETWEN 2 SUPERCHARGERS
            else:
                center = [
                    (stations_coords[solution[index + 1][1]]["lat"] + stations_coords[solution[index - 1][1]][
                        "lat"]) / 2,
                    (stations_coords[solution[index + 1][1]]["lng"] + stations_coords[solution[index - 1][1]][
                        "lng"]) / 2]
                print('2')

            available_stations = findStations(center[0], center[1], init_parameters[1][0],
                                              init_parameters[1][1], radius)

            if len(available_stations) != 0:
                for i in range(len(solution) - 4):
                    available_stations.pop(solution[i][1], None)
                if len(available_stations) != 0:
                    drawn_station = random.choice(list(available_stations))

                    solution[index] = [100, drawn_station, 40]
        # calkowity czas i kary sie gdzies indziej potem zmieniaja czy to trzeba tutaj jeszcze uwzglednic?
        # nie trzeba, to i tak jest usuwane do rysowania

    print('ladowarki za blisko dystans wynik')
    for solution in new_solutions:
        print(solution)
    return new_solutions


def mutate_number_of_superchargers_remove_distance(solutions, init_parameters):
    new_solutions = copy.deepcopy(solutions)
    index_list = [0, 0]
    print('usuwanie ladowarki dystans set')
    for solution in new_solutions:
        print(solution)

    for solution in new_solutions:
        if len(solution) > 3:
            max_distance = 0
            for i in range(len(solution) - 2):
                if i == 0:  # od pkt startowego do pierwszej ladowarki
                    distance = calculate_distance(init_parameters[0],
                                                  [stations_coords[solution[i + 1][1]]['lat'],
                                                   stations_coords[solution[i + 1][1]]['lng']])[0]

                elif i == len(solution) - 3:  # od ostatniej ladowarki do pkt koncowego
                    distance = calculate_distance(init_parameters[1], [stations_coords[solution[i - 2][1]]['lat'],
                                                                       stations_coords[solution[i - 2][1]]['lng']])[0]

                elif i > 0 and i < len(solution) - 4:  # od ladowarki do ladowarki
                    # print("pierwsza ladowarka ", stations_id[solution[i-1][1]])
                    # print("druga ladowarka ", stations_id[solution[i][1]])
                    # print('blad',stations_distances['matrix'][stations_id[solution[i - 1][1]]][stations_id[solution[i][1]]])
                    if stations_distances['matrix'][stations_id[solution[i - 1][1]]][
                        stations_id[solution[i + 1][1]]] == -1:
                        distance = stations_distances['matrix'][stations_id[solution[i + 1][1]]][
                            stations_id[solution[i - 1][1]]]
                    else:
                        distance = stations_distances['matrix'][stations_id[solution[i - 1][1]]][
                            stations_id[solution[i + 1][1]]]
                if distance < max_distance:
                    max_distance = distance
                    index = i
                    index_list[1] = index_list[0]
                    index_list[0] = index

            index = random.randint(0, 1)
            print('sol', solution[index_list[index]])
            solution.remove(solution[index_list[index]])
        # calkowity czas i kary sie gdzies indziej potem zmieniaja czy to trzeba tutaj jeszcze uwzglednic?
        # nie trzeba, to i tak jest usuwane do rysowania

    print('usuwanie ladowarki dystans wynik')
    for solution in new_solutions:
        print(solution)
    return new_solutions


def mutateSupercharger(solutions, init_parameters):
    new_solutions = copy.deepcopy(solutions)
    print('zmiana ladowarki set')
    for solution in new_solutions:
        print(solution)

    for solution in new_solutions:
        if len(solution) > 3:
            penalty = solution[(len(solution) - 1)][0] + solution[(len(solution) - 1)][1]
            index = 0
            # FINDING BIGGEST PENALTY IN SOLUTION
            for i in range(len(solution[len(solution) - 1]) - 1):
                if solution[len(solution) - 1][i] + solution[len(solution) - 1][i + 1] > penalty:
                    index = i
                    penalty = solution[len(solution) - 1][i] + solution[len(solution) - 1][i + 1]

            # NO SUPERCHARGERS IN SOLUTION
            if len(solution) == 3:
                center = [init_parameters[0][0], init_parameters[0][1], init_parameters[1][0], init_parameters[1][1]]

            # SUPERCHARGERS IN SOLUTION
            if len(solution) > 3:
                # PENALTY BEETWEN START AND FIRST SUPERCHARGER
                if index == 0:
                    center = [
                        (init_parameters[0][0] + stations_coords[solution[index + 1][1]]["lat"]) / 2,
                        (init_parameters[0][1] + stations_coords[solution[index + 1][1]]["lng"]) / 2]
                    print('0')
                # PENALTY BEETWEN LAST SUPERCHARGER AND END
                elif index == len(solution) - 4:
                    center = [
                        (stations_coords[solution[index - 1][1]]["lat"] + init_parameters[1][0]) / 2,
                        (stations_coords[solution[index - 1][1]]["lng"] + init_parameters[1][1]) / 2]
                    print('1')
                # PENALTY BEETWEN 2 SUPERCHARGERS
                else:
                    center = [
                        (stations_coords[solution[index + 1][1]]["lat"] + stations_coords[solution[index - 1][1]][
                            "lat"]) / 2,
                        (stations_coords[solution[index + 1][1]]["lng"] + stations_coords[solution[index - 1][1]][
                            "lng"]) / 2]
                    print('2')

            available_stations = findStations(center[0], center[1], init_parameters[1][0], init_parameters[1][1],
                                              radius)

            if len(available_stations) != 0:
                for i in range(len(solution) - 3):
                    available_stations.pop(solution[i][1], None)
                if len(available_stations) != 0:
                    drawn_station = random.choice(list(available_stations))

                    solution[index] = [100, drawn_station, 40]
                # calkowity czas i kary sie gdzies indziej potem zmieniaja czy to trzeba tutaj jeszcze uwzglednic?
                # nie trzeba, to i tak jest usuwane do rysowania
        else:
            None
    print('zmiana ladowarki wynik')
    for solution in new_solutions:
        print(solution)
    return new_solutions


def mutateNumberOfSuperchargers(solutions, init_parameters):
    # -------------------------
    # trzeba rozwazyc przypadki gdy nie ma ladowarek

    new_solutions = copy.deepcopy(solutions)
    print('dodawanie ladowrki set')
    for solution in new_solutions:
        print(solution)

    for solution in new_solutions:
        penalty = solution[(len(solution) - 1)][0]
        index = 0
        # FINDING BIGGEST PENALTY IN SOLUTION
        for i in range(len(solution[len(solution) - 1])):
            if solution[len(solution) - 1][i] > penalty:
                index = i
                penalty = solution[len(solution) - 1][i]

        # FINDING CENTER POINT
        print('index', index)
        # NO SUPERCHARGERS IN SOLUTION
        if len(solution) == 3:
            center = [init_parameters[0][0], init_parameters[0][1], init_parameters[1][0], init_parameters[1][1]]

        # SUPERCHARGERS IN SOLUTION
        if len(solution) > 3:
            # PENALTY BEETWEN START AND FIRST SUPERCHARGER
            if index == 0:
                center = [
                    (init_parameters[0][0] + stations_coords[solution[index][1]]["lat"]) / 2,
                    (init_parameters[0][1] + stations_coords[solution[index][1]]["lng"]) / 2]
                print('0')
            # PENALTY BEETWEN LAST SUPERCHARGER AND END
            elif index == len(solution[len(solution) - 1]) - 1:
                # ???? co to jest? -> gdy wylosowano ostatni element listy kar czyli wrzucasz pomiedzy ostatnia ladowarka a koncem
                center = [
                    (stations_coords[solution[index][1]]["lat"] + init_parameters[1][0]) / 2,
                    (stations_coords[solution[index][1]]["lng"] + init_parameters[1][1]) / 2]
                print('1')

            # PENALTY BEETWEN 2 SUPERCHARGERS
            else:
                center = [
                    (stations_coords[solution[index][1]]["lat"] + stations_coords[solution[index - 1][1]]["lat"]) / 2,
                    (stations_coords[solution[index][1]]["lng"] + stations_coords[solution[index - 1][1]]["lng"]) / 2]
                print('2')

        available_stations = findStations(center[0], center[1], init_parameters[1][0],
                                          init_parameters[1][1], radius)
        if len(available_stations) != 0:
            for i in range(len(solution) - 3):
                available_stations.pop(solution[i][1], None)
            if len(available_stations) != 0:
                drawn_station = random.choice(list(available_stations))

                solution.insert(index, [100, drawn_station, 40])
    print('dodawanie ladowarki wynik')
    for solution in new_solutions:
        print(solution)
    return new_solutions


def recombine(solutions):
    new_solutions = copy.deepcopy(solutions)
    print('recombine set')
    for solution in new_solutions:
        print(solution)
    pairs = []
    for i in range(int((len(new_solutions)) / 2)):
        chosen = random.choice(new_solutions)
        new_solutions.remove(chosen)
        chosen1 = random.choice(new_solutions)
        new_solutions.remove(chosen1)
        pairs.append([chosen, chosen1])
    # WHEN len(solutions)-1 is ODD number
    if len(new_solutions) == 1:
        for j in range(len(solutions)):
            chosen = random.choice(solutions)
            if chosen != new_solutions[0]:
                break
        pairs.append([chosen, new_solutions[0]])
    print('pairs')
    for pair in pairs:
        print(pair)
    return pairs


def crossover(solutions):
    print('crossover set', solutions)
    for solution in solutions:
        print(solution)
    new_solutions = []
    solutions1 = copy.deepcopy(solutions)
    pairs = recombine(solutions1)
    # -------------------
    # OGARNAC ZEBY PRZY LACZENIU NIE POWTARZALY SIE LADOWARKI
    # ---------------------------------------
    for pair in pairs:
        index = random.randint(0, min(len(pair[0]) - 3, len(pair[1]) - 3))
        print('index', index)
        while (pair[0][index - 1] == pair[1][index]):
            print('te same ladowarki')
            index = random.randint(0, min(len(pair[0]) - 3, len(pair[1]) - 3))
            print('index', index)
        new_solutions.append(pair[0][0:index] + pair[1][index:len(pair[1])])
        index = random.randint(0, min(len(pair[0]) - 3, len(pair[1]) - 3))
        print('index', index)
        while (pair[1][index - 1] == pair[0][index]):
            print('te same ladowarki')
            index = random.randint(0, min(len(pair[0]) - 3, len(pair[1]) - 3))
            print('index', index)
        new_solutions.append(pair[1][0:index] + pair[0][index:len(pair[0])])
    if len(solutions) % 2 != 0:
        new_solutions.remove(new_solutions[len(new_solutions) - 1])
    print('crossover results')
    for solution in new_solutions:
        print(solution)
    return new_solutions


def mutate(solutions, init_parameters):
    number_of_crossovers = int(len(solutions) / 5)
    crossover_set = []
    temp = copy.deepcopy(solutions)
    for i in range(number_of_crossovers):
        chosen = random.choice(temp)
        crossover_set.append(chosen)
        temp.remove(chosen)
    mutation_set = temp

    new_solutions = mutation(mutation_set, init_parameters) + crossover(crossover_set)
    return new_solutions
