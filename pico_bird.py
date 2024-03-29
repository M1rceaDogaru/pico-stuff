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
button_a = Button(12)

# Pens for drawing in color
background = display.create_pen(135, 206, 235)        
white = display.create_pen(20, 20, 20)       
red = display.create_pen(255, 0, 0)
dark_green = display.create_pen(34, 139, 34)
light_green = display.create_pen(124, 252, 0)

bird_sprite = [
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
        self.w = w
        self.h = h
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
        self.cleared = False
    
    def render(self):
        display.set_pen(self.pen)
        display.rectangle(self.x - self.thickness, 0, self.thickness, self.y - self.gap)
        display.rectangle(self.x - self.thickness, self.y + self.gap, self.thickness, height - self.y + self.gap)
        
    def is_collided(self, x, y):
        anchor_x = self.x - self.thickness
        collides_horizontally = x > anchor_x and x < anchor_x + self.thickness
        
        return (collides_horizontally and y < self.y - self.gap) or (collides_horizontally and y > self.y + self.gap)
        
class Tree:
    def __init__(self, x, w, pen):
        self.x = x
        self.pen = pen
        self.width = w
        self.reset_height()
    
    def render(self):
        display.set_pen(self.pen)
        display.rectangle(self.x, self.height, self.width, 135 - self.height)
        
    def reset_height(self):
        self.height = random.randint(40, 100)
            
bird = {}
obstacles = []
trees = []

for tree_index in range(0, 9):
    trees.append(Tree(int(tree_index * 30), 30, light_green))

angle = 0
_gravity = const(12)
_t = const(-15)
_jv = const(-5)
_obstacle_speed = const(100)
_background_speed = const(60)

_state_main = const(1)
_state_running = const(2)
_state_end = const(3)
_hi_score_filename = const("pico_bird_hi_score.txt")

score = 0
hi_score = 0
has_hi_score = False

lives = 3
game_state = _state_main

def read_hi_score():
    global hi_score
    
    try:
        hi_score_file = open(_hi_score_filename, "r")
        hi_score_raw = hi_score_file.read()
        if hi_score_raw != "":
            hi_score = int(hi_score_raw)
        hi_score_file.close()
    except OSError:
        pass
        
def write_hi_score():
    global hi_score
    if score < hi_score:
        return
    
    hi_score = score
    hi_score_file = open(_hi_score_filename, "w")
    hi_score_file.write(str(hi_score))
    hi_score_file.close()

@micropython.native
def start_game():
    global bird, obstacles, game_state, score, lives
    
    bird = Bird(40, int(height/2), 16, 16, 0, red, bird_sprite)
    
    obstacles = [
        Obstacle(200, random.randint(15, 120), 20, 20, dark_green),
        Obstacle(280, random.randint(15, 120), 20, 20, dark_green),
        Obstacle(360, random.randint(15, 120), 20, 20, dark_green) 
    ]
    
    if lives == 0:
        score = 0
        lives = 3
        
    game_state = _state_running
   
@micropython.native
def end_game():
    global lives, game_state, has_hi_score
    lives -= 1
    if lives == 0:
        has_hi_score = score > hi_score
        write_hi_score()
    
    game_state = _state_end
    
@micropython.native
def render_lives():
    if lives == 0:
        return
    
    display.set_pen(red)
    center_y = 10
    for life in range(lives):
        center_x = 10 + life * 12
        display.triangle(center_x - 5, center_y - 5, center_x + 5, center_y - 5, center_x, center_y + 5)

@micropython.native
def render_hi_score():
    display.set_pen(white)
    display.text("HI: " + str(hi_score), 5, 120, 100, 2)

@micropython.native
def update_obstacles():
    global score, game_state
    
    bird_anchor_x = bird.x + (bird.w / 2)
    bird_anchor_y = bird.y + (bird.h / 2)
    
    for obstacle in obstacles:
        obstacle.x -= int(delta * _obstacle_speed)
        if obstacle.is_collided(bird.x, bird.y):
            end_game()
            break
        
        if not obstacle.cleared and bird.x > obstacle.x:
            obstacle.cleared = True
            score += 1            
        
        if obstacle.x < -20:
            obstacle.x = 260
            obstacle.y = random.randint(15, 120)
            obstacle.cleared = False

@micropython.native
def update_trees():
    for tree in trees:
        tree.x -= int(delta * _background_speed)
        if tree.x <= -30:
            tree.x = 240 + (tree.x + 30)
            tree.reset_height()

@micropython.native
def run_logic():
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
        
    update_trees()
    update_obstacles()

@micropython.native    
def run_render():
    for tree in trees:
        tree.render()
    
    for obstacle in obstacles:
        obstacle.render()
    
    bird.render()
        
    display.set_pen(white)
    #display.text("FPS: " + str(int(1/delta)), 10, 10, 50, 1)
    display.text("Score: " + str(score), 140, 2, 100, 2)
    
    render_lives()
    render_hi_score()
    
    display.update()    
    
@micropython.native
def main_logic():
    if button_a.read():
        start_game()

@micropython.native
def main_render():
    for tree in trees:
        tree.render()
        
    display.set_pen(white)
    display.text("PICO BIRD", 60, 30, 130, 3)
    display.text("A - Start", 80, 80, 130, 2)
    render_hi_score()
    
    display.update()

@micropython.native
def end_logic():
    if button_a.read():
        start_game()

@micropython.native
def end_render():
    for tree in trees:
        tree.render()
    for obstacle in obstacles:
        obstacle.render()
    
    bird.render()
    
    display.set_pen(white)
    if lives == 0:
        display.text("Game over", 80, 15, 130, 3)
        if has_hi_score == True:
            display.text("NEW HI: " + str(score), 40, 70, 180, 3)
        else:
            display.text("Score: " + str(score), 60, 70, 180, 3)            
        display.text("A - Restart", 70, 100, 130, 2)
    else:
        display.text(str(lives) + " lives left", 30, 15, 200, 3)
        display.text("Score: " + str(score), 60, 70, 180, 3)
        display.text("A - Continue", 70, 100, 130, 2)
        
    render_hi_score()    
    display.update()
        
@micropython.native
def main_loop():
    global last_time, delta
    new_time = utime.ticks_ms()
    delta = utime.ticks_diff(new_time, last_time)/1000
    last_time = new_time
    
    display.set_pen(background)
    display.clear()
    
    if game_state == _state_running:
        run_logic()
        run_render()
    elif game_state == _state_main:
        main_logic()
        main_render()
    else:
        end_logic()
        end_render()
    
    #gc.collect()

read_hi_score()
while True:
    main_loop()    