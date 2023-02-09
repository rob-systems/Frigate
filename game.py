#Imports
import pygame, sys
from shapely.geometry import Point, Polygon
from pygame.locals import *
import random, time, math

class TimerError(Exception):
    """A custom exception used to report errors in use of Timer class"""

class Timer:
    def __init__(self):
        self._start_time = None

    def start(self):
        """Start a new timer"""
        if self._start_time is not None:
            raise TimerError(f"Timer is running. Use .stop() to stop it")

        self._start_time = time.perf_counter()

    def stop(self):
        """Stop the timer, and report the elapsed time"""
        if self._start_time is None:
            raise TimerError(f"Timer is not running. Use .start() to start it")

        elapsed_time = time.perf_counter() - self._start_time
        self._start_time = None
        print(f"Elapsed time: {elapsed_time:0.4f} seconds")

    def return_elapsed_time(self):
        pass

pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SHIP_POS = (384, 568)
ORIGIN = (400, 300)
font = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 20)
 #entity movement types [enemy, bullet, player] 

def inverted(img):
   inv = pygame.Surface(img.get_rect().size, pygame.SRCALPHA)
   inv.fill((255,255,255,255))
   #BLEND_RGB_SUB
   inv.set_colorkey((0,0,0))
   #inv = inv.convert_alpha()
   inv.blit(img, (0,0), None, BLEND_RGB_SUB)
   return inv

def vector_length(x, y):
    return math.sqrt(x*x + y*y)

def normalize_vector(x, y):
    norm = vector_length(x, y)
    if norm != 0:
        return x/norm, y/norm
    else:
        return x, y

class Island():
    def __init__(self, data):
       super().__init__()
       self.arr_of_coordinates = []
       self.radius = 60
       #self.center = random.randint()
       x0 = random.randint(200, 600)
       y0 = random.randint(0, 200)
       # vary y and x values perpendicular to the circumference of an island
       for i in range(0, 19):
           
           x = x0 + self.radius*math.cos(math.radians(i * 18)) + random.randint(-10, 10)
           y = y0 + self.radius*math.sin(math.radians(i * 18)) + random.randint(-10, 10)
           self.arr_of_coordinates.append((x,y))
       #self.type = "coast"
       #self.side = data
       #self.arr_of_coordinates = []
       #for y in range(0, 30):
       #      randx = random.randint(120, 300) if (self.side == 'left') else random.randint(420, 600)
       #      self.arr_of_coordinates.insert(0, (randx, y * 20))
       #self.arr_of_coordinates.reverse()

    def shift_down(self):
       y = self.arr_of_coordinates[0][1] - 20
       randx = random.randint(120, 300) if (self.side == 'left') else random.randint(420, 600)
       self.arr_of_coordinates.insert(0, (randx, y))
       for x, item in enumerate(self.arr_of_coordinates):
           self.arr_of_coordinates[x] = (item[0], item[1] + 0.5)

    def collision_check(self, player):
        collision = False
        for point in self.arr_of_coordinates:
            if player.rect.collidepoint(point):
                collision = True
            else:
                collision = collision
                
        return collision

    def draw(self, screen):
       #print('hey', self.arr_of_coordinates)
       #pygame.draw.lines(screen, (255,255,255), False, (self.arr_of_coordinates))
       pygame.draw.polygon(screen, (255,255,255), self.arr_of_coordinates, width=0)

class Torpedo(pygame.sprite.Sprite):
    def __init__(self, is_friendly, ownerQ):
        super().__init__()
        self.type = "torpedo"
        self.cur_pos = [float(owner.position[0]), float(owner.position[1])]

    def spawn(self, target_pos, owner_pos):
        pass

