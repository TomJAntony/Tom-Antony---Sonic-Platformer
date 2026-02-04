import pygame as py
import sys
import random as r

py.init()
py.mixer.init()

class GameObject:
    def __init__(self, x, y, width, height, color=(255, 255, 255)):
        self.rect = py.Rect(x, y, width, height)
        self.surface = py.Surface((width, height))
        self.surface.fill(color)

    def draw(self, screen):
        screen.blit(self.surface, (self.rect.x, self.rect.y))


class Player(GameObject):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.is_disabled = False
        self.surface = py.image.load("images/sonic_icon2.png").convert_alpha()
        self.surface = py.transform.scale(self.surface, (width, height))
        self.visible = True
        self.facing_right = True  # Track last facing direction
        self.is_stationary = True  # Track if the player is stationary
        self.is_at_max_speed = False

        # Player-specific attributes
        self.x_speed = 0
        self.y_speed = 0
        self.max_speed = 15
        self.acceleration = 0.125
        self.air_acceleration = 0.8
        self.deceleration = 0.2
        self.max_speed_jump = 23
        self.gravity = 0.5
        self.low_gravity = 0.5
        self.grounded = False
        self.is_jumping = False
        self.holding_jump = False
        self.current_speed = 0

    def handle_movement(self, keys):
        self.is_at_max_speed = False
        if self.is_disabled:
            return

        if keys[py.K_d] or keys[py.K_RIGHT]:
            self.facing_right = True
            self.is_stationary = False
            if self.grounded:
                if self.current_speed < 0:
                    self.current_speed += self.deceleration * 2
                elif self.current_speed < self.max_speed:
                    self.   current_speed += self.acceleration
            else:
                self.current_speed = min(self.current_speed + self.air_acceleration, self.max_speed)
            self.rect.x += self.current_speed
            if not self.is_jumping:
                self.surface = py.transform.scale(
                py.transform.flip(py.image.load("images/SonicSpriteRun.png"), False, False)
                , (100, 100))
            if self.current_speed == self.max_speed:
                self.is_at_max_speed = True
            if not self.is_at_max_speed == True and self.current_speed <= 5 and not self.is_jumping:
                self.surface = py.transform.scale(py.transform.flip(py.image.load("images/SonicSpriteWalk1.png"),
                                                                    False, False), (100,100))
            elif not self.is_at_max_speed == True and self.current_speed <= 10 and not self.is_jumping:
                self.surface = py.transform.scale(py.transform.flip(py.image.load("images/SonicSpriteWalk2.png"),
                                                                    False, False), (100,100))

        elif keys[py.K_a] or keys[py.K_LEFT]:
            self.facing_right = False
            self.is_stationary = False
            if not self.is_jumping:
                self.surface = py.transform.scale(
                py.transform.flip(py.image.load("images/SonicSpriteRun.png"), True, False)
                , (100, 100))
            if self.grounded:
                if self.current_speed > 0:
                    self.current_speed -= self.deceleration * 2
                elif self.current_speed > -self.max_speed:
                    self.current_speed -= self.acceleration
            else:
                self.current_speed = max(self.current_speed - self.air_acceleration, -self.max_speed)
            self.rect.x += self.current_speed
            if self.current_speed == -self.max_speed:
                self.is_at_max_speed = True
            #sprite changes
            if not self.is_at_max_speed == True and self.current_speed <= 5 and not self.is_jumping:
                self.surface = py.transform.scale(py.transform.flip(py.image.load("images/SonicSpriteWalk1.png"),
                                                                    True, False), (100,100))
            elif not self.is_at_max_speed == True and self.current_speed <= 12 and not self.is_jumping:
                self.surface = py.transform.scale(py.transform.flip(py.image.load("images/SonicSpriteWalk2.png"),
                                                                    True, False), (100,100))

        else:  # Deceleration when no keys are pressed
            if self.current_speed > 0:
                self.current_speed -= self.deceleration
            elif self.current_speed < 0:
                self.current_speed += self.deceleration
            if abs(self.current_speed) < self.deceleration:
                self.current_speed = 0
                self.is_stationary = True
            self.rect.x += self.current_speed

        if self.is_stationary == True and self.facing_right == True and not self.is_jumping:
            self.surface = py.transform.flip(py.transform.scale(py.image.load("images/SonicSpriteIdle.png"),(100,100))
                                             ,False,False)
        elif self.is_stationary == True and self.facing_right == False and not self.is_jumping:
            self.surface = py.transform.flip(py.transform.scale(py.image.load("images/SonicSpriteIdle.png"),(100,100))
                                             ,True,False)


    def apply_gravity(self):
        if not self.grounded:
            self.y_speed += self.gravity
        self.rect.y += self.y_speed

    def jump(self, keys):
        if (keys[py.K_SPACE]) and self.grounded:
            self.y_speed = -self.max_speed_jump
            self.grounded = False
            self.is_jumping = True
            self.holding_jump = True
            Game.player_jump.play()
            self.surface = py.transform.scale(py.image.load("images/SonicSpriteJump.png"),(100,100)).convert_alpha()


        if self.is_jumping:
            if keys[py.K_SPACE]:
                self.y_speed += self.low_gravity
            else:
                self.holding_jump = False

        if not self.holding_jump:
            self.y_speed += self.gravity

    def update(self, keys):
        if not self.is_disabled:
            self.handle_movement(keys)
            self.apply_gravity()
            self.jump(keys)

