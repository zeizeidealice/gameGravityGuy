#coding=utf-8
from itertools import cycle
import random
import sys
import math
import pygame
from pygame.locals import *

#关于屏幕显示的一些设置，全部命名好以免出现magic number
#LEFT和RIGHT是因为小人稳定的状态会在左边或是右边，所以先设定好方便之后运算
FPS = 30
SCREENWIDTH  = 288
SCREENHEIGHT = 512
INITIAL_TIME = 0

# image, sound and hitmask  dicts
IMAGES, SOUNDS, HITMASKS = {}, {}, {}
LSIDEX = 0
RSIDEX = SCREENWIDTH
LEFTMAX = int(SCREENWIDTH * 0.1)
RIGHTMAX = int(SCREENWIDTH * 0.73)
'''
LEFT = 1
RIGHT = 0
'''

LEFT = 1
RIGHT = -1


starGap = 0
leftStarX = 0
rightStarX = 0
b1Gap = 0
lb1X = 0
rb1X = 0
#这几个list就像衣柜一样，之后选皮肤直接拿出一套换装
PLAYERS_LIST = (
    # running guy
    'assets/sprites/guy1.png',
    'assets/sprites/guy2.png',
    'assets/sprites/guy3.png',
    'assets/sprites/guy2.png',
)

# list of backgrounds
BACKGROUNDS_LIST = (
    'assets/sprites/background-1.png',
    'assets/sprites/background-2.png',
    'assets/sprites/background-3.png',
    'assets/sprites/background-4.png',
    'assets/sprites/background-5.png',
    'assets/sprites/background-6.png',
    'assets/sprites/background-7.png',
)

# list of barriers
BARRIERS_LIST = (
    'assets/sprites/lbarrier1.png',
    'assets/sprites/lbarrier1.png',
)

try:
    xrange
except NameError:
    xrange = range

def main():
    global SCREEN, FPSCLOCK, INITIAL_TIME
    pygame.init()

    FPSCLOCK = pygame.time.Clock()
    SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
    pygame.display.set_caption('Gravity Guy')

    # sounds
    if 'win' in sys.platform:
        soundExt = '.wav'
    else:
        soundExt = '.ogg'

    SOUNDS['die']    = pygame.mixer.Sound('assets/audio/die' + soundExt)
    SOUNDS['hit']    = pygame.mixer.Sound('assets/audio/hit' + soundExt)
    SOUNDS['point']  = pygame.mixer.Sound('assets/audio/point' + soundExt)
    SOUNDS['swoosh'] = pygame.mixer.Sound('assets/audio/swoosh' + soundExt)
    SOUNDS['wing']   = pygame.mixer.Sound('assets/audio/wing' + soundExt)

    # numbers sprites for score display
    IMAGES['numbers'] = (
        pygame.image.load('assets/sprites/0.png').convert_alpha(),
        pygame.image.load('assets/sprites/1.png').convert_alpha(),
        pygame.image.load('assets/sprites/2.png').convert_alpha(),
        pygame.image.load('assets/sprites/3.png').convert_alpha(),
        pygame.image.load('assets/sprites/4.png').convert_alpha(),
        pygame.image.load('assets/sprites/5.png').convert_alpha(),
        pygame.image.load('assets/sprites/6.png').convert_alpha(),
        pygame.image.load('assets/sprites/7.png').convert_alpha(),
        pygame.image.load('assets/sprites/8.png').convert_alpha(),
        pygame.image.load('assets/sprites/9.png').convert_alpha()
    )
     # message sprite for welcome screen
    IMAGES['message'] = pygame.image.load('assets/sprites/message.png').convert_alpha()
     # borders
    IMAGES['lside'] = pygame.image.load('assets/sprites/lside.png').convert_alpha()
    IMAGES['rside'] = pygame.image.load('assets/sprites/rside.png').convert_alpha()
     # star
    IMAGES['star'] = pygame.image.load('assets/sprites/star.png').convert_alpha()
     # barriers
    IMAGES['barriers'] = (
        pygame.image.load('assets/sprites/lbarrier1.png').convert_alpha(),
        pygame.image.load('assets/sprites/rbarrier1.png').convert_alpha(),
        )
    IMAGES['mbarrier'] = pygame.image.load('assets/sprites/mbarrier.png').convert_alpha()
     # stick
    IMAGES['stick'] = pygame.image.load('assets/sprites/stick.png').convert_alpha()
    IMAGES['ghost'] = pygame.image.load('assets/sprites/ghost.png').convert_alpha()
    IMAGES['ghost'] = pygame.transform.scale(IMAGES['ghost'],(64,64))

    while True:
        # select random background sprites
        randBg = random.randint(0, len(BACKGROUNDS_LIST) - 1)
        IMAGES['background'] = pygame.image.load(BACKGROUNDS_LIST[randBg]).convert()
        # game over pic
        IMAGES['gameover'] = pygame.image.load(
            BACKGROUNDS_LIST[randBg]).convert_alpha()
        # player sprites
        IMAGES['player'] = [
            pygame.image.load(PLAYERS_LIST[0]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[1]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[2]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[3]).convert_alpha(),
        ]
        # hismask for barriers
        HITMASKS['barrier'] = (
            getHitmask(IMAGES['barriers'][0]),
            getHitmask(IMAGES['barriers'][1]),
            getHitmask(IMAGES['mbarrier'])
        )
        # hitmask for player
        HITMASKS['player'] = (
            getHitmask(IMAGES['player'][0]),
            getHitmask(IMAGES['player'][1]),
            getHitmask(IMAGES['player'][2]),
            getHitmask(IMAGES['player'][3])
        )
        HITMASKS['star'] = (getHitmask(IMAGES['star']))

        movementInfo = showWelcomeAnimation()
        INITIAL_TIME = pygame.time.get_ticks()
        hitInfo = mainGame(movementInfo)
        sc=showGameOverScreen(hitInfo)
        showGameOver2(sc)


