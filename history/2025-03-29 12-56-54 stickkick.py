# stickkick.py
# -*- coding: utf-8 -*-
import pygame
import sys
import math
import random
import os
from datetime import datetime

# --- Get Timestamp ---
GENERATION_TIMESTAMP = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# --- Constants ---
SCREEN_WIDTH = 800; SCREEN_HEIGHT = 600; FPS = 60
WHITE = (255, 255, 255); BLACK = (0, 0, 0); SKY_BLUE = (135, 206, 235)
P1_COLOR_MAIN = (220, 220, 220); P1_COLOR_ACCENT = (30, 30, 30)
ITALY_GREEN = (0, 146, 70); ITALY_WHITE = (241, 242, 241); ITALY_RED = (206, 43, 55)
P2_COLOR_MAIN = ITALY_GREEN; P2_COLOR_ACCENT = ITALY_RED; P2_COLOR_WHITE = ITALY_WHITE
GRASS_GREEN = (34, 139, 34); YELLOW = (255, 255, 0); TEXT_COLOR = (10, 10, 50)
ARROW_RED = (255, 50, 50); STAR_YELLOW = (255, 255, 100); STAR_ORANGE = (255, 180, 0)
DEBUG_BLUE = (0, 0, 255)
GOAL_COLOR = (220, 220, 220); GOAL_NET_COLOR = (180, 180, 190)
GOAL_EXPLOSION_COLORS = [WHITE, YELLOW, STAR_YELLOW, (255, 215, 0)]
NOSE_COLOR = (50, 50, 50)
SCOREBOARD_BG_COLOR = (50, 50, 80, 180)
SCOREBOARD_BORDER_COLOR = (200, 200, 220)
SCOREBOARD_TEXT_FLASH_COLOR = YELLOW
SCREEN_FLASH_COLOR = (255, 255, 255, 100)
SCREEN_FLASH_DURATION = 0.15
DEBUG_KICK_ANGLES = False

# Physics
GRAVITY = 0.5; PLAYER_SPEED = 4; JUMP_POWER = -11
BASE_KICK_FORCE_X = 15; BASE_KICK_FORCE_Y = -2
KICK_FORCE_LEVEL = 1.5
HEADBUTT_UP_FORCE = 15.0; HEADBUTT_VY_MULTIPLIER = 1.2
HEADBUTT_PLAYER_VX_FACTOR = 0.6; HEADBUTT_POS_X_FACTOR = 0.15
BALL_FRICTION = 0.99; BALL_BOUNCE = 0.7; GROUND_Y = SCREEN_HEIGHT - 50

# Collision Specific
PLAYER_BODY_BOUNCE = 0.65; PLAYER_VEL_TRANSFER = 0.25
MIN_BODY_BOUNCE_VEL = 1.5; PLAYER_BODY_COLLISION_FRAMES = 4
HEAD_PLATFORM_RADIUS_BUFFER = 5

# Kick Collision Tweak
KICK_RADIUS_NORMAL = 16; KICK_RADIUS_FALLING_BONUS = 6
BALL_FALLING_VELOCITY_THRESHOLD = 5

# Goal Constants
GOAL_MARGIN_X = 40
GOAL_HEIGHT = 135; GOAL_POST_THICKNESS = 3; GOAL_Y_POS = GROUND_Y - GOAL_HEIGHT
GOAL_DEPTH_X = 30; GOAL_DEPTH_Y = -15
GOAL_LINE_X_LEFT = GOAL_MARGIN_X; GOAL_LINE_X_RIGHT = SCREEN_WIDTH - GOAL_MARGIN_X

# Animation Constants
WALK_CYCLE_SPEED = 0.25; BODY_WOBBLE_AMOUNT = 0
# ... (rest of animation constants) ...

# Star/Goal Explosion Constants
# ... (rest of particle constants) ...

# --- Power-up Constants ---
POWERUP_SPAWN_INTERVAL_MIN = 15.0
POWERUP_SPAWN_INTERVAL_MAX = 30.0
POWERUP_SPAWN_CHANCE = 0.5
POWERUP_DESCEND_SPEED = 100
POWERUP_DRIFT_SPEED = 25
POWERUP_BOX_SIZE = (30, 25)
POWERUP_CHUTE_COLOR = (255, 165, 0)
POWERUP_CHUTE_ALT_COLOR = (240, 240, 240)
POWERUP_BOX_COLOR = (210, 180, 140)
POWERUP_FLIGHT_DURATION = 30.0

# --- Debug Mode ---
debug_mode = False
DEBUG_BG_COLOR = (220, 180, 255)
DEBUG_MATCH_POINT_LIMIT = 1

# --- Flight Mode (Global Toggle - Optional, might remove if only powerup) ---
flight_mode_active = False # This now only controls background color if needed
FLIGHT_MODE_BG_COLOR = (255, 255, 200) # Light Yellow

# --- Game State Constants ---
MATCH_POINT_LIMIT = 5
GAME_WIN_LIMIT = 5
MATCH_OVER_DURATION = 3.0
GOAL_MESSAGE_DURATION = 1.5

# --- Custom Event Types ---
SOUND_FINISHED_EVENT = pygame.USEREVENT + 1

# --- Helper Functions ---
# ... (All helper drawing functions remain the same) ...
def draw_polygon_shape(surface, color, center, size, sides, angle=0, width=0): #...
    points = []
    for i in range(sides): offset_angle = math.pi / sides if sides % 2 == 0 else math.pi / 2.0; theta = offset_angle + (2.0 * math.pi * i / sides) + angle; x = center[0] + size * math.cos(theta); y = center[1] + size * math.sin(theta); points.append((int(x), int(y)))
    pygame.draw.polygon(surface, color, points, width)
def draw_pentagon(surface, color, center, size, angle=0, width=0): draw_polygon_shape(surface, color, center, size, 5, angle, width)
def draw_hexagon(surface, color, center, size, angle=0, width=0): draw_polygon_shape(surface, color, center, size, 6, angle, width)
def normalize(v): mag_sq = v[0]**2 + v[1]**2; mag = math.sqrt(mag_sq) if mag_sq > 0 else 0; return (v[0]/mag, v[1]/mag) if mag > 0 else (0,0)
def draw_rotated_rectangle(surface, color, rect_center, width, height, angle_rad): #...
    half_w, half_h = width / 2, height / 2; corners = [(-half_w, -half_h), ( half_w, -half_h), ( half_w,  half_h), (-half_w,  half_h)]
    cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad); rotated_corners = []
    for x, y in corners: x_rot = x * cos_a - y * sin_a; y_rot = x * sin_a + y * cos_a; rotated_corners.append((rect_center[0] + x_rot, rect_center[1] + y_rot))
    pygame.draw.polygon(surface, color, rotated_corners, 0); pygame.draw.polygon(surface, BLACK, rotated_corners, 1)
def draw_goal_isometric(surface, goal_line_x, goal_y, goal_height, depth_x, depth_y, thickness, post_color, net_color): #...
    front_top = (goal_line_x, goal_y); front_bottom = (goal_line_x, goal_y + goal_height)
    back_x = goal_line_x + depth_x; back_top_y = goal_y + depth_y; back_bottom_y = goal_y + goal_height + depth_y
    back_top = (back_x, back_top_y); back_bottom = (back_x, back_bottom_y)
    ft_int = (int(front_top[0]), int(front_top[1])); fb_int = (int(front_bottom[0]), int(front_bottom[1]))
    bt_int = (int(back_top[0]), int(back_top[1])); bb_int = (int(back_bottom[0]), int(back_bottom[1]))
    pygame.draw.line(surface, post_color, bt_int, bb_int, thickness); pygame.draw.line(surface, post_color, bt_int, ft_int, thickness)
    pygame.draw.line(surface, post_color, bb_int, fb_int, thickness); pygame.draw.line(surface, post_color, ft_int, fb_int, thickness)
    pygame.draw.line(surface, net_color, ft_int, bb_int, 1); pygame.draw.line(surface, net_color, fb_int, bt_int, 1)
def draw_scoreboard(surface, p1_score, p2_score, p1_games, p2_games, score_font, name_font, game_score_font, is_goal_active): # Updated Layout
    name_text = "Nils vs. Harry"; score_text = f"{p1_score} - {p2_score}"; game_score_text = f"({p1_games}-{p2_games})"
    score_text_color = SCOREBOARD_TEXT_FLASH_COLOR if is_goal_active else TEXT_COLOR
    score_surf = score_font.render(score_text, True, score_text_color); score_rect = score_surf.get_rect()
    name_surf = name_font.render(name_text, True, TEXT_COLOR); name_rect = name_surf.get_rect()
    game_score_surf = game_score_font.render(game_score_text, True, TEXT_COLOR); game_score_rect = game_score_surf.get_rect()
    panel_padding_x = 20; panel_padding_y = 10; text_spacing = 2
    panel_width = max(name_rect.width, score_rect.width, game_score_rect.width) + panel_padding_x * 2
    panel_height = (name_rect.height + text_spacing + score_rect.height + text_spacing + game_score_rect.height + panel_padding_y * 2)
    panel_rect = pygame.Rect(0, 0, panel_width, panel_height); panel_rect.centerx = SCREEN_WIDTH // 2; panel_rect.top = 5
    name_rect.centerx = panel_rect.centerx; name_rect.top = panel_rect.top + panel_padding_y
    score_rect.centerx = panel_rect.centerx; score_rect.top = name_rect.bottom + text_spacing
    game_score_rect.centerx = panel_rect.centerx; game_score_rect.top = score_rect.bottom + text_spacing
    panel_surf = pygame.Surface(panel_rect.size, pygame.SRCALPHA); panel_surf.fill(SCOREBOARD_BG_COLOR)
    pygame.draw.rect(panel_surf, SCOREBOARD_BORDER_COLOR, panel_surf.get_rect(), 2); surface.blit(panel_surf, panel_rect.topleft)
    surface.blit(name_surf, name_rect); surface.blit(score_surf, score_rect); surface.blit(game_score_surf, game_score_rect)
