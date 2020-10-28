import sys
import time
import random
import os
import configparser
from PySide2.QtWidgets import QHBoxLayout, QWidget, QApplication, QVBoxLayout,  QPushButton, QLabel, QMainWindow, QOpenGLWidget, QMessageBox
from PySide2.QtCore import *
from PySide2.QtGui import *
from OpenGL.GL import *
from typing import *
import json, pickle
import platform
from colors import BLUE,RED,WHITE,YELLOW,MAGENTA,GREEN,END

config = configparser.ConfigParser()
try:
    config.read('config.txt')
    with open('scores.txt', 'r') as f:
        top_players = eval(f.read())
except:
    print("scores or configuration file was not found")
    exit()

PLAYER_NAME = input("Digite o nome do jogador: ")

try:
    DIFICULDADE = int(input("Insira a dificuldade:\n1- Fácil\n2- Intermediário\n3- Difícil\n4- Impossível: \n"))
    DIFICULDADE = int(input("Insira a dificuldade:\n1- Fácil\n2- Intermediário\n3- Difícil\n4- Impossível: \n"))
except:
    print("Digite apenas números, saindo.")
    exit()
    
    #Game speed differs for each dificuldade.
game_speed = 2
if(DIFICULDADE == 1):
    game_speed = 2
elif(DIFICULDADE == 2):
    game_speed = 3
elif(DIFICULDADE == 3):
    game_speed = 4
elif(DIFICULDADE == 4):
    game_speed = 6
else:
    print("Dificuldade: {0} inexistente, saindo.")
    exit()

if(platform.system() == "Linux"):
    os.system("clear")
else:
    os.system("cls")

view_width = int(config['display']['width'])
view_height = int(config['display']['height'])
timeout_min = int(config['game']['timeout_min'])
timeout_max = int(config['game']['timeout_max'])
timeout = int(config['game']['timeout'])  
object_size = int(config['objects']['object_size'])
snake_move = float(config['objects']['snake_move'])
min_apples_rate = int(config['objects']['apples_rate_min'])
max_apples_rate = int(config['objects']['apples_rate_max'])
apples_rate = [min_apples_rate, max_apples_rate]
apples_limit = int(config['objects']['apples_limit'])

apples = list()
apples_counter = random.randint(*apples_rate)

snake = [{'x': 0.0, 'y': 0.0}] 
snake_dir = random.choice(['w', 's', 'd', 'a'])  
will_snake_extend = False

w_object_size = object_size/view_width
h_object_size = object_size/view_height

score = 0

class GameWidget(QOpenGLWidget):
    def initializeGL(self):
        self.setFixedSize(QSize(view_width, view_height))
        glViewport(0, 0, view_width, view_height)


    def paintGL(self):
        global apples_counter

        glClear(GL_COLOR_BUFFER_BIT)
        glClearColor(0.59, 0.67, 0.60, 1.0)
        glPointSize(object_size)

        if (apples_counter <= 0 and len(apples) < apples_limit):
            apples.append({'x': random.uniform(-1, 1),
                           'y': random.uniform(-1, 1)})
            apples_counter = random.randint(*apples_rate)

        glBegin(GL_POINTS)

        glColor3f(0.9, 0.2, 0.15) # apples
        draw_apples()

        glColor3f(0.0, 0.0, 0.0) # snake
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

    #Key press event, to move the snake.

    def keyPressEvent(self, event):
        global snake_dir
        key: chr = chr(event.key()).lower()
        control_keys: List = ['a', 'd', 'w', 's']

        if (key in control_keys):
            if (not (control_keys.index(snake_dir) < 2 and
                     control_keys.index(key) < 2) and
                not (control_keys.index(snake_dir) > 1 and
                     control_keys.index(key) > 1)):
                snake_dir = key


def check_collision(snake_x, snake_y, objects):
    for obj in objects:
        obj_x = obj.get('x')
        obj_y = obj.get('y')
        if (isinstance(obj_x, float) and isinstance(obj_y, float)):
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

#Moving snake
def move_snake(x: float, y: float):
        if (snake_dir == 'w'):
            y += snake_move
        elif (snake_dir == 's'):
            y -= snake_move
        if (snake_dir == 'a'):
            x -= snake_move
        elif (snake_dir == 'd'):
            x += snake_move
        return [x, y]

#Drawing snake
def draw_snake():
    global will_snake_extend, timeout, score

    sn_x: Optional[float] = snake[-1].get('x')
    sn_y: Optional[float] = snake[-1].get('y')
    if (isinstance(sn_x, float) and isinstance(sn_y, float)):
        x: float = sn_x
        y: float = sn_y
    else:
        raise ValueError
    x, y = move_snake(x, y)
    snake.append({'x': x, 'y': y})

    if (game_speed == 2):
        dif = "Fácil"
    elif(game_speed == 3):
        dif = "Intermediário"
    elif(game_speed == 4):
        dif = "Dificil"
    elif(game_speed == 6):
        dif = "Impossível"

    score_label.setText("Nome:{0}\nQuantidade de pontos: {1}\nDIFICULDADE: {2}".format(PLAYER_NAME, score, dif))
        
    collided_apple = check_collision(x, y, apples)
    if (collided_apple is not None):
        will_snake_extend = True
        apples.remove(collided_apple)
        score += 1

    if (not will_snake_extend):
        del snake[0]
    else:
        timeout += random.randint(timeout_min, timeout_max)
        will_snake_extend = False

    for i, snake_body in enumerate(snake):
        sn_x = snake_body.get('x')
        sn_y = snake_body.get('y')
        if (isinstance(sn_x, float) and isinstance(sn_y, float)):
            x = sn_x
            y = sn_y
        else:
            raise ValueError
        
        # COR -> PIXEL
        if(i == len(snake) -1 ):
            glColor3f(0.3, 0.3, 0.3) 
        else:
            glColor3f(0.0, 0.0, 0.0) 
        glVertex2f(x, y)
        
#Inserting score
def insert_score(name, score):
    global top_players
    top_players.append({"name":name, "score":score})            
    with open('scores.txt', 'w') as f:
        f.write(str(top_players))

# Printing top 10 scores
def print_top_10_scores():
    global top_players
    print("Pontuação: ")
    ordered = sorted(top_players, key=lambda item: item['score'], reverse=True)
    for i, player in enumerate(ordered):
        if(player['name'] == PLAYER_NAME and player['score'] == score):
            print('{0}{1} -> {2} pontuação: {3}{4}'.format(RED, i+1, player["name"], player["score"], END))
        else:
            print('{0} -> {1} pontuação: {2}'.format(i+1, player["name"], player["score"]))
        if(i == 9):
            break


def game_over(msg):
    global score
    print(msg)
    insert_score(PLAYER_NAME, score)
    print_top_10_scores()

    exit()

#Suicide
def self_colision():
    n = 0
    for part in snake:
        if(snake[0]['x'] == part['x'] and snake[0]['y'] == part['y']):
            n += 1
        if(n > 1):
            return True    
    return False

#Out of screen
def out_of_screen():
    if(snake[0]['x'] > 1 or snake[0]['x'] < -1 or snake[0]['y'] > 1 or snake[0]['y'] < -1):
        return True
    return False

#Update cenas
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

#main class
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

    timer = QTimer()
    timer.timeout.connect(update_scene)
    timer.start(100/game_speed)

    exit(app.exec_())
