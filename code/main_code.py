from create_maze import *
from algorithm import *
from time import sleep


# take level and mode from mode.txt
inp = open('mode.txt', 'r')
lst = inp.readlines()
inp.close()
game_level = int(lst[2])
game_mode = int(lst[3])

#Set level
if game_level == 20:
    create_maze.TILE = 60
    create_maze.cols, create_maze.rows = create_maze.WIDTH // 60, create_maze.HEIGHT // 60
    algorithm.MODE = 50
    create_maze.THICK = 4
    nums_food = 10
elif game_level == 40:
    create_maze.TILE = 40
    create_maze.cols, create_maze.rows = create_maze.WIDTH // 40, create_maze.HEIGHT // 40
    algorithm.MODE = 150
    create_maze.THICK = 3
    nums_food = 30
elif game_level == 100:
    create_maze.TILE = 20
    create_maze.cols, create_maze.rows = create_maze.WIDTH // 20, create_maze.HEIGHT // 20
    create_maze.THICK = 2
    algorithm.MODE = 300
    nums_food = 60

class Food:
    def __init__(self):
        self.img = pygame.image.load("img/cheese.png").convert_alpha()
        self.img = pygame.transform.scale(self.img, (create_maze.TILE - 10, create_maze.TILE - 10))
        self.rect = self.img.get_rect()
        self.set_pos()

    def set_pos(self):
        self.rect.topleft = randrange(create_maze.cols) * create_maze.TILE + 5, randrange(create_maze.rows) * create_maze.TILE + 5

    def draw(self):
        game_surface.blit(self.img, self.rect)

class Button:
    def __init__(self, img_path, col, row):
        self.img = pygame.image.load(img_path).convert_alpha()
        self.img = pygame.transform.scale(self.img, (60, 60))
        self.rect = self.img.get_rect()
        self.rect.topleft = (col, row)
        self.pos = (col,row)
    
    def draw(self,sc):
        sc.blit(self.img, self.rect)

def is_collide(x, y):
    tmp_rect = player_rect.move(x, y)
    if tmp_rect.collidelist(walls_collide_list) == -1:
        return False
    return True

def eat_food():
    for food in food_list:
        if player_rect.collidepoint(food.rect.center):
            food.set_pos()
            return True
    return False

def is_game_over():
    global time, score, record, FPS
    if time < 0:
        pygame.time.wait(700)
        [food.set_pos() for food in food_list]
        set_record(record, score)
        record = get_record()
        time, score, FPS = 150, 0, 60
        return False
    # return when lose

def get_record():
    try:
        with open("record") as f:
            return f.readline()
    except FileNotFoundError:
        with open("record", "w") as f:
            f.write("0")
            return 0

def set_record(record, score):
    rec = max(int(record), score)
    with open("record", "w") as f:
        f.write(str(rec))


FPS = 60
# FPS tăng thì tốc độ quét màn hình tăng -> tốc độ nhân vật tăng

pygame.init()
pygame.mixer.init()
game_surface = pygame.Surface(RES)
pause_surface = pygame.Surface((WIDTH + 300, HEIGHT))
end_game_surface = pygame.Surface((WIDTH + 300, HEIGHT))
surface = pygame.display.set_mode((WIDTH + 300, HEIGHT))
clock = pygame.time.Clock()

# images
bg_game = pygame.image.load("img/background.jpg").convert()
bg_game = pygame.transform.scale(bg_game, (WIDTH, HEIGHT))
bg_pause = pygame.image.load("img/bg_pause.png").convert()
bg = pygame.image.load("img/bg_main.jpg").convert()

# game icon
pygame.display.set_caption("Maze")
pygame_icon = pygame.image.load("img/maze_icon.png")
pygame.display.set_icon(pygame_icon)


def new_game():
    # get maze
    maze = create_maze.generate_maze()
    maze = generateTomAndJerryPos(maze)
    maze2D = getMaze2DArray(maze)

    # get Jerry position
    AimPos = findTomAndJerryPos(maze2D)[1]

    # get Tom position
    CurrentPos = findTomAndJerryPos(maze2D)[0]

    player_rect.topleft = (
        CurrentPos[1] * create_maze.TILE + maze[0].thickness,
        CurrentPos[0] * create_maze.TILE + maze[0].thickness,
    )
    
    des_rect.topleft = (
        AimPos[1] * create_maze.TILE + maze[0].thickness,
        AimPos[0] * create_maze.TILE + maze[0].thickness,
    )
    walls_collide_list = sum(
        [cell.get_rects() for cell in maze],
        [
            pygame.Rect(0, 0, create_maze.TILE * create_maze.cols, maze[0].thickness),
            pygame.Rect(0, 0, maze[0].thickness, create_maze.TILE * create_maze.rows),
            pygame.Rect(create_maze.cols * create_maze.TILE - maze[0].thickness, 0, maze[0].thickness, create_maze.TILE * create_maze.rows),
            pygame.Rect(0, create_maze.rows * create_maze.TILE - maze[0].thickness, create_maze.TILE * create_maze.cols, maze[0].thickness)
        ]
    )
    return maze, maze2D, walls_collide_list, player_rect.topleft,des_rect.topleft

