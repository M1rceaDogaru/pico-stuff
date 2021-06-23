import utime
import picodisplay as display
import math

width = display.get_width()
height = display.get_height()

display_buffer = bytearray(width * height * 2)  # 2-bytes per pixel (RGB565)
display.init(display_buffer)

display.set_backlight(0.3)

delta = 0.0
last_time = utime.ticks_ms()
pixel_skip = 3

class Pixel:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Sprite:
    def __init__(self, x, y, w, h, angle, pen):
        self.x = x
        self.y = y
        self.angle = angle
        self.pen = pen
        self.buffer = []
        
        minW = -int(w/2)
        minH = -int(h/2)
        for i in range(w):
            if i % pixel_skip == 0:
                for j in range(h):
                    if j % pixel_skip == 0:
                        self.buffer.append(Pixel(minW + i, minH + j))     
    
    def render(self):
        display.set_pen(self.pen)
        rad = math.radians(self.angle)
        s = math.sin(rad)
        c = math.cos(rad)
        for pixel in self.buffer:
            display.pixel(int(self.x + c * pixel.x - s * pixel.y), int(self.y + s * pixel.x + c * pixel.y))           
            
sprite = Sprite(int(width/2), int(height/2), 80, 32, 0, display.create_pen(255, 0 ,0))
angle = 0
x = int(width/2)
while True:
    new_time = utime.ticks_ms()
    delta = utime.ticks_diff(new_time, last_time)/1000
    last_time = new_time
    
    display.set_pen(40, 40, 40)
    display.clear()
    
    display.set_pen(255, 255, 255)
    display.text("FPS: " + str(int(1/delta)), 10, 10, 50, 1)
    
    x -= 30 * delta
    if x < 30:
       x = 200 
    
    angle += 50 * delta
    if angle > 360:
        angle -= 360
    
    sprite.angle = angle
    sprite.x = x
    sprite.render()

    display.update()

