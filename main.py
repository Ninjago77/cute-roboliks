"""
Python Version: 3.9.6
Packages: pygame
Author: Shanvanth Arunmozhi
Lisence: MIT
"""
import os,random,threading,json
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
pygame.init()
def distance(pos):
    return (abs(pos[0][0]-pos[1][0]),abs(pos[0][1]-pos[1][1]))

global RGB,ALL_ASSETS,WIDTH,HEIGHT,FPS,CLOCK,LAND,VOID,HITBOX,GRID,SPARKS,LEVEL,WINLAND,SETTINGS
with open("settings.json","r") as f:
    SETTINGS = json.loads(f.read())
HITBOX = SETTINGS["start-hitbox"]
RGB = {
    "white":(255,255,255),
    "black":(0,0,0),
    "red":(255,0,0),
    "blue":(0,0,255)
}
ALL_ASSETS = {
    "player": pygame.transform.scale(pygame.image.load("./assets/player.png"),(64,64)),
    "robot": pygame.transform.scale(pygame.image.load("./assets/robot.png"),(64,64)),
    "spark": pygame.transform.scale(pygame.image.load("./assets/spark.png"),(32,32)),
    "icon": pygame.image.load("./assets/robot.png"),
    "font": pygame.font.SysFont(SETTINGS["font-type"],SETTINGS["font-size-1"],bold=False),
    "font2": pygame.font.SysFont(SETTINGS["font-type"],SETTINGS["font-size-2"],bold=True),
    "tiles":[
        pygame.transform.scale(pygame.image.load("./assets/tiles/void.png"),(64,64)), # 0
        pygame.transform.scale(pygame.image.load("./assets/tiles/none.png"),(64,64)), # 1
        pygame.transform.scale(pygame.image.load("./assets/tiles/all.png"),(64,64)), # 2
        pygame.transform.scale(pygame.image.load("./assets/tiles/side.png"),(64,64)), # 3
        pygame.transform.scale(pygame.image.load("./assets/tiles/double_side.png"),(64,64)), #4
        pygame.transform.scale(pygame.image.load("./assets/tiles/corner.png"),(64,64)), # 5
        pygame.transform.scale(pygame.image.load("./assets/tiles/double_corner.png"),(64,64)),# 6
        pygame.transform.scale(pygame.image.load("./assets/tiles/end1.png"),(64,64)),# 7
        pygame.transform.scale(pygame.image.load("./assets/tiles/end2.png"),(64,64)),# 8
    ],
    "sound":{
        "spark": pygame.mixer.Sound("./assets/spark.wav"),
        "win": pygame.mixer.Sound("./assets/win.wav"),
        "switch": pygame.mixer.Sound("./assets/switch.wav"),
        "deswitch": pygame.mixer.Sound("./assets/deswitch.wav"),
    }
}
WIDTH,HEIGHT = 1536,768
# 24 x 12
FPS = SETTINGS["FPS"]
LEVEL = SETTINGS["start-level"]
CLOCK = pygame.time.Clock()

class Island():
    def __init__(self,x,y,sprite,size,void=False,**kwargs):
        self.sprite,self.size,self.void = sprite,size,void
        (self.x,self.y) = (x*64,y*64)
        self.rect = pygame.Rect(self.x,self.y,self.size,self.size)
    def update(self,win,**kwargs):
        win.blit(self.sprite,(self.x,self.y))
        if self.void:
            win.rect(self.rect)

class Win_Island(Island):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.isrobot = kwargs["robot"]
        self.done = False
    def update(self,*args,**kwargs):
        self.done = False
        if self.isrobot:
            if pygame.Rect.colliderect(self.rect,kwargs["robot"].rect):
                self.done = True
        else:
            if pygame.Rect.colliderect(self.rect,kwargs["player"].rect):
                self.done = True
        super().update(*args,**kwargs)



SPARKS,GRID,LAND,VOID,WINLAND = [],[],[],[],[]

