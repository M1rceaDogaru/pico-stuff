from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY
from pimoroni import Button

class MenuItem:
    def __init__(self, name, file):
        self.name = name
        self.file = file
        
file_to_execute = ""

def main():
    global file_to_execute
    
    display = PicoGraphics(display=DISPLAY_PICO_DISPLAY, rotate=180)
    display.set_backlight(0.3)
    
    background = display.create_pen(40, 40, 40)        
    white = display.create_pen(255, 255, 255)
    red = display.create_pen(255, 0, 0)
    
    button_x = Button(14)
    button_a = Button(12)
    
    # ADD MENU ITEMS HERE
    menu_items = [
        MenuItem("Pico Bird", "pico_bird.py"),
        MenuItem("Corporate BS", "corporate_bs.py"),
        MenuItem("Blank screen", "blank.py")
    ]

    selected_item = menu_items[0]
    
    while True:
        if button_x.read():
            item_index = menu_items.index(selected_item)
            item_index += 1
            if item_index >= len(menu_items):
                item_index = 0
            selected_item = menu_items[item_index]
            
        if button_a.read():
            file_to_execute = selected_item.file
            break
        
        display.set_pen(background)
        display.clear()
        
        display.set_pen(white)
        display.text("X - Change", 10, 115, 100, 2)
        display.text("A - Run", 160, 115, 100, 2)
        
        counter = 0
        for item in menu_items:
            if item == selected_item:
                display.set_pen(red)
            else:
                display.set_pen(white)
            display.text(item.name, 10, 10 + counter * 20, 220, 2)
            counter += 1
            
        display.update()

main()
if file_to_execute != "":
    exec(open(file_to_execute).read())