class Enemy:
    def __init__(self, x, y, width, height, color, speed_x, speed_y=0, flip = True):
        self.rect = py.Rect(x, y, width, height)
        self.flip = flip
        self.surface = py.image.load("images/BuzzBomberSpriteFly.png").convert_alpha()
        if not self.flip:
            self.surface = py.transform.flip(self.surface, True, False)
        self.surface = py.transform.scale(self.surface, (90, 85))
        self.initial_x = x
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.paused = False
        self.pause_start_time = 0

    def move(self):
        if not self.paused:
            self.rect = self.rect.move(self.speed_x, self.speed_y)
            distance = abs(self.rect.x - self.initial_x)
            if distance >= 100:
                self.toggle_pause()

    def reset_position_if_paused(self):
        if self.paused and py.time.get_ticks() - self.pause_start_time >= r.randint(2000, 5000):
            self.paused = False
            self.initial_x = self.rect.x
            self.surface = py.image.load("images/BuzzBomberSpriteFly.png").convert_alpha()
            if self.flip:
                self.surface = py.transform.flip(self.surface, True, False)
            self.surface = py.transform.flip(py.transform.scale(self.surface, (90, 85)),
                            True,False)

    def toggle_pause(self):
        self.paused = True
        self.pause_start_time = py.time.get_ticks()
        self.initial_x = self.rect.x

        self.surface = py.transform.flip(py.image.load("images/BuzzBomberSpriteShoot.png").convert_alpha(),
                                          True,False)
        if self.flip:
            self.surface = py.transform.flip(self.surface, True, False)

        self.surface = py.transform.scale(self.surface, (90, 85))

        if self.flip:
            new_projectile = Projectile(self.rect.x-40, self.rect.y+50,speed_x=-6)
        else:
            new_projectile = Projectile(self.rect.x+40, self.rect.y+50)
        
        Game.badnik_shoot.set_volume(0.1)
        Game.badnik_shoot.play()
        return new_projectile

class EnemyTypeB(Enemy):
    def __init__(self, x, y, width, height, color, speed_x,flip=False):
        super().__init__(x, y, width, height, color, speed_x,flip=flip)
        self.surface = py.transform.scale(py.transform.flip(py.image.load("images/MotobugSprite.png")
                                                            ,True, False), (100,100))
        self.initial_x = 400
        self.speed_y = 0
        if flip:
            self.surface = py.transform.flip(self.surface, True, False)

    def move(self):
        self.rect = self.rect.move(self.speed_x, 0)