def showWelcomeAnimation():
    playerIndex = 0
    playerIndexGen = cycle([0, 1, 2, 3])
    # iterator used to change playerIndex after every 2 iterations
    loopIter = 0
    playerx = LEFTMAX
    playery = int((SCREENHEIGHT - IMAGES['player'][0].get_height()) / 1.4)

    messagex = int((SCREENWIDTH - IMAGES['message'].get_width()) / 2)
    messagey = int(SCREENHEIGHT * 0.12)

    lsidey = rsidey = 0
    RSIDEX = int(SCREENWIDTH - IMAGES['rside'].get_width())

    playerShmVals = {'val': 0, 'dir': 1}

    SCREEN.blit(IMAGES['background'], (0, 0))
    SCREEN.blit(IMAGES['message'], (messagex, messagey))
    SCREEN.blit(IMAGES['lside'], (LSIDEX, lsidey))
    SCREEN.blit(IMAGES['rside'], (RSIDEX, rsidey))
    pygame.display.update()
    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                # make first flap sound and return values for mainGame
                SOUNDS['wing'].play()
                return {
                    'playerIndexGen': playerIndexGen,
                    'playerx': playerx
                }

        # adjust playery, playerIndex,
        if loopIter % 4 == 0:
            playerIndex = next(playerIndexGen)
        loopIter = (loopIter + 1) % 5
        playerShm(playerShmVals)

        # draw sprites
        SCREEN.blit(IMAGES['background'], (0, 0))
        SCREEN.blit(IMAGES['message'], (messagex, messagey))
        SCREEN.blit(IMAGES['lside'], (LSIDEX, lsidey))
        SCREEN.blit(IMAGES['rside'], (RSIDEX, rsidey))
        pygame.display.update()
        SCREEN.blit(IMAGES['player'][playerIndex],
                    (playerx, playery))

        pygame.display.update()
        FPSCLOCK.tick(FPS)

#游戏主体部分
def mainGame(movementInfo):
    score = playerIndex = loopIter = 0#初始化一下，之后要用
    #movementInfo是从showWelcomeAnimation()返回的字典，有playerx basex和playerIndexGen
    playerIndexGen = movementInfo['playerIndexGen']
    playerx,playery = movementInfo['playerx'],int((SCREENHEIGHT - IMAGES['player'][0].get_height())/1.4)