# Phần load game:
def read_saved_game(username : str):
    filename = 'saved_game/' + username + '.txt'
    fp = open(filename, 'r')
    game_mode = int(fp.readline())
    if game_mode == 0:
        game_level = int(fp.readline())
        #Vị trí Jerry
        Aimpos = fp.readline().split()
        Aimpos[0] = int(Aimpos[0])
        Aimpos[1] = int(Aimpos[1])
        #Vị trí Tom
        Currentpos = fp.readline().split()
        Currentpos[0] = int(Currentpos[0])
        Currentpos[1] = int(Currentpos[1])
        maze = []
        if game_level == 20:
            create_maze.TILE = 60
            create_maze.cols, create_maze.rows = create_maze.WIDTH // 60, create_maze.HEIGHT // 60
            create_maze.THICK = 4
            for i in range(216): # col = 18, row = 12
                pos = fp.readline().split()
                x, y = int(pos[0]), int(pos[1])
                cell = Cell(x, y)
                wall = fp.readline().split()
                if wall[0] == '0':
                    cell.walls['top'] = False
                if wall[1] == '0':
                    cell.walls['right'] = False
                if wall[2] == '0':
                    cell.walls['bottom'] = False
                if wall[3] == '0':
                    cell.walls['left'] = False  
                maze.append(cell)
        elif game_level == 40:
            create_maze.TILE = 40
            create_maze.cols, create_maze.rows = create_maze.WIDTH // 40, create_maze.HEIGHT // 40
            create_maze.THICK = 3
            for i in range(486): # col = 27, row = 18
                pos = fp.readline().split()
                x, y = int(pos[0]), int(pos[1])
                cell = Cell(x, y)
                wall = fp.readline().split()
                if wall[0] == '0':
                    cell.walls['top'] = False
                if wall[1] == '0':
                    cell.walls['right'] = False
                if wall[2] == '0':
                    cell.walls['bottom'] = False
                if wall[3] == '0':
                    cell.walls['left'] = False  
                maze.append(cell)
        elif game_level == 100:
            create_maze.TILE = 60
            create_maze.cols, create_maze.rows = create_maze.WIDTH // 20, create_maze.HEIGHT // 20
            create_maze.THICK = 2
            for i in range(1944): #col = 54, row = 36
                pos = fp.readline().split()
                x, y = int(pos[0]), int(pos[1])
                cell = Cell(x, y)
                wall = fp.readline().split()
                if wall[0] == '0':
                    cell.walls['top'] = False
                if wall[1] == '0':
                    cell.walls['right'] = False
                if wall[2] == '0':
                    cell.walls['bottom'] = False
                if wall[3] == '0':
                    cell.walls['left'] = False  
                maze.append(cell)
        return game_mode, maze, Currentpos, Aimpos
    elif game_mode == 1:
        time = int(fp.readline())
        game_level = int(fp.readline())
        #Vị trí Jerry
        Aimpos = fp.readline().split()
        Aimpos[0] = int(Aimpos[0])
        Aimpos[1] = int(Aimpos[1])
        #Vị trí Tom
        Currentpos = fp.readline().split()
        Currentpos[0] = int(Currentpos[0])
        Currentpos[1] = int(Currentpos[1])
        maze = []
        if game_level == 20:
            create_maze.TILE = 60
            create_maze.cols, create_maze.rows = create_maze.WIDTH // 60, create_maze.HEIGHT // 60
            create_maze.THICK = 4
            for i in range(216): # col = 18, row = 12
                pos = fp.readline().split()
                x, y = int(pos[0]), int(pos[1])
                cell = Cell(x, y)
                wall = fp.readline().split()
                if wall[0] == '0':
                    cell.walls['top'] = False
                if wall[1] == '0':
                    cell.walls['right'] = False
                if wall[2] == '0':
                    cell.walls['bottom'] = False
                if wall[3] == '0':
                    cell.walls['left'] = False  
                maze.append(cell)
        elif game_level == 40:
            create_maze.TILE = 40
            create_maze.cols, create_maze.rows = create_maze.WIDTH // 40, create_maze.HEIGHT // 40
            create_maze.THICK = 3
            for i in range(486): # col = 27, row = 18
                pos = fp.readline().split()
                x, y = int(pos[0]), int(pos[1])
                cell = Cell(x, y)
                wall = fp.readline().split()
                if wall[0] == '0':
                    cell.walls['top'] = False
                if wall[1] == '0':
                    cell.walls['right'] = False
                if wall[2] == '0':
                    cell.walls['bottom'] = False
                if wall[3] == '0':
                    cell.walls['left'] = False  
                maze.append(cell)
        elif game_level == 100:
            create_maze.TILE = 20
            create_maze.cols, create_maze.rows = create_maze.WIDTH // 20, create_maze.HEIGHT // 20
            create_maze.THICK = 2
            for i in range(1944): #col = 54, row = 36
                pos = fp.readline().split()
                x, y = int(pos[0]), int(pos[1])
                cell = Cell(x, y)
                wall = fp.readline().split()
                if wall[0] == '0':
                    cell.walls['top'] = False
                if wall[1] == '0':
                    cell.walls['right'] = False
                if wall[2] == '0':
                    cell.walls['bottom'] = False
                if wall[3] == '0':
                    cell.walls['left'] = False  
                maze.append(cell)
        return game_mode, maze, Currentpos, Aimpos, time
    elif game_mode == 2:
        score = int(fp.readline())
        time = int(fp.readline())
        game_level = int(fp.readline())
        #Vị trí Tom
        Currentpos = fp.readline().split()
        Currentpos[0] = int(Currentpos[0])
        Currentpos[1] = int(Currentpos[1])
        maze = []
        if game_level == 20:
            create_maze.TILE = 60
            create_maze.cols, create_maze.rows = create_maze.WIDTH // 60, create_maze.HEIGHT // 60
            create_maze.THICK = 4
            for i in range(216): # col = 18, row = 12
                pos = fp.readline().split()
                x, y = int(pos[0]), int(pos[1])
                cell = Cell(x, y)
                wall = fp.readline().split()
                if wall[0] == '0':
                    cell.walls['top'] = False
                if wall[1] == '0':
                    cell.walls['right'] = False
                if wall[2] == '0':
                    cell.walls['bottom'] = False
                if wall[3] == '0':
                    cell.walls['left'] = False  
                maze.append(cell)
        elif game_level == 40:
            create_maze.TILE = 40
            create_maze.cols, create_maze.rows = create_maze.WIDTH // 40, create_maze.HEIGHT // 40
            create_maze.THICK = 3
            for i in range(486): # col = 27, row = 18
                pos = fp.readline().split()
                x, y = int(pos[0]), int(pos[1])
                cell = Cell(x, y)
                wall = fp.readline().split()
                if wall[0] == '0':
                    cell.walls['top'] = False
                if wall[1] == '0':
                    cell.walls['right'] = False
                if wall[2] == '0':
                    cell.walls['bottom'] = False
                if wall[3] == '0':
                    cell.walls['left'] = False  
                maze.append(cell)
        elif game_level == 100:
            create_maze.TILE = 20
            create_maze.cols, create_maze.rows = create_maze.WIDTH // 20, create_maze.HEIGHT // 20
            create_maze.THICK = 2
            for i in range(1944): #col = 54, row = 36
                pos = fp.readline().split()
                x, y = int(pos[0]), int(pos[1])
                cell = Cell(x, y)
                wall = fp.readline().split()
                if wall[0] == '0':
                    cell.walls['top'] = False
                if wall[1] == '0':
                    cell.walls['right'] = False
                if wall[2] == '0':
                    cell.walls['bottom'] = False
                if wall[3] == '0':
                    cell.walls['left'] = False       
                maze.append(cell)
        return game_mode, maze, Currentpos, time, score
    fp.close()