def draw_game_scores(surface, scores_list, font): # Corrected Order, Added Winner
    start_x = 10; start_y = 10; current_y = start_y
    for score_tuple in reversed(scores_list):
        p1s, p2s = score_tuple; winner_name_str = ""
        current_limit = DEBUG_MATCH_POINT_LIMIT if debug_mode else MATCH_POINT_LIMIT
        if p1s >= current_limit and p1s > p2s: winner_name_str = " (Nils)"
        elif p2s >= current_limit and p2s > p1s: winner_name_str = " (Harry)"
        elif p1s == p2s and p1s >= current_limit: winner_name_str = " (Draw)"
        score_str = f"{p1s} - {p2s}{winner_name_str}"; score_surf = font.render(score_str, True, TEXT_COLOR)
        score_rect = score_surf.get_rect(topleft=(start_x, current_y)); surface.blit(score_surf, score_rect)
        current_y += score_rect.height + 1
def draw_trophy(surface, winner_name, title_font, name_font): # Added Rematch Text
    cup_color = (255, 215, 0); base_color = (139, 69, 19); engraved_color = BLACK
    trophy_center_x = SCREEN_WIDTH // 2; trophy_base_y = SCREEN_HEIGHT // 2 + 180
    cup_width = 80; cup_height = 100; base_width = 140; base_height = 40
    handle_width = 20; handle_height = 60
    base_rect = pygame.Rect(0, 0, base_width, base_height); base_rect.midbottom = (trophy_center_x, trophy_base_y); pygame.draw.rect(surface, base_color, base_rect); pygame.draw.rect(surface, BLACK, base_rect, 1)
    stem_top_y = base_rect.top; stem_bottom_y = stem_top_y - 40; pygame.draw.line(surface, cup_color, (trophy_center_x, stem_top_y), (trophy_center_x, stem_bottom_y), 10)
    cup_rect = pygame.Rect(0, 0, cup_width, cup_height); cup_rect.midbottom = (trophy_center_x, stem_bottom_y); pygame.draw.ellipse(surface, cup_color, cup_rect); pygame.draw.ellipse(surface, BLACK, cup_rect, 1)
    handle_left_rect = pygame.Rect(cup_rect.left - handle_width, cup_rect.top + 10, handle_width, handle_height); handle_right_rect = pygame.Rect(cup_rect.right, cup_rect.top + 10, handle_width, handle_height)
    pygame.draw.rect(surface, cup_color, handle_left_rect); pygame.draw.rect(surface, BLACK, handle_left_rect, 1)
    pygame.draw.rect(surface, cup_color, handle_right_rect); pygame.draw.rect(surface, BLACK, handle_right_rect, 1)
    title_text = "GAME WINNER!"; title_surf = title_font.render(title_text, True, YELLOW); title_rect = title_surf.get_rect(center=(trophy_center_x, trophy_base_y - 220))
    name_surf = name_font.render(winner_name, True, engraved_color); name_rect = name_surf.get_rect(center=base_rect.center)
    bg_rect = title_rect.inflate(40, 20); bg_surf = pygame.Surface(bg_rect.size, pygame.SRCALPHA); bg_surf.fill((0, 0, 100, 200)); surface.blit(bg_surf, bg_rect.topleft)
    surface.blit(title_surf, title_rect); surface.blit(name_surf, name_rect)
    rematch_font = name_font; rematch_text = "Press R for Rematch"; rematch_surf = rematch_font.render(rematch_text, True, WHITE); rematch_rect = rematch_surf.get_rect(center=(trophy_center_x, trophy_base_y + 40)); surface.blit(rematch_surf, rematch_rect)
def draw_offscreen_arrow(s, ball, p_pos):
    ar_sz = 15; pad = 25; is_off = False; tx, ty = ball.x, ball.y; ax = max(pad, min(ball.x, SCREEN_WIDTH - pad)); ay = max(pad, min(ball.y, SCREEN_HEIGHT - pad))
    if ball.x < 0 or ball.x > SCREEN_WIDTH: ax = pad if ball.x < 0 else SCREEN_WIDTH - pad; is_off = True
    if ball.y < 0 or ball.y > SCREEN_HEIGHT: ay = pad if ball.y < 0 else SCREEN_HEIGHT - pad; is_off = True
    if not is_off: return
    ang = math.atan2(ty - ay, tx - ax); p1 = (ar_sz, 0); p2 = (-ar_sz / 2, -ar_sz / 2); p3 = (-ar_sz / 2, ar_sz / 2)
    cos_a, sin_a = math.cos(ang), math.sin(ang); p1r = (p1[0] * cos_a - p1[1] * sin_a, p1[0] * sin_a + p1[1] * cos_a); p2r = (p2[0] * cos_a - p2[1] * sin_a, p2[0] * sin_a + p2[1] * cos_a); p3r = (p3[0] * cos_a - p3[1] * sin_a, p3[0] * sin_a + p3[1] * cos_a)
    pts = [(ax + p1r[0], ay + p1r[1]), (ax + p2r[0], ay + p2r[1]), (ax + p3r[0], ay + p3r[1])]; pygame.draw.polygon(s, ARROW_RED, [(int(p[0]), int(p[1])) for p in pts])

# --- Class Definitions ---
class Particle: #... (as before) ...
    def __init__(self, x, y, colors=[STAR_YELLOW, STAR_ORANGE, WHITE], speed_min=PARTICLE_SPEED * 0.5, speed_max=PARTICLE_SPEED * 1.5, lifespan=PARTICLE_LIFESPAN, size=PARTICLE_SIZE):
        self.x = x; self.y = y; angle = random.uniform(0, 2 * math.pi); speed = random.uniform(speed_min, speed_max); self.vx = math.cos(angle) * speed; self.vy = math.sin(angle) * speed; self.lifespan = lifespan; self.start_life = self.lifespan; self.size = size; self.color = random.choice(colors)
    def update(self, dt):
        self.x += self.vx * dt; self.y += self.vy * dt; self.vy += GRAVITY * 20 * dt; self.lifespan -= dt;
        self.size = PARTICLE_SIZE * max(0, (self.lifespan / self.start_life)) if self.start_life > 0 else 0
        return self.lifespan > 0 and self.size > 0.5
    def draw(self, screen):
        if self.size > 0: pygame.draw.rect(screen, self.color, (int(self.x - self.size/2), int(self.y - self.size/2), int(self.size), int(self.size)))

class ParachutePowerup: # <<< NEW CLASS
    def __init__(self):
        self.x = -100; self.y = -100; self.vy = POWERUP_DESCEND_SPEED; self.vx = 0
        self.width, self.height = POWERUP_BOX_SIZE; self.active = False
        self.image_chute = None; self.image_box = None; self.chute_radius = 35
    def spawn(self):
        self.active = True
        self.x = random.randint(GOAL_MARGIN_X + 50, SCREEN_WIDTH - GOAL_MARGIN_X - 50)
        self.y = -self.chute_radius * 2
        self.vx = random.uniform(-POWERUP_DRIFT_SPEED, POWERUP_DRIFT_SPEED)
        print(f"Powerup spawned at ({self.x:.0f}, {self.y:.0f}) with drift {self.vx:.1f}")
    def update(self, dt):
        if not self.active: return
        self.y += self.vy * dt; self.x += self.vx * dt
        if self.x - self.width/2 < 0 or self.x + self.width/2 > SCREEN_WIDTH: self.vx *= -0.8
        if self.y - self.chute_radius > SCREEN_HEIGHT: self.active = False; print("Powerup off screen")
    def get_box_rect(self):
        return pygame.Rect(self.x - self.width / 2, self.y, self.width, self.height)
    def check_collision(self, player):
        if not self.active: return False
        player_rect = player.get_body_rect(); powerup_box_rect = self.get_box_rect()
        if player_rect.colliderect(powerup_box_rect):
            self.active = False; print("Powerup collected!")
            # play_sound(loaded_sounds['powerup_collect']) # Add sound later if needed
            return True
        return False
    def draw(self, screen):
        if not self.active: return
        box_rect = self.get_box_rect(); pygame.draw.rect(screen, POWERUP_BOX_COLOR, box_rect); pygame.draw.rect(screen, BLACK, box_rect, 1)
        chute_center_x = int(self.x); chute_top_y = int(self.y - self.chute_radius)
        chute_rect = pygame.Rect(0, 0, self.chute_radius * 2, self.chute_radius * 1.5); chute_rect.center = (chute_center_x, chute_top_y)
        num_panels = 6; angle_step = math.pi / num_panels
        for i in range(num_panels):
            angle1 = math.pi + i * angle_step; angle2 = math.pi + (i + 1) * angle_step
            color = POWERUP_CHUTE_ALT_COLOR if i % 2 == 0 else POWERUP_CHUTE_COLOR
            p1 = (chute_center_x, chute_top_y)
            p2 = (chute_center_x + self.chute_radius * math.cos(angle1), chute_top_y + self.chute_radius * 0.75 * math.sin(angle1))
            p3 = (chute_center_x + self.chute_radius * math.cos(angle2), chute_top_y + self.chute_radius * 0.75 * math.sin(angle2))
            try: pygame.draw.polygon(screen, color, [p1, p2, p3])
            except ValueError: pass
        pygame.draw.ellipse(screen, BLACK, chute_rect, 1)
        string_points = [(box_rect.left + 3, box_rect.top), (box_rect.right - 3, box_rect.top), (box_rect.centerx, box_rect.top)]
        chute_bottom_center = (chute_center_x, chute_top_y + int(self.chute_radius * 0.75))
        for point in string_points: pygame.draw.line(screen, BLACK, point, chute_bottom_center, 1)

