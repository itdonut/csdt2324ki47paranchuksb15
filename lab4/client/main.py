"""! @brief This is the client side of the tic-tac-toe game."""

# Imports necessary libraries
import serial
import time
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
from enum import Enum

# Global constants
## The variable that is used for connect to the Arduino using UART-port
arduino = serial.Serial(port='COM3', baudrate=9600, timeout=.1)

## The variable used for set styles for the buttons
btnStyle = "QPushButton" \
           "{" \
           "border : 2px solid #00DEAD;" \
           "border-radius : 8px;" \
           "background : #252525;" \
           "font-size : 20px;" \
           "color: white;" \
           "}"

## The variable used for set styles for the score label
labelStyle = "QLabel" \
             "{" \
             "border : 2px solid #00DEAD;" \
             "border-radius : 8px;" \
             "background : #252525;" \
             "font-size : 20px;" \
             "color: white;" \
             "}"

## The variable used for set styles for the main window
mainWindowStyle = "QMainWindow" \
                  "{" \
                  "background : #252525;" \
                  "}"

## The variable used for set styles for the active button of the game mode
activeModeBtnStyle = "QPushButton" \
                     "{" \
                     "border : 2px solid red;" \
                     "border-radius : 8px;" \
                     "background : #252525;" \
                     "font-size : 20px;" \
                     "color: white;" \
                     "}"

## The variable used for set width of main window
mainWindowWidth = 500

## The variable used for set height of main window
mainWindowHeight = 500

## The variable used for set width of button of game field
fieldBtnWidth = 80

## The variable used for set height of button of game field
fieldBtnHeight = 80

## The variable used for set width of game result label
gameResultWidth = 260

## The variable used for set height of game result label
gameResultHeight = 80

## The variable used for set width of menu buttons
menuBtnWidth = 130

## The variable used for set height of menu buttons
menuBtnHeight = 80


class Response:
    """! Documentation for the Response class.

    The class used for save the data which was received from Arduino.
    """

    def __init__(self):
        """! The Response class initializer.

        Initializes the class variables with default data.
        """

        super().__init__()
        self.status = ''
        self.winner = 0
        self.winsPlayerX = 0
        self.winsPlayer0 = 0
        self.coordX = 0
        self.coordY = 0

    def print_data(self):
        """! Prints the object state.

        """

        print(' - Status:      ', self.status)
        print(' - Winner:      ', self.winner)
        print(' - WinsPlayerX: ', self.winsPlayerX)
        print(' - WinsPlayerY: ', self.winsPlayer0)
        print(' - CoordX:      ', self.coordX)
        print(' - CoordY:      ', self.coordY)
        print('')


class Action(Enum):
    """! Documentation for the Action class.

    The class used for select the action which the user did.
    """

    PUSH = 'PUSH'
    RESET = 'RESET'
    CONTINUE = 'CONTINUE'
    CHANGE_MODE = 'CHANGE_MODE'
    GET_AI_PUSH = 'GET_AI_PUSH'


class Mode(Enum):
    """! Documentation for the Mode class.

    The class used for select the mode which the user select.
    """

    PvsP = 'PvsP'
    PvsAI = 'PvsAI'
    AIvsAI = 'AIvsAI'


class Window(QMainWindow):
    """! Documentation for the Mode class.

    The class is the main class of the program. It controls user actions and communicates with Arduino.
    """

    def __init__(self):
        """! The Window class initializer.

        Initializes the class variables with default data and calls the functions which creates UI and shows it.
        """

        super().__init__()
        self.mode = Mode.PvsP  # initial
        self.action = Action.PUSH  # initial
        self.setFixedSize(mainWindowWidth, mainWindowHeight)
        self.setWindowTitle("Tic Tac Toe")
        self.setStyleSheet(mainWindowStyle)
        self.UiComponents()
        self.show()

    def UiComponents(self):
        """! The function which creates the user interface.

        Creates the game board, the info labels and the game menu.
        """

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
        """! The function which changes the style of the game mode buttons to default.

        """

        for btn in self.mode_btn_list:
            btn.setStyleSheet(btnStyle)

    def change_mode(self):
        """! The function which changes the mode of the game.

        """

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

    def reset_game_action(self):
        """! The function used for reset the game.

        """

        self.turn = 1
        self.times = 0
        self.countWinsO = 0
        self.countWinsX = 0

        self.gameResultLabel.setText("")
        self.gameScoreLabel.setText(f'X   {self.countWinsX} : {self.countWinsO}   O')

        for buttons in self.push_list:
            for button in buttons:
                button.setEnabled(True)
                button.setText("")

        config = self.generate_config(self.mode, Action.RESET)
        self.send_config(config)
        response = self.recv_config()

        if self.mode == Mode.AIvsAI:
            self.action_called()

    def continue_game_action(self):
        """! The function used for continue the game.

        """

        self.turn = 1
        self.times = 0

        self.gameResultLabel.setText("")
        self.gameScoreLabel.setText(f'X   {self.countWinsX} : {self.countWinsO}   O')

        for buttons in self.push_list:
            for button in buttons:
                button.setEnabled(True)
                button.setText("")

        config = self.generate_config(self.mode, Action.CONTINUE)
        self.send_config(config)
        response = self.recv_config()

    def action_called(self):
        """! The function called when a user set X or O.

        """

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
                        text = "O Won"
                    else:
                        text = "X Won"

                    for buttons in self.push_list:
                        for push in buttons:
                            push.setEnabled(False)

                    break

                if response.status == 'DRAW':
                    text = "Match is Draw"
                    break

                count += 1

        self.gameResultLabel.setText(text)
        self.gameScoreLabel.setText(f'X   {response.winsPlayerX} : {response.winsPlayer0}   O')

    def send_config(self, config):
        """! The function used for send the config to the Arduino.

        """

        arduino.write(config.encode(encoding='ascii'))
        time.sleep(0.05)

    def recv_config(self):
        """! The function used for receive the config from the Arduino.

        @returns The config string.
        """

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
        """! The function used for get the button which user pressed.

        @param button The pressed button by a user.

        @return 2d coordinates.
        """

        for (idx, row) in enumerate(self.push_list):
            for (idy, btn) in enumerate(row):
                if btn is button:
                    return idx, idy

    def generate_config(self, mode, action, coord_x=None, coord_y=None, turn=None):
        """! The function used for generate config.

        @param mode The current game mode.
        @param action The action user did.
        @param coord_x The coordinates of the user's push along the X axis, defaults to None.
        @param coord_y The coordinates of the user's push along the Y axis, defaults to None.
        @param turn The sign X or O, defaults to None.

        @return the generated config as a string.
        """

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
        """! The function used for parse the config which was received from Arduino.

        @param config The config string which contains important data.

        @return A object of Response class with parsed data.
        """

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
    """! Main program entry."""

    App = QApplication(sys.argv)
    window = Window()
    sys.exit(App.exec())


if __name__ == "__main__":
    main()
