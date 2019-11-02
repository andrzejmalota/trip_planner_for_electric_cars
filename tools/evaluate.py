import json
from tools.calculate_distance import calculate_distance
import copy
# 1 mila = 1.6 km

def time_soc(b):  # returns time needed to charge battery from 0 to b percent
    return 0.00032 * b ** 3 - 0.035 * b ** 2 + 1.3 * b - 1.3


# ---------------------------------- Nie jestem pewnien czy to jest dobrze ale wydaje mi sie ze chyba tak, sprawdze to pozniej dla kilku dnaych :P
def soc_time(b0, t):  # returns battery SOC after t-minutes of charging, b0 is the initial SOC
    # print("b0", b0)
    # print("t", t)

    # OGRANICZENIA:
    t = t + time_soc(b0)

    return 0.00012 * t ** 3 - 0.033 * t ** 2 + 3.1 * t - 2.7


def range_speed(v):  # returns range of car at constant speed of v
    v = v / 1.6
    return (-3.1115e-05 * v ** 4) + (8.7403e-03 * v ** 3) - (8.1119e-01 * v ** 2) + (2.4288e+01 * v) + 181


def cons_speed(v):  # returns consumption in kWh per kilometer at constant speed of v
    v = v / 1.6
    return (-6.9444e-04 * v ** 3 + 1.6012e-01 * v ** 2 - 6.7698e+00 * v + 2.7071e+02) / 1000


def remove_penalties(solutions):
    new_solutions = []
    print('dlugosc po usunieciu kar', len(solutions))
    for solution in solutions:
        new_solutions.append(copy.deepcopy(solution[0:len(solution) - 1]))
    print('dlugosc po usunieciu kar', len(new_solutions))
    return new_solutions


def evaluate(solutions, init_parameters, add_penalties=False, display=False):
    with open('tools/stations_coords.json') as f:
        stations = json.load(f)

    with open('tools/stations_id.json') as ff:
        stations_id = json.load(ff)

    battery_capacity = 85  # pojemnosc baterii -> 85 kWh
    with open('tools/stations_distances_matrix.json') as f:
        stations_distances = json.load(f)

    with open("tools/parameters.json") as f:
        parameters = json.load(f)

    if 'penalty_multiplier' in parameters['config1'].keys():
        penalty_multiplier = parameters['config1']['penalty_multiplier']
    else:
        penalty_multiplier = parameters['default']['penalty_multiplier']


    penalty = []
    new_solutions = []
    if add_penalties == False:
        for solution in solutions:
            new_solutions.append(copy.deepcopy(solution[0:len(solution) - 2]))
    else:
        new_solutions = copy.deepcopy(solutions)

    for solution in new_solutions:

        starting_SOC = init_parameters[2]
        # trzeba ogarnac jak wczytuje ta zmienna, czy jak argument funkcji evaluate czy inaczej
        evaluation = 0
        previous_section = [0, 0, 0]
        segment_penalty = []
        # print("dlugosc", len(solution))
        for i in range(0, len(solution)):
            # print("i ", i)
            # print(solution[i][1])
            # print("starting soc", starting_SOC)
            if starting_SOC < 0:
                starting_SOC = 0
            elif starting_SOC > 99:
                starting_SOC = 99
            start_SOC_and_charged_SOC = soc_time(starting_SOC, previous_section[2])
            #print(starting_SOC)
            if i == 0 and len(solution) != 1:  # od pkt startowego do pierwszej ladowarki
                distance = calculate_distance(init_parameters[0],
                                              [stations[solution[i][1]]['lat'], stations[solution[i][1]]['lng']])[0]

            elif i == 0 and len(solution) == 1:  # od pkt startowego do koncowego bez ladowania
                distance = calculate_distance(init_parameters[0], init_parameters[1])[0]

            elif i == len(solution) - 1 and len(solution) > 1:  # od ostatniej ladowarki do pkt koncowego
                distance = calculate_distance(init_parameters[1], [stations[solution[i - 1][1]]['lat'],
                                                                   stations[solution[i - 1][1]]['lng']])[0]

            else:  # od ladowarki do ladowarki
                # print("pierwsza ladowarka ", stations_id[solution[i-1][1]])
                # print("druga ladowarka ", stations_id[solution[i][1]])
                # print('blad',stations_distances['matrix'][stations_id[solution[i - 1][1]]][stations_id[solution[i][1]]])
                if stations_distances['matrix'][stations_id[solution[i - 1][1]]][stations_id[solution[i][1]]] == -1:
                    distance = stations_distances['matrix'][stations_id[solution[i][1]]][
                        stations_id[solution[i - 1][1]]]
                else:
                    distance = stations_distances['matrix'][stations_id[solution[i - 1][1]]][
                        stations_id[solution[i][1]]]

            # print("distance", distance)
            used_SOC = cons_speed(solution[i][0]) * distance / 1000 / battery_capacity * 100  # return percentage
            starting_SOC = float("{0:.2f}".format(start_SOC_and_charged_SOC - used_SOC))

            # print("used soc", used_SOC)
            # print("charged soc", start_SOC_and_charged_SOC)
            if starting_SOC < 0:
                penalty = (-1) * starting_SOC
                penalty1 = (-1) * starting_SOC
                # gdy zuzyje wiecej energi na tym odcinku niz mial dostepne
            elif starting_SOC >= 0:
                penalty1 = 0
                penalty = (-1) * starting_SOC
            segment_penalty.append(penalty)

            if display == False:
                evaluation = int(evaluation + solution[i][2] + (distance / 1000 * 60 / solution[i][0])
                                 + (penalty1 * penalty_multiplier))
            elif display == True:
                evaluation = int(evaluation + solution[i][2] + (distance / 1000 * 60 / solution[i][0]))

            previous_section = solution[i]
        solution.append(evaluation)
        if add_penalties == True:
            solution.append(segment_penalty)
    return new_solutions
