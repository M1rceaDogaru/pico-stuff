import time
import random
import picodisplay as display

width = display.get_width()
height = display.get_height()

display_buffer = bytearray(width * height * 2)  # 2-bytes per pixel (RGB565)
display.init(display_buffer)

display.set_backlight(0.3)

state_menu = 0
state_game = 1
state_end = 2

class Ball:
    def __init__(self, x, y, r, dx, dy, pen):
        self.x = x
        self.y = y
        self.r = r
        self.dx = dx
        self.dy = dy
        self.pen = pen
    def collides_with(self, bar):
        touch_x = self.x >= bar.x and self.x <= bar.x + bar.w
        touch_y = self.y >= bar.y and self.y <= bar.y + bar.l
        return touch_x and touch_y

class Bar:
    def __init__(self, x, y, w, l, move_up, move_down, speed, pen):
        self.x = x
        self.y = y
        self.w = w
        self.l = l
        self.move_up = move_up
        self.move_down = move_down
        self.speed = speed
        self.pen = pen
        self.wins = 0
        
    def handle_input(self):
        if display.is_pressed(self.move_up):
            self.y -= self.speed
        elif display.is_pressed(self.move_down):
            self.y += self.speed
        
player_green = Bar(5, int(height/2)-15, 5, 30, display.BUTTON_A, display.BUTTON_B, 4, display.create_pen(0, 255, 0))
player_blue = Bar(width - 15, int(height/2)-15, 5, 30, display.BUTTON_X, display.BUTTON_Y, 4, display.create_pen(0, 0, 255))
ball = Ball(width/2, height/2, 4, 4, 4, display.create_pen(random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)))

game_state = 0
winner = 0 #1-green 2-blue
    
def do_menu():
    global game_state
    display.set_pen(255, 255, 255)
    display.rectangle(int(width/2)-1,0, 3, height)
    display.text("Press A   to start", 40, int(height/2), 300, 2)
    if display.is_pressed(display.BUTTON_A):
        print("Button pressed")
        game_state = state_game

def do_end_game():
    global game_state
    display.set_pen(255, 255, 255)
    message = "Green wins!" if winner == 1 else "Blue wins!"
    display.text(message, 40, int(height/2) - 20, 300, 3)
    if (winner == 1):
        display.set_led(0, 255, 0)
    else:
        display.set_led(0, 0, 255)
    
    if display.is_pressed(display.BUTTON_A):
        display.set_led(0, 0, 0)
        ball.x = width/2
        ball.y = height/2
        game_state = state_game

def render_game():
    display.set_pen(255, 255, 255)
    display.rectangle(int(width/2)-1,0, 3, height)
    display.text(str(player_green.wins), 50, int(height/2) - 15, 40, 4)
    display.text(str(player_blue.wins), 170, int(height/2) - 15, 40, 4)
    display.set_pen(player_green.pen)
    display.rectangle(player_green.x, player_green.y, player_green.w, player_green.l)
    display.set_pen(player_blue.pen)
    display.rectangle(player_blue.x, player_blue.y, player_blue.w, player_blue.l)
    display.set_pen(ball.pen)
    display.circle(int(ball.x), int(ball.y), int(ball.r))

def handle_input():    
    player_green.handle_input()
    player_blue.handle_input()

def move_ball():
    global winner, game_state
    
    ball.x += ball.dx
    ball.y += ball.dy

    xmax = width - ball.r
    xmin = ball.r
    ymax = height - ball.r
    ymin = ball.r     

    if ball.y < ymin or ball.y > ymax:
        ball.dy *= -1
        
    if ball.collides_with(player_green) or ball.collides_with(player_blue):
        ball.dx *= -1
    
    if ball.x < xmin:
        winner = 2
        player_blue.wins += 1
        game_state = state_end
    elif ball.x > xmax:
        winner = 1
        player_green.wins += 1
        game_state = state_end
        
def do_game():
    move_ball()
    handle_input()    
    render_game()    

while True:
    display.set_pen(40, 40, 40)
    display.clear()
    
    if game_state == state_menu:
        do_menu()
    elif game_state == state_game:
        do_game()
    elif game_state == state_end:
        do_end_game()

    display.update()
    time.sleep(0.01)