def load_game(username: str):
    game_mode = read_saved_game[0]
    # get maze
    maze = read_saved_game(username)[1]
    maze2D = getMaze2DArray(maze)
    # get Tom position
    CurrentPos = read_saved_game(username)[2]

    if game_mode == 0:
        # get Jerry position
        AimPos = read_saved_game(username)[3]
    elif game_mode == 1:
        AimPos = read_saved_game(username)[3]
        time = read_saved_game(username)[4]
    elif game_mode == 2:
        time = read_saved_game(username)[3]
        score = read_saved_game(username)[4]

    player_rect.topleft = (
        CurrentPos[1] * create_maze.TILE + maze[0].thickness,
        CurrentPos[0] * create_maze.TILE + maze[0].thickness,
    )
    
    des_rect.topleft = (
        AimPos[1] * create_maze.TILE + maze[0].thickness,
        AimPos[0] * create_maze.TILE + maze[0].thickness,
    )
    walls_collide_list = sum(
        [cell.get_rects() for cell in maze],
        [
            pygame.Rect(0, 0, create_maze.TILE * create_maze.cols, maze[0].thickness),
            pygame.Rect(0, 0, maze[0].thickness, create_maze.TILE * create_maze.rows),
            pygame.Rect(create_maze.cols * create_maze.TILE - maze[0].thickness, 0, maze[0].thickness, create_maze.TILE * create_maze.rows),
            pygame.Rect(0, create_maze.rows * create_maze.TILE - maze[0].thickness, create_maze.TILE * create_maze.cols, maze[0].thickness)
        ]
    )
    return maze, maze2D, walls_collide_list, player_rect.topleft, des_rect.topleft, time, score


# get maze
maze = create_maze.generate_maze()
generateTomAndJerryPos(maze)
maze2D = getMaze2DArray(maze)

# get Jerry position
AimPos = findTomAndJerryPos(maze2D)[1]

# get Tom position
CurrentPos = findTomAndJerryPos(maze2D)[0]

