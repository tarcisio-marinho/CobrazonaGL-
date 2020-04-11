import sys
import time
import random
import os
import configparser
from PySide2.QtWidgets import QHBoxLayout, QWidget, QApplication, QVBoxLayout,  QPushButton, QLabel, QMainWindow, QOpenGLWidget
from PySide2.QtCore import *
from PySide2.QtGui import *
from OpenGL.GL import *
from typing import *


config = configparser.ConfigParser()
config.read('config.txt')

view_width: int = int(config['display']['width'])
view_height: int = int(config['display']['height'])
game_speed: int = int(config['game']['speed'])
timeout_min: int = int(config['game']['timeout_min'])
timeout_max: int = int(config['game']['timeout_max'])
timeout: int = int(config['game']['timeout'])  
object_size: int = int(config['objects']['object_size'])
snake_move: float = float(config['objects']['snake_move'])
min_apples_rate: int = int(config['objects']['apples_rate_min'])
max_apples_rate: int = int(config['objects']['apples_rate_max'])
apples_rate: List = [min_apples_rate, max_apples_rate]
apples_limit: int = int(config['objects']['apples_limit'])

apples: List[Dict[str, float]] = list()
apples_counter: int = random.randint(*apples_rate)

snake: List[Dict[str, float]] = [{'x': 0.0, 'y': 0.0}] 
snake_dir: str = random.choice(['w', 's', 'd', 'a'])  
will_snake_extend: bool = False

w_object_size: float = object_size/view_width
h_object_size: float = object_size/view_height

score: int = 0


def check_collision(
    snake_x: float,
    snake_y: float,
    objects: List[dict]
):
    # check if snake hit any obj in objects
    for obj in objects:
        obj_x: Optional[float] = obj.get('x')
        obj_y: Optional[float] = obj.get('y')
        if isinstance(obj_x, float) and isinstance(obj_y, float):
            x: float = obj_x
            y: float = obj_y
        else:
            raise ValueError

        if(abs(snake_x - x) < w_object_size * 2 and
           abs(snake_y - y) < h_object_size * 2):
            return obj
    return None


def draw_apples():
    for apple in apples:
        glVertex2f(apple.get('x'), apple.get('y'))


def draw_snake():
    global will_snake_extend, timeout, score

    def move_snake(x: float, y: float):
        # move snake in current direction
        if (snake_dir == 'w'):
            y += snake_move
        elif (snake_dir == 's'):
            y -= snake_move
        if (snake_dir == 'a'):
            x -= snake_move
        elif (snake_dir == 'd'):
            x += snake_move
        return [x, y]

    # create new head
    sn_x: Optional[float] = snake[-1].get('x')
    sn_y: Optional[float] = snake[-1].get('y')
    if (isinstance(sn_x, float) and isinstance(sn_y, float)):
        x: float = sn_x
        y: float = sn_y
    else:
        raise ValueError
    x, y = move_snake(x, y)
    snake.append({'x': x, 'y': y})

    # check whetever new head collide with some apple
    collided_apple = check_collision(x, y, apples)
    score_label.setText("Quantidade de pontos: " + str(score))
    if (collided_apple is not None):
        will_snake_extend = True
        apples.remove(collided_apple)
        score += 1

    # if snake didn't eat apple remove tail
    if (not will_snake_extend):
        del snake[0]
    else:
        timeout += random.randint(timeout_min, timeout_max)
        will_snake_extend = False

    # redraw snake body
    for snake_body in snake:
        sn_x = snake_body.get('x')
        sn_y = snake_body.get('y')
        if (isinstance(sn_x, float) and isinstance(sn_y, float)):
            x = sn_x
            y = sn_y
        else:
            raise ValueError

        glVertex2f(x, y)

def game_over(msg):
    print(msg)
    exit()
    pass

def self_colision():
    n = 0
    for part in snake:
        if(snake[0]['x'] == part['x'] and snake[0]['y'] == part['y']):
            n += 1
        if(n > 1):
            return True    
    return False

def out_of_screen():
    if(snake[0]['x'] > 1 or snake[0]['x'] < -1 or snake[0]['y'] > 1 or snake[0]['y'] < -1):
        return True
    return False

def update_scene():
    global apples_counter, timeout
    if(self_colision()):
        game_over("Você colidiu em você mesmo!")

    if(out_of_screen()):
        game_over("Você saiu da tela!")
    
    apples_counter -= 1
    timeout -= 1

    if (timeout == 0):
        game_over("O tempo acabou !")

    timeout_label.setText("Tempo restante: " + str(timeout))
    game_widget.update()


class GameWidget(QOpenGLWidget):
    def initializeGL(self):
        self.setFixedSize(QSize(view_width, view_height))
        glViewport(0, 0, view_width, view_height)

    def paintGL(self):
        global apples_counter

        glClear(GL_COLOR_BUFFER_BIT)
        glClearColor(0.59, 0.67, 0.60, 1.0)
        glPointSize(object_size)

        # check if should add new apple
        if (apples_counter <= 0 and len(apples) < apples_limit):
            apples.append({'x': random.uniform(-1, 1),
                           'y': random.uniform(-1, 1)})
            apples_counter = random.randint(*apples_rate)

        glBegin(GL_POINTS)

        # draw apples
        glColor3f(0.9, 0.2, 0.15)
        draw_apples()

        # draw snake
        glColor3f(0.0, 0.0, 0.0)
        draw_snake()

        glEnd()


class MainWindow(QWidget):
    
    def __init__(self, game_widget, score_label, timeout_label):
        super(MainWindow, self).__init__()

        self.game_widget = game_widget
        self.score_label = score_label
        self.timeout_label = timeout_label

        hor_border: int = int(config['display']['hborder'])
        ver_border: int = int(config['display']['vborder'])

        self.setFixedSize(view_width + hor_border, view_height + ver_border)
        self.setStyleSheet('background-color: #222222')
        self.autoFillBackground()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.addWidget(self.score_label)
        layout.addWidget(self.timeout_label)
        layout.addWidget(self.game_widget)
        self.setLayout(layout)

        self.show()

    def keyPressEvent(self, event):
        global snake_dir
        key: chr = chr(event.key()).lower()
        control_keys: List = ['a', 'd', 'w', 's']

        if (key in control_keys):
            if (not (control_keys.index(snake_dir) < 2 and
                     control_keys.index(key) < 2) and
                not (control_keys.index(snake_dir) > 1 and
                     control_keys.index(key) > 1)):
                # if user change dir by 90 deg
                snake_dir = key


if __name__ == "__main__":
    app = QApplication([])

    opengl_widget = QOpenGLWidget()
    opengl_widget.setFocusPolicy(Qt.StrongFocus)
    game_widget = GameWidget(opengl_widget)

    score_label = QLabel()
    score_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
    score_label.setStyleSheet('color: white')

    timeout_label = QLabel()
    timeout_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
    timeout_label.setStyleSheet('color: white')

    main_window = MainWindow(game_widget, score_label, timeout_label)

    # game updates
    timer = QTimer()
    timer.timeout.connect(update_scene)
    timer.start(100/game_speed)

    exit(app.exec_())
