import pygame
from random import randint, choice
import config
from ui import MenuButton, draw_text_with_shadow
from entities import Player, Enemy, Boss, Particle, GameSprite, PowerUp

pygame.init()

window = pygame.display.set_mode((config.W, config.H), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("UIA")

is_fullscreen = True
clock = pygame.time.Clock()
running = True

estado_actual = config.MENU_PRINCIPAL

gato_actual_idx = 0    
score = 0
vidas = 3  
nivel_inicial = 1
nivel_actual = 1
score_nivel = 0

boss_active = False
jefe_derrotado_3000 = False
jefe_derrotado_6000 = False
jefe_derrotado_9000 = False

y_fondo = 0
bg_actual_img = None
bg = None

def actualizar_fondo_nivel():
    global bg_actual_img, bg
    idx_fondo = nivel_actual - 1
    if idx_fondo >= len(config.FONDOS_NIVELES):
        idx_fondo = len(config.FONDOS_NIVELES) - 1
    
    archivo_fondo = config.FONDOS_NIVELES[idx_fondo]
    bg_loaded = pygame.image.load(archivo_fondo).convert()
    bg = pygame.transform.scale(bg_loaded, (config.W, config.H))
    bg_actual_img = archivo_fondo

actualizar_fondo_nivel()

try:
    corazon_original = pygame.image.load(config.get_path("imagenes/corazon.png")).convert_alpha()
    img_corazon = pygame.transform.scale(corazon_original, (36, 32))
except:
    img_corazon = pygame.Surface((36, 32))
    img_corazon.fill((255, 0, 0))

enemys = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
particles = pygame.sprite.Group() 
bosses = pygame.sprite.Group() 
powerups = pygame.sprite.Group() 
ethel = None

def obtener_recursos_nivel(n):
    if n == 1:
        return config.get_path("imagenes/alien.png"), config.get_path("imagenes/amburguesa.png"), 0.08, 0.15
    elif n == 2:
        return config.get_path("imagenes/bwater.png"), config.get_path("imagenes/esf_agua.png"), 0.15, 0.25 
    else: 
        return config.get_path("imagenes/perro.png"), config.get_path("imagenes/pizza.png"), 0.15, 0.15

def crear_enemigos():
    if boss_active: 
        return 

    enemys.empty()
    enemy_bullets.empty()
    bullets.empty()
    particles.empty()
    
    # Mantenemos powerups de proyectiles, eliminamos solo corazones
    for p in powerups:
        if p.tipo == "corazon":
            p.kill()
    
    img_enemy, img_bullet, b_scale, e_scale = obtener_recursos_nivel(nivel_actual)

    for i in range(7):  
        lado = choice(["izquierda", "derecha"])
        if lado == "izquierda":
            x_ini = randint(-300, -60)
        else:
            x_ini = randint(config.W + 60, config.W + 300)
        y_ini = randint(50, config.H // 2 - 50)
        enemy = Enemy(img_enemy, x_ini, y_ini, randint(3, 6), img_bullet, b_scale, escala=e_scale)
        enemys.add(enemy)

def spawn_boss(n):
    global boss_active
    boss_active = True
    enemys.empty() 
    bosses.empty()
    
    # Mantenemos powerups de proyectiles, eliminamos solo corazones
    for p in powerups:
        if p.tipo == "corazon":
            p.kill()
    
    img_boss, img_bullet, b_scale, _ = obtener_recursos_nivel(n)
    boss = Boss(img_boss, config.W//2 - 75, 50, 4, img_bullet, b_scale, vida=40, escala=0.5)
    bosses.add(boss)

def desencadenar_explosion(x, y):
    colores_fuego = [(255, 69, 0), (255, 140, 0), (255, 215, 0), (230, 230, 250)]
    for _ in range(randint(15, 25)):
        color_elegido = choice(colores_fuego)
        p = Particle(x, y, color_elegido)
        particles.add(p)

font_big = pygame.font.SysFont("Courier New", 56, bold=True)
font_btn = pygame.font.SysFont("Courier New", 28, bold=True)
font_small = pygame.font.SysFont("Courier New", 24, bold=True)
font_score = pygame.font.SysFont("Courier New", 26, bold=True)
font_pausa_btn = pygame.font.SysFont("Courier New", 18, bold=True) 

btn_jugar = MenuButton("JUGAR", config.W // 2 - 125, config.H // 2 - 100, 250, 55)
btn_niveles = MenuButton("NIVELES", config.W // 2 - 125, config.H // 2 - 30, 250, 55)
btn_salir = MenuButton("SALIR", config.W // 2 - 125, config.H // 2 + 40, 250, 55)

btn_reintentar = MenuButton("REINTENTAR", config.W // 2 - 125, config.H // 2 + 10, 250, 55)
btn_volver_go = MenuButton("VOLVER AL MENÚ", config.W // 2 - 150, config.H // 2 + 80, 300, 55)

btn_siguiente_nivel = MenuButton("SIGUIENTE NIVEL", config.W // 2 - 150, config.H // 2 + 30, 300, 55)
btn_menu_completado = MenuButton("SALIR AL MENÚ", config.W // 2 - 150, config.H // 2 + 100, 300, 55)

btn_prev = MenuButton("<", config.W // 2 - 190, config.H // 2 - 15, 50, 50, is_circle=True)
btn_next = MenuButton(">", config.W // 2 + 140, config.H // 2 - 15, 50, 50, is_circle=True)
btn_confirmar = MenuButton("SELECCIONAR", config.W // 2 - 125, config.H // 2 + 100, 250, 50)
btn_volver_seleccion = MenuButton("VOLVER", config.W // 2 - 100, config.H // 2 + 170, 200, 50)

btn_lvl1 = MenuButton("NIVEL 1: GALAXIA", config.W // 2 - 175, config.H // 2 - 80, 350, 50)
btn_lvl2 = MenuButton("NIVEL 2: TIERRA", config.W // 2 - 175, config.H // 2 - 10, 350, 50)
btn_lvl3 = MenuButton("NIVEL 3: MARTE", config.W // 2 - 175, config.H // 2 + 60, 350, 50)
btn_volver_niveles = MenuButton("VOLVER", config.W // 2 - 100, config.H // 2 + 140, 200, 50)

btn_hud_pausa = MenuButton("||", config.W - 70, 10, 50, 35) 
btn_reanudar = MenuButton("REANUDAR", config.W // 2 - 125, config.H // 2 - 20, 250, 55)
btn_menu_pausa = MenuButton("SALIR AL MENÚ", config.W // 2 - 125, config.H // 2 + 50, 250, 55)

while running:
    clock.tick(60)
    mouse_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                is_fullscreen = not is_fullscreen
                if is_fullscreen:
                    window = pygame.display.set_mode((config.W, config.H), pygame.FULLSCREEN | pygame.SCALED)
                else:
                    window = pygame.display.set_mode((config.W, config.H), pygame.SCALED)
            
            if estado_actual == config.SELECCION_GATO:
                if event.key == pygame.K_LEFT:
                    gato_actual_idx = (gato_actual_idx - 1) % len(config.GATOS_DISPONIBLES)
                if event.key == pygame.K_RIGHT:
                    gato_actual_idx = (gato_actual_idx + 1) % len(config.GATOS_DISPONIBLES)
                if event.key == pygame.K_ESCAPE:
                    estado_actual = config.MENU_PRINCIPAL
                if event.key == pygame.K_RETURN:
                    ethel = Player(config.GATOS_DISPONIBLES[gato_actual_idx], 400, 500, 8, escala=0.15)
                    score = 0
                    score_nivel = 0
                    vidas = 3  
                    nivel_actual = nivel_inicial
                    boss_active = False
                    bosses.empty()
                    powerups.empty()
                    jefe_derrotado_3000 = False
                    jefe_derrotado_6000 = False
                    jefe_derrotado_9000 = False
                    actualizar_fondo_nivel()
                    crear_enemigos()
                    estado_actual = config.JUEGO
            
            elif estado_actual == config.MENU_NIVELES:
                if event.key == pygame.K_ESCAPE:
                    estado_actual = config.MENU_PRINCIPAL

            elif estado_actual == config.JUEGO:
                if event.key == pygame.K_SPACE:
                    ethel.fire(bullets)
                if event.key == pygame.K_ESCAPE:
                    estado_actual = config.PAUSA

            elif estado_actual == config.PAUSA:
                if event.key == pygame.K_ESCAPE:
                    estado_actual = config.JUEGO
                    
            elif estado_actual == config.NIVEL_COMPLETADO:
                if event.key == pygame.K_RETURN:
                    nivel_actual += 1
                    if nivel_actual > 3:
                        nivel_actual = 1
                        score = 0
                        jefe_derrotado_3000 = False
                        jefe_derrotado_6000 = False
                        jefe_derrotado_9000 = False
                    score_nivel = 0
                    actualizar_fondo_nivel()
                    crear_enemigos()
                    estado_actual = config.JUEGO
                if event.key == pygame.K_ESCAPE:
                    estado_actual = config.MENU_PRINCIPAL

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if estado_actual == config.MENU_PRINCIPAL:
                if btn_jugar.check_hover(mouse_pos):
                    estado_actual = config.SELECCION_GATO
                elif btn_niveles.check_hover(mouse_pos):
                    estado_actual = config.MENU_NIVELES
                elif btn_salir.check_hover(mouse_pos):
                    running = False

            elif estado_actual == config.MENU_NIVELES:
                if btn_lvl1.check_hover(mouse_pos):
                    nivel_inicial = 1
                    nivel_actual = 1
                    actualizar_fondo_nivel()
                    estado_actual = config.MENU_PRINCIPAL
                elif btn_lvl2.check_hover(mouse_pos):
                    nivel_inicial = 2
                    nivel_actual = 2
                    actualizar_fondo_nivel()
                    estado_actual = config.MENU_PRINCIPAL
                elif btn_lvl3.check_hover(mouse_pos):
                    nivel_inicial = 3
                    nivel_actual = 3
                    actualizar_fondo_nivel()
                    estado_actual = config.MENU_PRINCIPAL
                elif btn_volver_niveles.check_hover(mouse_pos):
                    estado_actual = config.MENU_PRINCIPAL

            elif estado_actual == config.SELECCION_GATO:
                if btn_prev.check_hover(mouse_pos):
                    gato_actual_idx = (gato_actual_idx - 1) % len(config.GATOS_DISPONIBLES)
                elif btn_next.check_hover(mouse_pos):
                    gato_actual_idx = (gato_actual_idx + 1) % len(config.GATOS_DISPONIBLES)
                elif btn_confirmar.check_hover(mouse_pos):
                    ethel = Player(config.GATOS_DISPONIBLES[gato_actual_idx], 400, 500, 8, escala=0.15)
                    score = 0
                    score_nivel = 0
                    vidas = 3  
                    nivel_actual = nivel_inicial
                    boss_active = False
                    bosses.empty()
                    powerups.empty()
                    jefe_derrotado_3000 = False
                    jefe_derrotado_6000 = False
                    jefe_derrotado_9000 = False
                    actualizar_fondo_nivel()
                    crear_enemigos()
                    estado_actual = config.JUEGO
                elif btn_volver_seleccion.check_hover(mouse_pos):
                    estado_actual = config.MENU_PRINCIPAL

            elif estado_actual == config.JUEGO:
                if btn_hud_pausa.check_hover(mouse_pos):
                    estado_actual = config.PAUSA

            elif estado_actual == config.PAUSA:
                if btn_reanudar.check_hover(mouse_pos):
                    estado_actual = config.JUEGO
                elif btn_menu_pausa.check_hover(mouse_pos):
                    estado_actual = config.MENU_PRINCIPAL

            elif estado_actual == config.NIVEL_COMPLETADO:
                if btn_siguiente_nivel.check_hover(mouse_pos):
                    nivel_actual += 1
                    if nivel_actual > 3:
                        nivel_actual = 1
                        score = 0
                        jefe_derrotado_3000 = False
                        jefe_derrotado_6000 = False
                        jefe_derrotado_9000 = False
                    score_nivel = 0 
                    actualizar_fondo_nivel()
                    crear_enemigos()
                    estado_actual = config.JUEGO
                elif btn_menu_completado.check_hover(mouse_pos):
                    estado_actual = config.MENU_PRINCIPAL

            elif estado_actual == config.GAME_OVER:
                if btn_reintentar.check_hover(mouse_pos):
                    ethel = Player(config.GATOS_DISPONIBLES[gato_actual_idx], 400, 500, 8, escala=0.15)
                    score = 0
                    score_nivel = 0
                    vidas = 3  
                    nivel_actual = nivel_inicial
                    boss_active = False
                    bosses.empty()
                    powerups.empty()
                    jefe_derrotado_3000 = False
                    jefe_derrotado_6000 = False
                    jefe_derrotado_9000 = False
                    actualizar_fondo_nivel()
                    crear_enemigos()
                    estado_actual = config.JUEGO
                elif btn_volver_go.check_hover(mouse_pos):
                    estado_actual = config.MENU_PRINCIPAL

    if bg_actual_img and "galaxia.jpg" in bg_actual_img:
        if estado_actual != config.GAME_OVER and estado_actual != config.PAUSA and estado_actual != config.NIVEL_COMPLETADO:
            y_fondo = (y_fondo + 1) % config.H
        window.blit(bg, (0, y_fondo))
        window.blit(bg, (0, y_fondo - config.H))
    else:
        window.blit(bg, (0, 0))

    if estado_actual == config.MENU_PRINCIPAL:
        btn_jugar.check_hover(mouse_pos)
        btn_niveles.check_hover(mouse_pos)
        btn_salir.check_hover(mouse_pos)
        
        t_titulo = "ETHEL(UIA)"
        w_tit = font_big.render(t_titulo, True, (0,0,0)).get_width()
        draw_text_with_shadow(window, t_titulo, font_big, (212, 175, 55), config.W // 2 - w_tit // 2, 80)
        
        draw_text_with_shadow(window, f"MUNDO INICIAL: {nivel_inicial}", font_small, (255, 255, 255), 20, config.H - 40)
        
        btn_jugar.draw(window, font_btn)
        btn_niveles.draw(window, font_btn)
        btn_salir.draw(window, font_btn)

    elif estado_actual == config.MENU_NIVELES:
        btn_lvl1.check_hover(mouse_pos)
        btn_lvl2.check_hover(mouse_pos)
        btn_lvl3.check_hover(mouse_pos)
        btn_volver_niveles.check_hover(mouse_pos)

        t_niv = "SELECCIONA NIVEL"
        w_niv = font_big.render(t_niv, True, (0,0,0)).get_width()
        draw_text_with_shadow(window, t_niv, font_big, (212, 175, 55), config.W // 2 - w_niv // 2, 50)

        btn_lvl1.draw(window, font_btn)
        btn_lvl2.draw(window, font_btn)
        btn_lvl3.draw(window, font_btn)
        btn_volver_niveles.draw(window, font_btn)

    elif estado_actual == config.SELECCION_GATO:
        btn_prev.check_hover(mouse_pos)
        btn_next.check_hover(mouse_pos)
        btn_confirmar.check_hover(mouse_pos)
        btn_volver_seleccion.check_hover(mouse_pos)

        t1 = "SELECCIONA TU PILOTO"
        w1 = font_big.render(t1, True, (0,0,0)).get_width()
        draw_text_with_shadow(window, t1, font_big, (212, 175, 55), config.W // 2 - w1 // 2, 40)
        
        marco_rect = pygame.Rect(config.W // 2 - 110, config.H // 2 - 110, 220, 200)
        bg_marco = pygame.Surface((220, 200))
        bg_marco.set_alpha(100)
        bg_marco.fill((20, 10, 40))
        window.blit(bg_marco, (config.W // 2 - 110, config.H // 2 - 110))
        pygame.draw.rect(window, (90, 41, 163), marco_rect, border_radius=15)
        pygame.draw.rect(window, (212, 175, 55), marco_rect, width=3, border_radius=15)

        gato_preview = GameSprite(config.GATOS_DISPONIBLES[gato_actual_idx], config.W // 2 - 50, config.H // 2 - 75, 0, escala=0.20)
        gato_preview.draw(window)

        nombre_txt = config.NOMBRES_GATOS[gato_actual_idx]
        w_nom = font_btn.render(nombre_txt, True, (0,0,0)).get_width()
        draw_text_with_shadow(window, nombre_txt, font_btn, (255, 255, 255), config.W // 2 - w_nom // 2, config.H // 2 - 155)

        btn_prev.draw(window, font_btn)
        btn_next.draw(window, font_btn)
        btn_confirmar.draw(window, font_btn)
        btn_volver_seleccion.draw(window, font_btn)

    elif estado_actual == config.JUEGO:
        ethel.move()
        ethel.update_inmunidad()  
        ethel.draw(window)

        enemys.update(enemy_bullets)
        bullets.update()
        enemy_bullets.update()
        particles.update() 
        bosses.update(enemy_bullets)
        powerups.update()  
        
        enemys.draw(window)
        bullets.draw(window)
        enemy_bullets.draw(window)
        particles.draw(window) 
        bosses.draw(window)
        powerups.draw(window)  
        
        items_recogidos = pygame.sprite.spritecollide(ethel, powerups, True)
        for item in items_recogidos:
            if item.tipo == "corazon":
                if vidas < 5:  
                    vidas += 1
            else:
                ethel.activar_powerup(item.tipo)
            
            desencadenar_explosion(item.rect.centerx, item.rect.centery)
        
        if not boss_active:
            if nivel_actual == 1 and not jefe_derrotado_3000 and score >= 3000:
                spawn_boss(1)
                jefe_derrotado_3000 = True
            elif nivel_actual == 2 and not jefe_derrotado_6000 and score >= 6000:
                spawn_boss(2)
                jefe_derrotado_6000 = True
            elif nivel_actual == 3 and not jefe_derrotado_9000 and score >= 9000:
                spawn_boss(3)
                jefe_derrotado_9000 = True
            else:
                collided = pygame.sprite.groupcollide(enemys, bullets, True, True)
                for hit in collided:
                    score += 100  
                    score_nivel += 100
                    
                    desencadenar_explosion(hit.rect.centerx, hit.rect.centery)
                    
                    if randint(1, 10) <= 2:
                        tipo_spawn = choice(["corazon", "alfa", "omega"])
                        
                        ruta_img = config.get_path("imagenes/corazon.png")
                        if tipo_spawn == "alfa":
                            ruta_img = config.get_path("imagenes/alfa.png")
                        elif tipo_spawn == "omega":
                            ruta_img = config.get_path("imagenes/omega.png")
                            
                        spawned_item = PowerUp(ruta_img, hit.rect.centerx, hit.rect.centery, speed=3, escala=0.15) 
                        powerups.add(spawned_item)
                    
                    img_e, img_b, b_scale, e_scale = obtener_recursos_nivel(nivel_actual)
                    lado = choice(["izquierda", "derecha"])
                    x_spawn = -60 if lado == "izquierda" else config.W + 60
                    enemy = Enemy(img_e, x_spawn, randint(50, config.H // 2 - 50), randint(3, 6), img_b, b_scale, escala=e_scale)
                    enemys.add(enemy)
        else:
            collided_boss = pygame.sprite.groupcollide(bosses, bullets, False, True)
            for boss, hit_bullets in collided_boss.items():
                for b in hit_bullets:
                    boss.vida -= b.damage
                    desencadenar_explosion(boss.rect.centerx, boss.rect.centery)
                if boss.vida <= 0:
                    score += 500
                    score_nivel += 500
                    boss.kill()
                    boss_active = False
                    estado_actual = config.NIVEL_COMPLETADO

        if not ethel.inmune:
            if pygame.sprite.spritecollide(ethel, enemys, False) or pygame.sprite.spritecollide(ethel, enemy_bullets, False) or pygame.sprite.spritecollide(ethel, bosses, False):
                vidas -= 1  
                enemy_bullets.empty()  
                
                desencadenar_explosion(ethel.rect.centerx, ethel.rect.centery)
                
                if vidas <= 0:
                    estado_actual = config.GAME_OVER
                else:
                    ethel.inmune = True
                    ethel.tiempo_inmunidad = pygame.time.get_ticks() + 1500
                    if not boss_active:
                        crear_enemigos()

        hud_bar = pygame.Surface((config.W, 55))
        hud_bar.set_alpha(160)
        hud_bar.fill((35, 15, 65)) 
        window.blit(hud_bar, (0, 0))
        pygame.draw.line(window, (212, 175, 55), (0, 55), (config.W, 55), width=2) 

        draw_text_with_shadow(window, f"SCORE: {score}", font_score, (255, 255, 255), 20, 15)
        draw_text_with_shadow(window, f"NIVEL: {nivel_actual}", font_score, (255, 255, 255), config.W - 240, 15)

        draw_text_with_shadow(window, "VIDAS:", font_score, (255, 255, 255), 320, 15)
        for i in range(vidas):
            x_corazon = 410 + (i * 45)
            window.blit(img_corazon, (x_corazon, 12))
            
        if boss_active:
             for b in bosses:
                pygame.draw.rect(window, (255,0,0), (200, 60, 400, 20))
                pygame.draw.rect(window, (0,255,0), (200, 60, 400 * (b.vida/b.max_vida), 20))

        btn_hud_pausa.check_hover(mouse_pos)
        btn_hud_pausa.draw(window, font_pausa_btn)

    elif estado_actual == config.NIVEL_COMPLETADO:
        btn_siguiente_nivel.check_hover(mouse_pos)
        btn_menu_completado.check_hover(mouse_pos)

        enemys.draw(window)
        ethel.draw(window)
        bullets.draw(window)
        enemy_bullets.draw(window)
        particles.draw(window) 
        powerups.draw(window)
        
        overlay = pygame.Surface((config.W, config.H))
        overlay.set_alpha(160)
        overlay.fill((0, 0, 0))
        window.blit(overlay, (0, 0))
        
        t_comp = "¡NIVEL COMPLETADO!"
        w_comp = font_big.render(t_comp, True, (0,0,0)).get_width()
        draw_text_with_shadow(window, t_comp, font_big, (50, 255, 50), config.W // 2 - w_comp // 2, config.H // 2 - 120)
        
        t_pts = f"Puntuación del Nivel: {score_nivel}"
        w_pts = font_small.render(t_pts, True, (0,0,0)).get_width()
        draw_text_with_shadow(window, t_pts, font_small, (255, 255, 255), config.W // 2 - w_pts // 2, config.H // 2 - 40)
        
        btn_siguiente_nivel.draw(window, font_btn)
        btn_menu_completado.draw(window, font_btn)

    elif estado_actual == config.PAUSA:
        btn_reanudar.check_hover(mouse_pos)
        btn_menu_pausa.check_hover(mouse_pos)

        enemys.draw(window)
        ethel.draw(window)
        bullets.draw(window)
        enemy_bullets.draw(window)
        particles.draw(window) 
        bosses.draw(window)
        powerups.draw(window)
        
        hud_bar = pygame.Surface((config.W, 55))
        hud_bar.set_alpha(160)
        hud_bar.fill((35, 15, 65))
        window.blit(hud_bar, (0, 0))
        pygame.draw.line(window, (212, 175, 55), (0, 55), (config.W, 55), width=2)
        draw_text_with_shadow(window, f"SCORE: {score}", font_score, (255, 255, 255), 20, 15)
        draw_text_with_shadow(window, f"NIVEL: {nivel_actual}", font_score, (255, 255, 255), config.W - 240, 15)
        draw_text_with_shadow(window, "VIDAS:", font_score, (255, 255, 255), 320, 15)
        for i in range(vidas):
            window.blit(img_corazon, (410 + (i * 45), 12))

        overlay = pygame.Surface((config.W, config.H))
        overlay.set_alpha(130)
        overlay.fill((0, 0, 0))
        window.blit(overlay, (0, 0))

        t_p = "JUEGO PAUSADO"
        w_p = font_big.render(t_p, True, (0,0,0)).get_width()
        draw_text_with_shadow(window, t_p, font_big, (212, 175, 55), config.W // 2 - w_p // 2, config.H // 2 - 110)

        btn_reanudar.draw(window, font_btn)
        btn_menu_pausa.draw(window, font_btn)

    elif estado_actual == config.GAME_OVER:
        btn_reintentar.check_hover(mouse_pos)
        btn_volver_go.check_hover(mouse_pos)
        
        enemys.draw(window)
        ethel.draw(window)
        bullets.draw(window)
        enemy_bullets.draw(window)
        bosses.draw(window)
        powerups.draw(window)

        overlay = pygame.Surface((config.W, config.H))
        overlay.set_alpha(150) 
        overlay.fill((0, 0, 0)) 
        window.blit(overlay, (0, 0))
        
        t_go = "GAME OVER"
        t_sc = f"Puntuación Final: {score}"
        w_go = font_big.render(t_go, True, (0,0,0)).get_width()
        w_sc = font_small.render(t_sc, True, (0,0,0)).get_width()
        
        draw_text_with_shadow(window, t_go, font_big, (255, 50, 50), config.W // 2 - w_go // 2, config.H // 2 - 120)
        draw_text_with_shadow(window, t_sc, font_small, (255, 255, 255), config.W // 2 - w_sc // 2, config.H // 2 - 40)
        
        btn_reintentar.draw(window, font_btn)
        btn_volver_go.draw(window, font_btn)
        
    pygame.display.update()

pygame.quit()