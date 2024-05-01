import turtle
import random
import time
from functools import partial

# there are several global variables
g_screen = None
g_snake = None     # snake's head
g_monster = []
g_original_snake_sz = g_snake_sz = 6  # size of the snake
g_intro = None
g_key_pressed = None
g_status = None
g_pause = False # whether the snake is paused
g_eaten_food = []
g_number_of_monsters = 4
g_game_running = True
g_food = {}
g_food_number = 5
g_previous_key_pressed = None
g_contact_count = 0
g_start_time = time.time()


COLOR_BODY = ("blue", "black")
COLOR_HEAD = "red"
COLOR_MONSTER = "purple"
FONT_INTRO = ("Arial",14,"normal")
FONT_STATUS = ("Arial",20,"normal")
TIMER_SNAKE = 200  # refresh rate for snake
SZ_SQUARE = 20      # square size in pixels

DIM_PLAY_AREA = 500
DIM_STAT_AREA = 40 # size of status area
DIM_MARGIN = 30

KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_SPACE = \
       "Up", "Down", "Left", "Right", "space"

HEADING_BY_KEY = {KEY_UP:90, KEY_DOWN:270, KEY_LEFT:180, KEY_RIGHT:0, KEY_SPACE: True}

# to create a square turtle
def create_turtle(x, y, color="red", border="black"):
    t = turtle.Turtle("square")
    t.color(border, color)
    t.up()
    t.goto(x,y)
    return t

