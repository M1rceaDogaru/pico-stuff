from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY
from pimoroni import Button
import random
import time

words = []
def prepare_words():
    for cat_index in range(0, 5):
        with open("/data/" + str(cat_index) + '.txt', 'r') as f:
            lines = f.readlines()
            words.append(lines)
            
display = PicoGraphics(display=DISPLAY_PICO_DISPLAY, rotate=180)
text_pen = display.create_pen(255, 255, 0)
background_pen = display.create_pen(0, 0, 0)
button_x = Button(14)
button_x_pressed = False

display.set_font("bitmap8")

def update_text(text):
    display.set_pen(background_pen)
    display.clear()
    display.set_pen(text_pen)
    display.text(text, 0, 0, wordwrap=230, scale=2)
    display.update()
    
update_text("Loading data...")
prepare_words()
update_text("Welcome to Corporate BS. Press X to...well, get some BS")
    
while True:
    time.sleep(0.1)
    if button_x.read() and not button_x_pressed:
        button_x_pressed = True
        text = "You "
        for cat_index in range(0, 5):
            lines = words[cat_index]
            index = random.randrange(0, len(lines))
            text += lines[index]
        update_text(text)
    else:
        button_x_pressed = False
        

        
        
