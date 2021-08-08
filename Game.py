######################################################
# Importing and initialising modules
# setting up the screen and clock
# opening the highscore data from the file
# EWidth is the horizontal resolution of the enemy sprites
# timing events for spawning enemies and enemy shooting

import pygame
import random
from tkinter import *
from tkinter import ttk

pygame.init()
#pygame.mixer.init()
pygame.font.init()

Font = pygame.font.SysFont("None", 24)
BigFont = pygame.font.SysFont("None", 72)

clock = pygame.time.Clock()

Screen = pygame.display.set_mode([700, 1000])
pygame.display.set_caption("Alien Blaster")

EWidth = 80

EnemyShoot = pygame.USEREVENT + 1
EnemySpawn = pygame.USEREVENT + 2
Invincibility = pygame.USEREVENT + 3
pygame.time.set_timer(EnemyShoot, 2000)
pygame.time.set_timer(EnemySpawn, 500)

######################################################
# CLASS DEFINITIONS
######################################################
# Player sprite class
# the sprite is moved with the mouse

class Player(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super().__init__()

        self.image = LoadImage("image3.png")

        self.rect = self.image.get_rect(midtop=(x, y))

    def update(self):
        MousePos = pygame.mouse.get_pos()
        self.rect.x = MousePos[0]
        self.rect.y = MousePos[1]


######################################################
# Enemy sprite class
# Extra argument MovementType defines their movement pattern
# If they move off the screen they die, without awarding points

class Enemy(pygame.sprite.Sprite):

    def __init__(self, x, y, MovementType):
        super().__init__()

        self.image = LoadImage("enemy.png")

        self.rect = self.image.get_rect(topleft=(x, y))

        self.MovementType = MovementType

    def update(self):
        if self.MovementType == 1:
            self.rect.move_ip(-1, 0)
        if self.MovementType == 2:
            self.rect.move_ip(1, 0)
        if self.MovementType == 3:
            self.rect.move_ip(1, 1)
        if self.MovementType == 4:
            self.rect.move_ip(-1, 1)
        if self.MovementType == 5:
            self.rect.move_ip(0, 1)

        if self.rect.x < -EWidth - 10 or self.rect.x > 700 + EWidth or self.rect.y > 1000:
            self.kill()
            print("kill")


######################################################
# Player bullets class
# Move up the screen until the top

class PlayerBullet(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super().__init__()

        self.image = LoadImage("bullet.png")

        self.rect = self.image.get_rect(topleft=(x + 22, y))

    def update(self):
        self.rect.move_ip(0, -10)
        if self.rect.top <= 0:
            self.kill()


######################################################
# Enemy bullet class
# Moves down screen until bottom
# Different centre due to different sprite width

class EnemyBullet(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super().__init__()

        self.image = LoadImage("enemyb.png")

        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self):
        self.rect.move_ip(0, 7)
        if self.rect.top <= 0:
            self.kill()


######################################################
# boss class
# moves onto screen and stays still for boss battle

class Boss(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super().__init__()

        self.image = LoadImage("boss.png")

        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self):
        if self.rect.y < 0:
            self.rect.move_ip(0, 1)


######################################################
# a function to load images for the sprites

def LoadImage(File):
    Image = pygame.image.load(File)
    return Image.convert_alpha()


######################################################
# a function to load sounds for the game

def LoadSound(File):
    Sound = pygame.mixer.Sound(File)
    return Sound


######################################################
# The function controlling the game's menus
# Only the main menu displays the rules
# only the post-game menus display the previous score
# The Type argument decides if it should show Main Menu, Game Over or Victory screens.Stra

def Menu(Title, Image, CurrentScore, Type):
    # I'm using global for Root since it has to be accessed by other functions
    global Root
    Root = Tk()
    Root.title("Game Menu")

    HighscoreFile = open("highscore.txt", "r")
    Highscore = HighscoreFile.read()

    Img = PhotoImage(file=Image)

    StartButton = ttk.Button(Root, text="Start Game", command=StartGame)
    Image = ttk.Label(Root, image=Img)
    MenuTitle = ttk.Label(Root, text=Title, font = ("None", 60))
    YourScore = ttk.Label(Root, text="Your score: " + CurrentScore, font = ("None", 30))
    HighScoreLabel = ttk.Label(Root, text="Highscore: " + Highscore, font = ("None", 35))
    ExitButton = ttk.Button(Root, text="Exit Game", command=Exit)
    Rule1 = ttk.Label(Root, text="Rules:")
    Rule2 = ttk.Label(Root, text="50 Enemies will randomly spawn,")
    Rule3 = ttk.Label(Root, text="Kill them to score points,")
    Rule4 = ttk.Label(Root, text="You can shoot enemy projectiles,")
    Rule5 = ttk.Label(Root, text="After 50 enemies a boss will spawn,")
    Rule6 = ttk.Label(Root, text="The boss is worth 20 points and has 30 HP,")
    Rule7 = ttk.Label(Root, text="You are invincible for a second after losing a life.")

    if Type == 1:
        MenuTitle.pack()
        HighScoreLabel.pack()
        Image.pack()
        Rule1.pack()
        Rule2.pack()
        Rule3.pack()
        Rule4.pack()
        Rule5.pack()
        Rule6.pack()
        Rule7.pack()
        StartButton.pack()
        ExitButton.pack()
    if Type == 2:
        MenuTitle.pack()
        HighScoreLabel.pack()
        YourScore.pack()
        Image.pack()
        StartButton["text"] = "Try Again"
        StartButton.pack()
        ExitButton.pack()
    if Type == 3:
        MenuTitle.pack()
        HighScoreLabel.pack()
        YourScore.pack()
        Image.pack()
        StartButton["text"] = "Play Again"
        StartButton.pack()
        ExitButton.pack()

    Root.mainloop()


######################################################
# Destroys the menu and starts the game

def StartGame():
    Root.destroy()
    Game()


######################################################
# Destroys the menu and exits the program

def Exit():
    Root.destroy()
    sys.exit()


######################################################
# Main game function containing the main loop
# Begins by creating sprite groups and assigning variables to control the loop
# some variables are assigned here since they must be rest if a new game is started

def Game():
    pygame.mixer.music.load("music.wav")
    pygame.mixer.music.play(-1)

    Done = False

    PlayerBulletsList = pygame.sprite.Group()
    EnemyBulletsList = pygame.sprite.Group()
    SpritesList = pygame.sprite.Group()
    Wave = pygame.sprite.Group()
    BossWave = pygame.sprite.Group()

    Player1 = Player(0, 900)
    SpritesList.add(Player1)

    pygame.mouse.set_visible(False)

    Score = 0
    EnemyCounter = 0
    BossHealth = 30
    Lives = 3
    Invincible = False

    HighscoreFileRead = open("highscore.txt", "r")
    Highscore = HighscoreFileRead.read()

    Pew = LoadSound("pew.wav")
    Explosion = LoadSound("explosion.wav")
    BossArrives = LoadSound("bossarrives.wav")
    BigExplosion = LoadSound("bigexplosion.wav")
    Win = LoadSound("win.wav")

    while not Done:
        # finds the mouse position for the player movement
        MousePos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Done = True

            elif event.type == pygame.MOUSEBUTTONDOWN and len(PlayerBulletsList) < 5:
                # spawns player bullets at player sprite location
                Pew.play()
                PlayerBulletsList.add(PlayerBullet(MousePos[0], MousePos[1]))
                print("click")

            elif event.type == EnemyShoot:
                # spawns enemy bullets on a timer at their sprite locations
                # spawns multiple bullets for boss attack pattern
                for E in Wave:
                    EnemyBulletsList.add(EnemyBullet(E.rect.x + 20, E.rect.y + 80))
                for B in BossWave:
                    for n in range(0, 700, 35):
                        EnemyBulletsList.add(EnemyBullet(B.rect.x + n, 160))

            elif len(Wave) < 5 and event.type == EnemySpawn and EnemyCounter <= 50:
                # spawns random enemy if there are less than 5 onscreen and less than 50 total have been spawned
                EnemyCounter += 1
                I = random.randint(1, 5)
                print("adding to wave")
                if I == 1:
                    RandEnemy1 = Enemy(700, random.randint(1, 500), 1)
                    Wave.add(RandEnemy1)
                elif I == 2:
                    RandEnemy2 = Enemy(-80, random.randint(1, 500), 2)
                    Wave.add(RandEnemy2)
                elif I == 3:
                    RandEnemy3 = Enemy(random.randint(0, 350 - EWidth), -EWidth, 3)
                    Wave.add(RandEnemy3)
                elif I == 4:
                    RandEnemy4 = Enemy(random.randint(350, 700 - EWidth), -EWidth, 4)
                    Wave.add(RandEnemy4)
                elif I == 5:
                    RandEnemy5 = Enemy(random.randint(0, 700 - EWidth), -EWidth, 5)
                    Wave.add(RandEnemy5)

            if 15 > BossHealth > 0 and len(Wave) < 10:
                # spawns enemies for boss fight phase 2
                if event.type == EnemySpawn:
                    RandEnemy3 = Enemy(-EWidth, random.randint(150, 300), 3)
                    Wave.add(RandEnemy3)
                if event.type == EnemySpawn:
                    RandEnemy4 = Enemy(700, random.randint(150, 300), 4)
                    Wave.add(RandEnemy4)

            if event.type == Invincibility:
                # returns the player to being not invincible after a second
                Invincible = False
                pygame.time.set_timer(Invincibility, 0)

        for B in PlayerBulletsList:
            # PLayer bullet collisions
            Kills = pygame.sprite.spritecollide(B, Wave, True)
            for item in Kills:
                B.kill()
                Score += 1
            BulletCollisions = pygame.sprite.spritecollide(B, EnemyBulletsList, True)
            for item in BulletCollisions:
                B.kill()
            BossHits = pygame.sprite.spritecollide(B, BossWave, False)
            for item in BossHits:
                BossHealth -= 1
                B.kill()

        for B in EnemyBulletsList:
            # enemy bullet collisions
            if not Invincible:
                LivesLost = pygame.sprite.spritecollide(Player1, EnemyBulletsList, True)
                for item in LivesLost:
                    B.kill()
                    Lives -= 1
                    Explosion.play()
                    Invincible = True
                    pygame.time.set_timer(Invincibility, 1000)

        for En in Wave:
            # player and enemy sprite collisions
            if not Invincible:
                PlayerEnemyCollisions = pygame.sprite.spritecollide(Player1, Wave, True)
                for item in PlayerEnemyCollisions:
                    Lives -= 1
                    Explosion.play()
                    En.kill()
                    Invincible = True
                    pygame.time.set_timer(Invincibility, 1000)

        if EnemyCounter == 50:
            # spawns boss once 50 enemies have been spawned
            BossArrives.play()
            pygame.mixer.music.load("bossmusic.wav")
            pygame.mixer.music.play(-1)
            EnemyCounter += 1
            print("adding boss")
            Boss1 = Boss(5, -179)
            BossWave.add(Boss1)

        if BossHealth == 0:
            # Victory condition
            # awards points and saves highscore
            # opens victory menu
            print("boss kill")
            for B in BossWave:
                B.kill()
            Score += 20
            Done = True
            pygame.mixer.music.stop()
            Win.play()
            if Score > int(Highscore):
                HighscoreFileWrite = open("highscore.txt", "w")
                HighscoreFileWrite.write(str(Score))
                HighscoreFileWrite.close()
            Menu("VICTORY!", "image3.png", str(Score), 3)

        if Lives <= 0:
            # Game Over condition
            # saves highscore
            # opens Game Over screen
            Player1.kill()
            Done = True
            print("player dead")
            pygame.mixer.music.stop()
            BigExplosion.play()
            if Score > int(Highscore):
                HighscoreFileWrite = open("highscore.txt", "w")
                HighscoreFileWrite.write(str(Score))
                HighscoreFileWrite.close()
            Menu("GAME OVER", "enemy.png", str(Score), 2)

        ######################################################
        # updating all the sprites

        SpritesList.update()
        PlayerBulletsList.update()
        BossWave.update()
        Wave.update()
        EnemyBulletsList.update()

        ######################################################
        # drawing everything
        # if the player beats the highscore, the new highscore is written to the file
        # this means the highscore will be retained between games

        Screen.fill((255, 255, 255))
        Screen.blit(LoadImage("background.png"), (0, 0))
        SpritesList.draw(Screen)
        PlayerBulletsList.draw(Screen)
        Wave.draw(Screen)
        BossWave.draw(Screen)
        EnemyBulletsList.draw(Screen)

        ScoreDisplay = Font.render("Score: " + str(Score), 1, (0, 0, 0), (255, 255, 255))
        Screen.blit(ScoreDisplay, (10, 10))
        LivesDisplay = Font.render("Lives: " + str(Lives), 1, (0, 0, 0), (255, 255, 255))
        Screen.blit(LivesDisplay, (600, 10))
        HScoreDisplay = Font.render("Highscore: " + str(Highscore), 1, (0, 0, 0), (255, 255, 255))
        Screen.blit(HScoreDisplay, (10, 30))

        pygame.display.flip()
        clock.tick(60)

######################################################
# defines the Done variable
# opens the main menu which will lead to main game loop


Done = True
Menu("MAIN MENU", "image3.png", str(0), 1)