def GEN_LEVEL(level):
    global GRID
    SPARKS.clear()
    GRID.clear()
    LAND.clear()
    VOID.clear()
    WINLAND.clear()
    plyspeed,rbtspeed = SETTINGS["player-speed"],SETTINGS["robot-speed"]
    if islvl(level):
        with open(str("./levels/lvl"+str(level)+".csv"),"r") as f:
            text = f.read()
            GRID = [i.split(",") for i in text.split("\n")]
            if GRID[-1][-1] == "":
                GRID.pop()
        for y in range(len(GRID)-1):
            for x in range(len(GRID[y])):
                if GRID[y][x] != "-1":
                    if GRID[y][x] == "0":
                        VOID.append(Island(x,y,ALL_ASSETS["tiles"][0],64,void=True))
                    elif GRID[y][x] == "-2":
                        WINLAND.append(Win_Island(x,y,ALL_ASSETS["tiles"][7],64,robot=False))
                    elif GRID[y][x] == "-3":
                        WINLAND.append(Win_Island(x,y,ALL_ASSETS["tiles"][8],64,robot=True))
                    else:
                        if GRID[y][x][1] == "0":
                            LAND.append(Island(x,y,ALL_ASSETS["tiles"][int(GRID[y][x][0])],64))
                        if GRID[y][x][1] == "1":
                            LAND.append(Island(x,y,pygame.transform.rotate(
                                ALL_ASSETS["tiles"][int(GRID[y][x][0])], 270),64))
                        if GRID[y][x][1] == "2":
                            LAND.append(Island(x,y,pygame.transform.rotate(
                                ALL_ASSETS["tiles"][int(GRID[y][x][0])], 180),64))
                        if GRID[y][x][1] == "3":
                            LAND.append(Island(x,y,pygame.transform.rotate(
                                ALL_ASSETS["tiles"][int(GRID[y][x][0])], 90),64))
        return (Player(int(GRID[12][0]),int(GRID[12][1]),plyspeed,64,ALL_ASSETS["player"]),
            Robot(int(GRID[12][2]),int(GRID[12][3]),rbtspeed,64,ALL_ASSETS["robot"]))
    else:
        WINLAND.append(Win_Island(4,6,ALL_ASSETS["tiles"][7],64,robot=False))
        WINLAND.append(Win_Island(9,6,ALL_ASSETS["tiles"][8],64,robot=True))
        return (Player(5,6,plyspeed,64,ALL_ASSETS["player"]),
            Robot(8,6,rbtspeed,64,ALL_ASSETS["robot"]))

def Text(win,typ,text,x,y):
    if typ != 1: f = ALL_ASSETS["font2"]
    else: f = ALL_ASSETS["font"]
    win.blit(f.render(text, False, RGB["white"], RGB["black"]),(x*64,y*64))

def islvl(lvl):
    return os.path.exists(str("./levels/lvl"+str(lvl)+".csv"))

class Spark():
    def __init__(self,speed,size,sprite,player,pos):
        threading.Thread(target=lambda:ALL_ASSETS["sound"]["spark"].play()).start()
        self.sprite,self.speed,self.size,self.freeze = sprite,speed,size,False
        (self.x,self.y) = player[0] - self.size//2,player[1] - self.size//2
        if abs(self.x - pos[0]) > abs(self.y - pos[1]):
            if (self.x - pos[0]) < 0:
                self.x_vel = self.speed
            else:
                self.x_vel = self.speed*-1
            self.y_vel = 0
        else:
            if (self.y - pos[1]) < 0:
                self.y_vel = self.speed
            else:
                self.y_vel = self.speed*-1
            self.x_vel = 0
        self.update_rect()

    def update_rect(self):
        self.rect = pygame.Rect(self.x,self.y,self.size,self.size)
    def check_del(self):
        temp = -1
        for spark in range(len(SPARKS)):
            if SPARKS[spark].x == self.x and SPARKS[spark].y == self.y:
                temp = spark
        if temp != -1:
            del SPARKS[temp]
    def update(self,robot):
        if not self.freeze:
            # X Coordinate
            self.x += self.x_vel
            if (self.x < 0) or ((self.x+self.size) > WIDTH):
                self.x -= self.x_vel
                self.check_del()
            self.update_rect()
            if pygame.Rect.collidelist(self.rect,VOID) != -1:
                self.check_del()

            # Y Coordinate

            self.y += self.y_vel
            if (self.y < 0) or ((self.y+self.size) > HEIGHT):
                self.y -= self.y_vel
                self.x -= self.x_vel
                self.check_del()
            self.update_rect()
            if pygame.Rect.collidelist(self.rect,VOID) != -1:
                self.check_del()

            if pygame.Rect.colliderect(self.rect,robot.rect):
                self.y -= self.y_vel
                self.x -= self.x_vel
                self.freeze = True  

            self.update_rect()

    def draw(self,win):
        win.blit(self.sprite,(self.x,self.y))
        win.rect(self.rect)