#这里就是设定小人移动的时候的加速度的，playerVel是小人的当前速度，AccL是往左的加速度，AccR是往右的加速度
    '''
    playerAccL  = -0.5
    playerAccR  =  0.5
    playerVel   =  0
    POSITION = LEFT
    '''
    playerAcc = 0.55
    playerVel = 0
    POSITION = LEFT
    tempAcc = 0



    loopIter = 0
    angel = 0

    lsidey = rsidey = 0
    RSIDEX = int(SCREENWIDTH - IMAGES['rside'].get_width())
    shiftAmount = int(IMAGES['lside'].get_height() - IMAGES['background'].get_height())

    starGap = 3 * IMAGES['star'].get_height()
    leftStarX = IMAGES['lside'].get_width() + IMAGES['barriers'][0].get_width() + 5
    rightStarX = SCREENWIDTH - IMAGES['rside'].get_width() - IMAGES['barriers'][1].get_width() - IMAGES[
        'star'].get_width() - 5
    b1Gap = 4 * IMAGES['barriers'][0].get_height()
    lb1X = IMAGES['lside'].get_width()
    rb1X = SCREENWIDTH - IMAGES['rside'].get_width() - IMAGES['barriers'][1].get_width()
    stickX = (SCREENWIDTH - IMAGES['stick'].get_width()) / 2
    mbX = (SCREENWIDTH - IMAGES['mbarrier'].get_width()) / 2
    stickGap = SCREENHEIGHT / 2
    playerwid = IMAGES['player'][0].get_width()
    stickhig = IMAGES['stick'].get_height()
    playerhig = IMAGES['player'][0].get_height()
    MID = SCREENWIDTH/2

    velY = 3

    leftStary = []
    rightStary = []
    # left/right barrier 1
    lb1y = []
    rb1y = []
    # middle barrier
    mby = []
    sticky = []

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE):
                '''按下空格键表示要换位置，换位置时小人只能在LEFT或者RIGHT上
                然后根据在什么位置判断往哪个方向移动给速度赋值
                '''
                SOUNDS['wing'].play()
                for i in range(4):
                    IMAGES['player'][i] = pygame.transform.flip(IMAGES['player'][i], 1, 0)
                '''
                if POSITION == LEFT:
                    playerVel = playerAccR
                    POSITION = RIGHT
                elif POSITION == RIGHT:
                    playerVel = playerAccL
                    POSITION = LEFT
                    '''
                tempAcc = playerAcc * POSITION
                POSITION = -POSITION


        if (loopIter + 1) % 3 == 0:
            playerIndex = next(playerIndexGen)
        loopIter = (loopIter + 1) % 30
        #这个地方时根据加速度算速度
        '''
        if playerVel > 0:
            playerVel += playerAccR
        elif playerVel < 0:
            playerVel += playerAccL
            '''

        playerVel += tempAcc


        #然后这里是在算小人的位移，要保证小人不能出到屏幕外面，所以取min和max什么的
        #这里先算如果在中间停留什么时候到两边去
        if playerx == stickX or playerx == stickX - playerwid:
            if playerVel == 0:
                '''
                if POSITION == LEFT:
                    playerVel = playerAccL
                else:
                    playerVel = playerAccR
                    '''

                playerVel = -playerAcc * POSITION




                for y in sticky:
                    if (y -  playerhig < playery) and (y +  stickhig > playery):
                        playerVel = 0
                        break
        #这里是算位移，包括了如果碰到中间stick的情况
        if playerVel > 0:
            if (playerx <= stickX - playerwid) and (playerx + min(playerVel,RIGHTMAX - playerx) >= stickX - IMAGES['player'][0].get_width()):
                for y in sticky:
                    if (y < playery) and (y +  stickhig > playery):
                        playerVel = 0
                        playerx = stickX - playerwid
                        break
            playerx += min(playerVel,RIGHTMAX - playerx)
            if playerx == RIGHTMAX:
                playerVel = 0
        elif playerVel < 0:
            if (playerx >= stickX) and (playerx + max(playerVel,LEFTMAX - playerx) <= stickX):
                for y in sticky:
                    if (y < playery) and (y +  stickhig > playery):
                        playerVel = 0
                        playerx = stickX
                        break
            playerx += max(playerVel,LEFTMAX - playerx)
            if playerx == LEFTMAX:
                playerVel = 0

        #更新屏幕
        SCREEN.blit(IMAGES['background'],(0,0))
        SCREEN.blit(IMAGES['player'][playerIndex],(playerx,playery))

        for i in range(len(leftStary)):
            leftStary[i] = leftStary[i] + velY
        for i in range(len(rightStary)):
            rightStary[i] = rightStary[i] + velY
        for i in range(len(lb1y)):
            lb1y[i] = lb1y[i] + velY
        for i in range(len(rb1y)):
            rb1y[i] = rb1y[i] + velY
        for i in range(len(sticky)):
            sticky[i] = sticky[i] + velY
        for i in range(len(mby)):
            mby[i] = mby[i] + 2 * velY



        # delete stars and barriers
        if (len(leftStary) > 0) and (leftStary[0] > SCREENHEIGHT):
            leftStary.pop(0)
        if len(rightStary) > 0 and rightStary[0] > SCREENHEIGHT:
            rightStary.pop(0)
        if len(lb1y) > 0 and lb1y[0] > SCREENHEIGHT:
            lb1y.pop(0)
        if len(rb1y) > 0 and rb1y[0] > SCREENHEIGHT:
            rb1y.pop(0)
        if len(mby) > 0 and mby[0] > SCREENHEIGHT:
            mby.pop(0)
        if len(sticky) > 0 and sticky[0] > SCREENHEIGHT:
            sticky.pop(0)

        # new stars
        if (len(leftStary) == 0) or (len(leftStary) < 4 and leftStary[len(leftStary)-1] > starGap):
            leftStary = leftStary + newthing(starGap)
        if (len(rightStary) == 0) or (len(rightStary) < 4 and rightStary[len(rightStary)-1] > starGap):
            rightStary = rightStary + newthing(starGap)

        # new barriers
        if pygame.time.get_ticks() - INITIAL_TIME > 3000:
            if (len(lb1y) == 0) or (len(lb1y) < 3 and lb1y[len(lb1y)-1] > b1Gap):
                lb1y = lb1y + newthing(b1Gap)
            if (len(rb1y) == 0) or (len(rb1y) < 3 and rb1y[len(rb1y)-1] > b1Gap):
                rb1y = rb1y + newthing(b1Gap)

        # new stick or middle barrier
        if pygame.time.get_ticks() - INITIAL_TIME > 8000:
            if (len(sticky) == 0 or (len(sticky) == 1 and sticky[0] > SCREENHEIGHT/2)) \
            and (len(mby) == 0 or (len(mby) == 1 and mby[0] > SCREENHEIGHT/2)):
                rd = random.randint(1, 2)
                if rd == 1:
                    sticky.append(- random.randint(stickGap/2, stickGap))
                else:
                    mby.append(- random.randint(stickGap/2, stickGap))

        # update loopIter
        loopIter = (loopIter + 1) % 30
        temp = shiftAmount + lsidey
        temp = (temp + velY) % shiftAmount
        lsidey = rsidey = temp - shiftAmount

        starhig=IMAGES['star'].get_height()
        #检查星星
        if playerx <= LEFTMAX:
            flag=0
            for y in range(len(leftStary)):
                if (leftStary[y - 1] - playerhig <= playery) and (leftStary[y - 1] >= playery-starhig):
                    leftStary.pop(y - 1)
                    flag=1
                if flag:
                    score+=1
                    SOUNDS['point'].play()
                    break

        elif playerx + playerwid/2 >= RIGHTMAX:
            flag = 0
            for y in range(len(rightStary)):
                if (rightStary[y - 1] - playerhig <= playery) and (rightStary[y - 1] >= playery-starhig):
                    rightStary.pop(y - 1)
                    flag=1
                if flag:
                    score+=1
                    SOUNDS['point'].play()
                    break

        #检查碰撞
        lbhig=IMAGES['barriers'][0].get_height()
        if playerx <= LEFTMAX:
            #flag=0
            for y in range(len(lb1y)):
                if (lb1y[y - 1] - playerhig <= playery) and (lb1y[y - 1] >= playery-lbhig):
                    lb1y.pop(y - 1)
                    SOUNDS['hit'].play()
                    return {
                    'x': playerx,
                    'y': playery,
                    'leftStary': leftStary,
                    'rightStary': rightStary,
                    'lb1y':lb1y,
                    'rb1y': rb1y,
                    'lsidey': lsidey,
                    'rsidey':rsidey,
                    'score': score
                }

        elif playerx + playerwid/2 >= RIGHTMAX+10:
            flag = 0
            for y in range(len(rb1y)):
                if (rb1y[y - 1] - playerhig <= playery) and (rb1y[y - 1] >= playery -lbhig):
                    rb1y.pop(y - 1)
                    SOUNDS['hit'].play()
                    return {
                    'x': playerx,
                    'y': playery,
                    'leftStary': leftStary,
                    'rightStary': rightStary,
                    'lb1y':lb1y,
                    'rb1y': rb1y,
                    'lsidey': lsidey,
                    'rsidey':rsidey,
                    'score': score
                }

        #检查中间飞盘
        mbhig=IMAGES['mbarrier'].get_height()
        if (playerx <= MID) and (playerx + playerwid >= MID):
            for y in range(len(mby)):
                if (mby[y - 1] - playerhig <= playery) and (mby[y - 1] + velY >= playery - mbhig):
                    mby.pop(y - 1)
                    SOUNDS['hit'].play()
                    return {
                    'x': playerx,
                    'y': playery,
                    'leftStary': leftStary,
                    'rightStary': rightStary,
                    'lb1y':lb1y,
                    'rb1y': rb1y,
                    'lsidey': lsidey,
                    'rsidey':rsidey,
                    'score': score
                }

        # draw sprites
        SCREEN.blit(IMAGES['lside'], (LSIDEX, lsidey))
        SCREEN.blit(IMAGES['rside'], (RSIDEX, rsidey))

        for ls in leftStary:
            SCREEN.blit(IMAGES['star'], (leftStarX, ls))
        for rs in rightStary:
            SCREEN.blit(IMAGES['star'], (rightStarX, rs))

        for lb in lb1y:
            SCREEN.blit(IMAGES['barriers'][0], (lb1X, lb))
        for rb in rb1y:
            SCREEN.blit(IMAGES['barriers'][1], (rb1X, rb))

        showScore(score)

        if len(sticky) > 0:
            for st in sticky:
                SCREEN.blit(IMAGES['stick'], (stickX, st))
        angel = (angel + 15) % 90
        dx = 15 * (2 ** 0.5) * math.sin(float(angel + 45) / 180 * math.pi) - 15
        if len(mby) > 0:
            for mb in mby:
                SCREEN.blit(pygame.transform.rotate(IMAGES['mbarrier'], angel), (mbX - dx, mb - dx))
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def newthing(gap):
    templist = []
    firsty = random.randint(gap, 2 * gap)
    num = random.randint(2, 3)
    for i in range(num):
        templist.append(-(firsty + i * gap))
    return templist

