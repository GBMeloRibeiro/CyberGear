import pygame
import sys
from pygame import mixer
from button import Button
import asyncio
import pygame as pg
import sys, platform, math, random
import time
from datetime import datetime

async def jogofoda():
    pygame.init()
    mixer.music.load('assets/musica_verde.ogg')
    mixer.music.play(-1)
    mixer.music.set_volume(0.1)
    screen_size = [320, 180]

    if sys.platform == "emscripten":
        platform.window.canvas.style.imageRendering = "pixelated"
        screen = pg.display.set_mode(screen_size)
    else:
        screen = pg.display.set_mode(screen_size, pg.SCALED)

    clock = pg.time.Clock()
    road_texture = pg.image.load("assets/road.png").convert()
    mountains_texture = pg.image.load("assets/mountains.png").convert()
    car_sprite = pg.image.load("assets/car.png").convert()
    car_sprite.set_colorkey((255, 0, 255))
    car_sprite2 = pg.image.load("assets/car2.png").convert()
    car_sprite2.set_colorkey((255, 0, 255))
    tree_sprite = pg.image.load("assets/tree.png").convert()
    tree_sprite.set_colorkey((255, 0, 255))
    cacto_sprite = pg.image.load("assets/tree.png").convert()
    cacto_sprite.set_colorkey((255, 0, 255))

    position1 = -70
    position2 = -220
    position3 = -370
    positions = [-70, -220, -370]
    cor = 50
    pontos = 1
    multi = 0.2 * pontos
    lvl = 1
    mob2 = 1
    PRETO = (255,255,255)
    vidas = 3
    icone_vida =  pg.image.load('assets/motor.png')
    icone_vida = pg.transform.scale(icone_vida, (30,30))
    icone_vida.set_colorkey((255, 0, 255))
    vida = [icone_vida, icone_vida, icone_vida]
    espaco_entre = 2
    posicoes = [(0 + i * (icone_vida.get_width() + espaco_entre), 15) for i in range(len(vida))]

    a = 1
    font1 = pg.font.Font('assets/fonts/font1.ttf', 10)
    font2 = pg.font.Font('assets/fonts/font1.ttf', 23)
    
    car = Player()
    cars = [Car(60)]
    cars2 = [Car(55)]
    cars3 = [Car(65)]
    trees = [Tree(-67), Tree(-55), Tree(-43), Tree(-33), Tree(-25), Tree(-13), Tree(-19), Tree(-15), Tree(-7), Tree(-3)]
    cactos = [Tree(-100), Tree(-65)]

    largura_tela = 320
    altura_tela = 180
    qualquernome = 0
    superfice_transparente = pg.Surface((largura_tela, altura_tela))
    superfice_transparente.set_alpha(100)
    superfice_transparente.fill(PRETO)

    nome = "Beta_Player"
    
    running = True
    total_time = 0

    primeira = 1
    
    while running:  # Game loop
        
        delta = clock.tick() / 1000 + 0.00001
        total_time += delta
        car.controls(delta)
        for event in pg.event.get():
            if event.type == pg.QUIT: running = 0
        pressed_keys = pg.key.get_pressed()
        
        screen.blit(mountains_texture, (-65- car.angle*82,0))#screen.fill((100,150,250))
        screen.blit(superfice_transparente, (0,0))
        vertical, draw_distance = 180, 1
        car.z = calc_z(car.x)
        z_buffer = [999 for element in range(180)]

        while draw_distance < 120:
            last_vertical = vertical
            while vertical >= last_vertical and draw_distance < 120:
                draw_distance += draw_distance/150
                x = car.x + draw_distance
                scale = 1/draw_distance
                z = calc_z(x) - car.z
                vertical = int(60+160*scale + z*scale)

            if draw_distance < 120:
                z_buffer[int(vertical)] = draw_distance
                road_slice = road_texture.subsurface((0, 50*x%360,489, 1))
                color = (int(cor-draw_distance/3),int(130-draw_distance), int(50-z/20+30*math.sin(x)))
                pg.draw.rect(screen, color, (0, vertical, 320, 1))
                render_element(screen, road_slice, 500*scale, 1, scale, x,  car, car.y, z_buffer)
        
        for index in reversed(range(len(trees)-1)):
            scale = max(0.0001, 1/(trees[index].x - car.x))
            render_element(screen, tree_sprite, 200*scale, 300*scale, scale, trees[index].x, car, trees[index].y+car.y, z_buffer)
        
        if trees[0].x < car.x+1 and len(trees) != 1:
            trees.pop(0)
            trees.append(Tree(trees[-1].x))
        if len(trees) == 1:
            trees.pop(0)

        if cor > 100:
            cacto_sprite = pg.image.load("assets/cacto.png").convert()
            cacto_sprite.set_colorkey((255, 0, 255))
            tree_sprite = pg.image.load("assets/cacto.png").convert()
            tree_sprite.set_colorkey((255, 0, 255))
            
        for index in reversed(range(len(cactos)-1)):
            scale = max(0.0001, 1/(cactos[index].x - car.x))
            render_element(screen, cacto_sprite, 200*scale, 300*scale, scale, cactos[index].x, car, cactos[index].y+car.y, z_buffer)
        if cor > 100:
            if cactos[0].x < car.x+1:
                cactos.pop(0)
                cactos.append(Tree(cactos[-1].x))

        if (pontos > 100) and (mob2 == 1):
            mixer.music.load('assets/musica_deserto.ogg')
            mixer.music.play(-1)
            mixer.music.set_volume(0.1)
            cars.append(Car(car.x+17))
            cars2.append(Car(car.x+21))
            cars3.append(Car(car.x+10))
            mob2 = 0

        if abs(car.y - calc_y(car.x+2) -100) > 280 and car.velocity > 5:
            car.velocity += -car.velocity*delta
            car.acceleration += -car.acceleration*delta
            pg.draw.circle(screen, (255,0,0), (300, 170), 3)
            pontos -= 5
            pontos = max(pontos, 1)


        # Draw adversary cars and check collisions
        for adversary_cars, position in zip([cars, cars2, cars3], [position1, position2, position3]):
            for adversary_car in adversary_cars:
                scale = max(0.0001, 1 / (adversary_car.x - car.x))
                car_rect = render_element(screen, car_sprite2, 100 * scale, 80 * scale, scale, adversary_car.x, car, position + car.y, z_buffer, draw_rect=True)

                if car_rect and car.get_rect().colliderect(car_rect):
                    vidas -= 1
                    if vidas > 0:
                        crash= mixer.Sound('assets/som_batida.mp3')
                        crash.set_volume(0.1)
                        crash.play()
                    vida.pop(0)
                    car.velocity *= -0.1                   
                    adversary_cars.pop(0)
                    adversary_cars.append(Car(car.x + random.randint(50, 100)))
                    pg.draw.circle(screen, (255,0,0), (300, 170), 3)
                    if vidas == 0:
                        await asyncio.sleep(0)
                        mixer.music.stop()
                        screen.fill((0,0,0))
                        fim_de_jogo = font2.render("FIM DE JOGO!", True, 'red')
                        pg.display.flip()
                        acidente = mixer.Sound('assets/som_morte.mp3')
                        acidente.set_volume(0.5)
                        acidente.play()
                        time.sleep(4)
                        screen.blit(fim_de_jogo, (30,90))
                        pg.display.flip()
                        arcade = mixer.Sound('assets/efeito_sonoro_morte.mp3')
                        arcade.set_volume(0.5)
                        arcade.play()
                        time.sleep(5)
                        mixer.music.load('assets/musica_principal.mp3')
                        mixer.music.play(-1)
                        mixer.music.set_volume(0.1)
                        salvar_ranking(nome, pontos)
                        screen = pygame.display.set_mode((800, 500))
                        principal()
                        pg.display.flip()
                        

            # Update adversary car position
            for adversary_car in adversary_cars:
                adversary_car.x -= random.randint(15, 40) * delta * multi

            if adversary_cars[0].x < car.x + 1:
                adversary_cars.pop(0)
                pontos += 10
                qualquernome +=10
                if qualquernome < 100:
                    superfice_transparente.set_alpha(130-qualquernome)
                    
                adversary_cars.append(Car(car.x + random.randint(50, 100)))
                position = random.choice(positions)
                if cor < 200:
                    cor += 10
                    if cor < 100:
                        cactos.append(Tree(cactos[-1].x))
                        trees.pop(0)

        # Update player sprite based on angle
        car.update_sprite()
        screen.blit(car.car_sprite, (120, 120 + math.sin(total_time * car.velocity)))
    
        Ponto_tela_sombra = font1.render(f"Pontos:{pontos-1}", True, 'black')
        screen.blit(Ponto_tela_sombra, (1,1))
        Ponto_tela = font1.render(f"Pontos:{pontos-1}", True, 'white')
        screen.blit(Ponto_tela, (0,0))
        for vidao, pos in zip(vida, posicoes):
            screen.blit(vidao, pos)

        pg.display.update()
        await asyncio.sleep(0)

