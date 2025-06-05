import numpy as np
from pynput import keyboard
from controls.state_selector import StateSelector

class KeyButton(StateSelector):

    def __init__(self, keycode, toggle=True):
        self.state = 0
        self.keycode = keycode
        self.toggle = toggle
        self.pressed = False

        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

    def on_press(self, key):
        if key == self.keycode:
            if self.toggle:
                if not self.pressed: #prevents unwanted toggling through windows autorepeating key function
                    if self.state == 0:
                        self.state = 1
                    elif self.state == 1:
                        self.state = 0
            else:
                self.state = 1
        self.pressed = True

    def on_release(self, key):
        
        if key == self.keycode:
            if not self.toggle:
                self.state = 0
        self.pressed = False

    def getState(self):
        return self.state