# player settings
player_speed = 10  # TILE must be divided by player_speed
player_img = pygame.image.load("img/tomface.png").convert_alpha()
player_img = pygame.transform.scale(
    player_img, (create_maze.TILE - 2 * maze[0].thickness, create_maze.TILE - 2 * maze[0].thickness)
)
player_rect = player_img.get_rect()
player_rect.topleft = (
    CurrentPos[1] * create_maze.TILE + maze[0].thickness,
    CurrentPos[0] * create_maze.TILE + maze[0].thickness,
)

# destination settings
des_img = pygame.image.load("img/jerryface.png").convert_alpha()
des_img = pygame.transform.scale(
    des_img, (create_maze.TILE - 2 * maze[0].thickness, create_maze.TILE - 2 * maze[0].thickness)
)
des_rect = des_img.get_rect()
des_rect.topleft = (
    AimPos[1] * create_maze.TILE + maze[0].thickness,
    AimPos[0] * create_maze.TILE + maze[0].thickness,
)
#hint
hint_img = pygame.image.load("img/star.png").convert_alpha()
hint_img = pygame.transform.scale(
    hint_img, (create_maze.TILE - 2 * maze[0].thickness, create_maze.TILE - 2 * maze[0].thickness)
)
hint_rect = hint_img.get_rect()
# directions = {'a': (-player_speed, 0), 'd': (player_speed, 0), 'w': (0, -player_speed), 's': (0, player_speed)}
# keys = {'a': pygame.K_a, 'd': pygame.K_d, 'w': pygame.K_w, 's': pygame.K_s}
# directions = {'a': (-player_speed, 0), 'd': (player_speed, 0), 'w': (0, -player_speed), 's': (0, player_speed)}
# keys = {'a': pygame.K_a, 'd': pygame.K_d, 'w': pygame.K_w, 's': pygame.K_s}
directions = {
    "a": (-player_speed, 0),
    "d": (player_speed, 0),
    "w": (0, -player_speed),
    "s": (0, player_speed),
}
keys = {"a": pygame.K_a, "d": pygame.K_d, "w": pygame.K_w, "s": pygame.K_s}
direction = (0, 0)

# food settings
food_list = [Food() for i in range(nums_food)]

# collision list
walls_collide_list = sum(
    [cell.get_rects() for cell in maze],
    [
        pygame.Rect(0, 0, create_maze.TILE * create_maze.cols, maze[0].thickness),
        pygame.Rect(0, 0, maze[0].thickness, create_maze.TILE * create_maze.rows),
        pygame.Rect(
            create_maze.cols * create_maze.TILE - maze[0].thickness,
            0,
            maze[0].thickness,
            create_maze.TILE * create_maze.rows,
        ),
        pygame.Rect(
            0,
            create_maze.rows * create_maze.TILE - maze[0].thickness,
            create_maze.TILE * create_maze.cols,
            maze[0].thickness,
        ),
    ],
)

def get_way_between_2point(currp, nextp, maze2D):
    if currp[0] == nextp[0]:
        if (currp[1]+1 == nextp[1]) and not maze2D[currp].walls['right'] and not maze2D[nextp].walls['left']:
            return 'd'
        if (currp[1]-1== nextp[1]) and not maze2D[currp].walls['left'] and not maze2D[nextp].walls['right']:
            return 'a'
    if currp[1] == nextp[1]:
        if (currp[0]+1== nextp[0]) and not maze2D[currp].walls['bottom'] and not maze2D[nextp].walls['top']:
            return 's'
        if (currp[0]-1== nextp[0]) and not maze2D[currp].walls['top'] and not maze2D[nextp].walls['bottom']:
            return 'w'  
    return None          


# timer, score, record
pygame.time.set_timer(pygame.USEREVENT, 1000)
time = 150
score = 0
record = get_record()

# fonts
font = pygame.font.Font(r"./font/Shermlock.ttf", 150)
text_font = pygame.font.Font(r"./font/Shermlock.ttf", 80)
mini_text_font = pygame.font.Font(r"./font/Shermlock.ttf", 40)

# save last position and the state of setting lastpos
lastpos = (-1, -1)
is_set = False
current_direction = None
default_algo = 1
# pause status, win status
autoplay_pause = False
pause = False
finish = False
# hint status
hint = False
hint_1 = False
hint_2 = False

# button
play_button = Button("img/playbutton.png", 900, 520)
home_button = Button("img/menubutton.png", 1100, 520)
pause_button = Button("img/pausebutton.png", 1300,50)
hint_button_1 = Button("img/hintbutton.png", 1300,300)
hint_button_2 = Button("img/hintbutton.png", 1300,500)
# sound_button = Button("img/resumebutton.png", 1200,570)
# <<<<<<< main
# =======

