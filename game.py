import time
import pygame
import sys
from bullet import *
from characters import *
from util import *
from walls import *

class TreasureChest:
    def __init__(self, x, y):
        self.closed_image = pygame.image.load("images/chest_closed.png").convert_alpha()
        self.opened_image = pygame.image.load("images/chest_opened.png").convert_alpha()
        self.size = 50
        self.closed_image = pygame.transform.scale(self.closed_image, (self.size, self.size))
        self.opened_image = pygame.transform.scale(self.opened_image, (self.size, self.size))

        self.rect = pygame.Rect(x, y, self.size, self.size)
        self.is_opened = False

    def draw(self, screen, camera_x, camera_y):
        if self.is_opened:
            screen.blit(self.opened_image, (self.rect.x - camera_x, self.rect.y - camera_y))
        else:
            screen.blit(self.closed_image, (self.rect.x - camera_x, self.rect.y - camera_y))
            

class HealthDrop:
    def __init__(self, x, y):
        self.image = pygame.image.load("images/heart.png").convert_alpha()
        self.size = 30
        self.image = pygame.transform.scale(self.image, (self.size, self.size))

        self.x = x
        self.y = y
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)

    def draw(self, screen, camera_x, camera_y):
        screen.blit(self.image, (self.x - camera_x, self.y - camera_y))