class StickMan: # Added flight attributes, nose randomization, updated jump/draw
    def __init__(self, x, y, facing=1):
        self.x = x; self.y = y; self.base_y = y; self.width = 20; self.height = 80; self.vx = 0; self.vy = 0; self.is_jumping = False; self.is_kicking = False; self.kick_timer = 0; self.kick_duration = 18; self.walk_cycle_timer = 0.0; self.head_radius = 12; self.torso_length = 36; self.limb_width = 10; self.upper_arm_length = 12; self.forearm_length = 12; self.thigh_length = 14; self.shin_length = 14; self.torso_colors = [P2_COLOR_MAIN, P2_COLOR_WHITE, P2_COLOR_ACCENT]; self.arm_colors = [P2_COLOR_ACCENT, P2_COLOR_MAIN]; self.leg_colors = [P2_COLOR_WHITE, P2_COLOR_ACCENT]; self.l_upper_arm_angle = 0; self.r_upper_arm_angle = 0; self.l_forearm_angle = 0; self.r_forearm_angle = 0; self.l_thigh_angle = 0; self.r_thigh_angle = 0; self.l_shin_angle = 0; self.r_shin_angle = 0; self.head_pos = (0, 0); self.neck_pos = (0, 0); self.hip_pos = (0, 0); self.shoulder_pos = (0, 0); self.l_elbow_pos = (0, 0); self.r_elbow_pos = (0, 0); self.l_hand_pos = (0, 0); self.r_hand_pos = (0, 0); self.l_knee_pos = (0, 0); self.r_knee_pos = (0, 0); self.l_foot_pos = (0, 0); self.r_foot_pos = (0, 0); self.body_rect = pygame.Rect(0,0,0,0); self.facing_direction = facing; self.on_other_player_head = False
        # --- Wing Attributes ---
        self.wing_color = (173, 216, 230); self.wing_outline_color = (50, 50, 100)
        self.wing_rest_angle_offset = math.pi * 0.1 + (math.pi / 6)
        self.l_wing_base_angle = math.pi + self.wing_rest_angle_offset; self.r_wing_base_angle = -self.wing_rest_angle_offset
        self.l_wing_upper_angle = self.l_wing_base_angle - 0.4; self.l_wing_lower_angle = self.l_wing_base_angle + 0.6
        self.r_wing_upper_angle = self.r_wing_base_angle + 0.4; self.r_wing_lower_angle = self.r_wing_base_angle - 0.6
        self.wing_flap_timer = 0.0; self.wing_flap_duration = 0.2; self.wing_flapping = False
        self.wing_flap_magnitude = math.pi * 0.4
        self.wing_upper_lobe_size = (30, 22); self.wing_lower_lobe_size = (28, 25)
        # --- Head Feature Colors ---
        self.eye_color = BLACK
        if facing == 1: self.cap_color = (50, 50, 50)
        else: self.cap_color = ITALY_RED
        self.cap_brim_color = (40, 40, 40)
        # --- Nose Attributes ---
        self.base_nose_length = self.head_radius * 0.5; self.base_nose_width = self.head_radius * 0.3
        self.current_nose_length = self.base_nose_length; self.current_nose_width = self.base_nose_width
        # --- Flight Attributes ---
        self.is_flying = False; self.flight_timer = 0.0
    def move(self, direction):
        if not self.is_kicking: self.vx = direction * PLAYER_SPEED
        if direction != 0: self.facing_direction = direction
    def stop_move(self): self.vx = 0
    def jump(self): # Conditional mid-air jump based on self.is_flying
        can_jump_now = False
        if self.is_flying: # Allows multi-jump when flying
            if not self.is_kicking: can_jump_now = True
        else: # Normal jump rules
            if (not self.is_jumping or self.on_other_player_head) and not self.is_kicking: can_jump_now = True
        if can_jump_now:
            was_on_head = self.on_other_player_head
            play_sound(loaded_sounds['jump']);
            if was_on_head: play_sound(loaded_sounds['combo'])
            self.is_jumping = True; self.on_other_player_head = False
            self.vy = JUMP_POWER; self.walk_cycle_timer = 0
            if self.is_flying: self.start_wing_flap() # Flap only if flying
    def start_kick(self):
        if not self.is_kicking: self.is_kicking = True; self.kick_timer = 0; self.vx = 0
    def start_wing_flap(self):
         if not self.wing_flapping: self.wing_flapping = True; self.wing_flap_timer = self.wing_flap_duration
    def randomize_nose(self): # Randomizes nose at start of match
        random_factor = random.uniform(1.0, 5.0) # Max 5 times base size
        self.current_nose_length = self.base_nose_length * random_factor
        self.current_nose_width = self.base_nose_width * random_factor
        self.current_nose_width = min(self.current_nose_width, self.current_nose_length * 0.8)
        # print(f"Player {1 if self.facing_direction == 1 else 2} new nose factor: {random_factor:.2f}") # More reliable player ID
    def update(self, dt, other_player): # Added flight timer logic
        # --- Flight Timer Countdown ---
        if self.is_flying:
            self.flight_timer -= dt
            if self.flight_timer <= 0: self.is_flying = False; self.flight_timer = 0; print("Flight ended for player")
        # --- Physics ---
        was_airborne = self.is_jumping or (not self.on_other_player_head and self.y < self.base_y); time_ms = pygame.time.get_ticks()
        was_on_head = self.on_other_player_head; landed_on_head_this_frame = False; landed_on_ground_this_frame = False
        platform_y = self.base_y; other_head_pos, other_head_radius = other_player.get_head_position_radius()
        head_top_y = other_head_pos[1] - other_head_radius; dist_x_head = self.x - other_head_pos[0]
        is_aligned_for_head = abs(dist_x_head) < (other_head_radius + HEAD_PLATFORM_RADIUS_BUFFER)
        if not was_on_head: self.vy += GRAVITY
        elif was_on_head and not is_aligned_for_head: self.on_other_player_head = False; self.is_jumping = True; self.vy += GRAVITY
        elif was_on_head and is_aligned_for_head: self.y = head_top_y; self.vy = 0
        next_y = self.y + self.vy
        if self.vy >= 0:
            can_land_on_head_now = (is_aligned_for_head and next_y >= head_top_y and self.y < head_top_y + 5)
            if can_land_on_head_now: self.y = head_top_y; self.vy = 0; self.is_jumping = False; self.on_other_player_head = True; landed_on_head_this_frame = True
            elif not landed_on_head_this_frame and next_y >= self.base_y: self.y = self.base_y; self.vy = 0; self.is_jumping = False; self.on_other_player_head = False; landed_on_ground_this_frame = True
            else: self.y = next_y;
            if self.y < self.base_y and not landed_on_head_this_frame: self.on_other_player_head = False
        else: self.y = next_y; self.on_other_player_head = False
        if self.y > self.base_y and not self.on_other_player_head: self.y = self.base_y;
        if self.vy > 0 and self.y == self.base_y: self.vy = 0; self.is_jumping = False;
        is_now_grounded = landed_on_ground_this_frame or landed_on_head_this_frame
        if was_airborne and is_now_grounded: play_sound(loaded_sounds['land'])
        intended_vx = self.vx
        if not self.is_kicking:
            effective_vx = intended_vx
            if self.on_other_player_head: effective_vx += other_player.vx
            self.x += effective_vx; self.x = max(self.limb_width / 2, min(self.x, SCREEN_WIDTH - self.limb_width / 2))
        # --- Wing Animation Update (Only if flying) ---
        if self.is_flying:
            rest_l_base = math.pi * 0.8; rest_r_base = math.pi * 0.2
            flap_down_l_base = rest_l_base + self.wing_flap_magnitude
            flap_down_r_base = rest_r_base - self.wing_flap_magnitude
            if self.wing_flapping:
                self.wing_flap_timer -= dt
                if self.wing_flap_timer <= 0: self.wing_flapping = False; self.wing_flap_timer = 0.0; self.l_wing_base_angle = rest_l_base; self.r_wing_base_angle = rest_r_base
                else: progress = 1.0 - (self.wing_flap_timer / self.wing_flap_duration); flap_phase = math.sin(progress * math.pi); self.l_wing_base_angle = rest_l_base + (flap_down_l_base - rest_l_base) * flap_phase; self.r_wing_base_angle = rest_r_base + (flap_down_r_base - rest_r_base) * flap_phase
            else:
                lerp_speed = 6.0 * dt; self.l_wing_base_angle += (rest_l_base - self.l_wing_base_angle) * lerp_speed; self.r_wing_base_angle += (rest_r_base - self.r_wing_base_angle) * lerp_speed
            self.l_wing_upper_angle = self.l_wing_base_angle - 0.4; self.l_wing_lower_angle = self.l_wing_base_angle + 0.6
            self.r_wing_upper_angle = self.r_wing_base_angle + 0.4; self.r_wing_lower_angle = self.r_wing_base_angle - 0.6
        # --- Body Animation ---
        is_walking = abs(intended_vx) > 0 and not self.is_jumping and not self.is_kicking and not self.on_other_player_head
        if is_walking: self.walk_cycle_timer += WALK_CYCLE_SPEED
        elif not self.is_jumping and not self.is_kicking: self.walk_cycle_timer *= 0.9
        if abs(self.walk_cycle_timer) < 0.1: self.walk_cycle_timer = 0
        if self.is_kicking: # ... (kick animation logic) ...
             self.walk_cycle_timer = 0; self.kick_timer += 1; progress = min(self.kick_timer / self.kick_duration, 1.0); windup_end = 0.20; impact_start = 0.25; impact_end = 0.50; follow_end = 1.0
             if progress < windup_end: thigh_prog_angle = KICK_THIGH_WINDUP_ANGLE * (progress / windup_end)
             elif progress < impact_end: impact_progress = (progress - windup_end) / (impact_end - windup_end); thigh_prog_angle = KICK_THIGH_WINDUP_ANGLE + (KICK_THIGH_FOLLOW_ANGLE - KICK_THIGH_WINDUP_ANGLE) * impact_progress
             else: follow_progress = (progress - impact_end) / (follow_end - impact_end); ease_out_factor = 1.0 - follow_progress**1.5; thigh_prog_angle = KICK_THIGH_FOLLOW_ANGLE * ease_out_factor
             if progress < impact_start: shin_prog_angle = KICK_SHIN_WINDUP_ANGLE * (progress / impact_start)
             elif progress < impact_end: impact_progress = (progress - impact_start) / (impact_end - impact_start); ease_in_factor = impact_progress ** 2; shin_prog_angle = KICK_SHIN_WINDUP_ANGLE + (KICK_SHIN_IMPACT_ANGLE - KICK_SHIN_WINDUP_ANGLE) * ease_in_factor
             else: follow_progress = (progress - impact_end) / (follow_end - impact_end); shin_prog_angle = KICK_SHIN_IMPACT_ANGLE + (KICK_SHIN_FOLLOW_ANGLE - KICK_SHIN_IMPACT_ANGLE) * follow_progress
             kick_direction_multiplier = self.facing_direction
             if kick_direction_multiplier == 1: self.r_thigh_angle = thigh_prog_angle; self.r_shin_angle = shin_prog_angle; self.l_thigh_angle = -thigh_prog_angle * 0.3; self.l_shin_angle = 0.3
             else: self.l_thigh_angle = thigh_prog_angle * kick_direction_multiplier; self.l_shin_angle = shin_prog_angle; self.r_thigh_angle = -thigh_prog_angle * 0.3 * kick_direction_multiplier; self.r_shin_angle = 0.3
             base_thigh_abs = abs(thigh_prog_angle); self.l_upper_arm_angle = -base_thigh_abs * 0.15 if self.facing_direction == 1 else base_thigh_abs * 0.12; self.r_upper_arm_angle = base_thigh_abs * 0.12 if self.facing_direction == 1 else -base_thigh_abs * 0.15
             self.l_forearm_angle = 0.2; self.r_forearm_angle = 0.2
             if self.kick_timer >= self.kick_duration: self.is_kicking = False; self.kick_timer = 0;
        else: # Not kicking
             if is_walking: walk_sin = math.sin(self.walk_cycle_timer); self.l_upper_arm_angle = RUN_UPPER_ARM_SWING * walk_sin * self.facing_direction; self.r_upper_arm_angle = -RUN_UPPER_ARM_SWING * walk_sin * self.facing_direction; self.l_forearm_angle = RUN_FOREARM_SWING * math.sin(self.walk_cycle_timer - RUN_FOREARM_OFFSET_FACTOR) * self.facing_direction; self.r_forearm_angle = -RUN_FOREARM_SWING * math.sin(self.walk_cycle_timer - RUN_FOREARM_OFFSET_FACTOR) * self.facing_direction; self.l_thigh_angle = -LEG_THIGH_SWING * walk_sin * self.facing_direction; self.r_thigh_angle = LEG_THIGH_SWING * walk_sin * self.facing_direction; shin_bend = LEG_SHIN_BEND_WALK * max(0, math.sin(self.walk_cycle_timer + LEG_SHIN_BEND_SHIFT)); self.l_shin_angle = shin_bend if self.l_thigh_angle * self.facing_direction < 0 else 0.1; self.r_shin_angle = shin_bend if self.r_thigh_angle * self.facing_direction < 0 else 0.1
             elif self.is_jumping and not self.on_other_player_head: base_up_angle = JUMP_UPPER_ARM_BASE - self.vy * JUMP_UPPER_ARM_VY_FACTOR; self.l_upper_arm_angle = base_up_angle; self.r_upper_arm_angle = base_up_angle; base_fore_angle = JUMP_FOREARM_BASE; self.l_forearm_angle = base_fore_angle; self.r_forearm_angle = base_fore_angle; jump_progress = max(0, min(1, 1 - (self.y / self.base_y))); thigh_tuck = JUMP_THIGH_TUCK * jump_progress; shin_tuck = JUMP_SHIN_TUCK * jump_progress; self.l_thigh_angle = thigh_tuck; self.r_thigh_angle = thigh_tuck; self.l_shin_angle = shin_tuck; self.r_shin_angle = shin_tuck
             else: self.l_upper_arm_angle = 0; self.r_upper_arm_angle = 0; self.l_forearm_angle = 0; self.r_forearm_angle = 0; self.l_thigh_angle = 0; self.r_thigh_angle = 0; self.l_shin_angle = 0; self.r_shin_angle = 0
        # --- Calculate Joint Positions ---
        current_y = self.y; current_x = self.x; total_leg_visual_height = self.thigh_length + self.shin_length; self.hip_pos = (current_x, current_y - total_leg_visual_height); upper_body_x = current_x; self.neck_pos = (upper_body_x, self.hip_pos[1] - self.torso_length); self.head_pos = (upper_body_x, self.neck_pos[1] - self.head_radius); self.shoulder_pos = self.neck_pos; l_elbow_x = self.shoulder_pos[0] + self.upper_arm_length * math.sin(self.l_upper_arm_angle); l_elbow_y = self.shoulder_pos[1] + self.upper_arm_length * math.cos(self.l_upper_arm_angle); self.l_elbow_pos = (l_elbow_x, l_elbow_y); l_hand_angle_world = self.l_upper_arm_angle + self.l_forearm_angle; l_hand_x = self.l_elbow_pos[0] + self.forearm_length * math.sin(l_hand_angle_world); l_hand_y = self.l_elbow_pos[1] + self.forearm_length * math.cos(l_hand_angle_world); self.l_hand_pos = (l_hand_x, l_hand_y); r_elbow_x = self.shoulder_pos[0] + self.upper_arm_length * math.sin(self.r_upper_arm_angle); r_elbow_y = self.shoulder_pos[1] + self.upper_arm_length * math.cos(self.r_upper_arm_angle); self.r_elbow_pos = (r_elbow_x, r_elbow_y); r_hand_angle_world = self.r_upper_arm_angle + self.r_forearm_angle; r_hand_x = self.r_elbow_pos[0] + self.forearm_length * math.sin(r_hand_angle_world); r_hand_y = self.r_elbow_pos[1] + self.forearm_length * math.cos(r_hand_angle_world); self.r_hand_pos = (r_hand_x, r_hand_y); l_knee_x = self.hip_pos[0] + self.thigh_length * math.sin(self.l_thigh_angle); l_knee_y = self.hip_pos[1] + self.thigh_length * math.cos(self.l_thigh_angle); self.l_knee_pos = (l_knee_x, l_knee_y); l_foot_angle_world = self.l_thigh_angle + self.l_shin_angle; l_foot_x = self.l_knee_pos[0] + self.shin_length * math.sin(l_foot_angle_world); l_foot_y = self.l_knee_pos[1] + self.shin_length * math.cos(l_foot_angle_world); self.l_foot_pos = (l_foot_x, l_foot_y); r_knee_x = self.hip_pos[0] + self.thigh_length * math.sin(self.r_thigh_angle); r_knee_y = self.hip_pos[1] + self.thigh_length * math.cos(self.r_thigh_angle); self.r_knee_pos = (r_knee_x, r_knee_y); r_foot_angle_world = self.r_thigh_angle + self.r_shin_angle; r_foot_x = self.r_knee_pos[0] + self.shin_length * math.sin(r_foot_angle_world); r_foot_y = self.r_knee_pos[1] + self.shin_length * math.cos(r_foot_angle_world)
        self.l_foot_pos = (l_foot_x, l_foot_y); self.r_foot_pos = (r_foot_x, r_foot_y)
        # --- Update Body Rect ---
        body_width = self.limb_width * 1.5; self.body_rect.width = int(body_width); self.body_rect.height = max(1, int(self.hip_pos[1] - self.neck_pos[1])); self.body_rect.centerx = int(self.hip_pos[0]); self.body_rect.top = int(self.neck_pos[1])
    # Getters
    def get_kick_impact_point(self): #...
        impact_start = 0.25; impact_end = 0.6
        if self.is_kicking:
            if self.kick_duration <= 0: return None
            progress = self.kick_timer / self.kick_duration
            if impact_start < progress < impact_end: return self.r_foot_pos if self.facing_direction == 1 else self.l_foot_pos
        return None
    def get_head_position_radius(self): return self.head_pos, self.head_radius
    def get_body_rect(self): return self.body_rect
    # Draw Method
    def draw(self, screen): # Updated head and wings
        head_center_x = int(self.head_pos[0]); head_center_y = int(self.head_pos[1]); head_center_int = (head_center_x, head_center_y)
        # --- Draw Head Features ---
        cap_height = self.head_radius * 0.8; cap_width = self.head_radius * 1.8; cap_rect = pygame.Rect(0, 0, cap_width, cap_height); cap_rect.center = (head_center_x, head_center_y - self.head_radius * 0.5); pygame.draw.ellipse(screen, self.cap_color, cap_rect)
        brim_width = self.head_radius * 1.2; brim_height = self.head_radius * 0.4; brim_x = head_center_x + (self.head_radius * 0.5) * self.facing_direction; brim_y = cap_rect.centery + cap_height * 0.1; brim_rect = pygame.Rect(0, 0, brim_width, brim_height); brim_rect.center = (brim_x, brim_y); pygame.draw.rect(screen, self.cap_brim_color, brim_rect)
        pygame.draw.circle(screen, ITALY_WHITE, head_center_int, self.head_radius, 0) # Head Fill
        eye_offset_x = self.head_radius * 0.35 * self.facing_direction; eye_offset_y = -self.head_radius * 0.1; eye_radius = 3
        eye_pos_x = int(head_center_x + eye_offset_x); eye_y = int(head_center_y + eye_offset_y)
        pygame.draw.circle(screen, self.eye_color, (eye_pos_x, eye_y - eye_radius // 2 - 1), eye_radius); pygame.draw.circle(screen, self.eye_color, (eye_pos_x, eye_y + eye_radius // 2 + 1), eye_radius)
        nose_tip_x = head_center_x + (self.head_radius * 0.5 + self.current_nose_length) * self.facing_direction
        nose_tip_y = head_center_y + self.head_radius * 0.1 # Slightly lower on face
        nose_base_x = head_center_x + (self.head_radius * 0.3) * self.facing_direction # Base closer to center
        nose_base_y1 = nose_tip_y - self.current_nose_width / 2; nose_base_y2 = nose_tip_y + self.current_nose_width / 2
        nose_points = [(int(nose_base_x), int(nose_base_y1)), (int(nose_tip_x), int(nose_tip_y)), (int(nose_base_x), int(nose_base_y2))]; pygame.draw.polygon(screen, NOSE_COLOR, nose_points)
        pygame.draw.circle(screen, BLACK, head_center_int, self.head_radius, 1) # Head Outline
        # --- Draw Torso/Limbs ---
        torso_segment_height = self.torso_length / 3; current_torso_y = self.neck_pos[1]
        for i in range(3): rect_center_x = self.neck_pos[0]; rect_center_y = current_torso_y + torso_segment_height / 2; draw_rotated_rectangle(screen, self.torso_colors[i], (rect_center_x, rect_center_y), self.limb_width, torso_segment_height, 0); current_torso_y += torso_segment_height
        def draw_limb_segment(start_pos, end_pos, length, color):
            center_x = (start_pos[0] + end_pos[0]) / 2; center_y = (start_pos[1] + end_pos[1]) / 2
            dx = end_pos[0] - start_pos[0]; dy = end_pos[1] - start_pos[1]; draw_length = math.hypot(dx, dy);
            if draw_length < 1: draw_length = 1
            angle = math.atan2(dy, dx); draw_rotated_rectangle(screen, color, (center_x, center_y), draw_length, self.limb_width, angle + math.pi/2)
        draw_limb_segment(self.shoulder_pos, self.l_elbow_pos, self.upper_arm_length, self.arm_colors[0]); draw_limb_segment(self.l_elbow_pos, self.l_hand_pos, self.forearm_length, self.arm_colors[1])
        draw_limb_segment(self.shoulder_pos, self.r_elbow_pos, self.upper_arm_length, self.arm_colors[0]); draw_limb_segment(self.r_elbow_pos, self.r_hand_pos, self.forearm_length, self.arm_colors[1])
        draw_limb_segment(self.hip_pos, self.l_knee_pos, self.thigh_length, self.leg_colors[0]); draw_limb_segment(self.l_knee_pos, self.l_foot_pos, self.shin_length, self.leg_colors[1])
        draw_limb_segment(self.hip_pos, self.r_knee_pos, self.thigh_length, self.leg_colors[0]); draw_limb_segment(self.r_knee_pos, self.r_foot_pos, self.shin_length, self.leg_colors[1])
        # --- Draw Wings (Only if flying) using Polygons ---
        if self.is_flying: # Draw wings if the player *instance* is flying
            upper_attach_x = self.shoulder_pos[0]; upper_attach_y = self.shoulder_pos[1] + 5
            lower_attach_x = self.hip_pos[0]; lower_attach_y = self.hip_pos[1] - 5 # Attach lower wing near hip
            upper_length = self.wing_upper_lobe_size[0]; upper_width = self.wing_upper_lobe_size[1]
            lower_length = self.wing_lower_lobe_size[0]; lower_width = self.wing_lower_lobe_size[1]
            def create_wing_poly(attach_point, angle, length, width):
                cos_a = math.cos(angle); sin_a = math.sin(angle); cos_w = math.cos(angle + math.pi/2); sin_w = math.sin(angle + math.pi/2)
                p1 = attach_point
                p2 = (attach_point[0] + length * 0.6 * cos_a + width * 0.5 * cos_w, attach_point[1] + length * 0.6 * sin_a + width * 0.5 * sin_w)
                p3 = (attach_point[0] + length * cos_a, attach_point[1] + length * sin_a)
                p4 = (attach_point[0] + length * 0.6 * cos_a - width * 0.5 * cos_w, attach_point[1] + length * 0.6 * sin_a - width * 0.5 * sin_w)
                p5 = (attach_point[0] + length*0.2 * cos_a - width*0.2 * cos_w, attach_point[1] + length*0.2 * sin_a - width*0.2 * sin_w)
                return [(int(p[0]), int(p[1])) for p in [p1, p2, p3, p4, p5]]
            l_attach_upper = (upper_attach_x - 4, upper_attach_y); l_attach_lower = (lower_attach_x - 4, lower_attach_y)
            l_upper_poly = create_wing_poly(l_attach_upper, self.l_wing_upper_angle, upper_length, upper_width)
            l_lower_poly = create_wing_poly(l_attach_lower, self.l_wing_lower_angle, lower_length, lower_width)
            pygame.draw.polygon(screen, self.wing_color, l_upper_poly); pygame.draw.polygon(screen, self.wing_outline_color, l_upper_poly, 1)
            pygame.draw.polygon(screen, self.wing_color, l_lower_poly); pygame.draw.polygon(screen, self.wing_outline_color, l_lower_poly, 1)
            r_attach_upper = (upper_attach_x + 4, upper_attach_y); r_attach_lower = (lower_attach_x + 4, lower_attach_y)
            r_upper_poly = create_wing_poly(r_attach_upper, self.r_wing_upper_angle, upper_length, upper_width)
            r_lower_poly = create_wing_poly(r_attach_lower, self.r_wing_lower_angle, lower_length, lower_width)
            pygame.draw.polygon(screen, self.wing_color, r_upper_poly); pygame.draw.polygon(screen, self.wing_outline_color, r_upper_poly, 1)
            pygame.draw.polygon(screen, self.wing_color, r_lower_poly); pygame.draw.polygon(screen, self.wing_outline_color, r_lower_poly, 1)
        # --- Draw Flight Timer ---
        if self.is_flying and self.flight_timer > 0:
            timer_text = f"{self.flight_timer:.1f}"; timer_font = font_small; timer_color = WHITE
            timer_surf = timer_font.render(timer_text, True, timer_color); timer_rect = timer_surf.get_rect()
            timer_rect.centerx = head_center_x; timer_rect.bottom = head_center_y - self.head_radius - 5
            bg_rect = timer_rect.inflate(4, 2); bg_surf = pygame.Surface(bg_rect.size, pygame.SRCALPHA); bg_surf.fill((0, 0, 0, 150))
            screen.blit(bg_surf, bg_rect); screen.blit(timer_surf, timer_rect)

# --- Ball Class ---
# ... (Ball class remains the same) ...
class Ball:
    def __init__(self, x, y, radius): self.x = x; self.y = y; self.radius = radius; self.vx = 0; self.vy = 0; self.last_hit_by = None; self.rotation_angle = 0
    def apply_force(self, force_x, force_y, hitter='player'): self.vx += force_x; self.vy += force_y; self.last_hit_by = hitter
    def update(self, dt):
        self.rotation_angle += self.vx * 0.015; self.rotation_angle %= (2 * math.pi); self.vy += GRAVITY; self.vx *= BALL_FRICTION; self.x += self.vx; self.y += self.vy
        hit_ground = False; hit_wall_this_frame = False
        if self.x + self.radius >= SCREEN_WIDTH: self.x = SCREEN_WIDTH - self.radius; self.vx *= -BALL_BOUNCE * 0.8; hit_wall_this_frame = True
        elif self.x - self.radius <= 0: self.x = self.radius; self.vx *= -BALL_BOUNCE * 0.8; hit_wall_this_frame = True
        if hit_wall_this_frame: play_sound(loaded_sounds['wall_hit'])
        if self.y + self.radius >= GROUND_Y:
            if self.vy >= 0:
                impact_vy = abs(self.vy)
                self.y = GROUND_Y - self.radius; self.vy *= -BALL_BOUNCE; self.vx *= 0.9
                if abs(self.vy) < 1: self.vy = 0
                if impact_vy > 1.5: play_sound(loaded_sounds['ball_bounce'])
                hit_ground = True
        if abs(self.vx) < 0.1 and self.is_on_ground(): self.vx = 0
        return hit_ground
    def is_on_ground(self): return self.y + self.radius >= GROUND_Y - 0.5
    def draw(self, screen):
        center_tuple = (int(self.x), int(self.y)); pygame.draw.circle(screen, WHITE, center_tuple, self.radius)
        pent_size = self.radius * 0.40; hex_size = self.radius * 0.42; dist_factor = 0.65; num_around = 5; angle_step = 2 * math.pi / num_around
        draw_pentagon(screen, BLACK, center_tuple, pent_size, self.rotation_angle)
        for i in range(num_around):
            angle = self.rotation_angle + (i * angle_step) + angle_step / 2; shape_center_x = center_tuple[0] + self.radius * dist_factor * math.cos(angle); shape_center_y = center_tuple[1] + self.radius * dist_factor * math.sin(angle); shape_center = (shape_center_x, shape_center_y)
            if i % 2 == 0: draw_hexagon(screen, BLACK, shape_center, hex_size, angle + self.rotation_angle * 0.5, width=1)
            else: draw_pentagon(screen, BLACK, shape_center, pent_size, angle + self.rotation_angle * 0.5)
        pygame.draw.circle(screen, BLACK, center_tuple, self.radius, 1)

# --- Game Setup ---
pygame.init(); pygame.mixer.pre_init(44100, -16, 2, 512); pygame.mixer.init()
announcement_channel = pygame.mixer.Channel(0)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)); pygame.display.set_caption("Ciao Kick!");
clock = pygame.time.Clock()

