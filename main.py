import threading
import pygame
import pytmx
import random

from time import sleep


def draw_map(map, window):
    for layer in map.visible_layers:
        for x, y, gid, in layer:
            tile = map.get_tile_image_by_gid(gid)
            if tile is not None:
                window.blit(tile, (x * gameMap.tilewidth, y * gameMap.tileheight))


def is_car_coming(vehicleList, dir):  # function checks if there is a car front of traffic lights
    for v in vehicleList:
        if v[1][dir] >= 320:  # dir = 1 is A, dir = 0 is B direction.
            return True
    return False


def case_to_char(arg):
    if arg == [False, False]:
        return 'a'
    if arg == [True, False]:
        return 'b'
    if arg == [False, True]:
        return 'c'
    if arg == [True, True]:
        return 'd'


def next_state(arg, cur_state):
    switcher = {'a': 0, 'b': 0, 'c': 0, 'd': 0}
    if cur_state == 0:
        switcher = {'a': 1, 'b': 1, 'c': 3, 'd': 1}
    if cur_state == 1:
        switcher = {'a': 1, 'b': 2, 'c': 3, 'd': 2}
    if cur_state == 2:
        switcher = {'a': 2, 'b': 1, 'c': 3, 'd': 3}
    if cur_state == 3:
        switcher = {'a': 1, 'b': 1, 'c': 4, 'd': 1}
    if cur_state == 4:
        switcher = {'a': 1, 'b': 1, 'c': 4, 'd': 1}
    return switcher.get(arg, "nothing")


class TrafficLight(threading.Thread):
    def __init__(self, is_traffic, args=(), kwargs=None):
        threading.Thread.__init__(self, args=(), kwargs=None)
        self.is_traffic = is_traffic
        self.daemon = True
        self.traffic_lights = [args[0], args[1]]
        self.cur_state = 0

    def run(self):
        while True:
            val = self.is_traffic
            symbol = case_to_char(val)
            self.change_state(next_state(arg=symbol, cur_state=self.cur_state))

    def do_cycle(self, dir):
        for i in range(4):
            self.traffic_lights[dir] = i
            sleep(2)
        sleep(3)
        for i in range(3, -1, -1):
            if i == 1:
                continue
            self.traffic_lights[dir] = i
            sleep(2)

    def change_state(self, state):
        if state == 0:
            self.traffic_lights[0] = 0
            self.traffic_lights[1] = 0
        elif state == 1:
            self.traffic_lights[1] = 0
            self.do_cycle(0)
        elif state == 2:
            self.traffic_lights[1] = 0
            self.do_cycle(0)
        elif state == 3:
            self.traffic_lights[0] = 0
            self.do_cycle(1)
        elif state == 4:
            self.traffic_lights[0] = 0
            self.do_cycle(1)
        self.cur_state = state

    def get_tl_val(self):
        return self.traffic_lights


pygame.init()
display = pygame.display.set_mode((640, 640))
clock = pygame.time.Clock()
gameMap = pytmx.load_pygame("resources/mymap.tmx")

# images
tlPost = pygame.image.load("resources/post.png")
trafficLight = [pygame.image.load("resources/frame_01.png"), pygame.image.load("resources/frame_02.png"),
                pygame.image.load("resources/frame_03.png"), pygame.image.load("resources/frame_04.png")]
car = [pygame.image.load("resources/car_01.png"), pygame.image.load("resources/car_02.png"),
       pygame.image.load("resources/car_03.png"), pygame.image.load("resources/car_04.png")]
vehicleList = [[], []]
pygame.display.set_icon(trafficLight[3])
pygame.display.set_caption('Intersection simulator')

tl = [0, 0]  # state of the traffic lights A, B

tlCoord = [(32 * 11, 32 * 9 + 20), (32 * 11, 32 * 6 + 20)]
t = TrafficLight(None, args=(tl[0], tl[1],))
t.start()

while True:

    clock.tick(50)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()

    if keys[pygame.K_ESCAPE]:
        quit()
    draw_map(gameMap, display)

    # traffic simulator
    #
    # 1/10 chance of a car spawning
    # 1/3 chance for B direction and 2/3 for A
    #
    #
    if random.randint(0, 10) == 1:  # spawning car
        if random.randint(0, 2) == 0:  # B direction
            vehicleList[0].append([pygame.transform.rotate(car[random.randint(0, 3)], 90), [32 * 19, 32 * 9]])
        else:  # A direction
            vehicleList[1].append([car[random.randint(0, 3)], [32 * 10, 32 * 19]])

    vehicleList[0] = vehicleList[0][:9]
    vehicleList[1] = vehicleList[1][:9]

    for i in range(2):
        prev_vehicle_pos = -64
        for vehicle in vehicleList[i]:
            display.blit(vehicle[0], vehicle[1])  # vehicle[0] = image, vehicle[1] = coord.
            if (vehicle[1][i] == 352 and tl[i] in [0, 1, 2]) or prev_vehicle_pos + 32 == vehicle[1][i]:  # traffic jam
                prev_vehicle_pos = vehicle[1][i]
                continue
            vehicle[1][i] -= 32
        for vehicle in vehicleList[i]:
            if vehicle[1][i] < 0:
                vehicleList[i].remove(vehicle)

    t.is_traffic = [is_car_coming(vehicleList[1], 1), is_car_coming(vehicleList[0], 0)]
    #
    # changing state of traffic lights
    #
    tlVal = t.get_tl_val()
    tl = [tlVal[1], tlVal[0]]
    display.blit(tlPost, tlCoord[0])
    display.blit(trafficLight[tl[1]], tlCoord[0])
    display.blit(tlPost, tlCoord[1])
    display.blit(trafficLight[tl[0]], tlCoord[1])

    pygame.display.update()