class ZombieShooter:
    def __init__(self, window_width, window_height, world_width, world_height, fps, sound=False):
        self.window_width = window_width
        self.window_height = window_height
        self.world_width = world_width
        self.world_height = world_height
        self.treasure_chest = None
        self.health_drop = None
        self.paused = False
        self.gun_type = "single"
        self.fire_mode = "single"

        pygame.init()
        self.screen = pygame.display.set_mode((window_width, window_height))
        pygame.display.set_caption("Zombie Shooter")
        self.font = pygame.font.SysFont(None, 36)
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.walls = walls_1

        self.player = Player(world_width=self.world_width, world_height=self.world_height, walls=self.walls)

        self.background_color = (181, 101, 29)
        self.wall_color = (1, 50, 32)
        self.border_color = (255, 0, 0)
        self.announcement_font = pygame.font.SysFont(None, 100)
        self.out_of_ammo_message_displayed = False
        self.bullets = []
        self.zombies = []
        self.zombie_top_speed = 1
        self.level_goal = 5
        self.shotgun_ammo = 10
        self.max_zombie_count = 5
        self.level = 1
        self.sound = sound

        if self.sound:
            pygame.mixer.pre_init(44100, -16, 2, 64)
            pygame.mixer.init()
            pygame.mixer.music.load("sounds/background_music.wav")
            pygame.mixer.music.play(-1, 0, 0)

            self.last_walk_play_time = 0

            self.zombie_bite = pygame.mixer.Sound("sounds/zombie_bite_1.wav")
            self.zombie_hit = pygame.mixer.Sound("sounds/zombie_hit.wav")
            self.shotgun_blast = pygame.mixer.Sound("sounds/shotgun_blast.wav")
            self.zombie_snarl = pygame.mixer.Sound("sounds/zombie_snarl.wav")
            self.footstep = pygame.mixer.Sound("sounds/footstep.wav")
            self.vocals_1 = pygame.mixer.Sound("sounds/one_of_those_things_got_in.wav")
            self.vocals_2 = pygame.mixer.Sound("sounds/virus_infection_alert.wav")
            self.vocals_3 = pygame.mixer.Sound("sounds/come_and_see.wav")

            self.vocals_1.play()

    def play_walking_sound(self):
        if self.sound:
            current_time = pygame.time.get_ticks()
            if (current_time - self.last_walk_play_time > 1000):
                self.footstep.play()
                self.last_walk_play_time = current_time 

    def start_next_level(self):
        self.level += 1

        if self.level > 3:
            next_level_surface = self.announcement_font.render("You Won!", True, (255, 0, 0))
        else:
            next_level_surface = self.announcement_font.render(f"Starting level {self.level}", True, (255, 0, 0))

        next_level_rect = next_level_surface.get_rect(center=(self.window_width // 2, self.window_height // 2))
        self.zombies = []
        self.bullets = []

        if self.level == 2:
            self.vocals_2.play()
            self.walls = walls_2
            self.level_goal = 15
        elif self.level == 3:
            self.vocals_3.play()
            self.walls = walls_3
            self.level_goal = 30

        self.screen.blit(next_level_surface, next_level_rect)

        x, y = random.randint(50, self.world_width - 50), random.randint(50, self.world_height - 50)
        self.treasure_chest = TreasureChest(x, y)

        self.zombie_top_speed += 1
        self.max_zombie_count += 2

        self.player = Player(world_height=self.world_height, world_width=self.world_width, walls=self.walls)
        pygame.display.flip()
        pygame.time.wait(4000)

        if self.level > 3:
            pygame.quit()
            sys.exit()

    def game_over(self):
        game_over_surface = self.announcement_font.render('You Died', True, (255, 0, 0))
        game_over_rect = game_over_surface.get_rect(center=(self.window_width // 2, self.window_height // 2))
        self.screen.blit(game_over_surface, game_over_rect)
        pygame.display.flip()

        self.zombie_snarl.play()

        pygame.time.wait(2000)

        pygame.quit()
        sys.exit()

    def fill_background(self):
        self.screen.fill(self.background_color)

        score_surface = self.font.render(f"Score: {self.player.score}", True, (0, 0, 0))
        self.screen.blit(score_surface, (10, 10))

        health_surface = self.font.render(f"Health: {self.player.health}", True, (0, 0, 0))
        self.screen.blit(health_surface, (10, 35))

        level_surface = self.font.render(f"Level: {self.level}", True, (0, 0, 0))
        self.screen.blit(level_surface, (10, 60))

        ammo_surface = self.font.render(f"Shotgun Ammo: {self.shotgun_ammo}", True, (0, 0, 0))
        self.screen.blit(ammo_surface, (10, 85))
        
        gun_type_surface = self.font.render(f"Gun: {self.gun_type}", True, (0, 0, 0))
        self.screen.blit(gun_type_surface, (10, 110))

        if self.out_of_ammo_message_displayed and self.gun_type == "shotgun":
            out_of_ammo_surface = self.font.render(
                "Out of shotgun ammo! Press TAB to switch to a single shot.", True, (255, 0, 0)
            )
            out_of_ammo_rect = out_of_ammo_surface.get_rect(center=(self.window_width // 2, self.window_height // 2))
            self.screen.blit(out_of_ammo_surface, out_of_ammo_rect)

    def fire_single_bullet(self):
        bullet = SingleBullet(self.player.x, self.player.y, self.player.direction)
        self.bullets.append(bullet)
        self.shotgun_blast.play()

    def fire_shotgun_bullet(self):
        if self.shotgun_ammo > 0:
            directions = [
                (self.player.direction, 0),
                (self.player.direction, -10),
                (self.player.direction, 10)
            ]

            for direction, angle_offset in directions:
                bullet = ShotgunBullet(self.player.x, self.player.y, direction, angle_offset)
                self.bullets.append(bullet)

            self.shotgun_ammo -= 1
            self.out_of_ammo_message_displayed = False
            self.shotgun_blast.play()
        else:
            print("Out of shotgun ammo")
            self.out_of_ammo_message_displayed = True

    def toggle_pause(self):
        self.paused = not self.paused
        if self.paused:
            pause_surface = self.announcement_font.render("Game Paused", True, (255, 255, 255))
            pause_rect = pause_surface.get_rect(center=(self.window_width // 2, self.window_height // 2))
            self.screen.blit(pause_surface, pause_rect)
            pygame.display.flip()

            while self.paused:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.paused = False
                self.clock.tick(10)
    
    def step(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    self.gun_type = "single" if self.gun_type == "shotgun" else "shotgun"
                    print(f"Switched to {self.gun_type} mode")
                elif event.key == pygame.K_SPACE:
                    if self.gun_type == "single":
                        self.fire_single_bullet()
                    else:
                        self.fire_shotgun_bullet()
                elif event.key == pygame.K_ESCAPE:
                    self.toggle_pause()

        if self.paused:
            return
        
        player_moved = False

        if len(self.zombies) < self.max_zombie_count and random.randint(1, 100) < 3:
            self.zombies.append(Zombie(world_height=self.world_height, world_width=self.world_width, size=80, speed=random.randint(1, self.zombie_top_speed)))

        keys = pygame.key.get_pressed()

        new_player_x = self.player.x

        if keys[pygame.K_a]:
            new_player_x -= self.player.speed
            self.player.direction = "left"
        if keys[pygame.K_d]:
            new_player_x += self.player.speed
            self.player.direction = "right"

        new_player_rect = pygame.Rect(new_player_x, self.player.y, self.player.size, self.player.size)
        collision = check_collision(new_player_rect, self.walls)

        if not collision and self.player.x != new_player_x \
            and (0 <= new_player_x <= self.world_width - self.player.size):
            self.player.x = new_player_x 
            self.play_walking_sound()

        new_player_y = self.player.y

        if keys[pygame.K_w]:
            new_player_y -= self.player.speed
            self.player.direction = "up"
        if keys[pygame.K_s]:
            new_player_y += self.player.speed
            self.player.direction = "down"

        new_player_rect = pygame.Rect(self.player.x, new_player_y, self.player.size, self.player.size)
        collision = check_collision(new_player_rect, self.walls)

        if not collision and self.player.y != new_player_y \
            and (0 <= new_player_y <= self.world_height - self.player.size):
            self.player.y = new_player_y
            self.play_walking_sound()

        self.player.rect = pygame.Rect(self.player.x, self.player.y, self.player.size, self.player.size)
        collision = False

        camera_x = self.player.x - self.window_width // 2
        camera_y = self.player.y - self.window_height // 2

        camera_x = max(0, min(camera_x, self.world_width - self.window_width))
        camera_y = max(0, min(camera_y, self.world_height - self.window_height))

        self.zombies_temp = []

        for zombie in self.zombies:
            if check_collision(zombie.rect, self.bullets):
                bullet = get_collision(zombie.rect, self.bullets)
                self.player.score += 1
                self.bullets.remove(bullet)
                if self.sound:
                    self.zombie_hit.play()

                if random.randint(1, 100) <= 20:
                    self.health_drop = HealthDrop(zombie.rect.x, zombie.rect.y)

            elif check_collision(zombie.rect, [self.player.rect]):
                self.player.health -= 1
                if self.sound:
                    self.zombie_bite.play()
            else:
                self.zombies_temp.append(zombie)
        
        self.zombies = self.zombies_temp

        for zombie in self.zombies:
            zombie.move_toward_player(self.player.x, self.player.y, self.walls)

        self.fill_background()

        for bullet in self.bullets:
            bullet.move()
            bullet.draw(self.screen, camera_x, camera_y)

            if check_collision(bullet.rect, self.walls):
                self.bullets.remove(bullet)

        self.player.draw(self.screen, camera_x, camera_y)

        for zombie in self.zombies:
            zombie.draw(self.screen, camera_x, camera_y)

        if self.health_drop:
            self.health_drop.draw(self.screen, camera_x, camera_y)

        pygame.draw.rect(self.screen, self.border_color, (0 - camera_x, 0 - camera_y, self.world_width, self.world_height), 5)

        for wall in self.walls:
            pygame.draw.rect(self.screen, self.wall_color, (wall.x - camera_x, wall.y - camera_y, wall.width, wall.height))

        if self.treasure_chest:
            self.treasure_chest.draw(self.screen, camera_x, camera_y)

        if self.treasure_chest and self.player.rect.colliderect(self.treasure_chest):
            if not self.treasure_chest.is_opened:
                self.treasure_chest.is_opened = True
                self.shotgun_ammo = min(self.shotgun_ammo + 5, 20)
                print(f"Ammo refilled! Current ammo: {self.shotgun_ammo}")
        
        if self.health_drop and self.player.rect.colliderect(self.health_drop.rect):
            self.player.health = min(self.player.health + 1, 100)
            print("Heart collected!")
            self.health_drop = None

        pygame.display.flip()

        if self.player.health <=0:
            self.game_over()

        self.clock.tick(self.fps)

        if self.level_goal <= self.player.score:
            self.start_next_level()