# --- Sound Loading ---
# ... (load_sounds definition as before) ...
def load_sounds(sound_dir="sounds"):
    sounds = {}
    sound_files = {"kick": ["kick_ball1.wav", "kick_ball2.wav"], "jump": ["jump1.wav"], "land": ["land1.wav"],"wall_hit": ["wall_hit1.wav"], "player_bump": ["player_bump1.wav"], "headbutt": ["headbutt1.wav"], "body_hit": ["body_hit1.wav"], "combo": ["combo_sparkle1.wav", "combo_sparkle2.wav", "combo_sparkle3.wav", "combo_sparkle4.wav"], "ball_bounce": ["ball_bounce1.wav"], "nils_wins": ["nils_wins.wav"], "harry_wins": ["harry_wins.wav"], "nils_ahead": ["nils_ahead.wav"], "harry_ahead": ["harry_ahead.wav"],}
    for name, filenames in sound_files.items():
        sounds[name] = []
        for filename in filenames:
            path = os.path.join(sound_dir, filename)
            try: sound = pygame.mixer.Sound(path); sounds[name].append(sound); print(f"Loaded sound: {path}")
            except pygame.error as e: print(f"Warning: Could not load sound '{path}': {e}")
    sounds['numbers'] = {}
    for i in range(0, 6):
        filename = f"{i}.wav"; path = os.path.join(sound_dir, filename)
        try: sound = pygame.mixer.Sound(path); sounds['numbers'][i] = sound; print(f"Loaded sound: {path} as number {i}")
        except pygame.error as e: print(f"Warning: Could not load number sound '{path}': {e}"); sounds['numbers'][i] = None
    for player_num in [1, 2]:
        goal_key = f"goal_p{player_num}"; sounds[goal_key] = []; i = 1
        while True:
            filename = f"player{player_num}_goal{i}.wav"; path = os.path.join(sound_dir, filename)
            if os.path.exists(path):
                try: sound = pygame.mixer.Sound(path); sounds[goal_key].append(sound); print(f"Loaded sound: {path}"); i += 1
                except pygame.error as e: print(f"Warning: Could not load sound '{path}': {e}"); break
            else: break
        if not sounds[goal_key]: print(f"Warning: No goal sounds found for Player {player_num}")
    required_keys = ["goal_p1", "goal_p2", "kick", "jump", "land", "wall_hit", "player_bump", "headbutt", "body_hit", "combo", "ball_bounce", "nils_wins", "harry_wins", "nils_ahead", "harry_ahead"]
    for key in required_keys:
        if key not in sounds: sounds[key] = []
    if 'numbers' not in sounds: sounds['numbers'] = {}
    return sounds
