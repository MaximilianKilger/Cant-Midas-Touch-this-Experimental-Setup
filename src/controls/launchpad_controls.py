import sys
import time
import pyautogui
import pygame.midi
import launchpad_py as launchpad
from .manual_controls import manualControls
from .finger_slider_2d import FingerSlider2d
from .rotation_valuator import RotationValuator
from .marker_visibility import MarkerVisibility

lp = launchpad.Launchpad()

class launchpadControls():
    active_map = [
        (0, 8),
        (1, 8),
        (2, 8),
        (3, 8),
        (4, 8),
        (5, 8),
        (6, 8),
        (7, 8)
    ]
    
    # keeps track of the state of different buttons, i.e. whether they are active or inactive.
    button_states = {}
    all_functions_active = False 

    # @param function_map: dictionary mapping launchpad button indices to an associated opportunistic control
    def __init__(self, function_map):

        self.function_map = function_map

    # clutches a tangible associated with a button.
    # Also toggles the LED of that button for visual feedback.
    def toggle_function(self, x, y, pressed):
        if pressed: # only act on buttonDown events, not when it is released
            if (x, y) not in self.button_states or not self.button_states[(x, y)]:
                print(f"Button aktiviert (LED an): ({x}, {y})")
                lp.LedCtrlXY(x, y, 0, 3) # activate LED
                self.button_states[(x, y)] = True # internally mark button as active
                for i in range(1,3):
                    if (x, y - i) in self.function_map.keys():
                        self.function_map[(x, y - i)].activate() # find all controls mapped to a button in the same column and activate them
                    print("Funktion aktiviert!")
            else:
                print(f"Button deaktiviert (LED aus): ({x}, {y})")
                lp.LedCtrlXY(x, y, 0, 0)  #turn LED off
                self.button_states[(x, y)] = False # internally mark button as inactive
                for i in range(1,3) :
                    if (x, y - i) in self.function_map.keys():
                        self.function_map[(x, y - i)].deactivate() # find all controls mapped to a button in the same column and deactivate them
                    print("Funktion deaktiviert!")
    
    # does the same as toggle_function to all buttons and controls on the launchpad
    def toggle_all_functions(self, pressed):
        if pressed:
            if not self.all_functions_active:
                
                for coord, func in self.function_map.items():
                    func.activate()
                    if not self.button_states.get((coord[0], 8), False):  
                        
                        lp.LedCtrlXY(coord[0], 8, 0, 3)  
                        self.button_states[(coord[0], 8)] = True
                self.all_functions_active = True
                print("Alle Funktionen wurden aktiviert")
            else:
                for coord, func in self.function_map.items():
                    func.deactivate()
                    if self.button_states.get((coord[0], 8), False):  
                        
                        lp.LedCtrlXY(coord[0], 8, 0, 0)  
                        self.button_states[(coord[0], 8)] = False
                self.all_functions_active = False
                print("Alle Funktionen wurden deaktiviert")

    # triggers the function of a manualControl associated with a certain button.
    def execute_function(self, x, y, pressed):
        if pressed and (x, y) in self.function_map:
            try:
                print(f"Execute function for button ({x}, {y})")
                self.function_map[(x, y)].trigger()
            except Exception as e:
                print(f"Error while executing function for ({x}, {y}): {e}")
                raise

    # handles manual clutching
    def activate_colors(self, x, y, pressed):
        if (x, y) == (8, 8):
            self.toggle_all_functions(pressed)
        elif (x, y) in self.active_map:
            self.toggle_function(x, y, pressed)

    # main loop. processes input from the launchpad
    def update(self):
        # establish contact to the Launchpad
        pygame.midi.init()
        output_id = pygame.midi.get_default_output_id()
        if output_id == -1:
            print("Kein MIDI-Ausgang verfügbar")
        else:
            print("MIDI-Ausgang gefunden:", output_id)
            print("Start Launchpad")

        if not launchpad.Launchpad().Check(0):
            print("Kein Launchpad gefunden")
            return
        
        if not lp.Open(0):
            print("Fehler beim Starten des Launchpads")
            return
        
        print("Launchpad erfolgreich gestartet")
        time.sleep(3)

        # switch all LEDs off
        lp.LedAllOn(0)
        self.running = True
        while self.running:
            # get latest button event
            buttons = lp.ButtonStateXY()
                
            if buttons != []:
                x, y, pressed = buttons[0], buttons[1], buttons[2]

                self.execute_function(x, y, pressed)
                self.activate_colors(x, y, pressed)

    def stop(self):
        self.running = False