class Robot():
    def __init__(self,x,y,speed,size,sprite):
        self.sprite,self.speed,self.size = sprite,speed,size
        (self.x,self.y,self.x_vel,self.y_vel) = (x*64,y*64,0,0)
        self.reverse_sprite = pygame.transform.flip(self.sprite,True,False)
        self.curr_sprite = self.sprite
        self.curr_choice = 0
        self.update_rect()
    def update_rect(self):
        self.rect = pygame.Rect(self.x+16,self.y+16,self.size-16,self.size-16)
    def _reduce_y(self):
        if not self.y_red:
            self.y -= self.y_vel
            self.y_red = True
    def _reduce_x(self):
        if not self.x_red:
            self.x -= self.x_vel
            self.x_red = True
    def update(self,keys,opp,lc):
        self.x_vel,self.y_vel = 0,0
        self.x_red,self.y_red = False,False
        if lc == RGB["blue"]:
            self.choice = {
                "up":keys[pygame.K_UP],
                "down":keys[pygame.K_DOWN],
                "right":keys[pygame.K_RIGHT],
                "left":keys[pygame.K_LEFT],
                "":False
            }
        else:
            if self.curr_choice == 0:
                self.choice = {"up":False,"down":False,"right":False,"left":False,"":False}
                choices = ["up","down","right","left"]+["" for i in range(SETTINGS["rand-null"])]
                self.choice[random.choice(choices)] = True
            self.curr_choice += 1
            if self.curr_choice == SETTINGS["rand-threshold"]:
                self.curr_choice = 0

        # X Coordinate
        if self.choice["left"]:
            self.x_vel -= self.speed
        if self.choice["right"]:
            self.x_vel += self.speed
        self.x += self.x_vel
        if (self.x < 0) or ((self.x+self.size) > WIDTH): self._reduce_x()
        self.update_rect()
        if pygame.Rect.colliderect(self.rect,opp.rect):
            self._reduce_x()
        if pygame.Rect.collidelist(self.rect,VOID) != -1:
            self._reduce_x()
        if pygame.Rect.collidelist(self.rect,SPARKS) != -1:
            self._reduce_x()

        # Y Coordinate
        if self.choice["up"]:
            self.y_vel -= self.speed
        if self.choice["down"]:
            self.y_vel += self.speed
        self.y += self.y_vel
        if (self.y < 0) or ((self.y+self.size) > HEIGHT): self._reduce_y()
        self.update_rect()
        if pygame.Rect.colliderect(self.rect,opp.rect):
            self._reduce_y()
        if pygame.Rect.collidelist(self.rect,VOID) != -1:
            self._reduce_y()
        if pygame.Rect.collidelist(self.rect,SPARKS) != -1:
            self._reduce_y()

        self.update_rect()
        if self.x_vel < 0:
            self.curr_sprite = self.reverse_sprite
        if self.x_vel > 0:
            self.curr_sprite = self.sprite

    def draw(self,win):
        win.blit(self.curr_sprite,(self.x,self.y))
        win.rect(self.rect)

