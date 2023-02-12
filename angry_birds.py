import utime
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY
from pimoroni import Button
import math
import random
from micropython import const
import gc

display = PicoGraphics(display=DISPLAY_PICO_DISPLAY, rotate=180)
display.set_backlight(0.3)
height = const(135)
width = const(240)

delta = 0.0
last_time = utime.ticks_ms()
_pixel_skip = const(0)

button_x = Button(14)

background = display.create_pen(40, 40, 40)        
white = display.create_pen(255, 255, 255)       
red = display.create_pen(255, 0, 0)

bird = [
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0],
[0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
[0,0,0,1,1,1,1,1,1,0,0,1,1,0,0,0],
[1,1,1,1,1,1,1,1,1,0,0,1,1,1,0,0],
[0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
[0,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0],
[0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0],
[0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0],
[0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0],
[0,0,0,0,0,1,1,1,0,1,1,0,0,0,0,0],
[0,0,0,0,1,1,0,0,1,0,1,1,0,0,0,0]]

class Pixel:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Bird:
    def __init__(self, x, y, w, h, angle, pen, pixels):
        self.x = x
        self.y = y
        self.angle = angle
        self.pen = pen
        self.buffer = []
        self.velocity = 0
        
        minW = -int(w/2)
        minH = -int(h/2)
        i_counter = -1
        j_counter = -1
        for i in pixels:
            i_counter += 1
            if _pixel_skip == 0 or i_counter % _pixel_skip == 0:
                for j in i:
                    j_counter += 1
                    if j == 0:
                        continue
                    if _pixel_skip == 0 or j_counter % _pixel_skip == 0:
                        self.buffer.append(Pixel(minW + j_counter, minH + i_counter))
                j_counter = -1
    
    def render(self):
        display.set_pen(self.pen)
        rad = math.radians(self.angle)
        s = math.sin(rad)
        c = math.cos(rad)
        b = self.buffer
        x = self.x
        y = self.y
        for pixel in b:
            display.pixel(int(x + c * pixel.x - s * pixel.y), int(y + s * pixel.x + c * pixel.y))

class Obstacle:
    def __init__(self, x, y, gap, thickness, pen):
        self.x = x
        self.y = y
        self.gap = gap
        self.thickness = thickness
        self.pen = pen
    
    def render(self):
        display.set_pen(self.pen)
        display.rectangle(self.x - self.thickness, 0, self.thickness, self.y - self.gap)
        display.rectangle(self.x - self.thickness, self.y + self.gap, self.thickness, height - self.y + self.gap)        
            
bird = Bird(40, int(height/2), 16, 16, 0, red, bird)
obstacles = [
Obstacle(200, random.randint(15, 120), 20, 20, red),
Obstacle(280, random.randint(15, 120), 20, 20, red),
Obstacle(360, random.randint(15, 120), 20, 20, red) 
]

angle = 0
_gravity = const(12)
_t = const(-15)
_jv = const(-5)
_obstacle_speed = const(100)

@micropython.native
def update_obstacles():
    for obstacle in obstacles:
        obstacle.x -= int(delta * _obstacle_speed)
        print(obstacle.x)
        if obstacle.x < -20:
            obstacle.x = 260
            obstacle.y = random.randint(15, 120)

@micropython.native
def logic():
    if button_x.read():
        bird.velocity = _jv
        
    bird.velocity += _gravity * delta
    if bird.velocity < _t:
        bird.velocity = _t
        
    bird.y += bird.velocity
    if bird.y > height:
        bird.y = height
        
    if bird.velocity >= 0:
        bird.angle = bird.velocity * 3
    else:
        bird.angle = 360 + bird.velocity * 3
        
    update_obstacles()

@micropython.native    
def render():
    bird.render()
    for obstacle in obstacles:
        obstacle.render()
    display.update()    
    
@micropython.native
def main_loop():
    global last_time, delta
    new_time = utime.ticks_ms()
    delta = utime.ticks_diff(new_time, last_time)/1000
    last_time = new_time
    
    display.set_pen(background)
    display.clear()
    
    display.set_pen(white)
    display.text("FPS: " + str(int(1/delta)), 10, 10, 50, 1)
    
    logic()
    render()    
    
    #gc.collect()

while True:
    main_loop()    