def create_user_saved_game(username : str):
    # get Jerry position
    AimPos = findTomAndJerryPos(maze2D)[1]
    # get Tom position
    CurrentPos = findTomAndJerryPos(maze2D)[0]

    filename = 'saved_game/' + username + '.txt'
    open(filename, 'w').close()
    fp = open(filename, 'w')
    if game_mode == 0:
        # Dòng 1: in game_mode
        # Dòng 2: in game_level
        # Dòng 3: in vị trí Jerry
        # Dòng 4: in vị trí Tom
        fp.write('0\n')
        fp.write(str(game_level) + '\n')
        fp.write(str(AimPos[0]) + ' ')
        fp.write(str(AimPos[1]) + '\n')
        fp.write(str(CurrentPos[0])+ ' ')
        fp.write(str(CurrentPos[1]) + '\n')

    elif game_mode == 1:
        # Dòng 1: in game_mode
        # Dòng 2: in thời gian còn lại
        # Dong 3: in game_level
        # Dòng 4: in vị trí Jerry
        # Dòng 5: in vị trí Tom
        fp.write('1\n')
        fp.write(str(time) + '\n')
        fp.write(str(game_level) + '\n')
        fp.write(str(AimPos[0]) + ' ')
        fp.write(str(AimPos[1]) + '\n')
        fp.write(str(CurrentPos[0])+ ' ')
        fp.write(str(CurrentPos[1]) + '\n')

    elif game_mode == 2:
        # Dòng 1: in game_mode
        # Dòng 2: in số điểm hiện tại
        # Dòng 3: in thời gian còn lại
        # Dòng 4: in game_level
        # Dòng 5: in vị trí Tom
        fp.write('2\n')
        fp.write(str(score) + '\n')
        fp.write(str(time) + '\n')
        fp.write(str(game_level) + '\n')
        fp.write(str(CurrentPos[0])+ ' ')
        fp.write(str(CurrentPos[1]) + '\n')

    for cell in maze:
        fp.write(str(cell.x))
        fp.write(' ')
        fp.write(str(cell.y))
        fp.write('\n')
        for i in ['top', 'right', 'bottom', 'left']:
            if cell.walls[i] == True:
                fp.write('1 ')
            else:
                fp.write('0 ')
        fp.write('\n')  
    fp.close()             
# >>>>>>> main
    
def pause_game():
    surface.blit(pause_surface,(0,0))
    pause_surface.blit(bg_pause, (0,0))
    pause_surface.blit(text_font.render("CONTINUE?", True, pygame.Color("white")), (880, 400))
    play_button.draw(pause_surface)
    home_button.draw(pause_surface)
    if pygame.mouse.get_pressed()[0]:
        if play_button.rect.collidepoint(pygame.mouse.get_pos()):
            return 0
        if home_button.rect.collidepoint(pygame.mouse.get_pos()):