#后面不用管，随便写的，还没有试过正不正确毕竟现在不会gameover
def showGameOverScreen(crashInfo):
    """crashes the player down ans shows gameover image"""
    score = crashInfo['score']
    SOUNDS['die'].play()
    playerx = crashInfo['x']
    playery = crashInfo['y']
    playerHeight = IMAGES['ghost'].get_height()
    playerVelY = 0
    playerAccY = 2

    leftStary, rightStary, lb1y, rb1y = crashInfo['leftStary'], crashInfo['rightStary'],crashInfo['lb1y'], crashInfo['rb1y']
    lsidey,rsidey=crashInfo['lsidey'],crashInfo['rsidey']
    RSIDEX = int(SCREENWIDTH - IMAGES['rside'].get_width())
    leftStarX = IMAGES['lside'].get_width() + IMAGES['barriers'][0].get_width() + 5
    rightStarX = SCREENWIDTH - IMAGES['rside'].get_width() - IMAGES['barriers'][1].get_width() - IMAGES[
        'star'].get_width() - 5
    lb1X = IMAGES['lside'].get_width()
    rb1X = SCREENWIDTH - IMAGES['rside'].get_width() - IMAGES['barriers'][1].get_width()
    # play hit and die sounds
    #SOUNDS['hit'].play()#####可以使用
    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):####还没落地就返回
                if playery + playerHeight<=0 :
                    return score
