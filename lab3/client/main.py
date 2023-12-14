import serial
import time
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
from enum import Enum

arduino = serial.Serial(port='COM3', baudrate=9600, timeout=.1)

btnStyle = "QPushButton" \
           "{" \
           "border : 2px solid #00DEAD;" \
           "border-radius : 8px;" \
           "background : #252525;" \
           "font-size : 20px;" \
           "color: white;" \
           "}"

labelStyle = "QLabel" \
             "{" \
             "border : 2px solid #00DEAD;" \
             "border-radius : 8px;" \
             "background : #252525;" \
             "font-size : 20px;" \
             "color: white;" \
             "}"

mainWindowStyle = "QMainWindow" \
                  "{" \
                  "background : #252525;" \
                  "}"

activeModeBtnStyle = "QPushButton" \
                     "{" \
                     "border : 2px solid red;" \
                     "border-radius : 8px;" \
                     "background : #252525;" \
                     "font-size : 20px;" \
                     "color: white;" \
                     "}"

mainWindowWidth = 500
mainWindowHeight = 500
fieldBtnWidth = 80
fieldBtnHeight = 80
gameResultWidth = 260
gameResultHeight = 80
menuBtnWidth = 130
menuBtnHeight = 80


class Response:
    def __init__(self):
        super().__init__()
        self.status = ''
        self.winner = 0
        self.winsPlayerX = 0
        self.winsPlayer0 = 0
        self.coordX = 0
        self.coordY = 0

    def print_data(self):
        print(' - Status:      ', self.status)
        print(' - Winner:      ', self.winner)
        print(' - WinsPlayerX: ', self.winsPlayerX)
        print(' - WinsPlayerY: ', self.winsPlayer0)
        print(' - CoordX:      ', self.coordX)
        print(' - CoordY:      ', self.coordY)
        print('')


class Action(Enum):
    PUSH = 'PUSH'
    RESET = 'RESET'
    CONTINUE = 'CONTINUE'
    CHANGE_MODE = 'CHANGE_MODE'
    GET_AI_PUSH = 'GET_AI_PUSH'


class Mode(Enum):
    PvsP = 'PvsP'
    PvsAI = 'PvsAI'
    AIvsAI = 'AIvsAI'


