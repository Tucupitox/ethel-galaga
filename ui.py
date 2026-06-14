import pygame

class MenuButton:
    def __init__(self, text, x, y, width, height, is_circle=False):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.base_color = (90, 41, 163)
        self.hover_color = (117, 59, 206)
        self.border_color = (212, 175, 55)
        self.hover_border_color = (255, 240, 170)
        self.is_hovered = False
        self.is_circle = is_circle

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered

    def draw(self, surface, font):
        color = self.hover_color if self.is_hovered else self.base_color
        b_color = self.hover_border_color if self.is_hovered else self.border_color
        rad = self.rect.width // 2 if self.is_circle else 12
        
        pygame.draw.rect(surface, color, self.rect, border_radius=rad)
        pygame.draw.rect(surface, b_color, self.rect, width=3, border_radius=rad)
        
        text_surf = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        
        text_shadow = font.render(self.text, True, (0, 0, 0))
        surface.blit(text_shadow, (text_rect.x + 2, text_rect.y + 2))
        surface.blit(text_surf, text_rect)

def draw_text_with_shadow(surface, text, font, color=(255, 255, 255), x=0, y=0):
    text_shadow = font.render(text, True, (0, 0, 0))
    text_main = font.render(text, True, color)
    surface.blit(text_shadow, (x + 2, y + 2))
    surface.blit(text_main, (x, y))