# <<<<<<< main
#             # Go back home()
#             return 1
# =======
            DISPLAYSURF = surface
            pygame.draw.rect(DISPLAYSURF, WHITE, (1280//2 - 250, 300, 550, 240))
            pygame.draw.rect(DISPLAYSURF, BLUE, (1280//2 - 250, 300, 550, 40))
            write_screen('Go out', WHITE, None, (1280//2 - 240 + 80, 320), 1, DISPLAYSURF, 20)
            write_screen("  x  ", WHITE, RED, (1280//2 + 280, 320), -1, DISPLAYSURF, 20)
            write_screen("Do u want to save your current game?", BLACK, None, (1280//2, 380), 1, DISPLAYSURF, 18)
            write_screen("SURE                                     NO", BLACK, WHITE, (1280//2, 500), 1, DISPLAYSURF, 18)
            while True:
                for event in pygame.event.get(): 
                    tempx = pygame.mouse.get_pos()[0]
                    tempy = pygame.mouse.get_pos()[1]
                    if event.type == pygame.MOUSEBUTTONUP:
                        if (900 < tempx < 940 and 302 < tempy < 340) or (724 < tempx < 748 and 490 < tempy < 506): #quit dialog
                            return 1
                        elif 542 < tempx < 567 and 489 < tempy < 506:
                            # lưu mê cung
                            f = open('current_account.txt', 'r')
                            username = f.read()
                            f.close()
                            create_user_saved_game(username)
                            return 1
                    else:
                        if 542 < tempx < 567 and 489 < tempy < 506:
                            write_screen("SURE", BLACK, BROWN, ((542+568)//2, 500), 1, DISPLAYSURF, 18)
                        elif 724 < tempx < 748 and 490 < tempy < 506:
                            write_screen("NO", BLACK, BROWN, ((720 + 746)//2, 500), 1, DISPLAYSURF, 18)
                        else:
                            write_screen("SURE                                     NO", BLACK, WHITE, (1280//2, 500), 1, DISPLAYSURF, 18)
                pygame.display.update((380, 300, 600, 250))
# >>>>>>> main
    # continue to pause
    return 2

def get_player_current_cell():
    # Get player position (Tom's Position)
    if current_direction == "w" or current_direction == "a":
        pos = (
            np.ceil((player_rect.top - maze[0].thickness) / create_maze.TILE),
            np.ceil((player_rect.left -  maze[0].thickness) / create_maze.TILE),
        )
    else:
        pos = (
            np.floor((player_rect.top - maze[0].thickness) / create_maze.TILE),
            np.floor((player_rect.left - maze[0].thickness) / create_maze.TILE),
        )
    pos = (int(pos[0]),int(pos[1]))
    return pos


#main    
count = 0
times_move = 0
#main    
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            inp = open('result.txt', 'w')
            inp.write('-1')
            inp.close()
            running = False
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                pause = False if pause else True
            if event.key == pygame.K_h:
                autoplay_pause = False if autoplay_pause else True
        if event.type == pygame.USEREVENT and not pause:
            time -= 1
    # Menu pause game
    if pause:
        f = pause_game()
        if f == 1:
            inp = open('result.txt', 'w')
            inp.write('-1')
            inp.close()
            running = False
            exit()
        elif f == 0:
            pause = False
        else:
            pause = True
    else:
        pos = get_player_current_cell()
        #Normal mode
        if game_mode == 0:
            # Action when player won
            if player_rect.colliderect(des_rect):
                result = open('result.txt', 'w')
                result.write('1')
                result.close()
                hint1, hint_2, hint = False, False, False
                is_set = False
                finish = True
                # End game
                running = False
                break

            else:
                surface.blit(bg, (WIDTH, 0))
                surface.blit(game_surface, (0, 0))
                game_surface.blit(bg_game, (0, 0))

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        inp = open('result.txt', 'w')
                        inp.write('-1')
                        inp.close()
                        running = False
                        exit()
                    if event.type == pygame.USEREVENT:
                        time -= 1

                # controls and movement
                pos = get_player_current_cell()
                pressed_key = pygame.key.get_pressed()
                # Kiểm tra xem có thể rẽ vào hướng nút bấm không (nếu không bị tường chặn)
                for key, key_value in keys.items():
                    if pressed_key[key_value] and not is_collide(*directions[key]):
                        direction = directions[key]
                        if not is_set:
                            is_set = True
                            current_direction = key
                            lastpos = pos
                        break

                if pos == lastpos and not is_collide(*direction):
                    player_rect.move_ip(direction)
                else:
                    is_set = False

                # Press ESC to see path dfs
                if hint_1 and not hint:
                    hint = True
                    maze2D[CurrentPos[0]][CurrentPos[1]].make_blank()
                    maze2D[pos[0]][pos[1]].make_tom_pos()
                    CurrentPos = pos
                    maze = list(maze2D.flatten())
                    path1 = findPathBetween2Point(maze, algo=1)
                    path_cell_list_dfs = getPathCellList(path1, maze2D)
                    five_first_step = path_cell_list_dfs[1:6].copy()
                    [cell.draw(game_surface) for cell in maze]

                if hint_2 and not hint:
                    hint = True
                    maze2D[CurrentPos[0]][CurrentPos[1]].make_blank()
                    maze2D[pos[0]][pos[1]].make_tom_pos()
                    CurrentPos = pos
                    maze = list(maze2D.flatten())
                    path2 = findPathBetween2Point(maze, algo=2)
                    path_cell_list_bfs = getPathCellList(path2, maze2D)
                    five_first_step = path_cell_list_bfs[1:6].copy()
                    [cell.draw(game_surface) for cell in maze]


                if hint:
                    for i in range(5):
                        hint_rect.topleft = (maze[0].thickness + five_first_step[i].x*create_maze.TILE,maze[0].thickness + five_first_step[i].y*create_maze.TILE)
                        game_surface.blit(hint_img, hint_rect)
                # draw maze
                [cell.draw(game_surface) for cell in maze]

                # draw player
                game_surface.blit(player_img, player_rect)
                game_surface.blit(des_img, des_rect)

                clock.tick(FPS)

        #Speedrun mode
        elif game_mode == 1:
            # Action when player won
            if player_rect.colliderect(des_rect):
                finish = True
                result = open('result.txt', 'w')
                result.write('1')
                result.close()
                # End game
                hint1, hint_2, hint = False, False, False
                is_set = False
                running = False
                break

            # Action when player failed
            elif time < 0:
                finish = True
                result = open('result.txt', 'w')
                result.write('0')
                result.close()
                hint1, hint_2, hint = False, False, False
                is_set = False
                running = False
                break
            else:
                surface.blit(bg, (WIDTH, 0))
                surface.blit(game_surface, (0, 0))
                game_surface.blit(bg_game, (0, 0))

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        inp = open('result.txt', 'w')
                        inp.write('-1')
                        inp.close()
                        running = False
                        exit()
                    if event.type == pygame.USEREVENT:
                        time -= 1

                # controls and movement
                pos = get_player_current_cell()
                pressed_key = pygame.key.get_pressed()
                # Kiểm tra xem có thể rẽ vào hướng nút bấm không (nếu không bị tường chặn)
                for key, key_value in keys.items():
                    if pressed_key[key_value] and not is_collide(*directions[key]):
                        direction = directions[key]
                        if not is_set:
                            is_set = True
                            current_direction = key
                            lastpos = pos
                        break

                if pos == lastpos and not is_collide(*direction):
                    player_rect.move_ip(direction)
                else:
                    is_set = False
                # path dfs
                if hint_1 and not hint:
                    hint = True
                    maze2D[CurrentPos[0]][CurrentPos[1]].make_blank()
                    maze2D[pos[0]][pos[1]].make_tom_pos()
                    CurrentPos = pos
                    maze = list(maze2D.flatten())
                    path1 = findPathBetween2Point(maze, algo=1)
                    path_cell_list_dfs = getPathCellList(path1, maze2D)
                    five_first_step = path_cell_list_dfs[1:6].copy()
                    [cell.draw(game_surface) for cell in maze]

                if hint_2 and not hint:
                    hint = True
                    maze2D[CurrentPos[0]][CurrentPos[1]].make_blank()
                    maze2D[pos[0]][pos[1]].make_tom_pos()
                    CurrentPos = pos
                    maze = list(maze2D.flatten())
                    path2 = findPathBetween2Point(maze, algo=2)
                    path_cell_list_bfs = getPathCellList(path2, maze2D)
                    five_first_step = path_cell_list_bfs[1:6].copy()
                    [cell.draw(game_surface) for cell in maze]

                if hint:
                    for i in range(5):
                        hint_rect.topleft = (maze[0].thickness + five_first_step[i].x*create_maze.TILE,maze[0].thickness + five_first_step[i].y*create_maze.TILE)
                        game_surface.blit(hint_img, hint_rect)
                # draw maze
                [cell.draw(game_surface) for cell in maze]

                # draw player
                game_surface.blit(player_img, player_rect)
                game_surface.blit(des_img, des_rect)

                # draw stats
                surface.blit(
                    text_font.render("TIME", True, pygame.Color("cyan")), (WIDTH + 20, 10)
                )
                surface.blit(font.render(f"{time}", True, pygame.Color("cyan")), (WIDTH + 20, 80))
                clock.tick(FPS)

        #Collect mode
        elif game_mode == 2:
            surface.blit(bg, (WIDTH, 0))
            surface.blit(game_surface, (0, 0))
            game_surface.blit(bg_game, (0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    inp = open('result.txt', 'w')
                    inp.write('-1')
                    inp.close()
                    running = False
                    exit()
                if event.type == pygame.USEREVENT:
                    time -= 1

            # controls and movement
            pos = get_player_current_cell()
            pressed_key = pygame.key.get_pressed()
            # Kiểm tra xem có thể rẽ vào hướng nút bấm không (nếu không bị tường chặn)
            for key, key_value in keys.items():
                if pressed_key[key_value] and not is_collide(*directions[key]):
                    direction = directions[key]
                    if not is_set:
                        is_set = True
                        current_direction = key
                        lastpos = pos
                    break

            if pos == lastpos and not is_collide(*direction):
                player_rect.move_ip(direction)
            else:
                is_set = False

            # draw maze
            [cell.draw(game_surface) for cell in maze]

            # gameplay
            if eat_food():
                # FPS += 10
                score += 1
            if is_game_over() == False:
                running = False
                finish = True
                result = open('result.txt', 'w')
                result.write('1')
                result.close()
                break

            # draw player
            game_surface.blit(player_img, player_rect)

            # draw food
            [food.draw() for food in food_list]

            # draw stats
            surface.blit(
                text_font.render("TIME", True, pygame.Color("cyan")), (WIDTH + 20, 10)
            )
            surface.blit(font.render(f"{time}", True, pygame.Color("cyan")), (WIDTH + 20, 80))
            surface.blit(
                text_font.render("score", True, pygame.Color("forestgreen")),
                (WIDTH + 20, 240),
            )
            surface.blit(
                font.render(f"{score}", True, pygame.Color("forestgreen")), (WIDTH + 20, 310)
            )
            surface.blit(
                text_font.render("record", True, pygame.Color("magenta")),
                (WIDTH + 20, 470),
            )
            surface.blit(
                font.render(f"{record}", True, pygame.Color("magenta")), (WIDTH + 20, 540)
            )

            clock.tick(FPS)
        
        #Load game
        elif game_mode == 3:
            maze, maze2D, walls_collide_list, player_rect.topleft, des_rect.topleft, time, score = load_game()
            # Action when player won
            if player_rect.colliderect(des_rect):
                hint1, hint_2, hint = False, False, False
                is_set = False
                finish = True
                # End game
                running = False
                break

            else:
                surface.blit(bg, (WIDTH, 0))
                surface.blit(game_surface, (0, 0))
                game_surface.blit(bg_game, (0, 0))

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        inp = open('result.txt', 'w')
                        inp.write('-1')
                        inp.close()
                        running = False
                        exit()
                    if event.type == pygame.USEREVENT:
                        time -= 1

                # controls and movement
                pos = get_player_current_cell()
                pressed_key = pygame.key.get_pressed()
                # Kiểm tra xem có thể rẽ vào hướng nút bấm không (nếu không bị tường chặn)
                for key, key_value in keys.items():
                    if pressed_key[key_value] and not is_collide(*directions[key]):
                        direction = directions[key]
                        if not is_set:
                            is_set = True
                            current_direction = key
                            lastpos = pos
                        break

                if pos == lastpos and not is_collide(*direction):
                    player_rect.move_ip(direction)
                else:
                    is_set = False

                # Press ESC to see path dfs
                if hint_1 and not hint:
                    hint = True
                    maze2D[CurrentPos[0]][CurrentPos[1]].make_blank()
                    maze2D[pos[0]][pos[1]].make_tom_pos()
                    CurrentPos = pos
                    maze = list(maze2D.flatten())
                    path1 = findPathBetween2Point(maze, algo=1)
                    path_cell_list_dfs = getPathCellList(path1, maze2D)
                    five_first_step = path_cell_list_dfs[1:6].copy()
                    [cell.draw(game_surface) for cell in maze]

                if hint_2 and not hint:
                    hint = True
                    maze2D[CurrentPos[0]][CurrentPos[1]].make_blank()
                    maze2D[pos[0]][pos[1]].make_tom_pos()
                    CurrentPos = pos
                    maze = list(maze2D.flatten())
                    path2 = findPathBetween2Point(maze, algo=2)
                    path_cell_list_bfs = getPathCellList(path2, maze2D)
                    five_first_step = path_cell_list_bfs[1:6].copy()
                    [cell.draw(game_surface) for cell in maze]


                if hint:
                    for i in range(5):
                        hint_rect.topleft = (maze[0].thickness + five_first_step[i].x*create_maze.TILE,maze[0].thickness + five_first_step[i].y*create_maze.TILE)
                        game_surface.blit(hint_img, hint_rect)
                # draw maze
                [cell.draw(game_surface) for cell in maze]

                # draw player
                game_surface.blit(player_img, player_rect)
                game_surface.blit(des_img, des_rect)

                clock.tick(FPS)
        
        #draw pause button
        elif game_mode == 4:
            surface.blit(bg, (WIDTH, 0))
            surface.blit(game_surface, (0, 0))
            game_surface.blit(bg_game, (0, 0))
            if not autoplay_pause:
                path = findPathBetween2Point(maze, algo=default_algo) if findPathBetween2Point(maze, algo=default_algo) else []
                pos = get_player_current_cell()
                if not is_set:
                    is_set = True
                    lastpos = pos
                if lastpos == pos:
                    if len(path)>=2:
                        pA = path[0]
                        pB = path[1]
                        current_direction = get_way_between_2point(pA,pB,maze2D)
                        player_rect.move_ip(directions[current_direction])
                    if not len(path):
                        bg.blit(text_font.render("FINISH", True, pygame.Color("pink")),(0,0))
                        bg.blit(mini_text_font.render("Click on the screen to restart!", True, pygame.Color("white")), (850, 500))
                        if pygame.mouse.get_pressed()[0]:
                            maze, maze2D,walls_collide_list ,player_rect.topleft,des_rect.topleft= new_game()
                            # get Jerry position
                            AimPos = findTomAndJerryPos(maze2D)[1]
                            # get Tom position
                            CurrentPos = findTomAndJerryPos(maze2D)[0]
                            time = -1
                            is_game_over()
                            finish = False
                            hint1, hint_2, hint = False, False, False
                            is_set = False
                else:
                    maze2D[CurrentPos[0]][CurrentPos[1]].make_blank()
                    maze2D[pos[0]][pos[1]].make_tom_pos()
                    CurrentPos = pos
                    maze = list(maze2D.flatten())                    
                    is_set = False
            if hint_1:
                default_algo = 1
                [cell.draw(game_surface) for cell in maze]
                [cell.color_cell(game_surface, "blue") for cell in getPathCellList(path,maze2D)[1:]]
                
            if hint_2:
                default_algo = 2
                [cell.draw(game_surface) for cell in maze]
                [cell.color_cell(game_surface, "green") for cell in getPathCellList(path,maze2D)[1:]]
            game_surface.blit(des_img,des_rect)
            game_surface.blit(player_img, player_rect)
            [cell.draw(game_surface) for cell in maze]
                    
            clock.tick(FPS)

        if not finish:
            #draw pause button
            pause_button.draw(surface)
            if pygame.mouse.get_pressed()[0]:
                if pause_button.rect.collidepoint(pygame.mouse.get_pos()):
                    pause = True
            #draw hint button
            if (game_mode == 0 or game_mode == 1 or game_mode == 4) and not pause:
                hint_button_1.draw(surface)
                surface.blit(mini_text_font.render("HINT 1", True, pygame.Color("white")), (1200, 400))

                hint_button_2.draw(surface)
                surface.blit(mini_text_font.render("HINT 2", True, pygame.Color("white")), (1200, 600))
                if pygame.mouse.get_pressed()[0]:
                    if hint_button_1.rect.collidepoint(pygame.mouse.get_pos()):
                        if not hint_1:
                            hint_1 = True
                            hint_2 = False
                            
                if pygame.mouse.get_pressed()[0]:
                    if hint_button_2.rect.collidepoint(pygame.mouse.get_pos()):
                        if not hint_2:
                            hint_2 = True
                            hint_1 = False
    pygame.display.update()