# --- Sound Playing Helpers ---
def play_sound(sound_list): # Plays on any free channel
    if sound_list:
        sound_to_play = random.choice(sound_list)
        ch = pygame.mixer.find_channel(True)
        if ch: ch.play(sound_to_play)
def queue_sound(sound_list): # Adds random sound to announcement queue
    global announcement_queue
    if sound_list:
        sound_to_play = random.choice(sound_list)
        if sound_to_play: announcement_queue.append(sound_to_play)
def queue_specific_sound(sound_obj): # Adds specific sound obj to queue
    global announcement_queue
    if sound_obj: announcement_queue.append(sound_obj)
def play_next_announcement(): # Plays next from queue if channel free
    global announcement_queue, announcement_channel
    if announcement_queue and not announcement_channel.get_busy():
        next_sound = announcement_queue.pop(0)
        if next_sound:
            announcement_channel.play(next_sound)
            announcement_channel.set_endevent(SOUND_FINISHED_EVENT)
        else: pygame.event.post(pygame.event.Event(SOUND_FINISHED_EVENT))
loaded_sounds = load_sounds()

# --- Player/Ball/Font/Powerup Setup ---
powerup = ParachutePowerup()
player1 = StickMan(SCREEN_WIDTH // 4, GROUND_Y, facing=1); player2 = StickMan(SCREEN_WIDTH * 3 // 4, GROUND_Y, facing=-1)
player1.torso_colors = [P1_COLOR_MAIN, P1_COLOR_ACCENT, P1_COLOR_MAIN]; player1.arm_colors = [P1_COLOR_ACCENT, P1_COLOR_MAIN]; player1.leg_colors = [P1_COLOR_MAIN, P1_COLOR_ACCENT]
ball = Ball(SCREEN_WIDTH // 2, GROUND_Y - 20, 15)
font_large = pygame.font.Font(None, 50); font_medium = pygame.font.Font(None, 36); font_small = pygame.font.Font(None, 28)
font_timestamp = pygame.font.Font(None, 20); font_goal = pygame.font.Font(None, 80)

# --- Score & State Variables ---
player1_score = 0; player2_score = 0; p1_games_won = 0; p2_games_won = 0
game_scores = []; match_active = True; match_over_timer = 0.0; game_over = False
match_winner = None; overall_winner = None; match_end_sound_played = False
game_over_sound_played = False
announcement_queue = []
goal_message_timer = 0; screen_flash_timer = 0
ball_was_on_ground = True; particles = []; p1_can_headbutt = True; p2_can_headbutt = True
p1_body_collision_timer = 0; p2_body_collision_timer = 0; current_hit_count = 0
flight_mode_active = False
powerup_spawn_timer = random.uniform(POWERUP_SPAWN_INTERVAL_MIN, POWERUP_SPAWN_INTERVAL_MAX)

# --- Reset/Start Functions ---
def reset_positions():
    global ball_was_on_ground, current_hit_count, p1_can_headbutt, p2_can_headbutt, p1_body_collision_timer, p2_body_collision_timer
    ball.x = SCREEN_WIDTH // 2; ball.y = SCREEN_HEIGHT // 3; ball.vx = 0; ball.vy = 0
    player1.x = SCREEN_WIDTH // 4; player1.y = GROUND_Y; player1.vx = 0; player1.vy = 0; player1.is_kicking = False; player1.on_other_player_head = False; player1.facing_direction = 1; player1.is_jumping = False; player1.is_flying = False; player1.flight_timer = 0.0
    player2.x = SCREEN_WIDTH * 3 // 4; player2.y = GROUND_Y; player2.vx = 0; player2.vy = 0; player2.is_kicking = False; player2.on_other_player_head = False; player2.facing_direction = -1; player2.is_jumping = False; player2.is_flying = False; player2.flight_timer = 0.0
    current_hit_count = 0; ball_was_on_ground = False; p1_can_headbutt = True; p2_can_headbutt = True; p1_body_collision_timer = 0; p2_body_collision_timer = 0;
    powerup.active = False
def start_new_match():
    global player1_score, player2_score, match_active, match_winner, match_over_timer, match_end_sound_played, announcement_queue
    player1_score = 0; player2_score = 0; match_active = True; match_winner = None; match_over_timer = 0.0; match_end_sound_played = False
    announcement_queue = []; reset_positions()
    player1.randomize_nose(); player2.randomize_nose()
    print("Starting new match.")
def start_new_game():
    global p1_games_won, p2_games_won, game_scores, game_over, overall_winner, announcement_queue, game_over_sound_played
    p1_games_won = 0; p2_games_won = 0; game_scores = []; game_over = False; overall_winner = None; game_over_sound_played = False
    announcement_queue = []; start_new_match(); print("Starting new game.")

# --- Collision Handling Function (Player-Ball) ---
def handle_player_ball_collisions(player, ball, can_headbutt, body_collision_timer, is_ball_airborne): #... (as before) ...
    global current_hit_count
    kick_performed = False; headbutt_performed = False; score_increase = False; kick_pt = None
    local_kick_point = player.get_kick_impact_point()
    if local_kick_point:
        dist_x = local_kick_point[0] - ball.x; dist_y = local_kick_point[1] - ball.y; dist_sq = dist_x**2 + dist_y**2
        eff_kick_rad = KICK_RADIUS_NORMAL + (KICK_RADIUS_FALLING_BONUS if ball.vy > BALL_FALLING_VELOCITY_THRESHOLD else 0)
        if dist_sq < (ball.radius + eff_kick_rad)**2:
             progress = player.kick_timer / player.kick_duration
             if 0.25 < progress < 0.6:
                 kick_x = BASE_KICK_FORCE_X * KICK_FORCE_LEVEL * player.facing_direction; kick_y = BASE_KICK_FORCE_Y * KICK_FORCE_LEVEL
                 if player.vy < 0: kick_y += player.vy * 0.4
                 ball.apply_force(kick_x, kick_y, hitter=player); kick_performed = True; kick_pt = local_kick_point; play_sound(loaded_sounds['kick']);
                 if is_ball_airborne: current_hit_count += 1; score_increase = True
    head_pos, head_radius = player.get_head_position_radius(); dist_x_head = ball.x - head_pos[0]; dist_y_head = ball.y - head_pos[1]
    dist_head_sq = dist_x_head**2 + dist_y_head**2; headbutt_cooldown_just_applied = False
    if dist_head_sq < (ball.radius + head_radius)**2:
        if can_headbutt:
            force_y = -HEADBUTT_UP_FORCE;
            if player.vy < 0: force_y -= abs(player.vy) * HEADBUTT_VY_MULTIPLIER
            force_x = player.vx * HEADBUTT_PLAYER_VX_FACTOR - dist_x_head * HEADBUTT_POS_X_FACTOR
            ball.apply_force(force_x, force_y, hitter=player); headbutt_cooldown_just_applied = True; headbutt_performed = True; play_sound(loaded_sounds['headbutt']);
            if is_ball_airborne: current_hit_count += 1; score_increase = True
    new_can_headbutt = can_headbutt
    if headbutt_cooldown_just_applied: new_can_headbutt = False
    elif not new_can_headbutt and dist_head_sq > (ball.radius + head_radius + 15)**2: new_can_headbutt = True
    new_body_collision_timer = body_collision_timer
    if not kick_performed and not headbutt_performed and body_collision_timer == 0:
        player_rect = player.get_body_rect(); closest_x = max(player_rect.left, min(ball.x, player_rect.right)); closest_y = max(player_rect.top, min(ball.y, player_rect.bottom))
        delta_x = ball.x - closest_x; delta_y = ball.y - closest_y; dist_sq_body = delta_x**2 + delta_y**2
        if dist_sq_body < ball.radius**2:
             collision_occurred = False
             if dist_sq_body > 0:
                 distance = math.sqrt(dist_sq_body); overlap = ball.radius - distance; collision_normal_x = delta_x / distance; collision_normal_y = delta_y / distance
                 push_amount = overlap + 0.2; ball.x += collision_normal_x * push_amount; ball.y += collision_normal_y * push_amount
                 rel_vx = ball.vx - player.vx; rel_vy = ball.vy - player.vy; vel_along_normal = rel_vx * collision_normal_x + rel_vy * collision_normal_y
                 if vel_along_normal < 0:
                     impulse_scalar = -(1 + PLAYER_BODY_BOUNCE) * vel_along_normal; bounce_vx = impulse_scalar * collision_normal_x; bounce_vy = impulse_scalar * collision_normal_y
                     bounce_vx += player.vx * PLAYER_VEL_TRANSFER; bounce_vy += player.vy * PLAYER_VEL_TRANSFER
                     new_vel_mag_sq = bounce_vx**2 + bounce_vy**2
                     if new_vel_mag_sq < MIN_BODY_BOUNCE_VEL**2:
                         if new_vel_mag_sq > 0: scale = MIN_BODY_BOUNCE_VEL / math.sqrt(new_vel_mag_sq); bounce_vx *= scale; bounce_vy *= scale
                         else: bounce_vx = collision_normal_x * MIN_BODY_BOUNCE_VEL; bounce_vy = collision_normal_y * MIN_BODY_BOUNCE_VEL
                     ball.vx = bounce_vx; ball.vy = bounce_vy; new_body_collision_timer = PLAYER_BODY_COLLISION_FRAMES; collision_occurred = True
             elif dist_sq_body == 0:
                  ball.y = player_rect.top - ball.radius - 0.1
                  if ball.vy > 0: ball.vy *= -PLAYER_BODY_BOUNCE
                  new_body_collision_timer = PLAYER_BODY_COLLISION_FRAMES; collision_occurred = True
             if collision_occurred: play_sound(loaded_sounds['body_hit'])
    return score_increase, new_can_headbutt, new_body_collision_timer, kick_pt

# --- Start First Game ---
start_new_game()

# --- Main Game Loop ---
running = True
while running:
    dt = clock.tick(FPS) / 1000.0; dt = min(dt, 0.1) # <<< dt Calculation INSIDE loop

    # --- Global Input & Event Processing ---
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT: running = False
        if event.type == SOUND_FINISHED_EVENT: play_next_announcement() # Play next sound in queue
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: running = False
            if event.key == pygame.K_7: debug_mode = not debug_mode; print(f"Debug Mode {'ACT' if debug_mode else 'DEACT'}IVATED")
            if event.key == pygame.K_6: flight_mode_active = not flight_mode_active; print(f"Flight Mode {'ACT' if flight_mode_active else 'DEACT'}IVATED")
            if game_over and event.key == pygame.K_r: start_new_game()
            if match_active: # Gameplay Input
                if event.key == pygame.K_a: player1.move(-1)
                elif event.key == pygame.K_d: player1.move(1)
                elif event.key == pygame.K_w: player1.jump()
                elif event.key == pygame.K_s: player1.start_kick()
                elif event.key == pygame.K_LEFT: player2.move(-1)
                elif event.key == pygame.K_RIGHT: player2.move(1)
                elif event.key == pygame.K_UP: player2.jump()
                elif event.key == pygame.K_DOWN: player2.start_kick()
        if event.type == pygame.KEYUP: # Gameplay Stop Input
            if match_active:
                if event.key == pygame.K_a and player1.vx < 0: player1.stop_move()
                elif event.key == pygame.K_d and player1.vx > 0: player1.stop_move()
                elif event.key == pygame.K_LEFT and player2.vx < 0: player2.stop_move()
                elif event.key == pygame.K_RIGHT and player2.vx > 0: player2.stop_move()

    # --- Handle Game Over State ---
    if game_over:
        if not game_over_sound_played:
            announcement_queue = []; # Clear just in case
            if overall_winner == 1: queue_sound(loaded_sounds['nils_wins'])
            elif overall_winner == 2: queue_sound(loaded_sounds['harry_wins'])
            play_next_announcement(); game_over_sound_played = True
        bg_color = FLIGHT_MODE_BG_COLOR if flight_mode_active else (DEBUG_BG_COLOR if debug_mode else SKY_BLUE)
        screen.fill(bg_color); pygame.draw.rect(screen, GRASS_GREEN, (0, GROUND_Y, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y))
        winner_name = "Nils" if overall_winner == 1 else "Harry"; draw_trophy(screen, winner_name, font_goal, font_large)
        draw_game_scores(screen, game_scores, font_small); pygame.display.flip(); continue

    # --- Handle Match Over State ---
    if match_over_timer > 0:
        match_over_timer -= dt
        if match_over_timer <= 0 and not game_over: start_new_match()

    # --- Process Announcement Sound Queue (Relies on event system now) ---
    # Removed explicit call from main loop update cycle

    # --- ALWAYS Update Players ---
    player1.update(dt, player2)
    player2.update(dt, player1)

    # --- Updates (Only if match active) ---
    if match_active:
        if p1_body_collision_timer > 0: p1_body_collision_timer -= 1
        if p2_body_collision_timer > 0: p2_body_collision_timer -= 1
        if goal_message_timer > 0: goal_message_timer -= dt
        if screen_flash_timer > 0: screen_flash_timer -= dt
        # Player updates moved above
        ball_hit_ground_this_frame = ball.update(dt)
        particles = [p for p in particles if p.update(dt)]
        powerup.update(dt) # Update powerup

        # --- Power-up Collection ---
        if powerup.active:
            if powerup.check_collision(player1): player1.is_flying = True; player1.flight_timer = POWERUP_FLIGHT_DURATION; # play_sound powerup collect
            elif powerup.check_collision(player2): player2.is_flying = True; player2.flight_timer = POWERUP_FLIGHT_DURATION; # play_sound powerup collect

        # --- Player Collisions ---
        p1_rect = player1.get_body_rect(); p2_rect = player2.get_body_rect()
        if p1_rect.colliderect(p2_rect): # Body Collision
            p1_is_on_p2 = player1.on_other_player_head; p2_is_on_p1 = player2.on_other_player_head
            if p1_is_on_p2 and abs(player1.y - (player2.head_pos[1] - player2.head_radius)) > 10: p1_is_on_p2 = False
            if p2_is_on_p1 and abs(player2.y - (player1.head_pos[1] - player1.head_radius)) > 10: p2_is_on_p1 = False
            if not p1_is_on_p2 and not p2_is_on_p1:
                overlap_x = 0
                if player1.x < player2.x: overlap_x = p1_rect.right - p2_rect.left
                else: overlap_x = p2_rect.right - p1_rect.left
                if overlap_x > 0: play_sound(loaded_sounds['player_bump']); push = overlap_x / 2 + 0.1
                if player1.x < player2.x: player1.x -= push; player2.x += push;
                if player1.vx > 0: player1.vx = 0
                if player2.vx < 0: player2.vx = 0
                else: player1.x += push; player2.x -= push;
                if player1.vx < 0: player1.vx = 0
                if player2.vx > 0: player2.vx = 0
        # Kick Collision
        kick_push_amount = ball.radius * 1.5; kick_push_vx = 5
        p1_kick_point = player1.get_kick_impact_point()
        if p1_kick_point and p2_rect.collidepoint(p1_kick_point): print("P1 kicked P2"); player2.x += kick_push_amount * player1.facing_direction; player2.vx += kick_push_vx * player1.facing_direction; play_sound(loaded_sounds['body_hit'])
        p2_kick_point = player2.get_kick_impact_point()
        if p2_kick_point and p1_rect.collidepoint(p2_kick_point): print("P2 kicked P1"); player1.x += kick_push_amount * player2.facing_direction; player1.vx += kick_push_vx * player2.facing_direction; play_sound(loaded_sounds['body_hit'])
        player1.x = max(player1.limb_width / 2, min(player1.x, SCREEN_WIDTH - player1.limb_width / 2)); player2.x = max(player2.limb_width / 2, min(player2.x, SCREEN_WIDTH - player2.limb_width / 2))
        # Combo Reset
        is_ball_airborne = not ball.is_on_ground()
        if not is_ball_airborne and ball_hit_ground_this_frame and not ball_was_on_ground: current_hit_count = 0
        ball_was_on_ground = not is_ball_airborne
        # Player-Ball Collisions
        p1_hit, p1_can_headbutt, p1_body_collision_timer, p1_kick_pt = handle_player_ball_collisions(player1, ball, p1_can_headbutt, p1_body_collision_timer, is_ball_airborne)
        p2_hit, p2_can_headbutt, p2_body_collision_timer, p2_kick_pt = handle_player_ball_collisions(player2, ball, p2_can_headbutt, p2_body_collision_timer, is_ball_airborne)
        score_increased_this_frame = p1_hit or p2_hit
        last_kick_point = p1_kick_pt if p1_kick_pt else p2_kick_pt
        # Combo Trigger
        if score_increased_this_frame and last_kick_point and current_hit_count > 0 and current_hit_count % 5 == 0:
            play_sound(loaded_sounds['combo'])
            num_kick_particles = PARTICLE_COUNT // 2
            for _ in range(num_kick_particles): particle_x = last_kick_point[0] + random.uniform(-5, 5); particle_y = last_kick_point[1] + random.uniform(-5, 5); particles.append(Particle(particle_x, particle_y))


    # --- Goal Detection & Effects ---
    goal_scored_this_frame = False; scorer = 0
    if match_active:
        if ball.x + ball.radius >= GOAL_LINE_X_RIGHT and ball.y > GOAL_Y_POS: player1_score += 1; scorer = 1; goal_message_timer = GOAL_MESSAGE_DURATION; goal_scored_this_frame = True; goal_pos_x = SCREEN_WIDTH; print(f"GOAL! Player 1 Score: {player1_score}"); screen_flash_timer = SCREEN_FLASH_DURATION
        elif ball.x - ball.radius <= GOAL_LINE_X_LEFT and ball.y > GOAL_Y_POS: player2_score += 1; scorer = 2; goal_message_timer = GOAL_MESSAGE_DURATION; goal_scored_this_frame = True; goal_pos_x = 0; print(f"GOAL! Player 2 Score: {player2_score}"); screen_flash_timer = SCREEN_FLASH_DURATION

    if goal_scored_this_frame:
        if scorer == 1: play_sound(loaded_sounds['goal_p1']);
        if player1_score > 0 and player1_score % 5 == 0: play_sound(loaded_sounds['combo'])
        elif scorer == 2: play_sound(loaded_sounds['goal_p2']);
        if player2_score > 0 and player2_score % 5 == 0: play_sound(loaded_sounds['combo'])
        goal_center_y = GOAL_Y_POS + GOAL_HEIGHT / 2
        for _ in range(GOAL_PARTICLE_COUNT): particles.append(Particle(goal_pos_x, goal_center_y, colors=GOAL_EXPLOSION_COLORS, speed_min=GOAL_PARTICLE_SPEED_MIN, speed_max=GOAL_PARTICLE_SPEED_MAX, lifespan=GOAL_PARTICLE_LIFESPAN))

        current_match_limit = DEBUG_MATCH_POINT_LIMIT if debug_mode else MATCH_POINT_LIMIT
        winner_found_this_match = False
        if player1_score >= current_match_limit: match_winner = 1; winner_found_this_match = True; print(f"Player 1 wins the match! (Limit: {current_match_limit})")
        elif player2_score >= current_match_limit: match_winner = 2; winner_found_this_match = True; print(f"Player 2 wins the match! (Limit: {current_match_limit})")

        if winner_found_this_match:
            match_active = False; match_over_timer = MATCH_OVER_DURATION; match_end_sound_played = False
            if match_winner == 1: p1_games_won += 1
            elif match_winner == 2: p2_games_won += 1
            game_scores.insert(0, (player1_score, player2_score));
            if len(game_scores) > 9: game_scores.pop()
            print(f"Games Won: P1={p1_games_won}, P2={p2_games_won}")
            # --- Queue Match End Sounds (if game not over) ---
            if not (p1_games_won >= GAME_WIN_LIMIT or p2_games_won >= GAME_WIN_LIMIT):
                announcement_queue = []; p1_games = p1_games_won; p2_games = p2_games_won
                if p1_games > p2_games: queue_sound(loaded_sounds['nils_ahead']); queue_specific_sound(loaded_sounds['numbers'].get(p1_games)); queue_specific_sound(loaded_sounds['numbers'].get(p2_games))
                elif p2_games > p1_games: queue_sound(loaded_sounds['harry_ahead']); queue_specific_sound(loaded_sounds['numbers'].get(p2_games)); queue_specific_sound(loaded_sounds['numbers'].get(p1_games))
                else: queue_specific_sound(loaded_sounds['numbers'].get(p1_games)); queue_specific_sound(loaded_sounds['numbers'].get(p2_games))
                play_next_announcement() # Trigger first sound
            # Check overall game win
            if p1_games_won >= GAME_WIN_LIMIT: overall_winner = 1; game_over = True; print("PLAYER 1 WINS THE GAME!")
            elif p2_games_won >= GAME_WIN_LIMIT: overall_winner = 2; game_over = True; print("PLAYER 2 WINS THE GAME!")
        else: # Match not won
            reset_positions()
            continue

    # --- Drawing ---
    bg_color = SKY_BLUE
    # Background color reflects global toggle modes, not individual player flight
    if flight_mode_active: bg_color = FLIGHT_MODE_BG_COLOR
    elif debug_mode: bg_color = DEBUG_BG_COLOR
    screen.fill(bg_color)
    pygame.draw.rect(screen, GRASS_GREEN, (0, GROUND_Y, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y))
    draw_goal_isometric(screen, GOAL_LINE_X_LEFT, GOAL_Y_POS, GOAL_HEIGHT, -GOAL_DEPTH_X, GOAL_DEPTH_Y, GOAL_POST_THICKNESS, GOAL_COLOR, GOAL_NET_COLOR)
    draw_goal_isometric(screen, GOAL_LINE_X_RIGHT, GOAL_Y_POS, GOAL_HEIGHT, GOAL_DEPTH_X, GOAL_DEPTH_Y, GOAL_POST_THICKNESS, GOAL_COLOR, GOAL_NET_COLOR)
    if screen_flash_timer > 0: flash_surf = pygame.Surface(screen.get_size(), pygame.SRCALPHA); flash_alpha = int(255 * (screen_flash_timer / SCREEN_FLASH_DURATION)); flash_surf.fill((SCREEN_FLASH_COLOR[0], SCREEN_FLASH_COLOR[1], SCREEN_FLASH_COLOR[2], flash_alpha)); screen.blit(flash_surf, (0,0))
    for p in particles: p.draw(screen)
    powerup.draw(screen) # Draw powerup
    player1.draw(screen); player2.draw(screen); ball.draw(screen); draw_offscreen_arrow(screen, ball, None)

    # --- Draw UI ---
    draw_scoreboard(screen, player1_score, player2_score, p1_games_won, p2_games_won, font_large, font_medium, font_small, goal_message_timer > 0 or match_over_timer > 0)
    draw_game_scores(screen, game_scores, font_small)
    if goal_message_timer > 0 and match_active:
        goal_text_surf = font_goal.render("GOAL!", True, ITALY_RED); goal_text_rect = goal_text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)); bg_rect = goal_text_rect.inflate(20, 10); bg_surf = pygame.Surface(bg_rect.size, pygame.SRCALPHA); bg_surf.fill((WHITE[0], WHITE[1], WHITE[2], 180)); screen.blit(bg_surf, bg_rect.topleft); screen.blit(goal_text_surf, goal_text_rect)
    if match_over_timer > 0 and not game_over:
        winner_name = "Nils" if match_winner == 1 else "Harry"
        match_win_text = f"{winner_name} Wins the Match!"; match_win_surf = font_large.render(match_win_text, True, YELLOW); match_win_rect = match_win_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        next_match_surf = font_medium.render("Next Match Starting...", True, WHITE); next_match_rect = next_match_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        bg_rect = match_win_rect.union(next_match_rect).inflate(40, 20); bg_surf = pygame.Surface(bg_rect.size, pygame.SRCALPHA); bg_surf.fill((0, 0, 100, 200)); screen.blit(bg_surf, bg_rect.topleft)
        screen.blit(match_win_surf, match_win_rect); screen.blit(next_match_surf, next_match_rect)
    if match_active: # Draw cooldowns only during active match
        cooldown_radius = 5; indicator_offset_y = - player1.head_radius - cooldown_radius - 2
        if not p1_can_headbutt: cooldown_color = (255, 0, 0, 180); head_x, head_y = player1.head_pos; indicator_x = int(head_x); indicator_y = int(head_y + indicator_offset_y); temp_surf = pygame.Surface((cooldown_radius*2, cooldown_radius*2), pygame.SRCALPHA); pygame.draw.circle(temp_surf, cooldown_color, (cooldown_radius, cooldown_radius), cooldown_radius); screen.blit(temp_surf, (indicator_x - cooldown_radius, indicator_y - cooldown_radius))
        if not p2_can_headbutt: cooldown_color = (0, 0, 255, 180); head_x, head_y = player2.head_pos; indicator_x = int(head_x); indicator_y = int(head_y + indicator_offset_y); temp_surf = pygame.Surface((cooldown_radius*2, cooldown_radius*2), pygame.SRCALPHA); pygame.draw.circle(temp_surf, cooldown_color, (cooldown_radius, cooldown_radius), cooldown_radius); screen.blit(temp_surf, (indicator_x - cooldown_radius, indicator_y - cooldown_radius))
    if debug_mode: # Draw Timestamp only in debug
        timestamp_surf = font_timestamp.render(GENERATION_TIMESTAMP, True, TEXT_COLOR); timestamp_rect = timestamp_surf.get_rect(bottomright=(SCREEN_WIDTH - 10, SCREEN_HEIGHT - 10)); screen.blit(timestamp_surf, timestamp_rect)

    pygame.display.flip()

# Cleanup
pygame.quit(); sys.exit()