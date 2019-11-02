# select best solutions from parent generation to be mutated etc
import random
import copy


# TOURNAMENT SELECTION
def select(generation):
    number_of_winers_from_tournament = 2
    tournament_size = int(len(generation) / 4)
    number_of_tournaments = int(len(generation) / 2)
    if len(generation) % 2 == 1:
        number_of_tournaments += 1
    selected_solutions = []


    for n in range(number_of_tournaments):
        temp_generation = copy.deepcopy(generation)
        drawn_solutions = []

        for i in range(tournament_size):
            index = random.randint(0, len(temp_generation) - 1)
            drawn_solution = temp_generation[index]
            drawn_solutions.append(drawn_solution)
            temp_generation.remove(drawn_solution)
            print(drawn_solution)

        for k in range(0, number_of_winers_from_tournament):

            best = drawn_solutions[0]
            for solution in drawn_solutions:
                if solution[len(solution) - 2] < best[len(best) - 2]:
                    best = solution

            selected_solutions.append(best)
    if len(generation) % 2 == 1:
        selected_solutions.remove(selected_solutions[len(selected_solutions) - 1])

    return selected_solutions