class Window(QMainWindow):
    # constructor
    def __init__(self):
        super().__init__()
        self.mode = Mode.PvsP  # initial
        self.action = Action.PUSH  # initial
        self.setFixedSize(mainWindowWidth, mainWindowHeight)
        self.setWindowTitle("Tic Tac Toe")
        self.setStyleSheet(mainWindowStyle)
        self.UiComponents()
        self.show()

    def UiComponents(self):

        # turn
        self.turn = 1

        # times
        self.times = 0

        self.countWinsX = 0
        self.countWinsO = 0

        # creating a push button list
        self.push_list = []

        # creating 2d list
        for _ in range(3):
            temp = []
            for _ in range(3):
                btn = QPushButton(self)
                btn.setStyleSheet(btnStyle)
                temp.append(btn)
            # adding 3 push button in single row
            self.push_list.append(temp)

        # x and y co-ordinate
        x = 90
        y = 90

        # traversing through push button list
        for i in range(3):
            for j in range(3):
                # setting geometry to the button
                self.push_list[i][j].setGeometry(x * i + 20,
                                                 y * j + 20,
                                                 fieldBtnWidth, fieldBtnHeight)

                # setting font to the button
                self.push_list[i][j].setFont(QFont(QFont('Times', 20)))

                # adding action
                self.push_list[i][j].clicked.connect(self.action_called)

        # creating label to tell the game result
        self.gameResultLabel = QLabel(self)
        self.gameResultLabel.setGeometry(20, 290, gameResultWidth, gameResultHeight)
        self.gameResultLabel.setAlignment(Qt.AlignCenter)
        self.gameResultLabel.setFont(QFont('Times', 15))
        self.gameResultLabel.setStyleSheet(labelStyle)

        # creating label to tell the score
        self.gameScoreLabel = QLabel(self)
        self.gameScoreLabel.setGeometry(20, 380, gameResultWidth, gameResultHeight)
        self.gameScoreLabel.setAlignment(Qt.AlignCenter)
        self.gameScoreLabel.setFont(QFont('Times', 15))
        self.gameScoreLabel.setStyleSheet(labelStyle)
        self.gameScoreLabel.setText(f'X   {self.countWinsX} : {self.countWinsO}   O')

        # create checkboxes
        self.gameModeBtnPvsP = QPushButton("P vs. P", self)
        self.gameModeBtnPvsP.setGeometry(350, 20, menuBtnWidth, menuBtnHeight)
        self.gameModeBtnPvsP.setStyleSheet(activeModeBtnStyle)
        self.gameModeBtnPvsP.clicked.connect(self.change_mode)
        self.gameModeBtnPvsP.setProperty('value', Mode.PvsP.value)
        self.gameModeBtnPvsAI = QPushButton("P vs. AI", self)
        self.gameModeBtnPvsAI.setGeometry(350, 110, menuBtnWidth, menuBtnHeight)
        self.gameModeBtnPvsAI.setStyleSheet(btnStyle)
        self.gameModeBtnPvsAI.clicked.connect(self.change_mode)
        self.gameModeBtnPvsAI.setProperty('value', Mode.PvsAI.value)
        self.gameModeBtnAIvsAI = QPushButton("AI vs. AI", self)
        self.gameModeBtnAIvsAI.setGeometry(350, 200, menuBtnWidth, menuBtnHeight)
        self.gameModeBtnAIvsAI.setStyleSheet(btnStyle)
        self.gameModeBtnAIvsAI.clicked.connect(self.change_mode)
        self.gameModeBtnAIvsAI.setProperty('value', Mode.AIvsAI.value)
        self.continueGameBtn = QPushButton("Continue", self)
        self.continueGameBtn.setGeometry(350, 290, menuBtnWidth, menuBtnHeight)
        self.continueGameBtn.setStyleSheet(btnStyle)
        self.continueGameBtn.clicked.connect(self.continue_game_action)
        self.resetGameBtn = QPushButton("Reset", self)
        self.resetGameBtn.setGeometry(350, 380, menuBtnWidth, menuBtnHeight)
        self.resetGameBtn.setStyleSheet(btnStyle)
        self.resetGameBtn.clicked.connect(self.reset_game_action)

        self.mode_btn_list = [self.gameModeBtnPvsP, self.gameModeBtnPvsAI, self.gameModeBtnAIvsAI]

    def reset_mode_btns_style(self):
        for btn in self.mode_btn_list:
            btn.setStyleSheet(btnStyle)

    def change_mode(self):
        button = self.sender()
        for btn in self.mode_btn_list:
            if btn is button:
                if self.mode.value != btn.property('value'):
                    self.reset_mode_btns_style()
                    btn.setStyleSheet(activeModeBtnStyle)
                    if btn.property('value') == 'PvsP':
                        self.mode = Mode.PvsP
                    if btn.property('value') == 'PvsAI':
                        self.mode = Mode.PvsAI
                    if btn.property('value') == 'AIvsAI':
                        self.mode = Mode.AIvsAI

        self.reset_game_action()

    # method called by reset button
    def reset_game_action(self):
        # resetting values
        self.turn = 1
        self.times = 0
        self.countWinsO = 0
        self.countWinsX = 0

        # making label text empty:
        self.gameResultLabel.setText("")
        self.gameScoreLabel.setText(f'X   {self.countWinsX} : {self.countWinsO}   O')

        # traversing push list
        for buttons in self.push_list:
            for button in buttons:
                # making all the button enabled
                button.setEnabled(True)
                # removing text of all the buttons
                button.setText("")

        config = self.generate_config(self.mode, Action.RESET)
        self.send_config(config)
        response = self.recv_config()

        if self.mode == Mode.AIvsAI:
            self.action_called()

    def continue_game_action(self):
        # resetting values
        self.turn = 1
        self.times = 0

        # making label text empty:
        self.gameResultLabel.setText("")
        self.gameScoreLabel.setText(f'X   {self.countWinsX} : {self.countWinsO}   O')

        # traversing push list
        for buttons in self.push_list:
            for button in buttons:
                # making all the button enabled
                button.setEnabled(True)
                # removing text of all the buttons
                button.setText("")

        config = self.generate_config(self.mode, Action.CONTINUE)
        self.send_config(config)
        response = self.recv_config()

    # action called by the push buttons
    def action_called(self):

        self.times += 1
        text = ""
        response = None
        button = None

        if self.mode != Mode.AIvsAI:
            button = self.sender()
            coord_x, coord_y = self.get_coords(button)
            config = self.generate_config(self.mode, Action.PUSH, coord_x=coord_x, coord_y=coord_y, turn=self.turn)
            self.send_config(config)
            new_config = self.recv_config()
            response = self.parse(new_config)

        if self.mode == Mode.PvsP:
            if response.status == 'IN_PROCESS':
                # making button disabled
                button.setEnabled(False)
                # checking the turn
                if self.turn == 1:
                    button.setText("X")
                    self.turn = 0
                else:
                    button.setText("O")
                    self.turn = 1

            if response.status == 'END':
                if response.winner == 0:
                    # O has won
                    button.setText("O")
                    text = "O Won"
                # X has won
                else:
                    button.setText("X")
                    text = "X Won"

                # disabling all the buttons
                for buttons in self.push_list:
                    for push in buttons:
                        push.setEnabled(False)

            if response.status == 'DRAW':
                text = "Match is Draw"

        if self.mode == Mode.PvsAI:
            if response.status == 'IN_PROCESS':
                # making button disabled
                button.setEnabled(False)
                button.setText("X")

                config = self.generate_config(self.mode, Action.GET_AI_PUSH)
                self.send_config(config)
                new_config = self.recv_config()
                response = self.parse(new_config)
                time.sleep(1)
                ai_button = self.push_list[response.coordX][response.coordY]
                ai_button.setText("0")
                ai_button.setEnabled(False)

            if response.status == 'END':
                if response.winner == 0:
                    # O has won
                    button.setText("X")
                    text = "O Won"
                # X has won
                else:
                    button.setText("O")
                    text = "X Won"

                # disabling all the buttons
                for buttons in self.push_list:
                    for push in buttons:
                        push.setEnabled(False)

            if response.status == 'DRAW':
                text = "Match is Draw"

        if self.mode == Mode.AIvsAI:

            count = 0

            while True:
                time.sleep(1)
                config = self.generate_config(self.mode, Action.GET_AI_PUSH)
                self.send_config(config)
                new_config = self.recv_config()
                response = self.parse(new_config)

                if response.status == 'IN_PROCESS' or response.status == 'END':
                    ai_button = self.push_list[response.coordX][response.coordY]
                    time.sleep(1)
                    if count % 2 == 0:
                        ai_button.setText("X")
                        ai_button.setEnabled(False)
                    else:
                        ai_button.setText("0")
                        ai_button.setEnabled(False)

                if response.status == 'END':
                    if response.winner == 0:
                        # O has won
                        text = "O Won"
                    # X has won
                    else:
                        text = "X Won"

                    # disabling all the buttons
                    for buttons in self.push_list:
                        for push in buttons:
                            push.setEnabled(False)

                    break

                if response.status == 'DRAW':
                    text = "Match is Draw"
                    break

                count += 1

        # setting text to the label
        self.gameResultLabel.setText(text)
        self.gameScoreLabel.setText(f'X   {response.winsPlayerX} : {response.winsPlayer0}   O')

    def send_config(self, config):
        arduino.write(config.encode(encoding='ascii'))
        time.sleep(0.05)

    def recv_config(self):
        data = ''
        while True:
            response = arduino.readline()
            if response != b'':
                data += response.decode()

            if ';' in data:
                break

        data = data.replace('\r\n', '')
        data = data.replace('b\'', '')
        data = data.replace('\'', '')
        data = data.replace(';', '')

        return data

    def get_coords(self, button):
        for (idx, row) in enumerate(self.push_list):
            for (idy, btn) in enumerate(row):
                if btn is button:
                    return idx, idy

    def generate_config(self, mode, action, coord_x=None, coord_y=None, turn=None):
        config = ''
        config += 'mode=' + mode.value + '\n'
        config += 'action=' + action.value + '\n'
        if (mode == Mode.PvsP or mode == Mode.PvsAI) and action == Action.PUSH:
            config += 'coordX=' + str(coord_x) + '\n'
            config += 'coordY=' + str(coord_y) + '\n'
            config += 'turn=' + str(turn) + '\n'

        config += ';'
        return config

    def parse(self, config):
        splitByNewLine = config.split('\n')
        key_val_list = []
        for value in splitByNewLine:
            key_val_list.append(value.split('='))

        response = Response()
        for key_val in key_val_list:
            if key_val[0] == 'status':
                response.status = key_val[1]
            if key_val[0] == 'winner':
                response.winner = int(key_val[1])
            if key_val[0] == 'winsPlayerX':
                response.winsPlayerX = int(key_val[1])
            if key_val[0] == 'winsPlayer0':
                response.winsPlayer0 = int(key_val[1])
            if key_val[0] == 'coordX':
                response.coordX = int(key_val[1])
            if key_val[0] == 'coordY':
                response.coordY = int(key_val[1])

        return response


def main():
    App = QApplication(sys.argv)
    window = Window()
    sys.exit(App.exec())


if __name__ == "__main__":
    main()
