import pygame
from random import randint, choice
import config
from ui import MenuButton, draw_text_with_shadow, draw_text_outlined
from entities import Player, Enemy, Boss, Particle, GameSprite, PowerUp
import json
import os

pygame.init()

window = pygame.display.set_mode((config.W, config.H), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("ethel(uia)")

is_fullscreen = True
clock = pygame.time.Clock()
running = True

estado_actual = config.MENU_PRINCIPAL

intro_text = [
    "Ethel ha estado buscando la legendaria",
    "'Galaxia Perdida' durante años.",
    "Al atravesar un agujero de gusano,",
    "descubre que no está sola...",
    "Fuerzas extrañas protegen los",
    "secretos de este lugar.",
    "Tu misión: descubrir la verdad,",
    "evitar que la galaxia sea destruida,",
    "y regresar a casa."
]
current_line = 0
char_index = 0
last_type_time = pygame.time.get_ticks()

ARCHIVO_GUARDADO = config.get_path("save_data.json")

def cargar_datos():
    if os.path.exists(ARCHIVO_GUARDADO):
        try:
            with open(ARCHIVO_GUARDADO, "r") as f:
                data = json.load(f)
                if "leaderboard" not in data:
                    lb = [{"nombre": data.get("nombre_record", "---"), "score": data.get("high_score", 0)}]
                    lb.extend([{"nombre": "---", "score": 0} for _ in range(4)])
                    data["leaderboard"] = lb
                return data
        except:
            pass
    return {"leaderboard": [{"nombre": "---", "score": 0} for _ in range(5)], "vidas": 3}

def guardar_datos(datos):
    try:
        with open(ARCHIVO_GUARDADO, "w") as f:
            json.dump(datos, f)
    except Exception as e:
        pass

def es_nuevo_record(score, leaderboard):
    return score > leaderboard[-1]["score"]

def insertar_record(nombre, score, leaderboard):
    leaderboard.append({"nombre": nombre, "score": score})
    leaderboard.sort(key=lambda x: x["score"], reverse=True)
    return leaderboard[:5]

datos_juego = cargar_datos()
nombre_ingresado = ""

gato_actual_idx = 0    
score = 0
vidas = datos_juego.get("vidas", 3)
nivel_inicial = 1
nivel_actual = 1
score_nivel = 0

boss_active = False
jefe_generado_nivel = False
tiempo_inicio_nivel = 0
TIEMPO_PARA_JEFE = 45000 

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
    bg = pygame.transform.smoothscale(bg_loaded, (config.W, config.H))
    bg_actual_img = archivo_fondo

actualizar_fondo_nivel()

try:
    corazon_original = pygame.image.load(config.get_path("imagenes/corazon.png")).convert_alpha()
    img_corazon = pygame.transform.smoothscale(corazon_original, (36, 32))
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
        return config.get_path("imagenes/alien.png"), config.get_path("imagenes/amburguesa.png"), 0.08, 0.15, 2500, 4500
    elif n == 2: 
        return config.get_path("imagenes/bwater.png"), config.get_path("imagenes/esf_agua.png"), 0.15, 0.25, 1500, 2500
    else: 
        return config.get_path("imagenes/perro.png"), config.get_path("imagenes/pizza.png"), 0.15, 0.15, 800, 1500

def crear_enemigos():
    if boss_active: return 
    enemys.empty()
    enemy_bullets.empty()
    bullets.empty()
    particles.empty()
    
    for p in powerups:
        if p.tipo == "corazon":
            p.kill()
    
    img_enemy, img_bullet, b_scale, e_scale, cd_min, cd_max = obtener_recursos_nivel(nivel_actual)
    speed_mod = score // 2000
    
    for i in range(7):  
        lado = choice(["izquierda", "derecha"])
        if lado == "izquierda":
            x_ini = randint(-300, -60)
        else:
            x_ini = randint(config.W + 60, config.W + 300)
        y_ini = randint(50, config.H // 2 - 50)
        enemy = Enemy(img_enemy, x_ini, y_ini, randint(3 + speed_mod, 6 + speed_mod), img_bullet, b_scale, escala=e_scale, cooldown_min=cd_min, cooldown_max=cd_max)
        enemys.add(enemy)

def spawn_boss(n):
    global boss_active
    boss_active = True
    enemys.empty() 
    bosses.empty()
    
    for p in powerups:
        if p.tipo == "corazon":
            p.kill()
    
    img_boss, img_bullet, b_scale, _, _, _ = obtener_recursos_nivel(n)
    boss = Boss(img_boss, config.W//2 - 75, 50, 4, img_bullet, b_scale, vida=40, escala=0.5)
    bosses.add(boss)

def desencadenar_explosion(x, y):
    colores_fuego = [(255, 69, 0), (255, 140, 0), (255, 215, 0), (230, 230, 250)]
    for _ in range(randint(15, 25)):
        color_elegido = choice(colores_fuego)
        p = Particle(x, y, color_elegido)
        particles.add(p)

def iniciar_juego_desde_nivel(n):
    global ethel, score, score_nivel, vidas, nivel_actual, nivel_inicial, boss_active, jefe_generado_nivel, estado_actual, tiempo_inicio_nivel
    ethel = Player(config.GATOS_DISPONIBLES[gato_actual_idx], 400, 500, 8, escala=0.15)
    score = 0
    score_nivel = 0
    vidas = cargar_datos().get("vidas", 3)
    nivel_inicial = n
    nivel_actual = n
    boss_active = False
    bosses.empty()
    powerups.empty()
    jefe_generado_nivel = False
    tiempo_inicio_nivel = pygame.time.get_ticks()
    actualizar_fondo_nivel()
    crear_enemigos()
    estado_actual = config.JUEGO

font_big = pygame.font.SysFont("Courier New", 56, bold=True)
font_btn = pygame.font.SysFont("Courier New", 28, bold=True)
font_small = pygame.font.SysFont("Courier New", 24, bold=True)
font_score = pygame.font.SysFont("Courier New", 26, bold=True)
font_pausa_btn = pygame.font.SysFont("Courier New", 18, bold=True)
font_story = pygame.font.SysFont("Courier New", 22, italic=True)

btn_jugar = MenuButton("JUGAR", config.W // 2 - 125, config.H // 2 - 20, 250, 50)
btn_controles = MenuButton("CONTROLES", config.W // 2 - 125, config.H // 2 + 45, 250, 50)
btn_salir = MenuButton("SALIR", config.W // 2 - 125, config.H // 2 + 110, 250, 50)
btn_volver_controles = MenuButton("VOLVER", config.W // 2 - 100, config.H // 2 + 190, 200, 50)

btn_skip = MenuButton("SALTAR", config.W - 130, config.H - 80, 100, 50)
btn_reintentar = MenuButton("REINTENTAR", config.W // 2 - 125, config.H // 2 + 170, 250, 55)
btn_volver_go = MenuButton("VOLVER AL MENÚ", config.W // 2 - 150, config.H // 2 + 240, 300, 55)
btn_siguiente_nivel = MenuButton("SIGUIENTE NIVEL", config.W // 2 - 150, config.H // 2 + 30, 300, 55)
btn_menu_completado = MenuButton("SALIR AL MENÚ", config.W // 2 - 150, config.H // 2 + 100, 300, 55)
btn_prev = MenuButton("<", config.W // 2 - 190, config.H // 2 - 15, 50, 50, is_circle=True)
btn_next = MenuButton(">", config.W // 2 + 140, config.H // 2 - 15, 50, 50, is_circle=True)
btn_confirmar = MenuButton("SELECCIONAR", config.W // 2 - 125, config.H // 2 + 100, 250, 50)
btn_volver_seleccion = MenuButton("VOLVER", config.W // 2 - 100, config.H // 2 + 170, 200, 50)

def cargar_miniatura(idx):
    try:
        if idx < len(config.FONDOS_NIVELES):
            img = pygame.image.load(config.FONDOS_NIVELES[idx]).convert()
            return pygame.transform.smoothscale(img, (400, 80))
    except:
        pass
    surf = pygame.Surface((400, 80))
    surf.fill((30, 30, 60))
    return surf

miniatura_lvl1 = cargar_miniatura(0)
miniatura_lvl2 = cargar_miniatura(1)
miniatura_lvl3 = cargar_miniatura(2)

rect_lvl1 = pygame.Rect(config.W // 2 - 200, config.H // 2 - 120, 400, 80)
rect_lvl2 = pygame.Rect(config.W // 2 - 200, config.H // 2 - 20, 400, 80)
rect_lvl3 = pygame.Rect(config.W // 2 - 200, config.H // 2 + 80, 400, 80)
btn_volver_niveles = MenuButton("VOLVER", config.W // 2 - 100, config.H // 2 + 200, 200, 50)
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
            
            if estado_actual == config.INTRO and event.key == pygame.K_SPACE:
                estado_actual = config.SELECCION_GATO
            
            elif estado_actual == config.CONTROLES:
                if event.key == pygame.K_ESCAPE:
                    estado_actual = config.MENU_PRINCIPAL
            
            elif estado_actual == config.SELECCION_GATO:
                if event.key == pygame.K_LEFT:
                    gato_actual_idx = (gato_actual_idx - 1) % len(config.GATOS_DISPONIBLES)
                if event.key == pygame.K_RIGHT:
                    gato_actual_idx = (gato_actual_idx + 1) % len(config.GATOS_DISPONIBLES)
                if event.key == pygame.K_ESCAPE:
                    estado_actual = config.MENU_PRINCIPAL
                if event.key == pygame.K_RETURN:
                    estado_actual = config.MENU_NIVELES
            
            elif estado_actual == config.MENU_NIVELES:
                if event.key == pygame.K_ESCAPE:
                    estado_actual = config.SELECCION_GATO

            elif estado_actual == config.JUEGO:
                if event.key == pygame.K_SPACE:
                    ethel.fire(bullets)
                if event.key == pygame.K_ESCAPE:
                    estado_actual = config.PAUSA
            
            elif estado_actual == config.INGRESO_NOMBRE:
                if event.key == pygame.K_RETURN and len(nombre_ingresado) > 0:
                    datos_juego["leaderboard"] = insertar_record(nombre_ingresado, score, datos_juego["leaderboard"])
                    datos_juego["vidas"] = 3
                    guardar_datos(datos_juego)
                    estado_actual = config.GAME_OVER
                elif event.key == pygame.K_BACKSPACE:
                    nombre_ingresado = nombre_ingresado[:-1]
                else:
                    if len(nombre_ingresado) < 3:
                        if event.unicode.isalpha():
                            nombre_ingresado += event.unicode.upper()

            elif estado_actual == config.PAUSA:
                if event.key == pygame.K_ESCAPE:
                    estado_actual = config.JUEGO
                    
            elif estado_actual == config.NIVEL_COMPLETADO:
                if event.key == pygame.K_RETURN:
                    nivel_actual += 1
                    if nivel_actual > 3:
                        nivel_actual = 1
                        score = 0
                    jefe_generado_nivel = False
                    score_nivel = 0
                    tiempo_inicio_nivel = pygame.time.get_ticks() 
                    actualizar_fondo_nivel()
                    crear_enemigos()
                    estado_actual = config.JUEGO
                if event.key == pygame.K_ESCAPE:
                    estado_actual = config.MENU_PRINCIPAL

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if estado_actual == config.MENU_PRINCIPAL:
                if btn_jugar.check_hover(mouse_pos):
                    estado_actual = config.INTRO
                    current_line = 0
                    char_index = 0
                elif btn_controles.check_hover(mouse_pos):
                    estado_actual = config.CONTROLES
                elif btn_salir.check_hover(mouse_pos):
                    running = False

            elif estado_actual == config.CONTROLES:
                if btn_volver_controles.check_hover(mouse_pos):
                    estado_actual = config.MENU_PRINCIPAL
            
            elif estado_actual == config.INTRO:
                if btn_skip.check_hover(mouse_pos):
                    estado_actual = config.SELECCION_GATO

            elif estado_actual == config.SELECCION_GATO:
                if btn_prev.check_hover(mouse_pos):
                    gato_actual_idx = (gato_actual_idx - 1) % len(config.GATOS_DISPONIBLES)
                elif btn_next.check_hover(mouse_pos):
                    gato_actual_idx = (gato_actual_idx + 1) % len(config.GATOS_DISPONIBLES)
                elif btn_confirmar.check_hover(mouse_pos):
                    estado_actual = config.MENU_NIVELES
                elif btn_volver_seleccion.check_hover(mouse_pos):
                    estado_actual = config.MENU_PRINCIPAL

            elif estado_actual == config.MENU_NIVELES:
                if rect_lvl1.collidepoint(mouse_pos):
                    iniciar_juego_desde_nivel(1)
                elif rect_lvl2.collidepoint(mouse_pos):
                    iniciar_juego_desde_nivel(2)
                elif rect_lvl3.collidepoint(mouse_pos):
                    iniciar_juego_desde_nivel(3)
                elif btn_volver_niveles.check_hover(mouse_pos):
                    estado_actual = config.SELECCION_GATO

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
                    jefe_generado_nivel = False
                    score_nivel = 0 
                    tiempo_inicio_nivel = pygame.time.get_ticks() 
                    actualizar_fondo_nivel()
                    crear_enemigos()
                    estado_actual = config.JUEGO
                elif btn_menu_completado.check_hover(mouse_pos):
                    estado_actual = config.MENU_PRINCIPAL

            elif estado_actual == config.GAME_OVER:
                if btn_reintentar.check_hover(mouse_pos):
                    iniciar_juego_desde_nivel(nivel_inicial)
                elif btn_volver_go.check_hover(mouse_pos):
                    estado_actual = config.MENU_PRINCIPAL

    if estado_actual != config.INTRO and estado_actual != config.CONTROLES:
        if bg_actual_img and "galaxia.jpg" in bg_actual_img:
            if estado_actual != config.GAME_OVER and estado_actual != config.PAUSA and estado_actual != config.NIVEL_COMPLETADO and estado_actual != config.INGRESO_NOMBRE:
                y_fondo = (y_fondo + 1) % config.H
            window.blit(bg, (0, y_fondo))
            window.blit(bg, (0, y_fondo - config.H))
        else:
            window.blit(bg, (0, 0))
    else:
        window.fill((0, 0, 0))

    if estado_actual == config.INTRO:
        now = pygame.time.get_ticks()
        if now - last_type_time > 50:
            if char_index < len(intro_text[current_line]):
                char_index += 1
            elif current_line < len(intro_text) - 1:
                current_line += 1
                char_index = 0
            else:
                if now - last_type_time > 2000:
                    estado_actual = config.SELECCION_GATO
            last_type_time = now

        for i in range(current_line + 1):
            text_to_draw = intro_text[i][:char_index] if i == current_line else intro_text[i]
            surf = font_story.render(text_to_draw, True, (255, 255, 255))
            window.blit(surf, (50, 100 + i * 50))
        
        btn_skip.check_hover(mouse_pos)
        btn_skip.draw(window, font_btn)

    elif estado_actual == config.MENU_PRINCIPAL:
        font_title = pygame.font.SysFont("Courier New", 80, bold=True)
        font_subtitle = pygame.font.SysFont("Courier New", 40, bold=True)

        btn_jugar.check_hover(mouse_pos)
        btn_controles.check_hover(mouse_pos)
        btn_salir.check_hover(mouse_pos)

        try:
            gato_img = pygame.image.load(config.GATOS_DISPONIBLES[0]).convert_alpha()
            gato_img = pygame.transform.smoothscale(gato_img, (130, 130))
            window.blit(gato_img, (config.W // 2 - 65, config.H // 2 - 300))
        except:
            pass

        t_titulo = "ETHEL(UIA)"
        w_tit = font_title.render(t_titulo, True, (0,0,0)).get_width()
        draw_text_outlined(window, t_titulo, font_title, (75, 0, 130), (255, 215, 0), config.W // 2 - w_tit // 2, config.H // 2 - 200)

        t_sub = "LOST GALAXY"
        w_sub = font_subtitle.render(t_sub, True, (0,0,0)).get_width()
        draw_text_with_shadow(window, t_sub, font_subtitle, (255, 255, 255), config.W // 2 - w_sub // 2, config.H // 2 - 120)

        btn_jugar.draw(window, font_btn)
        btn_controles.draw(window, font_btn)
        btn_salir.draw(window, font_btn)

    elif estado_actual == config.CONTROLES:
        t_ct = "CONTROLES"
        w_ct = font_big.render(t_ct, True, (0,0,0)).get_width()
        draw_text_with_shadow(window, t_ct, font_big, (212, 175, 55), config.W // 2 - w_ct // 2, 40)

        instrucciones = [
            ("FLECHAS / A-D", "Mover la nave"),
            ("ESPACIO", "Disparar proyectil"),
            ("ESC", "Pausar / Volver")
        ]

        for i, (tecla, desc) in enumerate(instrucciones):
            y_pos = 150 + (i * 65)
            draw_text_with_shadow(window, f"> {tecla}:", font_small, (255, 215, 0), config.W // 2 - 300, y_pos)
            draw_text_with_shadow(window, desc, font_small, (255, 255, 255), config.W // 2 + 10, y_pos)

        btn_volver_controles.check_hover(mouse_pos)
        btn_volver_controles.draw(window, font_btn)

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

    elif estado_actual == config.MENU_NIVELES:
        t_niv = "ELIGE TU DESTINO"
        w_niv = font_big.render(t_niv, True, (0,0,0)).get_width()
        draw_text_with_shadow(window, t_niv, font_big, (212, 175, 55), config.W // 2 - w_niv // 2, 40)
        para_renderizar = [
            (rect_lvl1, miniatura_lvl1, "ESPACIO", "FÁCIL"),
            (rect_lvl2, miniatura_lvl2, "TIERRA", "NORMAL"),
            (rect_lvl3, miniatura_lvl3, "MARTE", "DIFÍCIL")
        ]
        for rect, img_fondo, texto, dificultad in para_renderizar:
            window.blit(img_fondo, rect.topleft)
            if rect.collidepoint(mouse_pos):
                overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                overlay.fill((255, 255, 255, 60))
                window.blit(overlay, rect.topleft)
                color_borde = (255, 215, 0)
            else:
                color_borde = (255, 255, 255)
            pygame.draw.rect(window, color_borde, rect, width=3, border_radius=5)
            
            w_txt = font_btn.render(texto, True, (0,0,0)).get_width()
            draw_text_with_shadow(window, texto, font_btn, (255, 255, 255), rect.centerx - w_txt // 2, rect.centery - 25)
            
            color_dif = (200, 200, 200)
            if dificultad == "FÁCIL": color_dif = (0, 255, 0)
            elif dificultad == "NORMAL": color_dif = (255, 255, 0)
            elif dificultad == "DIFÍCIL": color_dif = (255, 0, 0)
            
            w_dif = font_small.render(dificultad, True, (0,0,0)).get_width()
            draw_text_with_shadow(window, dificultad, font_small, color_dif, rect.centerx - w_dif // 2, rect.centery + 5)
            
        btn_volver_niveles.check_hover(mouse_pos)
        btn_volver_niveles.draw(window, font_btn)

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
        
        tiempo_transcurrido = pygame.time.get_ticks() - tiempo_inicio_nivel
        
        if not boss_active:
            if not jefe_generado_nivel and (score_nivel >= 3000 or tiempo_transcurrido >= TIEMPO_PARA_JEFE):
                spawn_boss(nivel_actual)
                jefe_generado_nivel = True
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
                    
                    img_e, img_b, b_scale, e_scale, cd_min, cd_max = obtener_recursos_nivel(nivel_actual)
                    lado = choice(["izquierda", "derecha"])
                    x_spawn = -60 if lado == "izquierda" else config.W + 60
                    
                    speed_mod = score // 2000
                    enemy = Enemy(img_e, x_spawn, randint(50, config.H // 2 - 50), randint(3 + speed_mod, 6 + speed_mod), img_b, b_scale, escala=e_scale, cooldown_min=cd_min, cooldown_max=cd_max)
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
                    if nivel_actual == 3:
                        if es_nuevo_record(score, datos_juego["leaderboard"]):
                            estado_actual = config.INGRESO_NOMBRE
                            nombre_ingresado = ""
                        else:
                            estado_actual = config.GAME_OVER 
                    else:
                        estado_actual = config.NIVEL_COMPLETADO

        if not ethel.inmune:
            if pygame.sprite.spritecollide(ethel, enemys, False) or pygame.sprite.spritecollide(ethel, enemy_bullets, False) or pygame.sprite.spritecollide(ethel, bosses, False):
                vidas -= 1  
                enemy_bullets.empty()  
                desencadenar_explosion(ethel.rect.centerx, ethel.rect.centery)
                if vidas <= 0:
                    if es_nuevo_record(score, datos_juego["leaderboard"]):
                        estado_actual = config.INGRESO_NOMBRE
                        nombre_ingresado = ""
                    else:
                        datos_juego["vidas"] = 3
                        guardar_datos(datos_juego)
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
        draw_text_with_shadow(window, "VIDAS:", font_score, (255, 255, 255), 290, 15)
        max_corazones_visuales = min(vidas, 3)
        for i in range(max_corazones_visuales):
            x_corazon = 380 + (i * 45)
            window.blit(img_corazon, (x_corazon, 12))
        if vidas > 3:
            draw_text_with_shadow(window, f"+{vidas - 3}", font_score, (255, 50, 50), 380 + (3 * 45), 15)
        if boss_active:
             for b in bosses:
                pygame.draw.rect(window, (255,0,0), (200, 60, 400, 20))
                pygame.draw.rect(window, (0,255,0), (200, 60, 400 * (b.vida/b.max_vida), 20))
        btn_hud_pausa.check_hover(mouse_pos)
        btn_hud_pausa.draw(window, font_pausa_btn)
        
    elif estado_actual == config.INGRESO_NOMBRE:
        enemys.draw(window)
        ethel.draw(window)
        bullets.draw(window)
        enemy_bullets.draw(window)
        bosses.draw(window)
        powerups.draw(window)
        overlay = pygame.Surface((config.W, config.H))
        overlay.set_alpha(180) 
        overlay.fill((0, 0, 0)) 
        window.blit(overlay, (0, 0))
        t_nr = "¡NUEVO RÉCORD!"
        w_nr = font_big.render(t_nr, True, (0,0,0)).get_width()
        draw_text_with_shadow(window, t_nr, font_big, (255, 215, 0), config.W // 2 - w_nr // 2, config.H // 2 - 150)
        t_inst = "INGRESA TUS INICIALES (3)"
        w_inst = font_small.render(t_inst, True, (0,0,0)).get_width()
        draw_text_with_shadow(window, t_inst, font_small, (255, 255, 255), config.W // 2 - w_inst // 2, config.H // 2 - 80)
        t_name = nombre_ingresado + ("_" * (3 - len(nombre_ingresado)))
        w_name = font_big.render(t_name, True, (0,0,0)).get_width()
        draw_text_with_shadow(window, t_name, font_big, (255, 255, 255), config.W // 2 - w_name // 2, config.H // 2)

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
        draw_text_with_shadow(window, "VIDAS:", font_score, (255, 255, 255), 290, 15)
        max_corazones_visuales = min(vidas, 3)
        for i in range(max_corazones_visuales):
            window.blit(img_corazon, (380 + (i * 45), 12))
        if vidas > 3:
            draw_text_with_shadow(window, f"+{vidas - 3}", font_score, (255, 50, 50), 380 + (3 * 45), 15)
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
        overlay.set_alpha(180) 
        overlay.fill((0, 0, 0)) 
        window.blit(overlay, (0, 0))
        t_go = "GAME OVER"
        t_sc = f"TU PUNTUACIÓN: {score}"
        w_go = font_big.render(t_go, True, (0,0,0)).get_width()
        w_sc = font_score.render(t_sc, True, (0,0,0)).get_width()
        draw_text_with_shadow(window, t_go, font_big, (255, 50, 50), config.W // 2 - w_go // 2, config.H // 2 - 220)
        draw_text_with_shadow(window, t_sc, font_score, (255, 255, 255), config.W // 2 - w_sc // 2, config.H // 2 - 160) 
        t_lb = "--- MEJORES PILOTOS ---"
        w_lb = font_score.render(t_lb, True, (0,0,0)).get_width()
        draw_text_with_shadow(window, t_lb, font_score, (50, 255, 50), config.W // 2 - w_lb // 2, config.H // 2 - 100)
        for i, record in enumerate(datos_juego["leaderboard"]):
            t_rec = f"{i+1}. {record['nombre']} - {record['score']}"
            w_rec = font_score.render(t_rec, True, (0,0,0)).get_width()
            color = (255, 215, 0) if i == 0 else (255, 255, 255)
            draw_text_with_shadow(window, t_rec, font_score, color, config.W // 2 - w_rec // 2, config.H // 2 - 50 + (i * 35))
        btn_reintentar.draw(window, font_btn)
        btn_volver_go.draw(window, font_btn)
    pygame.display.update()

pygame.quit()