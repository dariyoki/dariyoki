import pygame


class ChooseOption:
    def __init__(self, option_images: list[pygame.Surface], screen):
        self.screen = screen
        self.option_rects = [img.get_rect() for img in option_images]
        self.size = 32
        for index, rect in enumerate(self.option_rects):
            rect.x = (index * rect.width) + 10
            rect.y += 10
        self.option_img_pos = list(zip(option_images, self.option_rects))
        self.chosen_option = 0
        self.dt = 0

    def update(self, mouse_pos, dt):
        self.dt = dt

        if pygame.mouse.get_pressed()[0]:
            for index, rect in enumerate(self.option_rects):
                if rect.collidepoint(mouse_pos):
                    self.chosen_option = index

    def draw(self):
        for image, rect in self.option_img_pos:
            self.screen.blit(image, rect)
        pygame.draw.rect(self.screen, "yellow", self.option_img_pos[self.chosen_option][1], width=2)
