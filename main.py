from tools.initialise import initialise, get_initial_parameters1
from tools.evaluate import evaluate, remove_penalties
from tools.select import select
from tools.mutate import mutate
from tools.select_next_generation import select_next_generation
from tools.display import display
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QStackedWidget
from PyQt5 import QtCore
import sys
import json
import random


def evolutionary_algorithm(init_parameters):
    str_time = 'Total time: \n'
    str_function = 'Function: \n'
    with open("tools/parameters.json") as f:
        parameters = json.load(f)

    if 'number_of_iterations' in parameters['config1'].keys():
        number_of_iterations = parameters['config1']['number_of_iterations']
    else:
        number_of_iterations = parameters['default']['number_of_iterations']

    current_generation = initialise(init_parameters)

    best_solution = evaluate(current_generation, init_parameters, True, True)[
        random.randint(0, len(current_generation) - 1)]

    content = display(best_solution, init_parameters, 0)
    image_map.loadFromData(content[0])
    label_map.setPixmap(image_map)
    label_best_solution.setText(content[1])
    # label_energy.setText(content[2])
    label_map.repaint()
    label_best_solution.repaint()
    #label_energy.repaint()

    for i in range(number_of_iterations):
        print('------------------------------')
        print('LOOP : ', i + 1)
        current_generation = evaluate(current_generation, init_parameters, True)
        parent_generation = current_generation
        parent_generation = remove_penalties(parent_generation)
        current_generation = select(current_generation)
        print('len po select', len(current_generation))
        current_generation = mutate(current_generation, init_parameters)
        print('len po mutate', len(current_generation))
        current_generation = evaluate(current_generation, init_parameters, False)
        current_generation = select_next_generation(parent_generation, current_generation)
        print('len po select for next gener', len(current_generation))
        print("END GENERATION: ", current_generation)
        current_generation = remove_penalties(current_generation)
        best_solution = evaluate(current_generation, init_parameters, True, True)[0]
        content = display(best_solution, init_parameters, i + 1)
        image_map.loadFromData(content[0])
        label_map.setPixmap(image_map)
        label_best_solution.setText(content[1])
        str_time += content[3]
        str_function += content[4]
        str_algo_time = '\n' + 'In average solution, for number of iterations 10 and population size of 12,' \
                               ' we get around 800 requests from gmaps' + '\n' + 'with 50ms per request sums up to 40 seconds ' \
                                                                                 'plus around 5 seconds for requests from mapbox gives 45 seconds total (33%). ' + '\n' + '' \
                                                                                                                                                                          'Total time of algorithm = 140 seconds, time of calculations = 95 seconds (67% of total time).'
        label_energy.setText(str_time + '\n' + str_function + '\n' + str_algo_time)
        label_map.repaint()
        label_best_solution.repaint()
        label_energy.repaint()

def on_click_save():
    config = {}
    with open('tools/parameters.json') as f:
        parameters = json.load(f)
    if line_edit_iterations.text() != '':
        config['number_of_iterations'] = int(line_edit_iterations.text())
    if line_edit_generation_size.text() != '':
        config['generation_size'] = int(line_edit_generation_size.text())
    if line_edit_penalty_multiplier.text() != '':
        config['penalty_multiplier'] = float(line_edit_penalty_multiplier.text())
    if line_edit_mutation_multiplier.text() != '':
        config['mutation_multiplier'] = float(line_edit_mutation_multiplier.text())
    if line_edit_parent_to_child_size.text() != '':
        config['parent_to_child_size'] = float(line_edit_parent_to_child_size.text())
    if line_edit_min_speed.text() != '':
        config['min_speed'] = int(line_edit_min_speed.text())
    if line_edit_max_speed.text() != '':
        config['max_speed'] = int(line_edit_max_speed.text())

    parameters['config1'] = config
    with open("tools/parameters.json", 'w') as f:
        json.dump(parameters, f)


def on_click():
    print("START")
    evolutionary_algorithm(get_initial_parameters1(line_edit_start.text(), line_edit_end.text(),
                                                   int(line_edit_soc.text())))


def on_click_start():
    stacked_widget.setCurrentIndex(0)
    widget_plots.setVisible(False)


def on_click_parameters():
    stacked_widget.setCurrentIndex(1)
    widget_plots.setVisible(True)