class Projectile:
    def __init__(self, x, y, width=20, height=20, color=(255, 255, 0), speed_x=6, speed_y=6):
        self.rect = py.Rect(x, y, width, height)
        self.surface = py.image.load("images/EnemyProjectile.png").convert_alpha()
        self.speed_x = speed_x
        self.speed_y = speed_y

    def move(self):
        self.rect = self.rect.move(self.speed_x, self.speed_y)

class Ring(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, 30, 30)
        self.surface = py.image.load("images/SonicRing.png").convert_alpha()
        self.surface = py.transform.scale(self.surface, (30, 30))
        self.spawn_time = py.time.get_ticks()
        self.lifetime = 10000

    def despawn(self):
        current_time = py.time.get_ticks()
        return current_time - self.spawn_time >= self.lifetime

class Game:
    # Class variables for sounds
    badnik_spawn = py.mixer.Sound("sounds/badnik_spawn.wav")
    badnik_shoot = py.mixer.Sound("sounds/badnik_shoot.mp3")
    badnik_explode = py.mixer.Sound("sounds/badnik_break.mp3")
    player_die = py.mixer.Sound("sounds/player_die.wav")
    player_jump = py.mixer.Sound("sounds/player_jump.wav")
    player_hit = py.mixer.Sound("sounds/player_hit.wav")


    def __init__(self):
        self.screen = py.display.set_mode((1200, 600))
        py.display.set_caption("Sonic Game Simulator")
        self.clock = py.time.Clock()

        self.bgm = py.mixer.Sound("sounds/Test Zone.mp3")
        self.bgm.set_volume(0.2)
        self.game_win = py.mixer.Sound("sounds/game_win.wav")
        self.game_win.set_volume(0.4)
        self.game_win_length = self.game_win.get_length()
        self.start_time = py.time.get_ticks()

        self.invincibility_timer = 0
        self.safe_platform_y = 200

        self.is_game_over = False
        self.is_game_won = False
        self.game_over_font = py.font.Font("fonts/sonic-1-hud-font.ttf", 64)

        # Initialize game objects
        y_boundary = -1000

        self.player = Player(100, 0, 100, 100)
        self.floor = GameObject(0, 500, 1200, 100, color=(255, 255, 255))
        self.floor.surface = py.image.load("images/floor.png").convert_alpha()
        self.platform = GameObject(300, 250, 500, 300, color=(255, 0, 0))
        self.platform.surface = py.image.load("images/platform.png").convert_alpha()
        self.boundary_left = GameObject(0, y_boundary, 10, 5000)
        self.boundary_right = GameObject(1190, y_boundary, 10, 5000)

        self.next_spawn_time = py.time.get_ticks() + r.randint(1000, 4000)

        # Initialize enemies and projectiles lists
        self.enemies = []
        self.projectiles = []

        # UI variables
        self.score = 0
        self.rings = 0
        self.lives = 3
        self.start_time = py.time.get_ticks()
        self.font_color1 = (255,255,255)
        self.font_color2 = (255,255,255)
        self.font_color3 = (255,255,255)

        #checklist variables
        self.score_checklist_goal = r.randint(1,3) * 1
        self.rings_checklist_goal = r.randint(3,4) * 1
        self.enemies_checklist_goal = r.randint(3,4) * 1
        self.enemies_destroyed_checklist = 0

        # Load fonts and images for UI
        self.sonic_font = py.font.Font('fonts/sonic-1-hud-font.ttf', 32)
        self.sonic_font_small = py.font.Font('fonts/sonic-1-hud-font.ttf', 18)
        self.sonic_icon = py.image.load('images/sonic_icon2.png').convert_alpha()
        self.sonic_icon = py.transform.scale(self.sonic_icon, (30, 30))

        self.rings_list = []
        self.last_ring_spawn_time = py.time.get_ticks()
        self.ring_spawn_interval = 1500
        self.ring_sound = py.mixer.Sound("sounds/ring_collect.wav")

    def game_over(self):
        self.is_game_over = True

    def check_game_won(self):
        if self.font_color1 == (0,255,0) and self.font_color2 == (0,255,0) and self.font_color3 == (0,255,0):
            self.bgm.stop()
            self.channel = self.game_win.play(0)
            self.is_game_won = True
            self.display_win_message()
            self.sound_start_time = py.time.get_ticks()

    def display_win_message(self):
        win_text = self.sonic_font.render("YOU WIN!", True, (0, 255, 0))  # Green text
        self.player.surface = py.transform.scale(py.image.load("images/SonicSpriteWin.png").convert_alpha(),(100, 100))
        self.screen.blit(win_text, (self.screen.get_width() // 2 - win_text.get_width() // 2,
                                    self.screen.get_height() // 2 - win_text.get_height() // 2))


    def handle_win(self):
        self.bgm.stop()
        self.is_game_won = True


    def handle_collisions(self):
        self.player.grounded = False

        # Floor collision
        if self.player.rect.colliderect(self.floor.rect):
            self.player.rect.y = self.floor.rect.top - self.player.rect.height
            self.player.grounded = True
            self.player.y_speed = 0
            self.player.is_jumping = False

        # Platform collision
        if self.player.rect.y <= self.platform.rect.top:
            if self.player.rect.colliderect(self.platform.rect) and self.player.y_speed > 0:
                self.player.rect.y = self.platform.rect.top - self.player.rect.height
                self.player.grounded = True
                self.player.is_jumping = False
                self.player.y_speed = 0

#note: the below is commented out bc it doesn't work!   
#        if not self.player.grounded:
#            self.player.surface = py.transform.scale(py.image.load("images/SonicSpriteJump.png").convert_alpha(),(100, 100))
#            if self.player.facing_right:
#                self.player.surface = py.transform.flip(self.player.surface,True,False)

        # Screen boundaries
        if self.player.rect.colliderect(self.boundary_right.rect):
            self.player.rect.right = self.boundary_right.rect.left
        if self.player.rect.colliderect(self.boundary_left.rect):
            self.player.rect.left = self.boundary_left.rect.right

        for ring in self.rings_list[:]:
            if self.player.rect.colliderect(ring.rect):
                self.rings_list.remove(ring)
                self.rings += 1
                self.ring_sound.play()

        # Check collisions with enemies and projectiles
        for enemy in self.enemies[:]:
            if self.player.rect.colliderect(enemy.rect):
                if self.player.y_speed > 0 and self.player.rect.bottom < enemy.rect.centery:
                    # Player is falling onto enemy - destroy enemy
                    self.enemies.remove(enemy)
                    self.enemies_destroyed_checklist += 1
                    self.score += 100
                    self.player.y_speed = -15  # Bounce off enemy
                    Game.badnik_explode.play()
                elif self.player.is_jumping == True and self.player.rect.colliderect(enemy.rect):
                    self.enemies.remove(enemy)
                    self.enemies_destroyed_checklist += 1
                    self.score += 100
                    Game.badnik_explode.play()
                else:
                    self.handle_damage()

        for projectile in self.projectiles[:]:
            if self.player.rect.colliderect(projectile.rect):
                self.handle_damage()
                self.projectiles.remove(projectile)

    def handle_damage(self):
        if self.invincibility_timer <= 0:  # Check if player is vulnerable
            if self.rings > 0:
                self.rings = 0
                self.player.current_speed = 0
                self.player.x_speed = 0
                self.player.acceleration = 0
                Game.player_hit.play()
            else:
                self.player.surface = py.transform.scale(py.image.load("images/SonicSpriteDeath.png").convert_alpha(),
                                                  (100, 100))
                self.lives -= 1
                self.is_disabled = True
                Game.player_die.play()
                self.player.current_speed = 0
                self.player.x_speed = 0
                self.player.acceleration = 0
                if self.lives <= 0:
                    self.lives = 0
                    self.game_over()
                    self.is_disabled = True
            # Set the invincibility timer after taking damage
            self.invincibility_timer = 1000
            self.player.visible = False

    def spawn_ring(self):
        current_time = py.time.get_ticks()
        if current_time - self.last_ring_spawn_time >= self.ring_spawn_interval:
            x = r.randint(50, 1150)
            y = r.randint(50, 450)
            new_ring = Ring(x, y)
            self.rings_list.append(new_ring)
            self.last_ring_spawn_time = current_time

    def update_rings(self):
        self.rings_list = [ring for ring in self.rings_list if not ring.despawn()]

    def draw_ui(self):
        # Update score and time
        if not self.is_game_over and not self.is_game_won:
            self.elapsed_time_ms = py.time.get_ticks() - self.start_time
        elapsed_time_ms = self.elapsed_time_ms
        elapsed_time_s = (elapsed_time_ms // 1000) % 60
        elapsed_time_m = (elapsed_time_ms // 1000) // 60
        formatted_time = f'{elapsed_time_m}:{elapsed_time_s:02d}'
        if elapsed_time_m > 120:
            sys.exit(0)

        # Render UI elements
        sonic_lives_text = self.sonic_font_small.render('SONIC', True, (255,255,0))
        score_text = self.sonic_font.render('SCORE', True, (255, 255, 0))
        score_value = self.sonic_font.render(f'{self.score}', True, (255, 255, 255))
        time_text = self.sonic_font.render('TIME', True, (255, 255, 0))
        time_value = self.sonic_font.render(f'{formatted_time}', True, (255, 255, 255))
        rings_text = self.sonic_font.render('RINGS', True, (255, 255, 0))
        rings_value = self.sonic_font.render(f'{self.rings}', True, (255, 255, 255))
        lives_text = self.sonic_font_small.render(f' x {self.lives}', True, (255, 255, 255))

        if self.score >= self.score_checklist_goal:
            self.font_color1 = (0,255,0)
        if self.enemies_destroyed_checklist >= self.enemies_checklist_goal:
            self.font_color3 = (0,255,0)
        if self.rings >= self.rings_checklist_goal:
            self.font_color2 = (0,255,0)


        #checklist
        checklist_text = self.sonic_font.render('Checklist: ',True,(255,255,255))
        score_checklist_text = self.sonic_font.render(f'Get a SCORE of {self.score_checklist_goal}',
                                                            True,self.font_color1)
        enemy_checklist_text = self.sonic_font.render(f'Defeat {self.enemies_checklist_goal} enemies'
                                                      ,True, self.font_color3)
        rings_checklist_text = self.sonic_font.render(f'Collect {self.rings_checklist_goal} rings',
                                                      True,self.font_color2)


        # Draw UI on screen
        self.screen.blit(self.sonic_icon, (30, 520))
        self.screen.blit(sonic_lives_text,(65,517))
        self.screen.blit(lives_text, (65, 532))
        self.screen.blit(score_text, (30, 15))
        self.screen.blit(score_value, (115, 15))
        self.screen.blit(time_text, (30, 50))
        self.screen.blit(time_value, (100, 50))
        self.screen.blit(rings_text, (30, 85))
        self.screen.blit(rings_value, (115, 85))
        self.screen.blit(rings_text, (30, 85))
        self.screen.blit(rings_value, (115, 85))
        self.screen.blit(checklist_text,(900,10))
        self.screen.blit(score_checklist_text,(900,40))
        self.screen.blit(enemy_checklist_text,(900,70))
        self.screen.blit(rings_checklist_text,(900,100))

    def log_enemy_spawn(self, enemy_type, spawn_side):
        print(f"Spawned {enemy_type} from the {spawn_side} side.")

    def handle_enemy_spawning(self, keys):
        current_time = py.time.get_ticks()
#        keys = py.key.get_pressed()

        spawn_from_left = r.choice([True, False])

        if spawn_from_left:
            x_pos = -60
            speed_x = r.randint(3, 5)
            spawn_side = "left"
            flip = False
        else:
            x_pos = self.screen.get_width() + 60
            speed_x = -r.randint(4, 7)
            spawn_side = "right"
            flip = True

        if current_time >= self.next_spawn_time:
            # Randomly choose which enemy to spawn
            if r.choice([True, False]):
                y_pos = 50
                new_enemy = Enemy(x_pos, y_pos, 50, 50, (255, 0, 0), speed_x=speed_x, flip=flip)
                enemy_type = "Enemy Type A"
            else:
                new_enemy = EnemyTypeB(x_pos, 410, 50, 50, (0, 0, 255), speed_x=speed_x, flip=flip)
                enemy_type = "Enemy Type B"

            self.log_enemy_spawn(enemy_type, spawn_side)



            Game.badnik_spawn.set_volume(0.2)
            Game.badnik_spawn.play()
            self.enemies.append(new_enemy)

            # Set the next spawn time to a random value between 1000 and 4000 ms
            self.next_spawn_time = current_time + r.randint(500, 3000)

    def update_enemies_and_projectiles(self):
        # Update projectiles
        for projectile in self.projectiles[:]:
            projectile.move()
            if (projectile.rect.right < 0 or projectile.rect.left > self.screen.get_width() or
                    projectile.rect.top > self.screen.get_height() or projectile.rect.bottom < 0):
                self.projectiles.remove(projectile)

        # Update enemies
        for enemy in self.enemies[:]:
            enemy.reset_position_if_paused()
            enemy.move()
            if isinstance(enemy, Enemy) and enemy.paused and py.time.get_ticks() - enemy.pause_start_time == 0:
                self.projectiles.append(enemy.toggle_pause())

    def run(self):
        self.bgm.play(-1)
        while True:
            keys = py.key.get_pressed()

            for event in py.event.get():
                if event.type == py.QUIT or keys[py.K_ESCAPE]:
                    py.quit()
                    sys.exit(0)
                elif event.type == py.USEREVENT:
                   py.quit()

            if not self.is_game_over and not self.is_game_won:
                self.handle_enemy_spawning(keys)
                self.player.update(keys)
                self.update_enemies_and_projectiles()
                self.spawn_ring()
                self.update_rings()
                self.handle_collisions()
                self.check_game_won()

            if self.is_game_won:
                self.display_win_message()
                if not self.channel.get_busy():
                    sys.exit(0)

            if self.invincibility_timer > 0:
                self.invincibility_timer -= self.clock.get_time()
                if self.invincibility_timer <= 0:
                    # Set player to idle state once invincibility timer is over
                    self.player.surface = py.image.load("images/SonicSpriteIdle.png").convert_alpha()
                    self.player.surface = py.transform.scale(self.player.surface, (100, 100))
                    self.player.visible = True  # Make the player visible again

                    # Reset the player's position after invincibility
                    if self.is_game_over:
                        self.player.rect.x = 350  # Set to desired X position
                        self.player.rect.y = self.safe_platform_y  # Move to the top of platform

                    # Disable movement while invincible (if applicable)
                    self.is_disabled = False

                else:
                    # While invincible, ensure the player doesn't switch to moving sprites
                    self.player.surface = py.image.load("images/SonicSpriteDeath.png").convert_alpha()
                    self.player.surface = py.transform.scale(self.player.surface, (100, 100))

            # Draw everything
            self.screen.fill((0, 0, 0))
            self.platform.draw(self.screen)
            self.floor.draw(self.screen)

            # Draw enemies and projectiles
            if not self.is_game_over:
                self.player.draw(self.screen)
                for enemy in self.enemies:
                    self.screen.blit(enemy.surface, (enemy.rect.x, enemy.rect.y))
                for projectile in self.projectiles:
                    self.screen.blit(projectile.surface, (projectile.rect.x, projectile.rect.y))
                for ring in self.rings_list:
                    ring.draw(self.screen)

            else:
                # Display "Game Over" text in the center of the screen
                game_over_text = self.game_over_font.render("GAME OVER", True, (255, 255, 255))
                text_rect = game_over_text.get_rect(
                    center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
                self.screen.blit(game_over_text, text_rect)
                self.player.surface = py.image.load("images/SonicSpriteIdle.png").convert_alpha()
                self.player.surface = py.transform.scale(self.player.surface, (100, 100))

            if not self.is_game_over:
                self.draw_ui()

            # Draw the UI
            self.draw_ui()

            py.display.flip()
            self.clock.tick(50)


if __name__ == "__main__":
    game = Game()
    game.run()