class Player():
    def __init__(self,x,y,speed,size,sprite):
        self.sprite,self.speed,self.size = sprite,speed,size
        (self.x,self.y,self.x_vel,self.y_vel) = (x*64,y*64,0,0)
        self.reverse_sprite = pygame.transform.flip(self.sprite,True,False)
        self.curr_sprite = self.sprite
        self.update_rect()
    def update_rect(self):
        self.rect = pygame.Rect(self.x+16,self.y+16,self.size-16,self.size-16)
    def _reduce_y(self):
        if not self.y_red:
            self.y -= self.y_vel
            self.y_red = True
    def _reduce_x(self):
        if not self.x_red:
            self.x -= self.x_vel
            self.x_red = True
    def update(self,keys,events,opp):
        self.x_vel,self.y_vel = 0,0
        self.x_red,self.y_red = False,False

        global HITBOX
        if SETTINGS["toggle-hitbox"]:
            for event in events:
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_h: HITBOX = not HITBOX


        # X Coordinate
        if keys[pygame.K_a]:
            self.x_vel -= self.speed
        if keys[pygame.K_d]:
            self.x_vel += self.speed
        self.x += self.x_vel
        if (self.x < 0) or ((self.x+self.size) > WIDTH): self._reduce_x()
        self.update_rect()
        if pygame.Rect.colliderect(self.rect,opp.rect):
            self._reduce_x()
        if pygame.Rect.collidelist(self.rect,VOID) != -1:
            self._reduce_x()


        # Y Coordinate
        if keys[pygame.K_w]:
            self.y_vel -= self.speed
        if keys[pygame.K_s]:
            self.y_vel += self.speed
        self.y += self.y_vel
        if (self.y < 0) or ((self.y+self.size) > HEIGHT): self._reduce_y()
        self.update_rect()
        if pygame.Rect.colliderect(self.rect,opp.rect):
            self._reduce_y()
        if pygame.Rect.collidelist(self.rect,VOID) != -1:
            self._reduce_y()

        self.update_rect()
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                SPARKS.append(Spark(SETTINGS["spark-speed"],32,
                    ALL_ASSETS["spark"],(
                        self.x+(self.size//2),
                        self.y+(self.size//2)
                    ),pygame.mouse.get_pos()))

        if self.x_vel < 0:
            self.curr_sprite = self.reverse_sprite
        if self.x_vel > 0:
            self.curr_sprite = self.sprite

        if keys[pygame.K_c]:
            SPARKS.clear()

    def draw(self,win):
        win.blit(self.curr_sprite,(self.x,self.y))
        win.rect(self.rect)


class Window():
    def __init__(self,title,width,height):
        self.width,self.height,self.title = width,height,title
        self.obj = pygame.display.set_mode((self.width,self.height))
        pygame.display.set_caption(title)
        pygame.display.set_icon(ALL_ASSETS["icon"])
        self.fill,self.blit = self.obj.fill,self.obj.blit
    def rect(self,value):
        if HITBOX:
            return pygame.draw.rect(self.obj, RGB["red"], value,5)
    def update(self):
        return pygame.display.update()

class Game():
    def __init__(self):
        self.run = False
        self.win = Window("Cute Roboliks <3",width=WIDTH,height=HEIGHT)
    def spark_update(self):
        for spark in SPARKS:
            spark.update(self.robot)
    def internal(self):
        global LEVEL
        self.threads = [
            threading.Thread(target=lambda:self.player.update(
                self.keys,self.events,self.robot)),
            threading.Thread(target=lambda:self.robot.update(
                self.keys,self.player,self.LINECOLOR)),
            threading.Thread(target=lambda:self.spark_update()),
        ]
        self.oldlc = self.LINECOLOR
        for thread in self.threads:
            thread.start()
        for land in LAND:
            land.update(self.win)
        for void in VOID:
            void.update(self.win)
        for winland in WINLAND:
            winland.update(self.win,robot=self.robot,player=self.player)
        if WINLAND[0].done and WINLAND[1].done:
            LEVEL +=1
            threading.Thread(target=lambda:ALL_ASSETS["sound"]["win"].play()).start()
            self.player,self.robot = GEN_LEVEL(LEVEL)
        temp_locate = ([self.player.x+self.player.size//2,self.player.y+self.player.size//2],
            [self.robot.x+self.robot.size//2,self.robot.y+self.robot.size//2])
        temp_distance = distance(temp_locate)
        if temp_distance[0]+temp_distance[1]>SETTINGS["min-distance"]:
            self.LINECOLOR = RGB["blue"]
        else: self.LINECOLOR = RGB["red"]
        pygame.draw.polygon(self.win.obj,self.LINECOLOR,temp_locate,6)
        if self.oldlc != self.LINECOLOR:
            if self.LINECOLOR == RGB["blue"]:
                threading.Thread(target=lambda:ALL_ASSETS["sound"]["switch"].play()).start()
            else:
                threading.Thread(target=lambda:ALL_ASSETS["sound"]["deswitch"].play()).start()
        for thread in self.threads:
            thread.join()
        self.player.draw(self.win)
        self.robot.draw(self.win)
        for spark in SPARKS:
            spark.draw(self.win)
        if LEVEL == 0:
            Text(self.win,1,"Welcome to Cute Roboliks <3!",11.5,2)
            Text(self.win,1,"WASD to move the player,",11.5,3)
            Text(self.win,1,"Arrow keys to move the cute robot,",11.5,4)
            Text(self.win,1,"but only when you are far enough.",11.5,5)
            Text(self.win,1,"The Red/Blue line between the",11.5,6)
            Text(self.win,1,"robot and you shows it. To win ",11.5,7)
            Text(self.win,1,"the robot has to reach the Red []",11.5,8)
            Text(self.win,1,"and you have to reach the Yellow []",11.5,9)
        if LEVEL == 3:
            Text(self.win,1,"If you right-click in any",11.5,2)
            Text(self.win,1,"direction, you will shoot",11.5,3)
            Text(self.win,1,"a Spark. When the spark",11.5,4)
            Text(self.win,1,"hits the robot it will freeze.",11.5,5)
            Text(self.win,1,"And the robot can't pass through.",11.5,6)
            Text(self.win,1,"Press \"C\" to clear all Sparks",11.5,7)
            Text(self.win,1,"The Void also kills Sparks",11.5,8)
        if not islvl(LEVEL):
            Text(self.win,1,"Congrats you have completed",11.5,1)
            Text(self.win,1,"Cute Roboliks <3 !!!",11.5,2)
            Text(self.win,1,"Game - Shanvanth",11.5,3)
            Text(self.win,1,"Tiles - Shanvanth",11.5,4)
            Text(self.win,1,"Sprites - Shanya (Sibling)",11.5,5)
            Text(self.win,1,"Sounds - SFXR",11.5,6)
            Text(self.win,1,"Source Code: https://github.com/",11.5,7)
            Text(self.win,1,"Ninjago77/cute-roboliks",11.5,8)
            Text(self.win,1,"Game Page: ",11.5,9)
            Text(self.win,1,"https://ninjago77.itch.io/",11.5,10)

        Text(self.win,0,str("  Level: "+str(LEVEL)),0,11)
        Text(self.win,0,"Cute Roboliks <3",18,11)
    def wrapper(self):
        CLOCK.tick(FPS)
        self.run = True
        self.LINECOLOR = RGB["red"]
        self.player,self.robot = GEN_LEVEL(LEVEL)
        while self.run:
            self.events = pygame.event.get()
            self.keys = pygame.key.get_pressed()
            for event in self.events:
                if event.type == pygame.QUIT:
                    self.run = False
            self.win.fill(RGB["black"])
            self.internal()
            self.win.update()
        pygame.quit()

def main():
    game = Game()
    game.wrapper()

if __name__ == "__main__":
    main()