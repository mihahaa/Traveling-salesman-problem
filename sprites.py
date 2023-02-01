import math
import random
import sys

import pygame
import os
import config
from heapq import heapify
from heapq import heappop
from heapq import heappush
from itertools import permutations


class BaseSprite(pygame.sprite.Sprite):
    images = dict()

    def __init__(self, x, y, file_name, transparent_color=None, wid=config.SPRITE_SIZE, hei=config.SPRITE_SIZE):
        pygame.sprite.Sprite.__init__(self)
        if file_name in BaseSprite.images:
            self.image = BaseSprite.images[file_name]
        else:
            self.image = pygame.image.load(os.path.join(config.IMG_FOLDER, file_name)).convert()
            self.image = pygame.transform.scale(self.image, (wid, hei))
            BaseSprite.images[file_name] = self.image
        # making the image transparent (if needed)
        if transparent_color:
            self.image.set_colorkey(transparent_color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)


class Surface(BaseSprite):
    def __init__(self):
        super(Surface, self).__init__(0, 0, 'terrain.png', None, config.WIDTH, config.HEIGHT)


class Coin(BaseSprite):
    def __init__(self, x, y, ident):
        self.ident = ident
        super(Coin, self).__init__(x, y, 'coin.png', config.DARK_GREEN)

    def get_ident(self):
        return self.ident

    def position(self):
        return self.rect.x, self.rect.y

    def draw(self, screen):
        text = config.COIN_FONT.render(f'{self.ident}', True, config.BLACK)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)


class CollectedCoin(BaseSprite):
    def __init__(self, coin):
        self.ident = coin.ident
        super(CollectedCoin, self).__init__(coin.rect.x, coin.rect.y, 'collected_coin.png', config.DARK_GREEN)

    def draw(self, screen):
        text = config.COIN_FONT.render(f'{self.ident}', True, config.RED)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)


class Agent(BaseSprite):
    def __init__(self, x, y, file_name):
        super(Agent, self).__init__(x, y, file_name, config.DARK_GREEN)
        self.x = self.rect.x
        self.y = self.rect.y
        self.step = None
        self.travelling = False
        self.destinationX = 0
        self.destinationY = 0

    def set_destination(self, x, y):
        self.destinationX = x
        self.destinationY = y
        self.step = [self.destinationX - self.x, self.destinationY - self.y]
        magnitude = math.sqrt(self.step[0] ** 2 + self.step[1] ** 2)
        self.step[0] /= magnitude
        self.step[1] /= magnitude
        self.step[0] *= config.TRAVEL_SPEED
        self.step[1] *= config.TRAVEL_SPEED
        self.travelling = True

    def move_one_step(self):
        if not self.travelling:
            return
        self.x += self.step[0]
        self.y += self.step[1]
        self.rect.x = self.x
        self.rect.y = self.y
        if abs(self.x - self.destinationX) < abs(self.step[0]) and abs(self.y - self.destinationY) < abs(self.step[1]):
            self.rect.x = self.destinationX
            self.rect.y = self.destinationY
            self.x = self.destinationX
            self.y = self.destinationY
            self.travelling = False

    def is_travelling(self):
        return self.travelling

    def place_to(self, position):
        self.x = self.destinationX = self.rect.x = position[0]
        self.y = self.destinationX = self.rect.y = position[1]

    # coin_distance - cost matrix
    # return value - list of coin identifiers (containing 0 as first and last element, as well)
    def get_agent_path(self, coin_distance):
        pass