class Tree:
    def __init__(self, distance):
        self.x = distance + random.randint(10, 20) + 0.5
        self.y = random.randint(500, 1500) * random.choice([-1, 1])

def calc_y(x):
    return 200 * math.sin(x / 17) + 170 * math.sin(x / 8)

def calc_z(x):
    return 200 + 80 * math.sin(x / 13) - 120 * math.sin(x / 7)

def render_element(screen, sprite, width, height, scale, x, car, y, z_buffer, draw_rect=False):
    y = calc_y(x) - y
    z = calc_z(x) - car.z
    vertical = int(60 + 160 * scale + z * scale)

    if 0 <= vertical < 180 and z_buffer[vertical] > 1 / scale - 10:
        horizontal = 160 - (160 - y) * scale + car.angle * (vertical - 150)
        scaled_sprite = pg.transform.scale(sprite, (int(width), int(height)))
        screen.blit(scaled_sprite, (horizontal, vertical - height+1))

        if draw_rect:
            rect = pg.Rect(horizontal, vertical - height, int(width), int(height))
            return rect

    return None

class Car:
    def __init__(self, distance):
        self.x = distance + random.randint(90, 110)

class Player:
    car_sprite = pg.image.load("assets/car.png")
    def __init__(self):
        self.x = 0
        self.y = 300
        self.z = 0
        self.angle = 0
        self.velocity = 0
        self.acceleration = 0

    def controls(self, delta):
        pressed_keys = pg.key.get_pressed()
        self.acceleration += -0.5 * self.acceleration * delta
        self.velocity += -0.5 * self.velocity * delta

        if pressed_keys[pg.K_w] or pressed_keys[pg.K_UP]:
            if self.velocity > -1:
                self.acceleration += 4 * delta
        elif pressed_keys[pg.K_s] or pressed_keys[pg.K_DOWN]:
            if self.velocity < 1:
                self.acceleration -= delta

        if pressed_keys[pg.K_a] or pressed_keys[pg.K_LEFT]:
            self.angle -= delta * self.velocity / 10
        elif pressed_keys[pg.K_d] or pressed_keys[pg.K_RIGHT]:
            self.angle += delta * self.velocity / 10

        self.velocity = max(-10, min(self.velocity, 20))
        self.angle = max(-1.1, min(0.8, self.angle))
        self.velocity += self.acceleration * delta
        self.x += self.velocity * delta * math.cos(self.angle)
        self.y += self.velocity * math.sin(self.angle) * delta * 100

    def update_sprite(self):
        if -0.3 < self.angle < 0.3:
            self.car_sprite = pg.image.load("assets/car.png").convert()
        elif self.angle <= -0.4:
            self.car_sprite = pg.image.load("assets/car_1.png").convert()
        elif self.angle >= 0.4:
            self.car_sprite = pg.image.load("assets/car_1_2.png").convert()
        self.car_sprite.set_colorkey((255, 0, 255))

    def get_rect(self):
        return pg.Rect(120, 120, self.car_sprite.get_width(), self.car_sprite.get_height())