#####完成升天
        # player y shift
        if playery + playerHeight > 0:
            playery -= playerVelY

        # player velocity change
        if playerVelY < 10:
            playerVelY += playerAccY


        # draw sprites
        SCREEN.blit(IMAGES['background'], (0,0))

        # draw sprites
        SCREEN.blit(IMAGES['lside'], (LSIDEX, lsidey))
        SCREEN.blit(IMAGES['rside'], (RSIDEX, rsidey))

        for ls in leftStary:
            SCREEN.blit(IMAGES['star'], (leftStarX, ls))
        for rs in rightStary:
            SCREEN.blit(IMAGES['star'], (rightStarX, rs))

        for lb in lb1y:
            SCREEN.blit(IMAGES['barriers'][0], (lb1X, lb))
        for rb in rb1y:
            SCREEN.blit(IMAGES['barriers'][1], (rb1X, rb))

        showScore(score)

        SCREEN.blit(IMAGES['ghost'], (playerx,playery))
        pygame.display.update()
        FPSCLOCK.tick(FPS)
        if playery + playerHeight<=0 :
            return score




def showGameOver2(score):
     ###下面是最后显示出gameover图标
    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):####还没落地就返回
                return
        SCREEN.blit(IMAGES['background'], (0, 0))
        gameoverx = int((SCREENWIDTH - IMAGES['message'].get_width()) / 2)
        gameovery = int(SCREENHEIGHT * 0.2)
        SCREEN.blit(IMAGES['gameover'], (gameoverx, gameovery))
        showScore2(score)
        FPSCLOCK.tick(FPS)
        pygame.display.update()