# to configure the play area
def configure_play_area():
    # motion border
    m = create_turtle(0,0,"","black")
    sz = DIM_PLAY_AREA//SZ_SQUARE #25
    m.shapesize(sz, sz, 3)
    m.goto(0,-DIM_STAT_AREA//2)  # shift down half the status

    # status border
    s = create_turtle(0,0,"","black")
    sz_w, sz_h = DIM_STAT_AREA//SZ_SQUARE, DIM_PLAY_AREA//SZ_SQUARE
    s.shapesize(sz_w, sz_h, 3)
    s.goto(0,DIM_PLAY_AREA//2)  # shift up half the motion

    # turtle to write introduction
    intro = create_turtle(-200,0)
    intro.hideturtle()
    intro.write("Snake By Lambert\n\n" + \
                "Use arrow keys to control the snake.\n\n" + \
                "Click anywhere to start, have fun!!!\n\n",  \
                font=FONT_INTRO)

    # turtle to write status
    status = create_turtle(0,0,"","black")
    status.hideturtle()
    status.goto(-200,s.ycor()-15)

    return intro, status

# to configure the screen
def configure_screen():
    s = turtle.Screen()
    s.tracer(0)    # disable auto screen refresh, 0=disable, 1=enable
    s.title("Snake by Lambert")
    w = DIM_PLAY_AREA + DIM_MARGIN*2
    h = DIM_PLAY_AREA + DIM_MARGIN*2 + DIM_STAT_AREA
    s.setup(w, h)
    s.mode("standard")

    return s

# to update the status
def update_status():
    global g_start_time
    g_elapsed_time = time.time() - g_start_time
    g_status.clear()
    status = f'Contact: {g_contact_count}   Time: {int(g_elapsed_time)}   Motion: {g_key_pressed} '
    g_status.write(status, font=FONT_STATUS)
    g_screen.update()

# to get the pressed key
def on_arrow_key_pressed(key):
    global g_key_pressed
    g_key_pressed = key
    update_status() # update the status according to the pressed key

# to move the snake
def on_timer_snake():
    global g_pause, g_key_pressed, g_start_time

    # check whether the game is running
    if not g_game_running:
        return
    
    # check whether the snake is paused
    if g_pause:
        # if any key pressed when the snake is paused, it will start to move
        if g_pause and g_key_pressed in [KEY_DOWN, KEY_UP, KEY_LEFT, KEY_RIGHT]:
            g_pause = False
        else:
            # update the status of pause
            g_status.clear()
            g_elapsed_time = time.time() - g_start_time
            status = f'Contact: {g_contact_count}   Time: {int(g_elapsed_time)}   Motion: {g_key_pressed} '
            g_status.write(status, font=FONT_STATUS)
            g_screen.update()
            g_screen.ontimer(on_timer_snake, TIMER_SNAKE)
            return
    
    # if no key pressed, the snke will keep the original status
    if g_key_pressed is None:
        g_screen.ontimer(on_timer_snake, TIMER_SNAKE)
        return
    
    update_status()

    x, y = g_snake.pos()

    # Check if the next move is within bounds
    next_x, next_y = x, y
    if g_key_pressed == KEY_UP:
        next_y += SZ_SQUARE
    elif g_key_pressed == KEY_DOWN:
        next_y -= SZ_SQUARE
    elif g_key_pressed == KEY_LEFT:
        next_x -= SZ_SQUARE
    elif g_key_pressed == KEY_RIGHT:
        next_x += SZ_SQUARE

    # If the next move would go out of bounds, do not move the snake
    if not (-260 < next_x < 260 and -270 < next_y < 240):
        g_screen.ontimer(on_timer_snake, TIMER_SNAKE)
        return

    # Clone the head as body
    g_snake.color(*COLOR_BODY)
    g_snake.stamp()
    g_snake.color(COLOR_HEAD)

    # Advance snake
    g_snake.setheading(HEADING_BY_KEY[g_key_pressed])
    g_snake.goto(next_x, next_y)

    consume_food(get_food())

    # Shifting or extending the tail.
    if len(g_snake.stampItems) > g_snake_sz:
        g_snake.clearstamps(1)

    # when the snake eat all the food and is fully expanded, the player wins the game
    if len(g_snake.stampItems) == ((1 + g_food_number) * g_food_number / 2) + g_original_snake_sz:
        game_win()

    g_screen.update()

    g_screen.ontimer(on_timer_snake, TIMER_SNAKE)

# when the key of pause is pressed, the status of pause will be shifted
def toggle_pause():
    global g_pause, g_key_pressed, g_previous_key_pressed
    if g_pause == False:
        g_previous_key_pressed = g_key_pressed
        g_key_pressed = None
        g_pause = True
    else:
        g_key_pressed = g_previous_key_pressed
        g_pause = False

# to create the monsters
def create_monster():
    # Define a safe distance that the monster needs to be from the snake
    safe_distance = 100  # Adjust the safe distance as you see fit
    while True:
        # Generate a random position inside the play area
        x = random.randint(int(-DIM_PLAY_AREA/2 + DIM_MARGIN), int(DIM_PLAY_AREA/2 - DIM_MARGIN))
        y = random.randint(int(-DIM_PLAY_AREA/2 + DIM_MARGIN), int(DIM_PLAY_AREA/2 - DIM_MARGIN))
        
        # Check the distance from the snake's head
        if ((x - g_snake.xcor())**2 + (y - g_snake.ycor())**2)**0.5 > safe_distance:
            # If the monster is far enough from the snake, create the monster
            return create_turtle(x, y, COLOR_MONSTER, "black")

# to move the monster towards the snake
def on_timer_monster():
    global g_contact_count

    # check whether the game is running
    if not g_game_running:
        return
    
    # move each monster towards the snake
    for i in range(g_number_of_monsters):
        angle = g_monster[i].towards(g_snake)
        qtr = angle//45 # (0,1,2,3,4,5,6,7)
        heading = qtr * 45 if qtr % 2 == 0 else (qtr+1) * 45

        g_monster[i].setheading(heading)
        g_monster[i].forward(SZ_SQUARE)
        
        # If the monster collides with the snake's body, the number of contact will add one
        if body_collision_with_monster(g_monster[i]):
            g_contact_count += 1
    
    # If the monster collides with the snake's head, the game is over
    if head_collision_with_monster():
       game_over()

    g_screen.update()
    # the movement of the monster has a random delay
    delay = random.randint(TIMER_SNAKE-50, TIMER_SNAKE+200)
    g_screen.ontimer(on_timer_monster, delay)

# check whether the snake's head is collided with the monsters
def head_collision_with_monster() -> bool:
    for i in range(g_number_of_monsters):
        if is_close_enough(g_monster[i].pos(), g_snake.pos(), 14):
            return True
    return False

# check whether the snake's body is collided with the monsters
def body_collision_with_monster(monster):
    for stamp_id in g_snake.stampItems:
        stamp_pos = g_screen.getcanvas().coords(stamp_id)
        if monster.distance(stamp_pos[0], stamp_pos[1]) < SZ_SQUARE:
            return True
    return False

    
# to generate the food
def generate_food():
    # We'll use a list to hold the food turtles for easy access and control later
    food_number_list = list(range(1, g_food_number + 1))  # generate the food of g_food_number
    for number in food_number_list:
        # Create a turtle for each number
        food_turtle = turtle.Turtle()
        food_turtle.hideturtle()
        food_turtle.color('black')
        food_turtle.penup()
        # make sure the food appears within the play area boundaries, avoiding the status area
        # generate the food randomly
        x = random.randint(1,25) * SZ_SQUARE - (SZ_SQUARE + DIM_PLAY_AREA) /2
        y = random.randint(1,25) * SZ_SQUARE - (SZ_SQUARE + DIM_PLAY_AREA) /2 - 30  
        food_turtle.goto(x, y)
        food_turtle.write(str(number), align="center", font=FONT_INTRO)
        # Store the turtle object using the number as a key for reference
        g_food[number] = food_turtle
    on_timer_food() # the food has a random movement

# to move the food
def on_timer_food():
    global g_food
    # check whether the game is running
    if not g_game_running:
        return
    
    shift_distance = 40 # the distance that the food will move

    # make sure the food moves within the play area boundaries
    x_min, x_max = -250, 250
    y_min, y_max = -285, 210

    for number, food_turtle in g_food.items():
        # the food has four directions to move
        directions = ["up", "down", "left", "right"]
        direction = random.choice(directions)

        # get the current position of the food
        x, y = food_turtle.position()
        food_turtle.reset()
        food_turtle.hideturtle()
        food_turtle.penup()

        # calculate the new position of the food
        if direction == "up" and (y + shift_distance) <= y_max:
            y += shift_distance
        elif direction == "down" and (y - shift_distance) >= y_min:
            y -= shift_distance
        elif direction == "left" and (x - shift_distance) >= x_min:
            x -= shift_distance
        elif direction == "right" and (x + shift_distance) <= x_max:
            x += shift_distance

        # move the food to the new position
        food_turtle.setposition(x, y)
        food_turtle.write(str(number), align="center", font=FONT_INTRO)
        g_food[number] = food_turtle
    
    # set the random time that the food will move
    timer_rate = random.randint(5000, 10000)
    g_screen.ontimer(on_timer_food, timer_rate)

# to check the index and the number that the snake ate
def get_food() -> int:
    for index, food in g_food.items():
        # check whether the snake's head and the food is close enough
        if is_close_enough(food.pos(), g_snake.pos()):
            g_eaten_food.append(index)
            g_food[index].reset()
            g_food[index].hideturtle()
            del g_food[index] # delete the eaten food from the g_food list
            return index
    return None

# to calculate whether the two positions are close enough
def is_close_enough(pos1, pos2, threshold = 14):
    x1, y1 = pos1
    x2, y2 = pos2
    distance = ((x1 - x2)**2 + (y1 - y2)**2) ** 0.5 # euclidean distance
    return distance < threshold

# to simulate the process of snake eating food
def consume_food(num):
    global g_snake_sz   
    if g_snake_sz < 100 and num != None:
        g_snake_sz += num # the size will increase according to the number of food
        update_status()

# to display the message when the game ends
def show_message(message, color):
    global g_game_running

    g_game_running = False # the game ends
    # a new turtle to display message
    message_turtle = turtle.Turtle()
    message_turtle.color(color)
    message_turtle.penup()
    message_turtle.hideturtle()
    message_turtle.goto(0, 0)  
    message_turtle.write(message, align="center", font=("Arial", 24, "bold"))

# if win the game
def game_win():
    show_message("Winner!!", "red")

# if fail the game
def game_over():
    show_message("Game Over!!", "red")

# if the player click the screen, the game starts
def cb_start_game(x, y):
    global g_start_time
    # start timing
    g_start_time = time.time()

    # the click will be None
    g_screen.onscreenclick(None)
    g_intro.clear()

    # the key of pause
    g_screen.onkey(toggle_pause, KEY_SPACE)
    
    # the key of up, down, right and left
    for key in (KEY_UP, KEY_DOWN, KEY_RIGHT, KEY_LEFT):
        g_screen.onkey(partial(on_arrow_key_pressed,key), key)

    # to move the snake and monsters
    on_timer_snake()
    on_timer_monster()

if __name__ == "__main__":
    # configure the screen and the play area
    g_screen = configure_screen()
    g_intro, g_status = configure_play_area()

    generate_food()

    update_status()

    g_snake = create_turtle(0,0, COLOR_HEAD, "black") # create the snake
    # Deploy monsters
    for _ in range(g_number_of_monsters):
        monster = create_monster()
        g_monster.append(monster) # store the monsters in a list

    # wherever the player clicks on the screen, the game starts
    g_screen.onscreenclick(cb_start_game) # set up a mouse-click call back

    g_screen.update()
    g_screen.listen()
    g_screen.mainloop()