def salvar_ranking(nome, pontuacao):
    with open("ranking.txt", "a") as arquivo:
        data = datetime.now().strftime("%d-%m-%Y")
        arquivo.write(f"{nome},{pontuacao},{data}\n")
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    width = img.get_width()
    screen.blit(img, (x - (width / 2), y))


def exibir_ranking_na_tela(screen):
    try:
        with open("ranking.txt", "r") as arquivo:
            dados = [linha.strip().split(",") for linha in arquivo.readlines()]
            dados.sort(key=lambda x: int(x[1]), reverse=True)
            ranking = font1.render('Ranking dos Melhores Jogadores', True, 'white')
            screen.blit(ranking, (60,50))
            for i, (nome, pontuacao, data) in enumerate(dados[:5]):
                placar = font2.render(f"{i + 1}. {nome} - Pontos: {pontuacao} - Data: {data}", True, 'white')
                screen.blit(placar, (30, 120 + i*40))
    except FileNotFoundError:
        ranking = font.render('Nenhum Ranking encontrado!', True, 'white')
        screen.blit(ranking, (90,50))

def placar1():
    pygame.display.set_caption("Ranking")

    while True:
        MENU_MOUSE_POS = pygame.mouse.get_pos()
        draw_gradient(screen, blue, purple)
        exibir_ranking_na_tela(screen)
        BACK_BUTTON = Button(image=None, pos=(404, 410), text_input="VOLTAR", font=get_font(23), base_color='#d7fcd4', hovering_color="Yellow")
        voltar = font1.render('VOLTAR', True, 'black')
        screen.blit(voltar, (340, 402))
        for button in [BACK_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(screen)


        # Voltar ao menu principal
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if BACK_BUTTON.checkForInput(MENU_MOUSE_POS):
                    principal()

        pygame.display.flip()

def draw_gradient(screen, color1, color2):
    """
    Fills the screen with a gradient between color1 and color2.
    """
    width, height = screen.get_size()
    for y in range(height):
        # Calculate the blend factor
        blend = y / height
        # Interpolate between the two colors
        r = int(color1[0] * (1 - blend) + color2[0] * blend)
        g = int(color1[1] * (1 - blend) + color2[1] * blend)
        b = int(color1[2] * (1 - blend) + color2[2] * blend)
        pygame.draw.line(screen, (r, g, b), (0, y), (width, y))

def principal():
    while True:
        clock.tick(fps)
        MENU_MOUSE_POS = pygame.mouse.get_pos()
        # Draw the gradient
        draw_gradient(screen, blue, purple)
        cyber = font3.render('CYBER', True, 'purple')
        screen.blit(cyber, (200, 100))
        cyber_sombra = font3.render('CYBER', True, 'black')
        screen.blit(cyber_sombra, (202, 102))
        gear = font3.render('GEAR', True, 'purple')
        screen.blit(gear, (250,180))
        gear_sombra = font3.render('GEAR', True, 'black')
        screen.blit(gear_sombra, (252, 182))
        PLAY_BUTTON = Button(image=None, pos=(400, 330), 
                             text_input="JOGAR", font=get_font(25), base_color="#d7fcd4", hovering_color="Yellow")
        jogar = font.render('JOGAR', True, 'black')
        screen.blit(jogar, (343,321))
        RANKING_BUTTON = Button(image=None, pos=(401, 370), 
                             text_input="RANKING", font=get_font(25), base_color="#d7fcd4", hovering_color="Yellow")
        ranking = font.render('RANKING', True, 'black')
        screen.blit(ranking, (320,361))
        QUIT_BUTTON = Button(image=None, pos=(404, 410), 
                              text_input="SAIR", font=get_font(25), base_color="#d7fcd4", hovering_color="Yellow")
        sair = font.render('SAIR', True, 'black')
        screen.blit(sair, (359,401))

        for button in [PLAY_BUTTON, RANKING_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    screen.fill((0,0,0))
                    pg.display.flip()
                    mixer.music.stop()
                    time.sleep(1)
                    pg.init()
                    asyncio.run(jogofoda())
                    pg.quit()
                if RANKING_BUTTON.checkForInput(MENU_MOUSE_POS):
                    placar1()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()


pygame.init()
mixer.music.load('assets/musica_principal.mp3')
mixer.music.play(-1)
mixer.music.set_volume(0.1)
clock = pygame.time.Clock()
fps = 60
def get_font(size): # Returns Press-Start-2P in the desired size
    return pygame.font.Font("assets/fonts/font1.ttf", size)
screen = pygame.display.set_mode((800, 500))
pygame.display.set_caption("Menu Principal")
blue = (0, 0, 0)
purple = (128, 0, 128)
font1 = pygame.font.Font('assets/fonts/font1.ttf', 23)
font2 = pygame.font.Font('assets/fonts/font1.ttf', 13)
font3 = pygame.font.Font('assets/fonts/font1.ttf', 80)
font = pygame.font.Font('assets/fonts/font1.ttf', 25)
principal()