def playerShm(playerShm):
    """oscillates the value of playerShm['val'] between 8 and -8"""
    if abs(playerShm['val']) == 8:
        playerShm['dir'] *= -1

    if playerShm['dir'] == 1:
         playerShm['val'] += 1
    else:
        playerShm['val'] -= 1

def showScore(score):
    """displays score in center of screen"""
    scoreDigits = [int(x) for x in list(str(score))]
    totalWidth = 0 # total width of all numbers to be printed

    for digit in scoreDigits:
        totalWidth += IMAGES['numbers'][digit].get_width()

    Xoffset = (SCREENWIDTH - totalWidth) / 2

    for digit in scoreDigits:
        SCREEN.blit(IMAGES['numbers'][digit], (Xoffset, SCREENHEIGHT * 0.1))
        Xoffset += IMAGES['numbers'][digit].get_width()

def showScore2(score):
    """displays score in bottom of screen"""
    scoreDigits = [int(x) for x in list(str(score))]
    totalWidth = 0 # total width of all numbers to be printed

    for digit in scoreDigits:
        totalWidth += IMAGES['numbers'][digit].get_width()

    Xoffset = (SCREENWIDTH - totalWidth) / 2

    for digit in scoreDigits:
        SCREEN.blit(IMAGES['numbers'][digit], (Xoffset, SCREENHEIGHT * 0.6))
        Xoffset += IMAGES['numbers'][digit].get_width()

def getHitmask(image):
    """returns a hitmask using an image's alpha."""
    mask = []
    for x in xrange(image.get_width()):
        mask.append([])
        for y in xrange(image.get_height()):
            mask[x].append(bool(image.get_at((x,y))[3]))
    return mask

if __name__ == '__main__':
    main()