class ExampleAgent(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        path = [i for i in range(1, len(coin_distance))]
        random.shuffle(path)
        return [0] + path + [0]


class Aki(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        def takefirst(elem):
            return elem[0]

        def takesec(elem):
            return elem[1]

        visit = list()
        visit.append(0)
        path = list()
        while 1:
            if len(path) == len(coin_distance):
                break
            now = visit.pop()
            path.append(now)
            sad = list()
            for i in range(len(coin_distance[now])):
                sad.append([coin_distance[now][i], i])
            sad.sort(key=takesec, reverse=True)
            sad.sort(key=takefirst, reverse=True)
            for i in range(len(sad)):
                if not (sad[i][1] in path):
                    visit.append(sad[i][1])
        path.append(0)
        return path


class Jocke(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        sad = list()
        minim = sys.maxsize
        mini = -1
        for i in range(len(coin_distance) - 1):
            sad.append(i)
        perm = permutations(sad)
        for i in list(perm):
            sumica = 0
            prev = -1
            for j in list(i):
                if prev == -1:
                    sumica = sumica + coin_distance[0][j + 1]
                    prev = j
                else:
                    sumica = sumica + coin_distance[prev + 1][j + 1]
                    prev = j
            sumica = sumica + coin_distance[0][prev + 1]
            if sumica < minim:
                minim = sumica
                mini = i
        sol = list()
        sol.append(0)
        for i in mini:
            sol.append(i + 1)
        sol.append(0)
        return sol


class Uki(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        h = list()
        heapify(h)
        tmp=list()
        tmp.append(0)
        for i in range(len(coin_distance)-1):
            heappush(h,(coin_distance[0][i+1],0,i+1,tmp))
        while 1:
            now=heappop(h)
            if len(list(now[3]))==(len(coin_distance)+1):
                break
            if len(list(now[3]))==len(coin_distance):
                tmp = list(now[3]).copy()
                tmp.append(0)
                heappush(h, (now[0] + coin_distance[0][now[2]], now[1] - 1, i, tmp))
            else:
                for i in range(len(coin_distance)):
                    if ((i!=now[2]) or (i==now[2] and len(list(now[3]))==len(coin_distance)-1)) and not(i in list(now[3])):
                        tmp=list(now[3]).copy()
                        tmp.append(now[2])
                        heappush(h,(now[0]+coin_distance[i][now[2]],now[1]-1,i,tmp))
        return list(now[3])

class Micko(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)


    def get_agent_path(self, coin_distance):
        sve=list()
        q=0
        w=0
        for i in coin_distance:
            q=0
            for j in i:
                if j!=0 and q<w:
                    sve.append((j,q,w))
                q=q+1
            w=w+1
        sve.sort()

        def prim(cvorovi):
            dodatni=list()
            mst=0
            dodatni.append(0)
            while len(dodatni)+len(cvorovi)<len(coin_distance):
                for i in sve:
                    if i[1] in dodatni and i[2] not in dodatni and i[2] not in cvorovi:
                        dodatni.append(i[2])
                        mst=mst+i[0]
                        break
                    if i[2] in dodatni and i[1] not in dodatni and i[1] not in cvorovi:
                        dodatni.append(i[1])
                        mst=mst+i[0]
                        break
            return mst

        h=list()
        heapify(h)
        tmp = list()
        tmp.append(0)
        tmp2=list()
        for i in range(len(coin_distance) - 1):
            heappush(h, (coin_distance[0][i + 1]+prim(tmp2), 0, i + 1, tmp,tmp2))
        while 1:
            now = heappop(h)
            if len(list(now[3])) == (len(coin_distance) + 1):
                break
            if len(list(now[3])) == len(coin_distance):
                tmp = list(now[3]).copy()
                tmp2=list(now[4]).copy()
                tmp2.append(0)
                tmp.append(0)
                heappush(h, (now[0] + coin_distance[0][now[2]]+prim(tmp2), now[1] - 1, i, tmp,tmp2))
            else:
                for i in range(len(coin_distance)):
                    if ((i != now[2]) or (i == now[2] and len(list(now[3])) == len(coin_distance) - 1)) and not (
                            i in list(now[3])):
                        tmp = list(now[3]).copy()
                        tmp2 = list(now[4]).copy()
                        tmp2.append(now[2])
                        tmp.append(now[2])
                        heappush(h, (now[0] + coin_distance[i][now[2]]+prim(tmp2), now[1] - 1, i, tmp,tmp2))
        return list(now[3])

