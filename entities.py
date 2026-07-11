import pygame
from random import randint, choice, uniform
import config
import math

class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        size = randint(3, 6)
        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.vel_x = uniform(-4, 4)
        self.vel_y = uniform(-4, 4)
        self.lifetime = randint(15, 30)

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()

class GameSprite(pygame.sprite.Sprite):
    def __init__(self, image, x, y, speed, escala=1.0):
        super().__init__()
        self.image_path = image 
        try:
            sprite_loaded = pygame.image.load(image).convert_alpha()
        except:
            sprite_loaded = pygame.Surface((50, 50))
            sprite_loaded.fill((255, 0, 0))
            
        ancho_orig = sprite_loaded.get_width()
        alto_orig = sprite_loaded.get_height()
        nuevo_ancho = int(ancho_orig * escala)
        nuevo_alto = int(alto_orig * escala)
        
        # Se ha aplicado smoothscale para mejorar la calidad visual en lugar de scale[cite: 6]
        self.image = pygame.transform.smoothscale(sprite_loaded, (nuevo_ancho, nuevo_alto))
        
        self.speed = speed
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y 
    
    def draw(self, window):
        window.blit(self.image, (self.rect.x, self.rect.y))

class Player(GameSprite):
    def __init__(self, image, x, y, speed, escala=1.0):
        super().__init__(image, x, y, speed, escala)
        self.inmune = False
        self.tiempo_inmunidad = 0
        self.visible = True  
        self.last_shot = pygame.time.get_ticks()
        self.cooldown = 250  
        self.shot_count = 0
        
        self.tipo_proyectil_activo = None 
        self.tiempo_fin_powerup = 0

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.x > 0: 
            self.rect.x -= self.speed 
        if keys[pygame.K_RIGHT] and self.rect.x < config.W - self.rect.width: 
            self.rect.x += self.speed 
            
    def fire(self, bullets_group):
        now = pygame.time.get_ticks()
        if self.tipo_proyectil_activo and now > self.tiempo_fin_powerup:
            self.tipo_proyectil_activo = None
            
        if now - self.last_shot > self.cooldown:
            self.last_shot = now
            if self.tipo_proyectil_activo == "alfa":
                bullet = Bullet(config.get_path("imagenes/f_azul.png"), self.rect.centerx - 15, self.rect.top, 7, escala=0.08)
                bullets_group.add(bullet)
            elif self.tipo_proyectil_activo == "omega":
                bullet = Bullet(config.get_path("imagenes/f_morado.png"), self.rect.centerx - 15, self.rect.top, 7, escala=0.08)
                bullets_group.add(bullet)
            else:
                self.shot_count += 1
                if self.shot_count % 5 == 0:
                    bullet = SpecialBullet(config.get_path("imagenes/amburguesa_fuego.png"), self.rect.centerx - 15, self.rect.top, 7, escala=0.10)
                else:
                    bullet = Bullet(config.get_path("imagenes/amburguesa.png"), self.rect.centerx - 15, self.rect.top, 7, escala=0.08)
                bullets_group.add(bullet)

    def activar_powerup(self, tipo):
        self.tipo_proyectil_activo = tipo
        self.tiempo_fin_powerup = pygame.time.get_ticks() + 6000

    def update_inmunidad(self):
        if self.inmune:
            ahora = pygame.time.get_ticks()
            if ahora > self.tiempo_inmunidad:
                self.inmune = False
                self.visible = True
            else:
                self.visible = (ahora // 100) % 2 == 0

    def draw(self, window):
        if self.visible:
            window.blit(self.image, (self.rect.x, self.rect.y))

class Enemy(GameSprite):
    def __init__(self, image, x, y, speed, bullet_img, bullet_scale, escala=1.0, cooldown_min=1000, cooldown_max=3000):
        super().__init__(image, x, y, speed, escala)
        self.bullet_img = bullet_img
        self.bullet_scale = bullet_scale
        self.last_shot = pygame.time.get_ticks()
        self.cooldown_min = cooldown_min
        self.cooldown_max = cooldown_max
        self.cooldown = randint(cooldown_min, cooldown_max)
        self.dir_x = 1 if x < 0 else -1
        
        # Parámetros para movimiento sinusoidal
        self.initial_y = y
        self.amplitude = randint(20, 50)
        self.frequency = uniform(0.01, 0.03)

    def update(self, enemy_bullets_group):
        self.rect.x += self.speed * self.dir_x
        # Cálculo de movimiento sinusoidal en Y
        self.rect.y = self.initial_y + int(math.sin(self.rect.x * self.frequency) * self.amplitude)
        
        if (self.dir_x == 1 and self.rect.x > config.W + 60) or (self.dir_x == -1 and self.rect.x < -60):
            self.respawn()
            
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.cooldown:
            self.last_shot = now
            self.fire(enemy_bullets_group)
            self.cooldown = randint(self.cooldown_min, self.cooldown_max)

    def fire(self, enemy_bullets_group):
        enemy_bullet = EnemyBullet(self.bullet_img, self.rect.centerx - 15, self.rect.bottom, 5, escala=self.bullet_scale)
        enemy_bullets_group.add(enemy_bullet)

    def respawn(self):
        lado = choice(["izquierda", "derecha"])
        self.rect.x = -60 if lado == "izquierda" else config.W + 60
        self.dir_x = 1 if lado == "izquierda" else -1
        self.initial_y = randint(50, config.H // 2 - 50)
        self.rect.y = self.initial_y
        self.speed = randint(3, 6)

class Boss(GameSprite):
    def __init__(self, image, x, y, speed, bullet_img, bullet_scale, vida, escala):
        super().__init__(image, x, y, speed, escala)
        self.bullet_img = bullet_img
        self.bullet_scale = bullet_scale
        self.vida = vida
        self.max_vida = vida
        self.dir_x = 1
        self.last_shot = pygame.time.get_ticks()
        self.cooldown = 800

    def update(self, enemy_bullets_group):
        self.rect.x += self.speed * self.dir_x
        if self.rect.right >= config.W or self.rect.left <= 0:
            self.dir_x *= -1
        if pygame.time.get_ticks() - self.last_shot > self.cooldown:
            self.last_shot = pygame.time.get_ticks()
            self.fire(enemy_bullets_group)

    def fire(self, enemy_bullets_group):
        enemy_bullet = EnemyBullet(self.bullet_img, self.rect.centerx - 15, self.rect.bottom, 7, escala=self.bullet_scale)
        enemy_bullets_group.add(enemy_bullet)

class Bullet(GameSprite):
    damage = 1  
    def update(self, *args):
        self.rect.y -= self.speed  
        if self.rect.y < 0: self.kill()

class SpecialBullet(Bullet):
    damage = 2  

class EnemyBullet(GameSprite):
    def __init__(self, image, x, y, speed, escala=1.0):
        super().__init__(image, x, y, speed, escala)
        self.rect.inflate_ip(-20, -20)

    def update(self, *args):
        self.rect.y += self.speed
        if self.rect.y > config.H: self.kill()

class PowerUp(GameSprite):
    def __init__(self, image, x, y, speed, escala=1.0):
        super().__init__(image, x, y, speed, escala)
        self.tipo = "alfa" if "alfa.png" in image else "omega" if "omega.png" in image else "corazon"

    def update(self, *args):
        self.rect.y += self.speed
        if self.rect.y > config.H: self.kill()
