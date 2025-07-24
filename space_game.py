import pygame
import random
import os
import sys

# Инициализация PyGame
pygame.init()

# Настройки экрана
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Космический защитник PRO")

# Путь к папке с ассетами
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")

# Проверка существования папки assets
if not os.path.exists(ASSETS_DIR):
    print(f"ОШИБКА: Папка {ASSETS_DIR} не найдена!")
    print("Создайте папку 'assets' в той же директории, где находится игра")
    print("И добавьте в неё все необходимые файлы:")
    print("- spaceship.png, asteroid.png, laser.png")
    print("- space_bg.png")
    print("- explosion01.png - explosion04.png")
    print("- laser.wav, explosion.wav, space_music.mp3")
    pygame.quit()
    sys.exit(1)

# Функция загрузки с проверкой
def load_asset(name, scale=1, required=True):
    path = os.path.join(ASSETS_DIR, name)
    try:
        img = pygame.image.load(path).convert_alpha()
        if scale != 1:
            width = int(img.get_width() * scale)
            height = int(img.get_height() * scale)
            img = pygame.transform.scale(img, (width, height))
        return img
    except Exception as e:
        if required:
            print(f"ОШИБКА: Не удалось загрузить {name}!")
            print(f"Проверьте наличие файла: {path}")
            print(f"Тип ошибки: {str(e)}")
            pygame.quit()
            sys.exit(1)
        return None

# Загрузка текстур с проверкой
try:
    print("Загрузка текстур...")
    background = load_asset("space_bg.png")
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    player_img = load_asset("spaceship.png", 0.1)
    asteroid_img = load_asset("asteroid.png", 0.08)
    bullet_img = load_asset("laser.png", 0.05)
    explosion_anim = [
        load_asset(f"explosion0{i}.png", 0.5) 
        for i in range(1, 5)
    ]
    print("Текстуры успешно загружены!")
except Exception as e:
    print("Критическая ошибка при загрузке текстур:")
    print(str(e))
    pygame.quit()
    sys.exit(1)

# Загрузка звуков (не критично)
def load_sound(name):
    path = os.path.join(ASSETS_DIR, name)
    try:
        return pygame.mixer.Sound(path)
    except:
        print(f"Предупреждение: Не удалось загрузить звук {name}")
        return None

shoot_sound = load_sound("laser.wav")
explosion_sound = load_sound("explosion.wav")

try:
    pygame.mixer.music.load(os.path.join(ASSETS_DIR, "space_music.mp3"))
    pygame.mixer.music.set_volume(0.4)
    pygame.mixer.music.play(loops=-1)
except:
    print("Предупреждение: Не удалось загрузить фоновую музыку")

# Класс игрока
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        self.speed = 8
        self.health = 100
        self.last_shot = pygame.time.get_ticks()
        self.shoot_delay = 250
    
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed
    
    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullet = Bullet(self.rect.centerx, self.rect.top)
            all_sprites.add(bullet)
            bullets.add(bullet)
            try:
                shoot_sound.play()
            except:
                pass

# Класс астероида
class Asteroid(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image_orig = asteroid_img
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-150, -100)
        self.speedy = random.randrange(1, 5)
        self.speedx = random.randrange(-3, 3)
        self.rotation = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()
    
    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rotation = (self.rotation + self.rot_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rotation)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center
    
    def update(self):
        self.rotate()
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > HEIGHT or self.rect.left < -100 or self.rect.right > WIDTH + 100:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-150, -100)
            self.speedy = random.randrange(1, 5)

# Класс пули
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10
    
    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

# Класс взрыва
class Explosion(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.frame = 0
        self.image = explosion_anim[self.frame]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50
    
    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center

# Создание групп спрайтов
all_sprites = pygame.sprite.Group()
asteroids = pygame.sprite.Group()
bullets = pygame.sprite.Group()

# Создание игрока
player = Player()
all_sprites.add(player)

# Создание астероидов
for i in range(8):
    a = Asteroid()
    all_sprites.add(a)
    asteroids.add(a)

# Счёт
score = 0
font = pygame.font.SysFont('comicsans', 36)

# Игровой цикл
clock = pygame.time.Clock()
running = True

while running:
    # Поддержание FPS
    clock.tick(60)
    
    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()
            if event.key == pygame.K_ESCAPE:
                running = False
    
    # Обновление
    all_sprites.update()
    
    # Проверка столкновений пуль с астероидами
    hits = pygame.sprite.groupcollide(bullets, asteroids, True, True)
    for hit in hits:
        score += 10
        try:
            explosion_sound.play()
        except:
            pass
        expl = Explosion(hit.rect.center)
        all_sprites.add(expl)
        a = Asteroid()
        all_sprites.add(a)
        asteroids.add(a)
    
    # Проверка столкновений игрока с астероидами
    hits = pygame.sprite.spritecollide(player, asteroids, True)
    for hit in hits:
        player.health -= 20
        expl = Explosion(hit.rect.center)
        all_sprites.add(expl)
        a = Asteroid()
        all_sprites.add(a)
        asteroids.add(a)
        if player.health <= 0:
            running = False
    
    # Рендеринг
    screen.blit(background, (0, 0))
    all_sprites.draw(screen)
    
    # Отображение счёта и здоровья
    score_text = font.render(f"Счёт: {score}", True, (255, 255, 255))
    health_text = font.render(f"Здоровье: {player.health}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))
    screen.blit(health_text, (10, 50))
    
    pygame.display.flip()

pygame.quit()
sys.exit()