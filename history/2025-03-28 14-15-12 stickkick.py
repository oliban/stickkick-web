import pygame
import random
import sys

# --- Konstanter ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WATER_LEVEL = 100  # Y-koordinat där vattenytan börjar

# Färger
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 200)  # Djupblå för vatten
SKY_BLUE = (135, 206, 235) # Himmelsblå
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Spelobjekt storlekar och hastigheter
SHIP_WIDTH = 60
SHIP_HEIGHT = 20
SHIP_SPEED = 5

SUB_WIDTH = 50
SUB_HEIGHT = 15
SUB_SPEED = 4

BOMB_WIDTH = 5
BOMB_HEIGHT = 10
BOMB_SPEED = 3

TORPEDO_WIDTH = 15
TORPEDO_HEIGHT = 5
TORPEDO_SPEED = 5

# Fördröjning för skjutning (i millisekunder)
BOMB_COOLDOWN = 500  # Halv sekund
TORPEDO_COOLDOWN = 800 # Lite längre för torpeder

# Poänggräns för vinst
WIN_SCORE = 5

# --- Klasser ---

class Ship(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([SHIP_WIDTH, SHIP_HEIGHT])
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH // 2 - SHIP_WIDTH // 2
        self.rect.y = WATER_LEVEL - SHIP_HEIGHT # Placeras precis på vattenytan
        self.speed = SHIP_SPEED
        self.last_bomb_time = 0

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed

    def drop_bomb(self, all_sprites, bombs):
        now = pygame.time.get_ticks()
        if now - self.last_bomb_time > BOMB_COOLDOWN:
            self.last_bomb_time = now
            bomb = Bomb(self.rect.centerx, self.rect.bottom)
            all_sprites.add(bomb)
            bombs.add(bomb)

class Submarine(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Använd en enkel rektangel för positionering, men den ritas inte normalt
        self.image = pygame.Surface([SUB_WIDTH, SUB_HEIGHT])
        self.image.fill(GREEN) # Grön för att synas i debug-läge
        self.image.set_colorkey(BLACK) # Gör svart transparent om vi skulle rita den
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH // 2 - SUB_WIDTH // 2
        self.rect.y = SCREEN_HEIGHT - SUB_HEIGHT - 20 # Starta nära botten
        self.speed = SUB_SPEED
        self.last_torpedo_time = 0
        # --- VIKTIGT: Gör den "osynlig" ---
        # Vi kommer helt enkelt inte att rita denna sprite i huvudloopen
        # Men vi behöver den för kollisionsdetektering och positionering.

    def update(self, keys):
        if keys[pygame.K_a] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_d] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed
        if keys[pygame.K_w] and self.rect.top > WATER_LEVEL + 5: # Kan inte gå upp till ytan
            self.rect.y -= self.speed
        if keys[pygame.K_s] and self.rect.bottom < SCREEN_HEIGHT:
            self.rect.y += self.speed

    def fire_torpedo(self, all_sprites, torpedoes):
        now = pygame.time.get_ticks()
        if now - self.last_torpedo_time > TORPEDO_COOLDOWN:
            self.last_torpedo_time = now
            torpedo = Torpedo(self.rect.centerx, self.rect.top)
            all_sprites.add(torpedo)
            torpedoes.add(torpedo)

class Bomb(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([BOMB_WIDTH, BOMB_HEIGHT])
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.speed = BOMB_SPEED

    def update(self):
        self.rect.y += self.speed
        # Ta bort bomben om den åker utanför skärmen
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Torpedo(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([TORPEDO_WIDTH, TORPEDO_HEIGHT])
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = TORPEDO_SPEED

    def update(self):
        self.rect.y -= self.speed
        # Ta bort torpeden om den åker utanför skärmen
        if self.rect.bottom < 0:
            self.kill()

# --- Funktioner ---
def draw_text(surf, text, size, x, y, color=WHITE):
    font = pygame.font.Font(pygame.font.match_font('arial'), size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

def reset_submarine(sub):
    """Återställer ubåtens position."""
    sub.rect.x = random.randint(0, SCREEN_WIDTH - SUB_WIDTH)
    sub.rect.y = random.randint(WATER_LEVEL + 50, SCREEN_HEIGHT - SUB_HEIGHT - 10)

def reset_ship(ship):
    """Återställer båtens position."""
    ship.rect.x = SCREEN_WIDTH // 2 - SHIP_WIDTH // 2
    ship.rect.y = WATER_LEVEL - SHIP_HEIGHT

def game_over_screen(screen, winner):
    """Visar Game Over-skärm."""
    screen.fill(BLACK)
    if winner == "Ship":
        draw_text(screen, "YTBÅTEN VANN!", 48, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4, RED)
    elif winner == "Submarine":
         draw_text(screen, "UBÅTEN VANN!", 48, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4, GREEN)
    else:
         draw_text(screen, "GAME OVER", 48, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)

    draw_text(screen, f"Slutpoäng - Båt: {ship_score} Ubåt: {sub_score}", 22,
              SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    draw_text(screen, "Tryck på valfri tangent för att spela igen", 18,
              SCREEN_WIDTH / 2, SCREEN_HEIGHT * 3 / 4)
    pygame.display.flip()
    waiting = True
    while waiting:
        pygame.time.Clock().tick(30) # Låg FPS i vänteläge
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYUP:
                waiting = False

# --- Spel Initiering ---
pygame.init()
pygame.mixer.init() # Om du vill lägga till ljud senare
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ubåtskrig")
clock = pygame.time.Clock()

# --- Spel Loop ---
running = True
game_over = False
while running:
    if game_over:
        if ship_score >= WIN_SCORE:
            game_over_screen(screen, "Ship")
        elif sub_score >= WIN_SCORE:
            game_over_screen(screen, "Submarine")
        else: # Skulle inte hända med nuvarande logik, men bra att ha
             game_over_screen(screen, "Ingen")

        # Återställ spelet för en ny runda
        game_over = False
        all_sprites = pygame.sprite.Group()
        ships = pygame.sprite.Group()
        submarines = pygame.sprite.Group() # Används mest för logik/kollision
        bombs = pygame.sprite.Group()
        torpedoes = pygame.sprite.Group()

        ship = Ship()
        submarine = Submarine() # Skapas men ritas inte

        all_sprites.add(ship)
        # Lägg INTE till ubåten i all_sprites om den ska vara osynlig!
        # Vi behöver dock en referens till den.
        # submarines.add(submarine) # Kan läggas till om man vill ha en grupp för den

        ship_score = 0
        sub_score = 0


    # Håll loopen igång med rätt hastighet
    clock.tick(60) # 60 FPS

    # --- Hantera Input (Events) ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN: # Ytbåt släpper bomb
                ship.drop_bomb(all_sprites, bombs)
            if event.key == pygame.K_SPACE: # Ubåt skjuter torped
                submarine.fire_torpedo(all_sprites, torpedoes)
            # Debug-tangent för att visa ubåten (frivilligt)
            # if event.key == pygame.K_p:
            #    if submarine in all_sprites:
            #        all_sprites.remove(submarine)
            #    else:
            #        all_sprites.add(submarine)


    # --- Uppdatera ---
    keys = pygame.key.get_pressed()
    ship.update(keys)
    submarine.update(keys) # Uppdatera ubåtens position även om den inte syns
    # Uppdatera bomber och torpeder (som finns i all_sprites)
    # Vi behöver inte kalla update på ship igen här om den redan finns i all_sprites
    bombs.update()
    torpedoes.update()


    # --- Kollisionsdetektering ---
    # Kolla om en bomb träffar ubåten
    # Vi kollar mot ubåtens rect direkt, inte via spritegrupper
    hits_sub = pygame.sprite.spritecollide(submarine, bombs, True) # True tar bort bomben vid träff
    for hit in hits_sub:
        print("Ubåten träffad!")
        ship_score += 1
        # Eventuellt: Lägg till explosionseffekt
        reset_submarine(submarine) # Återställ ubåtens position
        if ship_score >= WIN_SCORE:
            game_over = True


    # Kolla om en torped träffar ytbåten
    hits_ship = pygame.sprite.spritecollide(ship, torpedoes, True) # True tar bort torpeden vid träff
    for hit in hits_ship:
        print("Ytbåten träffad!")
        sub_score += 1
        # Eventuellt: Lägg till explosionseffekt
        reset_ship(ship) # Återställ båtens position (eller avsluta spelet direkt?)
        if sub_score >= WIN_SCORE:
            game_over = True


    # --- Rita / Rendera ---
    # Bakgrund
    screen.fill(SKY_BLUE) # Himmel
    pygame.draw.rect(screen, BLUE, (0, WATER_LEVEL, SCREEN_WIDTH, SCREEN_HEIGHT - WATER_LEVEL)) # Vatten

    # Rita alla synliga sprites (INTE ubåten)
    all_sprites.draw(screen)
    # Om du lade till en debug-tangent för att visa ubåten,
    # och 'submarine' finns i 'all_sprites', ritas den här.

    # Rita Poäng
    draw_text(screen, f"Båt Poäng: {ship_score}", 18, SCREEN_WIDTH / 4, 10, BLACK)
    draw_text(screen, f"Ubåt Poäng: {sub_score}", 18, SCREEN_WIDTH * 3 / 4, 10, BLACK)

    # EFTER att ha ritat allt, uppdatera skärmen
    pygame.display.flip()


# --- Avsluta Pygame ---
pygame.quit()
sys.exit()