class Bullet(pygame.sprite.Sprite):
    def __init__(self, is_friendly, owner):
        super().__init__()
        self.type = "bullet"
        self.cur_pos = [float(owner.position[0]), float(owner.position[1])]
        self.end_pos = None
        self.dx, self.dy = float(0), float(0)
        self.is_friendly = is_friendly

    def spawn(self, target_pos, owner_pos):
        spray = math.ceil(round(math.sqrt(pow(abs(target_pos[0] - owner_pos[0]), 2) + pow(abs(target_pos[1] - owner_pos[1]), 2))) / 5)
        self.end_pos = (target_pos[0] + random.randint(-spray,spray), target_pos[1] + random.randint(-spray,spray))
        raw_dx = ((self.end_pos[0] - owner_pos[0]) / SCREEN_WIDTH) * 10
        raw_dy = ((self.end_pos[1] - owner_pos[1]) / SCREEN_HEIGHT) * 10
        normalized_vector = normalize_vector(raw_dx, raw_dy)
        self.dx = normalized_vector[0]
        self.dy = normalized_vector[1]

    def de_spawn(self, all_sprites):
        all_sprites.remove(self)

    def move(self, all_sprites):
        if not((self.cur_pos[0] <= 0) or self.cur_pos[0] >= SCREEN_WIDTH or self.cur_pos[1] <= 0 or self.cur_pos[1] >= SCREEN_HEIGHT):
           self.cur_pos[0] += self.dx * 10
           self.cur_pos[1] += self.dy * 10
        else:
           self.de_spawn(all_sprites)

    def draw(self, screen):
        #pygame.draw.line(screen, (0, 0, 255), (0, 0 ), (400, 400), 2)
        #self.mask = pygame.mask.from_surface(self.image)
        pygame.draw.line(screen,
                         (255,255,0) if self.is_friendly else (255,0,0),
                         tuple(self.cur_pos),
                         (self.cur_pos[0] + (2 * self.dx), self.cur_pos[1] + (2 * self.dy)))

    
class Heli(pygame.sprite.Sprite):
    def __init__(self, P1):
        super().__init__()
        self.type = "a_enemy"
        self.friendly = False
        self.firing = True
        self.health = 35
        self.dimensions = (32,32)
        self.image = pygame.transform.scale(inverted(pygame.image.load('heli2.png')),self.dimensions)
        self.image_copy = self.image
        self.surf = pygame.Surface(self.dimensions)
        self.start_pos = (random.randint(40, SCREEN_WIDTH - 40), 50)
        self.position = self.start_pos
        self.rect = self.surf.get_rect(center = (self.start_pos))
        self.rect_copy = self.rect
        #self.mask = pygame.mask.from_surface(self.image)
        self.divisor = 1000
        self.normalized_vector = normalize_vector((P1.position[0] - self.start_pos[0]),
                                                  (P1.position[1] - self.start_pos[1]))
        #print(self.normalized_vector)
        self.dx = round(self.normalized_vector[0], 2)
        self.dy = round(self.normalized_vector[1], 2)
        #print(self.rect)
        self.rotation = 0
        

    def move(self, all_sprites):
       # tbc: slow down heli movement when boat is moving
       #print(self.rect.y)
       #print(self.surf.get_rect().y)
       if (self.rect.y + self.surf.get_rect().y > SCREEN_HEIGHT) or (self.rect.y < -50):
          self.dy = -self.dy
       if (self.rect.x + self.surf.get_rect().x > SCREEN_WIDTH) or (self.rect.x < -50):
           self.dx = -self.dx
       self.rect.move_ip(round(self.dx), round(self.dy))
       self.rect_copy = self.rect
       #print(self.dx, self.dy)
       self.position = (self.rect.x, self.rect.y)
       self.rotation += 45
       if self.rotation == 360:
           self.rotation = 0

    def attack(self, all_sprites, player, screen):
        if abs(self.rect.y - player.position[1]) < 150 and abs(self.rect.x - player.position[0]) < 150:
            B1 = Bullet(False, self)
            B1.spawn(player.position, self.position)
            B1.end_pos = player.position
            B1.x_dir = +1 if (player.position[0] > self.position[0]) else -1
            all_sprites.add(B1)

    def take_damage(self, all_sprites, PLAYER):
       self.health -= 1
       if self.health == 0:
           all_sprites.remove(self)
           PLAYER.score += 1000

    def draw(self, screen):
       #print(self.image.get_at((30,10)))
       #print(self.rect)
       me_tuple = (self.image.get_rect()[0], self.image.get_rect()[1])
       self.image = pygame.transform.rotate(self.image_copy, self.rotation)
       self.rect =  self.image.get_rect(center = self.image.get_rect(center = (int(self.position[0]), int(self.position[1]))).center)
       #print(self.rect[0], me_tuple[0], self.rect[1], me_tuple[1])
       #dx, dy = self.rect[0] - me_tuple[0], self.rect[1] - me_tuple[1]
       #print(dx, dy)
       #self.rect.move_ip(round(dx), round(dy))
       self.image.set_colorkey((0, 0, 0, 255))
       screen.blit(self.image, self.rect)
       rect = pygame.Rect(self.position[0] - 20, self.position[1] - 20, 7, self.health)
       pygame.draw.rect(screen, (0,0,0), (self.position[0]-20,self.position[1]-20,7,35))
       pygame.draw.rect(screen, (255,0,0), rect)

