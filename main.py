import pygame, sys, random, math

from constant import *
from Ball import Ball
from Paddle import Paddle



class GameMain:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.music_channel = pygame.mixer.Channel(0)
        self.sound_channel = pygame.mixer.Channel(1)  # ช่องเสียงสำหรับเอฟเฟกต์ทั่วไป
        self.skill_channel = pygame.mixer.Channel(2)  # ช่องเสียงเฉพาะสำหรับสกิล
        self.music_channel.set_volume(0.5)

        self.sounds_list = {
            'paddle_hit': pygame.mixer.Sound('sounds/paddle_hit.wav'),
            'score': pygame.mixer.Sound('sounds/score.wav'),
            'wall_hit': pygame.mixer.Sound('sounds/wall_hit.wav'),
            'crowd': pygame.mixer.Sound('sounds/crowds.mp3')
        }
        self.muay_thai_sounds_list ={
            'bell': pygame.mixer.Sound('sounds/Bell.mp3')
        }
        self.skill_sounds_list = {
            'light': pygame.mixer.Sound('sounds/light.mp3'),
            'ice': pygame.mixer.Sound('sounds/ice.mp3'),
            'warp': pygame.mixer.Sound('sounds/warp.mp3')
        }
    
        self.very_small_font = pygame.font.Font('./font.ttf', 18)
        self.small_font = pygame.font.Font('./font.ttf', 24)
        self.large_font = pygame.font.Font('./font.ttf', 48)
        self.score_font = pygame.font.Font('./font.ttf', 96)

        pygame.mixer.music.load('sounds/muay.mp3')
        pygame.mixer.music.set_volume(0.05)
        pygame.mixer.music.play(-1)
        self.music_playing = 'muay'
        self.music_playing_battlesong = False
        self.player1_score = 0
        self.player2_score = 0
        self.serving_player = 1
        self.winning_player = 0
        self.hit_counter = 0
        self.paddle_width = 15
        self.paddle_height = 60
        self.ball_size = 12
        self.default_paddle_width = 15
        self.default_paddle_height = 60
        self.ai_pause_time = 0
        self.is_ai_paused = False
        self.pause_duration = random.uniform(0.5, 1.5)
        self.skills = ['ice', 'light', 'warp']
        self.player_skill = None
        self.ai_skill = None
        self.player_skill_uses = 1
        self.ai_skill_uses = 1
        self.original_ball_dx = 0
        self.original_ball_dy = 0

        # Initializing paddles in the center
        self.player1 = Paddle(self.screen,
                              30,
                              HEIGHT / 2 - self.default_paddle_height / 2,
                              self.default_paddle_width,
                              self.default_paddle_height,
                              (255, 0, 0))

        self.player2 = Paddle(self.screen,
                              WIDTH - 30 - self.default_paddle_width,
                              HEIGHT / 2 - self.default_paddle_height / 2,
                              self.default_paddle_width,
                              self.default_paddle_height,
                              (0, 0, 255))

        self.ball = Ball(self.screen, WIDTH / 2 - 6, HEIGHT / 2 - 6, 12, 12)

        self.game_state = 'start'
        self.ai_mode = 'weak'
        self.is_multiplayer = False
        self.weak_ai_direction = random.choice([-1, 1])

    def reset_paddles(self):
        self.player1.rect.x = 30
        self.player1.rect.y = HEIGHT / 2 - self.default_paddle_height / 2
        self.player1.rect.width = self.default_paddle_width
        self.player1.rect.height = self.default_paddle_height

        self.player2.rect.x = WIDTH - 30 - self.default_paddle_width
        self.player2.rect.y = HEIGHT / 2 - self.default_paddle_height / 2
        self.player2.rect.width = self.default_paddle_width
        self.player2.rect.height = self.default_paddle_height

    def reset_game(self):
        self.player1_score = 0
        self.player2_score = 0
        self.hit_counter = 0
        self.serving_player = random.choice([1, 2])
        self.player_skill_uses = 1
        self.ai_skill_uses = 1
        self.ball.Reset()
        self.reset_paddles()

    def update(self, dt, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if self.game_state == 'start':
                    if event.key == pygame.K_1:
                        self.player_skill = 'ice'
                    elif event.key == pygame.K_2:
                        self.player_skill = 'light'
                    elif event.key == pygame.K_3:
                        self.player_skill = 'warp'
                    elif event.key == pygame.K_RETURN and self.player_skill:
                        self.ai_skill = random.choice(self.skills)
                        self.game_state = 'serve'
                        if not self.music_playing_battlesong:
                            pygame.mixer.music.load('sounds/battlesong.mp3')
                            pygame.mixer.music.set_volume(0.05)
                            pygame.mixer.music.play(-1)
                            self.music_playing = 'battlesong'
                            self.music_playing_battlesong = True

                elif self.game_state == 'serve':
                    self.game_state = 'play'
                    self.music_channel.play(self.muay_thai_sounds_list['bell'])
                elif self.game_state == 'done':
                    if self.winning_player == 1 and self.ai_mode == 'weak':
                        self.ai_mode = 'strong'
                        self.player_skill_uses = 1
                        self.ai_skill_uses = 1
                        self.ai_skill = random.choice(self.skills)
                        self.reset_game()
                        self.game_state = 'serve'
                    elif self.winning_player == 1 and self.ai_mode == 'strong':
                        self.ai_mode = 'weak'
                        self.player_skill = None
                        self.reset_game()
                        self.game_state = 'start'
                    else:
                        self.ai_mode = 'weak'
                        self.player_skill = None
                        pygame.mixer.music.load('sounds/battlesong.mp3')
                        pygame.mixer.music.set_volume(0.05)
                        pygame.mixer.music.play(-1)
                        self.reset_game()
                        self.game_state = 'start'

                if event.key == pygame.K_r and self.game_state == 'play':
                    if self.player_skill and self.player_skill_uses > 0:
                        if self.player_skill == 'ice':
                            self.activate_ice_skill()
                        elif self.player_skill == 'light':
                            self.activate_light_skill()
                        elif self.player_skill == 'warp':
                            self.activate_warp_skill()
                        self.player_skill_uses -= 1

        if self.game_state == 'play':
            if random.random() < 0.001 and self.ai_skill_uses > 0:
                if self.ai_skill == 'ice':
                    self.activate_ice_skill()
                elif self.ai_skill == 'light':
                    self.activate_light_skill()
                elif self.ai_skill == 'warp':
                    self.activate_warp_skill()
                self.ai_skill_uses -= 1

        if self.game_state == 'serve':
            self.ball.dy = random.uniform(-150, 150)
            self.ball.dx = random.uniform(420, 600) if self.serving_player == 1 else -random.uniform(420, 600)

        elif self.game_state == 'play':
            if not self.music_playing_battlesong:
                if self.music_playing == 'muay':
                    pygame.mixer.music.load('sounds/battlesong.mp3')
                    pygame.mixer.music.set_volume(0.05)
                    pygame.mixer.music.play(-1)
                    self.music_playing = 'battlesong'
                    self.music_playing_battlesong = True
            if self.ball.Collides(self.player1) or self.ball.Collides(self.player2):
                self.hit_counter += 1
                if self.hit_counter % 5 == 0:
                    self.ball.dx *= 1.2
                    self.ball.dy *= 1.2

            if self.ball.Collides(self.player1):
                self.ball.dx = -self.ball.dx * 1.03
                self.ball.rect.x = self.player1.rect.x + 15
                self.player1.color = (0, 0, 0)
                self.ball.dy = -random.uniform(30, 450) if self.ball.dy < 0 else random.uniform(30, 450)
                self.sound_channel.play(self.sounds_list['paddle_hit'])

            if self.ball.Collides(self.player2):
                self.ball.dx = -self.ball.dx * 1.03
                self.ball.rect.x = self.player2.rect.x - 12
                self.player2.color = (0, 0, 0)
                self.ball.dy = -random.uniform(30, 450) if self.ball.dy < 0 else random.uniform(30, 450)
                self.sound_channel.play(self.sounds_list['paddle_hit'])

            if not self.ball.Collides(self.player1):
                self.player1.reset_color()
            if not self.ball.Collides(self.player2):
                self.player2.reset_color()

            if self.ball.rect.y <= 0 or self.ball.rect.y >= HEIGHT - 12:
                self.ball.rect.y = max(0, min(HEIGHT - 12, self.ball.rect.y))
                self.ball.dy = -self.ball.dy
                self.sound_channel.play(self.sounds_list['wall_hit'])

            if self.ball.rect.x < 0:
                self.serving_player = 1
                self.player2_score += 1
                self.hit_counter = 0
                self.sound_channel.play(self.sounds_list['score'])
                if self.ai_mode == 'strong':
                    self.player2.rect.height = self.default_paddle_height
                if self.player2_score == WINNING_SCORE:
                    self.winning_player = 2
                    self.game_state = 'done'
                else:
                    self.game_state = 'serve'
                    self.ball.Reset()
                    self.reset_paddles()

            if self.ball.rect.x > WIDTH:
                self.serving_player = 2
                self.player1_score += 1
                self.hit_counter = 0
                self.sound_channel.play(self.sounds_list['score'])
                if self.ai_mode == 'strong':
                    self.player2.rect.height = self.default_paddle_height

                if self.player1_score == WINNING_SCORE:
                    self.winning_player = 1
                    self.game_state = 'done'
                else:
                    self.game_state = 'serve'
                    self.ball.Reset()

        if self.game_state == 'play':
            key = pygame.key.get_pressed()
            if key[pygame.K_w]:
                self.player1.dy = -PADDLE_SPEED
            elif key[pygame.K_s]:
                self.player1.dy = PADDLE_SPEED
            else:
                self.player1.dy = 0

            if self.ai_mode == 'weak':
                if random.random() < 0.15:
                    target_y = self.ball.rect.y - self.player2.rect.height / 2 + self.ball.rect.height / 2
                    self.player2.rect.y = max(0, min(HEIGHT - self.player2.rect.height, target_y))
                else:
                    if self.player2.rect.y <= 0:
                        self.weak_ai_direction = 1
                    elif self.player2.rect.y + self.player2.rect.height >= HEIGHT:
                        self.weak_ai_direction = -1
                    self.player2.dy = PADDLE_SPEED * self.weak_ai_direction
                
            elif self.ai_mode == 'strong':
                # if not self.is_ai_paused:
                #     if self.ball.rect.y > self.player2.rect.y + self.player2.rect.height / 2:
                #         self.player2.dy = PADDLE_SPEED
                #     elif self.ball.rect.y < self.player2.rect.y + self.player2.rect.height / 2:
                #         self.player2.dy = -PADDLE_SPEED
                #     else:
                #         self.player2.dy = 0
                    
                #     if random.random() < 0.005:
                #         self.is_ai_paused = True
                #         self.ai_pause_time = 0
                #         self.pause_duration = random.uniform(0.2, 0.5)
                # else:
                #     self.player2.dy = 0
                #     self.ai_pause_time += dt
                #     if self.ai_pause_time >= self.pause_duration:
                #         self.is_ai_paused = False
                if random.random() < 0.30:
                    target_y = self.ball.rect.y - self.player2.rect.height / 2 + self.ball.rect.height / 2
                    self.player2.rect.y = max(0, min(HEIGHT - self.player2.rect.height, target_y))
                else:
                    if self.player2.rect.y <= 0:
                        self.weak_ai_direction = 1
                    elif self.player2.rect.y + self.player2.rect.height >= HEIGHT:
                        self.weak_ai_direction = -1
                    self.player2.dy = PADDLE_SPEED * self.weak_ai_direction
              
                if self.ball.Collides(self.player2):
                    self.player2.rect.height += 10

            self.ball.update(dt)
            self.player1.update(dt)
            self.player2.update(dt)

    def render(self):
        self.screen.fill((0, 32, 64))

        if self.game_state == 'start':
            t_welcome = self.small_font.render("Welcome to Pong!", False, (255, 255, 255))
            text_rect = t_welcome.get_rect(center=(WIDTH / 2, 30))
            self.screen.blit(t_welcome, text_rect)
            t_select = self.small_font.render("Select Devil Fruit: 1: Ice, 2: Light, 3: Warp", False, (255, 255, 255))
            text_rect = t_select.get_rect(center=(WIDTH / 2, HEIGHT / 2))
            self.screen.blit(t_select, text_rect)
            if self.player_skill:
                t_selected = self.small_font.render(f"Selected: {self.player_skill.capitalize()}", False, (0, 255, 0))
                text_rect = t_selected.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 40))
                self.screen.blit(t_selected, text_rect)
                if self.player_skill == 'ice':
                    t_description = self.very_small_font.render("Ice: Freeze the ball temporarily.", False, (0, 255, 0))
                elif self.player_skill == 'light':
                    t_description = self.very_small_font.render("Light: Double the ball's speed.", False, (0, 255, 0))
                elif self.player_skill == 'warp':
                    t_description = self.very_small_font.render("Warp: Warp the ball to the other side.", False, (0, 255, 0))
                text_rect = t_selected.get_rect(center=((WIDTH / 2)-60, HEIGHT / 2 + 80))
                self.screen.blit(t_description, text_rect)
            t_start = self.small_font.render("Press Enter to start!", False, (255, 255, 255))
            text_rect = t_start.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 120))
            self.screen.blit(t_start, text_rect)
        elif self.game_state == 'serve':
            # t_serve = self.small_font.render(f"Player {self.serving_player}'s serve!", False, (255, 255, 255))
            if self.serving_player == 1:
                t_serve = self.small_font.render(f"Player {self.serving_player}'s serve!", False, (255, 255, 255))
            else:
                ai_name = "Weak AI" if self.ai_mode == 'weak' else "Strong AI"
                t_serve = self.small_font.render(f"{ai_name}'s serve!", False, (255, 255, 255))
            text_rect = t_serve.get_rect(center=(WIDTH/2, 30))
            self.screen.blit(t_serve, text_rect)
            t_enter_serve = self.small_font.render("Press Enter to serve!", False, (255, 255, 255))
            text_rect = t_enter_serve.get_rect(center=(WIDTH / 2, 60))
            self.screen.blit(t_enter_serve, text_rect)
        elif self.game_state == 'play':
            t_player_skill = self.small_font.render(f"R: {self.player_skill.capitalize()} ({self.player_skill_uses} uses left)", False, (255, 255, 255))
            text_rect = t_player_skill.get_rect(center=(150, HEIGHT - 30))
            self.screen.blit(t_player_skill, text_rect)

            t_ai_skill = self.small_font.render(f"R: {self.ai_skill.capitalize()} ({self.ai_skill_uses} uses left)", False, (255, 255, 255))
            text_rect = t_ai_skill.get_rect(center=(WIDTH - 150, HEIGHT - 30))
            self.screen.blit(t_ai_skill, text_rect)
        elif self.game_state == 'done':
            self.hit_counter = 0
            if self.winning_player == 1:
                t_win = self.large_font.render(f"Player 1 wins!", False, (255, 255, 255))
            else:
                ai_name = "Weak AI" if self.ai_mode == 'weak' else "Strong AI"
                t_win = self.large_font.render(f"{ai_name} wins!", False, (255, 255, 255))

            text_rect = t_win.get_rect(center=(WIDTH / 2, 30))
            self.screen.blit(t_win, text_rect)
            
            if self.winning_player == 1 and self.ai_mode == 'weak':
                t_restart = self.small_font.render("Press Enter to face Strong AI", False, (255, 255, 255))
            else:
                t_restart = self.small_font.render("Press Enter to restart", False, (255, 255, 255))
            text_rect = t_restart.get_rect(center=(WIDTH / 2, 70))
            self.screen.blit(t_restart, text_rect)

        self.DisplayScore()

        t_mode = self.small_font.render(f"{self.ai_mode.capitalize()} AI Mode", False, (255, 255, 255))
        text_rect = t_mode.get_rect(center=(WIDTH / 2, HEIGHT - 30))
        self.screen.blit(t_mode, text_rect)

        self.player1.render()
        self.player2.render()
        self.ball.render()

    def DisplayScore(self):
        self.t_p1_score = self.score_font.render(str(self.player1_score), False, (255, 255, 255))
        self.t_p2_score = self.score_font.render(str(self.player2_score), False, (255, 255, 255))
        self.screen.blit(self.t_p1_score, (WIDTH/2 - 150, HEIGHT/3))
        self.screen.blit(self.t_p2_score, (WIDTH / 2 + 90, HEIGHT / 3))

    def activate_ice_skill(self):
        self.original_ball_dx = self.ball.dx
        self.original_ball_dy = self.ball.dy
        self.ball.dx = 0
        self.ball.dy = 0
        self.skill_channel.play(self.skill_sounds_list['ice'])
        pygame.time.set_timer(pygame.USEREVENT, 1000)

    def activate_light_skill(self):
        self.ball.dx *= 2
        self.ball.dy *= 2
        self.skill_channel.play(self.skill_sounds_list['light'])

    def activate_warp_skill(self):
        self.ball.rect.x = WIDTH - self.ball.rect.x
        self.ball.dx *= -1
        self.skill_channel.play(self.skill_sounds_list['warp'])

    def handle_event(self, event):
        if event.type == pygame.USEREVENT:
            self.ball.dx = self.original_ball_dx
            self.ball.dy = self.original_ball_dy
            pygame.time.set_timer(pygame.USEREVENT, 0)




if __name__ == '__main__':
    main = GameMain()

    clock = pygame.time.Clock()

    while True:
        pygame.display.set_caption("Pong game running with {:d} FPS".format(int(clock.get_fps())))

        # elapsed time from the last call
        dt = clock.tick(MAX_FRAME_RATE)/1000.0

        events = pygame.event.get()
        for event in events:
            main.handle_event(event)
        main.update(dt, events)
        main.render()

        pygame.display.update()