if __name__ == "__main__":
    content = [0, 0]
    label_font_size = 12
    label_height = 25
    string_width = 400
    string_height = 640
    main_height = 900
    left_margin = 10
    main_width = 1280 + string_width + left_margin + 20
    with open('tools/parameters.json') as f:
        parameters = json.load(f)
    parameters['config1'] = {}
    with open("tools/parameters.json", 'w') as f:
        json.dump(parameters, f)

    app = QApplication([])
    main = QWidget()
    main.setWindowTitle('Route finder for electric cars')
    main.setStyleSheet('background-color: rgb(255,255,255); color: black')
    main.resize(main_width, main_height)

    # WIDGET MAIN
    label_line = QLabel(main)
    line = QPixmap('tools/line.svg').scaled(50, main_height + 100)
    label_line.setPixmap(line)
    label_line.setGeometry(QtCore.QRect(string_width, 0, 50, main_height))

    label_map = QLabel(main)
    image_map = QPixmap()
    label_map.setGeometry(QtCore.QRect(string_width + 30, 0, 1280, 680))



    label_energy = QLabel(main)
    label_energy.setFont(QFont("Ubuntu Mono", 15))
    label_energy.setGeometry(QtCore.QRect(left_margin + string_width + 30, 690, 1200, 200))


    stacked_widget_push_button_start_app = QPushButton('Start', main)
    stacked_widget_push_button_start_app.setGeometry(QtCore.QRect(left_margin, 0, 200, 40))
    stacked_widget_push_button_start_app.clicked.connect(on_click_start)

    stacked_widget_push_button_param = QPushButton('Parameters', main)
    stacked_widget_push_button_param.setGeometry(QtCore.QRect(left_margin + 200, 0, 200, 40))
    stacked_widget_push_button_param.clicked.connect(on_click_parameters)

    stacked_widget = QStackedWidget(main)
    stacked_widget.setGeometry(QtCore.QRect(0, 50, string_width + left_margin, main_height + 50))

    widget_start = QWidget()
    widget_parameters = QWidget()
    widget_plots = QWidget(main)
    widget_plots.setGeometry(QtCore.QRect(string_width + 100, 0, 1280, 900))
    widget_plots.setVisible(False)

    # -------------
    # WIDGET PLOTS
    l1 = QLabel(widget_plots)
    l1.setGeometry(QtCore.QRect(0, 0, 550, 450))
    px = QPixmap('tools/generation_size.png').scaled(550, 450)
    l1.setPixmap(px)

    l1 = QLabel(widget_plots)
    l1.setGeometry(QtCore.QRect(0, 450, 550, 450))
    px = QPixmap('tools/penalty_multiplier.png').scaled(550, 450)
    l1.setPixmap(px)

    l1 = QLabel(widget_plots)
    l1.setGeometry(QtCore.QRect(600, 0, 550, 450))
    px = QPixmap('tools/parent_to_child.png').scaled(550, 450)
    l1.setPixmap(px)

    l1 = QLabel(widget_plots)
    l1.setGeometry(QtCore.QRect(600, 450, 550, 450))
    px = QPixmap('tools/number_of_iterations.png').scaled(550, 450)
    l1.setPixmap(px)


    stacked_widget.addWidget(widget_start)
    stacked_widget.addWidget(widget_parameters)
    stacked_widget.setCurrentIndex(0)

    # WIDGET PARAMETERS
    label_iterations = QLabel(widget_parameters)
    label_iterations.setFont(QFont("Ubuntu Mono", label_font_size))
    label_iterations.setGeometry(QtCore.QRect(left_margin, 0, string_width, label_height))
    label_iterations.setText('Number of iterations')

    label_generation_size = QLabel(widget_parameters)
    label_generation_size.setFont(QFont("Ubuntu Mono", label_font_size))
    label_generation_size.setGeometry(QtCore.QRect(left_margin, 2 * label_height, string_width, label_height))
    label_generation_size.setText('Generation size')

    label_penalty_multiplier = QLabel(widget_parameters)
    label_penalty_multiplier.setFont(QFont("Ubuntu Mono", label_font_size))
    label_penalty_multiplier.setGeometry(QtCore.QRect(left_margin, 4 * label_height, string_width, label_height))
    label_penalty_multiplier.setText('Penalty multiplier')

    label_mutation_multiplier = QLabel(widget_parameters)
    label_mutation_multiplier.setFont(QFont("Ubuntu Mono", label_font_size))
    label_mutation_multiplier.setGeometry(QtCore.QRect(left_margin, 6 * label_height, string_width, label_height))
    label_mutation_multiplier.setText('Mutation multiplier')

    label_parent_to_child_size = QLabel(widget_parameters)
    label_parent_to_child_size.setFont(QFont("Ubuntu Mono", label_font_size))
    label_parent_to_child_size.setGeometry(QtCore.QRect(left_margin, 8 * label_height, string_width, label_height))
    label_parent_to_child_size.setText('Parent to new generation size (0-1)')

    label_min_speed = QLabel(widget_parameters)
    label_min_speed.setFont(QFont("Ubuntu Mono", label_font_size))
    label_min_speed.setGeometry(QtCore.QRect(left_margin, 10 * label_height, string_width, label_height))
    label_min_speed.setText('Minimum speed')

    label_max_speed = QLabel(widget_parameters)
    label_max_speed.setFont(QFont("Ubuntu Mono", label_font_size))
    label_max_speed.setGeometry(QtCore.QRect(left_margin, 12 * label_height, string_width, label_height))
    label_max_speed.setText('Maximum speed')

    line_edit_iterations = QLineEdit(widget_parameters)
    line_edit_iterations.setGeometry(QtCore.QRect(left_margin, label_height, string_width, label_height))

    line_edit_generation_size = QLineEdit(widget_parameters)
    line_edit_generation_size.setGeometry(QtCore.QRect(left_margin, 3 * label_height, string_width, label_height))

    line_edit_penalty_multiplier = QLineEdit(widget_parameters)
    line_edit_penalty_multiplier.setGeometry(QtCore.QRect(left_margin, 5 * label_height, string_width, label_height))

    line_edit_mutation_multiplier = QLineEdit(widget_parameters)
    line_edit_mutation_multiplier.setGeometry(QtCore.QRect(left_margin, 7 * label_height, string_width, label_height))

    line_edit_parent_to_child_size = QLineEdit(widget_parameters)
    line_edit_parent_to_child_size.setGeometry(QtCore.QRect(left_margin, 9 * label_height, string_width, label_height))

    line_edit_min_speed = QLineEdit(widget_parameters)
    line_edit_min_speed.setGeometry(QtCore.QRect(left_margin, 11 * label_height, string_width, label_height))

    line_edit_max_speed = QLineEdit(widget_parameters)
    line_edit_max_speed.setGeometry(QtCore.QRect(left_margin, 13 * label_height, string_width, label_height))

    push_button_save_parameters = QPushButton('Save', widget_parameters)
    push_button_save_parameters.setGeometry(QtCore.QRect(left_margin + 100, 14 * label_height + 10, 200, 50))
    push_button_save_parameters.clicked.connect(on_click_save)

    # WIDGET START
    label_start = QLabel(widget_start)
    label_start.setFont(QFont("Ubuntu Mono", label_font_size))
    label_start.setGeometry(QtCore.QRect(left_margin, 0, string_width, label_height))
    label_start.setText('Start')

    label_end = QLabel(widget_start)
    label_end.setFont(QFont("Ubuntu Mono", label_font_size))
    label_end.setGeometry(QtCore.QRect(left_margin, 2 * label_height, string_width, label_height))
    label_end.setText('Destination')

    label_soc = QLabel(widget_start)
    label_soc.setFont(QFont("Ubuntu Mono", label_font_size))
    label_soc.setGeometry(QtCore.QRect(left_margin, 4 * label_height, string_width, label_height))
    label_soc.setText('Starting battery SOC')

    line_edit_start = QLineEdit(widget_start)
    line_edit_start.setGeometry(QtCore.QRect(left_margin, label_height, string_width, label_height))

    line_edit_end = QLineEdit(widget_start)
    line_edit_end.setGeometry(QtCore.QRect(left_margin, 3 * label_height, string_width, label_height))

    line_edit_soc = QLineEdit(widget_start)
    line_edit_soc.setGeometry(QtCore.QRect(left_margin, 5 * label_height, string_width, label_height))

    push_button_start_app = QPushButton('Start', widget_start)
    push_button_start_app.setGeometry(QtCore.QRect(left_margin + 80, 6 * label_height + 5, 200, 30))
    push_button_start_app.clicked.connect(on_click)

    label_best_solution = QLabel(widget_start)
    label_best_solution.setFont(QFont("Ubuntu Mono", 15))
    label_best_solution.setGeometry(QtCore.QRect(left_margin, 6 * label_height + 50, string_width + 60, string_height))

    # --------------------------------
    # # CHANGED DYNAMICALLY

    # main.showFullScreen()
    main.show()
    sys.exit(app.exec_())
