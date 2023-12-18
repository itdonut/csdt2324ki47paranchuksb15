import time

from pytestqt.qt_compat import qt_api

import main
import pytestqt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


def test_UiComponents(qtbot):
    widget = main.Window()
    assert check_ui(widget) == True


def test_reset_mode_btns_style(qtbot):
    widget = main.Window()
    widget.reset_mode_btns_style()
    assert check_reset_style(widget) == True


def test_change_mode_1(qtbot):
    widget = main.Window()
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.gameModeBtnPvsAI, qt_api.QtCore.Qt.MouseButton.LeftButton)
    assert widget.mode == main.Mode.PvsAI


def test_change_mode_2(qtbot):
    widget = main.Window()
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.gameModeBtnAIvsAI, qt_api.QtCore.Qt.MouseButton.LeftButton)
    assert widget.mode == main.Mode.AIvsAI


def test_change_mode_3(qtbot):
    widget = main.Window()
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.gameModeBtnPvsP, qt_api.QtCore.Qt.MouseButton.LeftButton)
    assert widget.mode == main.Mode.PvsP


def test_reset_game_action(qtbot):
    widget = main.Window()
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.resetGameBtn, qt_api.QtCore.Qt.MouseButton.LeftButton)
    assert check_reset_action(widget) == True


def test_continue_game_action(qtbot):
    widget = main.Window()
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.continueGameBtn, qt_api.QtCore.Qt.MouseButton.LeftButton)
    assert check_continue_action(widget) == True


def test_action_called(qtbot):
    widget = main.Window()
    qtbot.addWidget(widget)
    btnX = widget.push_list[0][0]
    btnO = widget.push_list[0][1]
    qtbot.mouseClick(btnX, qt_api.QtCore.Qt.MouseButton.LeftButton)
    qtbot.mouseClick(btnO, qt_api.QtCore.Qt.MouseButton.LeftButton)
    assert widget.push_list[0][0].text() == 'X' and widget.push_list[0][1].text() == 'O'


def test_get_coords(qtbot):
    widget = main.Window()
    btn = widget.push_list[0][0]
    x, y = widget.get_coords(btn)
    assert x == 0 and y == 0


def test_generate_config(qtbot):
    widget = main.Window()
    config = widget.generate_config(main.Mode.PvsP, main.Action.PUSH, 1, 1, 1)
    assert config == 'mode=PvsP\naction=PUSH\ncoordX=1\ncoordY=1\nturn=1\n;'


def test_parse(qtbot):
    widget = main.Window()

    expected_response = main.Response()
    expected_response.status = 'IN_PROCESS'
    expected_response.winner = 0
    expected_response.coordY = 0
    expected_response.coordX = 0
    expected_response.winsPlayerX = 0
    expected_response.winsPlayer0 = 0

    config = 'status=IN_PROCESS\nwinner=0\ncoordX=0\ncoordY=0\nwinsPlayerX=0\nwinsPlayer0=0\n;'
    response = widget.parse(config)
    assert check_parse(response, expected_response) == True


def check_ui(widget):
    if len(widget.push_list) != 0 and \
            widget.gameResultLabel is not None and \
            widget.gameScoreLabel is not None and \
            widget.gameModeBtnPvsP is not None and \
            widget.gameModeBtnAIvsAI is not None and \
            widget.gameModeBtnPvsAI is not None and \
            widget.continueGameBtn is not None and \
            widget.resetGameBtn is not None:
        return True
    else:
        return False


def check_reset_style(widget):
    test_btn = QPushButton()
    test_btn.setStyleSheet(main.btnStyle)
    if f'{widget.gameModeBtnPvsAI.styleSheet()}' == f'{test_btn.styleSheet()}' and \
            f'{widget.gameModeBtnAIvsAI.styleSheet()}' == f'{test_btn.styleSheet()}' and \
            f'{widget.gameModeBtnPvsP.styleSheet()}' == f'{test_btn.styleSheet()}':
        return True
    else:
        return False


def check_reset_action(widget):
    if widget.turn != 1 or \
            widget.times != 0 or \
            widget.countWinsO != 0 or \
            widget.countWinsX != 0 or \
            widget.gameResultLabel.text() != "" or \
            widget.gameScoreLabel.text() != 'X   0 : 0   O':
        return False

    for buttons in widget.push_list:
        for button in buttons:
            if button.text() != "":
                return False

    return True


def check_continue_action(widget):
    if widget.turn != 1 or \
            widget.times != 0 or \
            widget.gameResultLabel.text() != "" or \
            widget.gameScoreLabel.text() != f'X   {widget.countWinsX} : {widget.countWinsO}   O':
        return False

    for buttons in widget.push_list:
        for button in buttons:
            if button.text() != "":
                return False

    return True


def check_parse(response, expected):
    if response.status != expected.status:
        return False
    if response.winner != expected.winner:
        return False
    if response.winsPlayer0 != expected.winsPlayer0:
        return False
    if response.winsPlayerX != expected.winsPlayerX:
        return False
    if response.coordY != expected.coordY:
        return False
    if response.coordX != expected.coordX:
        return False

    return True