class Sub(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.type = "s_enemy"
        self.start_pos = None
        self.rect = None
        self.flash = 0

    def spawn(self, island_polygon):
        island = Polygon(island_polygon)
        Bool = True
        while Bool:
            self.start_pos = (random.randint(40, SCREEN_WIDTH - 40), 10)
            sub_pos = Point(self.start_pos)
            if not sub_pos.within(island):
                Bool = False
        pass

    def update(self):
        self.flash += 1
        if self.flash == 200:
            self.flash = 0

    def move(self, all_sprites):
        pass

    def attack(self, all_sprites, player, screen):
        pass

    def draw(self, screen):
        color = (0,0,0) if self.flash > 40 else (255,0,0)
        self.rect = pygame.draw.circle(screen, color, self.start_pos, 5)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.type = "player"
        self.friendly = True
        self.firing = False
        self.health = 300
        self.score = 0
        self.position = (384.0, 568.0)
        self.last_y = 568
        self.turn = 0
        self.image = inverted(pygame.image.load("ship.png"))
        self.image_copy = self.image
        self.surf = pygame.Surface((32, 64))
        self.rect = self.surf.get_rect(center = (int(self.position[0]), int(self.position[1])))
        self.mask  = pygame.mask.from_surface( self.image )

    def move(self, all_sprites):
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[K_w]:
            self.position = (self.position[0] - math.sin(math.radians(self.turn)) / 2,
                             self.position[1] - math.cos(math.radians(self.turn)) / 2)
        elif pressed_keys[K_s]:
            self.position = (self.position[0] + math.sin(math.radians(self.turn)),
                             self.position[1] + math.cos(math.radians(self.turn)))
        if pressed_keys[K_d]:
            self.turn -= 0.5
            if self.turn == -360:
                self.turn == 0
        elif pressed_keys[K_a]:
            self.turn += 0.5
            if self.turn == 360:
                self.turn == 0

    def spray_bullets(self, all_sprites, mouse_pos, screen):
        B1 = Bullet(True, self)
        B1.spawn(mouse_pos, self.position)
        B1.end_pos = mouse_pos
        B1.x_dir = +1 if (mouse_pos[0] > self.position[0]) else -1
        all_sprites.add(B1)

    def take_damage(self, all_sprites):
        self.health -= 1
        #returns state of game_over
        return True if self.health <= 0 else False

    def draw(self, screen):
        self.image = pygame.transform.rotate(self.image_copy, self.turn)
        self.rect =  self.image.get_rect(center = self.image.get_rect(center = (int(self.position[0]), int(self.position[1]))).center)
        screen.blit(self.image, self.rect)
        self.draw_health_bar(screen)
        self.draw_cursor(screen)

    def draw_health_bar(self, screen):
        screen_rect = pygame.display.get_surface().get_size()
        rect = pygame.Rect(0, screen_rect[1] - 10, self.health, 10)
        pygame.draw.rect(screen, (0,0,0), (0,screen_rect[1] - 10,300,10))
        pygame.draw.rect(screen, (0,0,255), rect)

    def draw_cursor(self, screen):
        white = (255, 255, 255)
        mouse_pos = pygame.mouse.get_pos()
        pygame.draw.line(screen,white,(mouse_pos[0] + 5, mouse_pos[1]),(mouse_pos[0] + 10, mouse_pos[1]))
        pygame.draw.line(screen,white,(mouse_pos[0] - 5, mouse_pos[1]),(mouse_pos[0] - 10, mouse_pos[1]))
        pygame.draw.line(screen,white,(mouse_pos[0], mouse_pos[1] + 5),(mouse_pos[0], mouse_pos[1] + 10))
        pygame.draw.line(screen,white,(mouse_pos[0], mouse_pos[1] - 5),(mouse_pos[0], mouse_pos[1] - 10))

def rearrange_sprites(sprite_list):
    last_item = None
    bullets = []
    for sprite in sprite_list.sprites():
        if sprite.type == "player":
            sprite_list.remove(sprite)
            last_item = sprite
        elif sprite.type == "bullet":
            sprite_list.remove(sprite)
            bullets.append(sprite)
    sprite_list.add(last_item)
    sprite_list.add(bullets)

# define a main function
def main():
    game_over = False
    #timer.start()
    # load and set the logo
    logo = pygame.image.load("logo32x32.png")
    pygame.display.set_icon(logo)
    pygame.display.set_caption("minimal program")

    # hide cursor
    pygame.mouse.set_visible(False)
     
    # create a surface on screen that has the size of 500 x 500
    screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))

    P1 = Player()
    H1 = Heli(P1)
    H2 = Heli(P1)
    H3 = Heli(P1)

    I1 = Island('left')
    #C2 = Coast('right')

    S1 = Sub()
    S1.spawn(I1.arr_of_coordinates)

    all_sprites = pygame.sprite.Group()
    all_sprites.add(P1)
    all_sprites.add(H1)
    all_sprites.add(H2)
    all_sprites.add(H3)
    all_sprites.add(S1)
    # define a variable to control the main loop
    running = True

    # main loop
    while running:
        if game_over is False:  
            # event handling, gets all event from the event queue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                   P1.firing = True
                if event.type == pygame.MOUSEBUTTONUP:
                   P1.firing = False
            
            if P1.firing == True:
                P1.spray_bullets(all_sprites, pygame.mouse.get_pos(), screen)
            for enemy in all_sprites:
                if enemy.type == "enemy":
                    enemy.attack(all_sprites, P1, screen)
            for entity in all_sprites:
                if entity.type == "player":
                    #move player and coasts (C1, C2)
                    entity.move(all_sprites)
                    for entity2 in all_sprites:
                        if entity2.type == "bullet" and entity2.is_friendly is False:
                            if entity.rect.collidepoint(entity2.cur_pos):
                                game_over = entity.take_damage(all_sprites)
                                entity2.de_spawn(all_sprites)
                    #or C2.check_for_collision(entity)
                    game_over = I1.collision_check(entity) or game_over
                elif entity.type == "a_enemy":
                    # print(entity.rect)
                    entity.move(all_sprites)
                    for entity2 in all_sprites:
                        if entity2.type == "bullet" and entity2.is_friendly is True:
                            if entity.rect.collidepoint(entity2.cur_pos):
                                entity.take_damage(all_sprites, P1)
                                entity2.de_spawn(all_sprites)
                                
                else:
                    entity.move(all_sprites)
            S1.update()
            
            #ensure player is drawn last, push it to back of all_sprites list
            rearrange_sprites(all_sprites)
            
            # draw(screen)
            screen.fill((0,0,0))
            I1.draw(screen)
            #C2.draw(screen, P1.score)
            for entity in all_sprites:
                #if entity.type != 'bullet':
                entity.draw(screen)
            scores = font_small.render(str(math.floor(P1.score / 100)), True, (255,255,255))
            screen.blit(scores, (10,10))
            pygame.event.pump()
            pygame.display.update()
        else:
            screen.fill((255, 0, 0))
            screen.blit(font.render("Game Over", True, (0,0,0)), (30,250))
            pygame.display.update()
            time.sleep(1.5)
            pygame.quit()
            sys.exit()  
            
            
     
# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__=="__main__":
    # call the main function
    main()


