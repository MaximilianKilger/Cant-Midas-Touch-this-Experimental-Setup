import pyglet
from pyglet import shapes
from pyglet import text
import pyautogui

from controls.manual_controls import manualControls

window = pyglet.window.Window(caption="Wizard GUI", width=400, height=300)

# Farben für den Button, wenn aktiviert oder deaktiviert
color_inactive = (50, 50, 255)  # Blau für inaktiv
color_active = (255, 50, 50)   # Rot für aktiv
controls = manualControls()

# Erstelle Schaltflächen für mehrere Funktionen
buttons = {
    'stapler': {'label': 'Tacker', 'x': 100, 'y': 100, 'color': color_inactive, 'enabled': False},
    'eraser': {'label': 'Radierer', 'x': 100, 'y': 160, 'color': color_inactive, 'enabled': False}
}

def toggle_feature(feature):
    buttons[feature]['enabled'] = not buttons[feature]['enabled']
    
    # Ändere die Farbe des Buttons basierend auf dem Status
    if buttons[feature]['enabled']:
        buttons[feature]['color'] = color_active
        if feature == 'stapler':
            # Simuliere Tastenanschläge für "Kommentar hinzufügen" in Google Docs
            controls.stapler()  # Tacker, öffnet Kommentar-Dialog in Google Docs
            print("Tacker aktiviert: Kommentar-Funktion ausgelöst.")
        elif feature == 'eraser':
            controls.eraser()
            print("Radierer aktiviert: Rückgängig gemacht.")
    else:
        buttons[feature]['color'] = color_inactive

@window.event
def on_draw():
    window.clear()
    
    # Zeichne alle Buttons
    for key, value in buttons.items():
        button = shapes.Rectangle(value['x'], value['y'], 200, 50, color=value['color'])
        button.draw()
        
        # Zeichne den Text des Buttons
        label = pyglet.text.Label(value['label'], font_name='Times New Roman', font_size=14,
                                  x=value['x'] + 100, y=value['y'] + 25, anchor_x='center', anchor_y='center')
        label.draw()

@window.event
def on_mouse_press(x, y, button, modifiers):
    # Überprüfen, ob der Klick innerhalb eines Buttons liegt
    for feature, value in buttons.items():
        if value['x'] <= x <= value['x'] + 200 and value['y'] <= y <= value['y'] + 50:
            toggle_feature(feature)

pyglet.app.run()
