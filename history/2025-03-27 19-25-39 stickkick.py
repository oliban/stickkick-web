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
# Player Colors
P1_COLOR_MAIN = (220, 220, 220); P1_COLOR_ACCENT = (30, 30, 30)
ITALY_GREEN = (0, 146, 70); ITALY_WHITE = (241, 242, 241); ITALY_RED = (206, 43, 55)
P2_COLOR_MAIN = ITALY_GREEN; P2_COLOR_ACCENT = ITALY_RED; P2_COLOR_WHITE = ITALY_WHITE
# Other Colors
GRASS_GREEN = (34, 139, 34); YELLOW = (255, 255, 0); TEXT_COLOR = (10, 10, 50)
ARROW_RED = (255, 50, 50); STAR_YELLOW = (255, 255, 100); STAR_ORANGE = (255, 180, 0)
DEBUG_BLUE = (0, 0, 255)
GOAL_COLOR = (220, 220, 220); GOAL_NET_COLOR = (180, 180, 190)
GOAL_EXPLOSION_COLORS = [WHITE, YELLOW, STAR_YELLOW, (255, 215, 0)]
NOSE_COLOR = (50, 50, 50)
# Scoreboard & Effects
SCOREBOARD_BG_COLOR = (50, 50, 80, 180)
SCOREBOARD_BORDER_COLOR = (200, 200, 220)
SCOREBOARD_TEXT_FLASH_COLOR = YELLOW
SCREEN_FLASH_COLOR = (255, 255, 255, 100)
SCREEN_FLASH_DURATION = 0.15
DEBUG_KICK_ANGLES = False

# Physics
GRAVITY = 0.5; PLAYER_SPEED = 4; JUMP_POWER = -11
BASE_KICK_FORCE_X = 15; BASE_KICK_FORCE_Y = -10
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
GOAL_LINE_X_LEFT = GOAL_MARGIN_X
GOAL_LINE_X_RIGHT = SCREEN_WIDTH - GOAL_MARGIN_X

# Animation Constants (no changes needed)
# ... (Keep all animation constants) ...
WALK_CYCLE_SPEED = 0.25; BODY_WOBBLE_AMOUNT = 0
RUN_UPPER_ARM_SWING = math.pi / 6.0; RUN_UPPER_ARM_WOBBLE_AMP = 0; RUN_UPPER_ARM_WOBBLE_SPEED = 0
RUN_FOREARM_SWING = math.pi / 5.0; RUN_FOREARM_WOBBLE_AMP = 0; RUN_FOREARM_WOBBLE_SPEED = 0
RUN_FOREARM_OFFSET_FACTOR = 0.1; JUMP_UPPER_ARM_BASE = -math.pi * 0.1; JUMP_UPPER_ARM_WOBBLE_AMP = 0
JUMP_UPPER_ARM_WOBBLE_SPEED = 0; JUMP_UPPER_ARM_VY_FACTOR = 0.01; JUMP_FOREARM_BASE = math.pi * 0.1
JUMP_FOREARM_WOBBLE_AMP = 0; JUMP_FOREARM_WOBBLE_SPEED = 0
LEG_THIGH_SWING = math.pi / 7.0; LEG_SHIN_BEND_WALK = math.pi / 8.0; LEG_SHIN_BEND_SHIFT = math.pi / 2.5
KICK_THIGH_WINDUP_ANGLE = -math.pi / 4.5; KICK_THIGH_FOLLOW_ANGLE = math.pi * 0.7
KICK_SHIN_WINDUP_ANGLE = math.pi * 0.75; KICK_SHIN_IMPACT_ANGLE = -math.pi * 0.05
KICK_SHIN_FOLLOW_ANGLE = math.pi * 0.5
JUMP_THIGH_TUCK = math.pi * 0.1; JUMP_SHIN_TUCK = math.pi * 0.2

# Star/Goal Explosion Constants (no changes needed)
# ... (Keep all particle constants) ...
PARTICLE_LIFESPAN = 1.0; PARTICLE_SPEED = 150; PARTICLE_COUNT = 12; PARTICLE_SIZE = 6
GOAL_PARTICLE_COUNT = 30; GOAL_PARTICLE_SPEED_MIN = 200
GOAL_PARTICLE_SPEED_MAX = 350; GOAL_PARTICLE_LIFESPAN = 1.2

# --- Helper Functions --- (no changes needed)
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
    front_top = (goal_line_x, goal_y)
    front_bottom = (goal_line_x, goal_y + goal_height)
    back_x = goal_line_x + depth_x
    back_top_y = goal_y + depth_y
    back_bottom_y = goal_y + goal_height + depth_y
    back_top = (back_x, back_top_y)
    back_bottom = (back_x, back_bottom_y)
    ft_int = (int(front_top[0]), int(front_top[1]))
    fb_int = (int(front_bottom[0]), int(front_bottom[1]))
    bt_int = (int(back_top[0]), int(back_top[1]))
    bb_int = (int(back_bottom[0]), int(back_bottom[1]))
    pygame.draw.line(surface, post_color, bt_int, bb_int, thickness)
    pygame.draw.line(surface, post_color, bt_int, ft_int, thickness)
    pygame.draw.line(surface, post_color, bb_int, fb_int, thickness)
    pygame.draw.line(surface, post_color, ft_int, fb_int, thickness)
    pygame.draw.line(surface, net_color, ft_int, bb_int, 1)
    pygame.draw.line(surface, net_color, fb_int, bt_int, 1)

# --- Scoreboard Function (Modified) ---
def draw_scoreboard(surface, p1_score, p2_score, score_font, name_font, is_goal_active):
    score_text = f"{p1_score} - {p2_score}"
    name_text = "Nils vs. Harry" # Static name text

    # Render surfaces
    score_text_color = SCOREBOARD_TEXT_FLASH_COLOR if is_goal_active else TEXT_COLOR
    score_surf = score_font.render(score_text, True, score_text_color)
    score_rect = score_surf.get_rect()

    name_surf = name_font.render(name_text, True, TEXT_COLOR)
    name_rect = name_surf.get_rect()

    # Panel dimensions - Increased padding for more room
    panel_padding_x = 30 # More horizontal padding
    panel_padding_y_top = 15
    panel_padding_y_bottom = 10 # Padding below name
    text_spacing = 5 # Space between score and name

    panel_width = max(score_rect.width, name_rect.width) + panel_padding_x * 2
    panel_height = score_rect.height + text_spacing + name_rect.height + panel_padding_y_top + panel_padding_y_bottom
    panel_rect = pygame.Rect(0, 0, panel_width, panel_height)
    panel_rect.centerx = SCREEN_WIDTH // 2
    panel_rect.top = 5 # Small margin from screen top

    # Center score text horizontally, position near top
    score_rect.centerx = panel_rect.centerx
    score_rect.top = panel_rect.top + panel_padding_y_top

    # Center name text horizontally, position below score
    name_rect.centerx = panel_rect.centerx
    name_rect.top = score_rect.bottom + text_spacing

    # Draw Panel
    panel_surf = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
    panel_surf.fill(SCOREBOARD_BG_COLOR)
    pygame.draw.rect(panel_surf, SCOREBOARD_BORDER_COLOR, panel_surf.get_rect(), 2) # Border
    surface.blit(panel_surf, panel_rect.topleft)

    # Draw Score & Name Text
    surface.blit(score_surf, score_rect)
    surface.blit(name_surf, name_rect)


# --- Particle Class --- (no changes needed)
class Particle: #...
    def __init__(self, x, y, colors=[STAR_YELLOW, STAR_ORANGE, WHITE], speed_min=PARTICLE_SPEED * 0.5, speed_max=PARTICLE_SPEED * 1.5, lifespan=PARTICLE_LIFESPAN, size=PARTICLE_SIZE):
        self.x = x; self.y = y; angle = random.uniform(0, 2 * math.pi); speed = random.uniform(speed_min, speed_max)
        self.vx = math.cos(angle) * speed; self.vy = math.sin(angle) * speed; self.lifespan = lifespan
        self.start_life = self.lifespan; self.size = size; self.color = random.choice(colors)
    def update(self, dt):
        self.x += self.vx * dt; self.y += self.vy * dt; self.vy += GRAVITY * 20 * dt; self.lifespan -= dt;
        if self.start_life > 0: self.size = PARTICLE_SIZE * max(0, (self.lifespan / self.start_life))
        else: self.size = 0
        return self.lifespan > 0 and self.size > 0.5
    def draw(self, screen):
        if self.size > 0: pygame.draw.rect(screen, self.color, (int(self.x - self.size/2), int(self.y - self.size/2), int(self.size), int(self.size)))


# --- Stick Man Class --- (Added jump-off-head sound trigger)
class StickMan: # ... (init as before) ...
    def __init__(self, x, y, facing=1): # ... (rest of init as before) ...
        self.x = x; self.y = y; self.base_y = y; self.width = 20; self.height = 80; self.vx = 0; self.vy = 0; self.is_jumping = False; self.is_kicking = False
        self.kick_timer = 0; self.kick_duration = 18;
        self.walk_cycle_timer = 0.0; self.head_radius = 12; self.torso_length = 36; self.limb_width = 10; self.upper_arm_length = 12
        self.forearm_length = 12; self.thigh_length = 14; self.shin_length = 14;
        self.torso_colors = [P2_COLOR_MAIN, P2_COLOR_WHITE, P2_COLOR_ACCENT]
        self.arm_colors = [P2_COLOR_ACCENT, P2_COLOR_MAIN]
        self.leg_colors = [P2_COLOR_WHITE, P2_COLOR_ACCENT]
        self.l_upper_arm_angle = 0; self.r_upper_arm_angle = 0; self.l_forearm_angle = 0
        self.r_forearm_angle = 0; self.l_thigh_angle = 0; self.r_thigh_angle = 0; self.l_shin_angle = 0; self.r_shin_angle = 0; self.head_pos = (0, 0)
        self.neck_pos = (0, 0); self.hip_pos = (0, 0); self.shoulder_pos = (0, 0); self.l_elbow_pos = (0, 0); self.r_elbow_pos = (0, 0); self.l_hand_pos = (0, 0)
        self.r_hand_pos = (0, 0); self.l_knee_pos = (0, 0); self.r_knee_pos = (0, 0); self.l_foot_pos = (0, 0); self.r_foot_pos = (0, 0); self.body_rect = pygame.Rect(0,0,0,0)
        self.facing_direction = facing
        self.on_other_player_head = False
    def move(self, direction): # ... (as before) ...
        if not self.is_kicking:
            self.vx = direction * PLAYER_SPEED
            if direction != 0: self.facing_direction = direction
    def stop_move(self): # ... (as before) ...
        self.vx = 0

    def jump(self): # Added jump-off-head sound
        was_on_head = self.on_other_player_head # Store state BEFORE changing it
        if not self.is_jumping or was_on_head:
            play_sound(loaded_sounds['jump'])
            if was_on_head:
                play_sound(loaded_sounds['combo']) # Play combo sound when jumping off head
            self.is_jumping = True
            self.on_other_player_head = False
            self.vy = JUMP_POWER
            self.walk_cycle_timer = 0

    def start_kick(self): # ... (as before) ...
        if not self.is_kicking:
            self.is_kicking = True; self.kick_timer = 0; self.vx = 0

    def update(self, dt, other_player): # ... (Added landing sound trigger) ...
        was_airborne = self.is_jumping or (not self.on_other_player_head and self.y < self.base_y)
        time_ms = pygame.time.get_ticks()
        was_on_head = self.on_other_player_head
        landed_on_head_this_frame = False
        landed_on_ground_this_frame = False
        platform_y = self.base_y
        other_head_pos, other_head_radius = other_player.get_head_position_radius()
        head_top_y = other_head_pos[1] - other_head_radius
        dist_x_head = self.x - other_head_pos[0]
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
        if was_airborne and is_now_grounded:
            play_sound(loaded_sounds['land'])
        intended_vx = self.vx
        if not self.is_kicking:
            effective_vx = intended_vx
            if self.on_other_player_head: effective_vx += other_player.vx
            self.x += effective_vx
            self.x = max(self.limb_width / 2, min(self.x, SCREEN_WIDTH - self.limb_width / 2))
        is_walking = abs(intended_vx) > 0 and not self.is_jumping and not self.is_kicking and not self.on_other_player_head
        if is_walking: self.walk_cycle_timer += WALK_CYCLE_SPEED
        elif not self.is_jumping and not self.is_kicking: self.walk_cycle_timer *= 0.9
        if abs(self.walk_cycle_timer) < 0.1: self.walk_cycle_timer = 0
        if self.is_kicking: # ... (kick animation logic as before) ...
            self.walk_cycle_timer = 0; self.kick_timer += 1; progress = min(self.kick_timer / self.kick_duration, 1.0)
            windup_end = 0.20; impact_start = 0.25; impact_end = 0.50; follow_end = 1.0
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
        current_y = self.y; current_x = self.x; total_leg_visual_height = self.thigh_length + self.shin_length; self.hip_pos = (current_x, current_y - total_leg_visual_height); upper_body_x = current_x; self.neck_pos = (upper_body_x, self.hip_pos[1] - self.torso_length); self.head_pos = (upper_body_x, self.neck_pos[1] - self.head_radius); self.shoulder_pos = self.neck_pos; l_elbow_x = self.shoulder_pos[0] + self.upper_arm_length * math.sin(self.l_upper_arm_angle); l_elbow_y = self.shoulder_pos[1] + self.upper_arm_length * math.cos(self.l_upper_arm_angle); self.l_elbow_pos = (l_elbow_x, l_elbow_y); l_hand_angle_world = self.l_upper_arm_angle + self.l_forearm_angle; l_hand_x = self.l_elbow_pos[0] + self.forearm_length * math.sin(l_hand_angle_world); l_hand_y = self.l_elbow_pos[1] + self.forearm_length * math.cos(l_hand_angle_world); self.l_hand_pos = (l_hand_x, l_hand_y); r_elbow_x = self.shoulder_pos[0] + self.upper_arm_length * math.sin(self.r_upper_arm_angle); r_elbow_y = self.shoulder_pos[1] + self.upper_arm_length * math.cos(self.r_upper_arm_angle); self.r_elbow_pos = (r_elbow_x, r_elbow_y); r_hand_angle_world = self.r_upper_arm_angle + self.r_forearm_angle; r_hand_x = self.r_elbow_pos[0] + self.forearm_length * math.sin(r_hand_angle_world); r_hand_y = self.r_elbow_pos[1] + self.forearm_length * math.cos(r_hand_angle_world); self.r_hand_pos = (r_hand_x, r_hand_y); l_knee_x = self.hip_pos[0] + self.thigh_length * math.sin(self.l_thigh_angle); l_knee_y = self.hip_pos[1] + self.thigh_length * math.cos(self.l_thigh_angle); self.l_knee_pos = (l_knee_x, l_knee_y); l_foot_angle_world = self.l_thigh_angle + self.l_shin_angle; l_foot_x = self.l_knee_pos[0] + self.shin_length * math.sin(l_foot_angle_world); l_foot_y = self.l_knee_pos[1] + self.shin_length * math.cos(l_foot_angle_world); self.l_foot_pos = (l_foot_x, l_foot_y); r_knee_x = self.hip_pos[0] + self.thigh_length * math.sin(self.r_thigh_angle); r_knee_y = self.hip_pos[1] + self.thigh_length * math.cos(self.r_thigh_angle); self.r_knee_pos = (r_knee_x, r_knee_y); r_foot_angle_world = self.r_thigh_angle + self.r_shin_angle; r_foot_x = self.r_knee_pos[0] + self.shin_length * math.sin(r_foot_angle_world); r_foot_y = self.r_knee_pos[1] + self.shin_length * math.cos(r_foot_angle_world)
        self.l_foot_pos = (l_foot_x, l_foot_y); self.r_foot_pos = (r_foot_x, r_foot_y)
        body_width = self.limb_width * 1.5; self.body_rect.width = int(body_width); self.body_rect.height = max(1, int(self.hip_pos[1] - self.neck_pos[1])); self.body_rect.centerx = int(self.hip_pos[0]); self.body_rect.top = int(self.neck_pos[1])

    # Getters (as before)
    def get_kick_impact_point(self): #...
        if self.is_kicking:
            impact_start = 0.25; impact_end = 0.6
            progress = self.kick_timer / self.kick_duration
            if impact_start < progress < impact_end:
                return self.r_foot_pos if self.facing_direction == 1 else self.l_foot_pos
        return None
    def get_head_position_radius(self): return self.head_pos, self.head_radius
    def get_body_rect(self): return self.body_rect

    # Draw Method (as before)
    def draw(self, screen): # ...
        head_center_int = (int(self.head_pos[0]), int(self.head_pos[1])); pygame.draw.circle(screen, ITALY_WHITE, head_center_int, self.head_radius, 0); draw_pentagon(screen, BLACK, head_center_int, self.head_radius * 0.6, angle=0.1); draw_pentagon(screen, BLACK, head_center_int, self.head_radius * 0.3, angle=math.pi/5 + 0.1); pygame.draw.circle(screen, BLACK, head_center_int, self.head_radius, 1)
        nose_length = self.head_radius * 0.5; nose_end_x = head_center_int[0] + nose_length * self.facing_direction; nose_end_y = head_center_int[1] + 2; pygame.draw.line(screen, NOSE_COLOR, head_center_int, (int(nose_end_x), int(nose_end_y)), 2)
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


# --- Ball Class --- (Added sound trigger)
class Ball: # ... (init, apply_force as before) ...
    def __init__(self, x, y, radius): self.x = x; self.y = y; self.radius = radius; self.vx = 0; self.vy = 0; self.last_hit_by = None; self.rotation_angle = 0
    def apply_force(self, force_x, force_y, hitter='player'): self.vx += force_x; self.vy += force_y; self.last_hit_by = hitter
    def update(self, dt): # ... (Added sound trigger) ...
        self.rotation_angle += self.vx * 0.015; self.rotation_angle %= (2 * math.pi); self.vy += GRAVITY; self.vx *= BALL_FRICTION; self.x += self.vx; self.y += self.vy
        hit_ground = False
        hit_wall_this_frame = False
        if self.x + self.radius >= SCREEN_WIDTH: self.x = SCREEN_WIDTH - self.radius; self.vx *= -BALL_BOUNCE * 0.8; hit_wall_this_frame = True
        elif self.x - self.radius <= 0: self.x = self.radius; self.vx *= -BALL_BOUNCE * 0.8; hit_wall_this_frame = True
        if hit_wall_this_frame: play_sound(loaded_sounds['wall_hit'])
        if self.y + self.radius >= GROUND_Y:
            if self.vy >= 0: hit_ground = True
            self.y = GROUND_Y - self.radius; self.vy *= -BALL_BOUNCE; self.vx *= 0.9
            if abs(self.vy) < 1: self.vy = 0
        if abs(self.vx) < 0.1 and self.is_on_ground(): self.vx = 0
        return hit_ground
    def is_on_ground(self): return self.y + self.radius >= GROUND_Y - 0.5
    def draw(self, screen): #... (as before) ...
        center_tuple = (int(self.x), int(self.y)); pygame.draw.circle(screen, WHITE, center_tuple, self.radius)
        pent_size = self.radius * 0.40; hex_size = self.radius * 0.42; dist_factor = 0.65; num_around = 5; angle_step = 2 * math.pi / num_around
        draw_pentagon(screen, BLACK, center_tuple, pent_size, self.rotation_angle)
        for i in range(num_around):
            angle = self.rotation_angle + (i * angle_step) + angle_step / 2; shape_center_x = center_tuple[0] + self.radius * dist_factor * math.cos(angle)
            shape_center_y = center_tuple[1] + self.radius * dist_factor * math.sin(angle); shape_center = (shape_center_x, shape_center_y)
            if i % 2 == 0: draw_hexagon(screen, BLACK, shape_center, hex_size, angle + self.rotation_angle * 0.5, width=1)
            else: draw_pentagon(screen, BLACK, shape_center, pent_size, angle + self.rotation_angle * 0.5)
        pygame.draw.circle(screen, BLACK, center_tuple, self.radius, 1)


# --- Game Setup ---
pygame.init()
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.mixer.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ciao Kick!"); clock = pygame.time.Clock()

# --- Sound Loading ---
def load_sounds(sound_dir="sounds"): # ... (as before) ...
    sounds = {}
    sound_files = {
        "kick": ["kick_ball1.wav", "kick_ball2.wav"],
        "jump": ["jump1.wav"],
        "land": ["land1.wav"],
        "wall_hit": ["wall_hit1.wav"],
        "player_bump": ["player_bump1.wav"],
        "headbutt": ["headbutt1.wav"],
        "body_hit": ["body_hit1.wav"],
        "combo": ["combo_sparkle.wav"],
    }
    for name, filenames in sound_files.items():
        sounds[name] = []
        for filename in filenames:
            path = os.path.join(sound_dir, filename)
            try:
                sound = pygame.mixer.Sound(path)
                sounds[name].append(sound)
                print(f"Loaded sound: {path}")
            except pygame.error as e:
                print(f"Warning: Could not load sound '{path}': {e}")
    for player_num in [1, 2]:
        goal_key = f"goal_p{player_num}"
        sounds[goal_key] = []
        i = 1
        while True:
            filename = f"player{player_num}_goal{i}.wav"
            path = os.path.join(sound_dir, filename)
            if os.path.exists(path):
                try:
                    sound = pygame.mixer.Sound(path)
                    sounds[goal_key].append(sound)
                    print(f"Loaded sound: {path}")
                    i += 1
                except pygame.error as e:
                    print(f"Warning: Could not load sound '{path}': {e}")
                    break
            else: break
        if not sounds[goal_key]: print(f"Warning: No goal sounds found for Player {player_num}")
    for key in ["goal_p1", "goal_p2", "kick", "jump", "land", "wall_hit", "player_bump", "headbutt", "body_hit", "combo"]:
        if key not in sounds: sounds[key] = []
    return sounds
def play_sound(sound_list): # ... (as before) ...
    if sound_list:
        random.choice(sound_list).play()
loaded_sounds = load_sounds()

# --- Player/Ball/Font Setup --- (as before)
player1 = StickMan(SCREEN_WIDTH // 4, GROUND_Y, facing=1); player2 = StickMan(SCREEN_WIDTH * 3 // 4, GROUND_Y, facing=-1)
player1.torso_colors = [P1_COLOR_MAIN, P1_COLOR_ACCENT, P1_COLOR_MAIN]; player1.arm_colors = [P1_COLOR_ACCENT, P1_COLOR_MAIN]; player1.leg_colors = [P1_COLOR_MAIN, P1_COLOR_ACCENT]
ball = Ball(SCREEN_WIDTH // 2, GROUND_Y - 20, 15)
font_large = pygame.font.Font(None, 50); font_medium = pygame.font.Font(None, 36); font_small = pygame.font.Font(None, 28)
font_timestamp = pygame.font.Font(None, 20); font_goal = pygame.font.Font(None, 80)

# --- Score & State Variables --- (as before)
player1_score = 0; player2_score = 0; goal_message_timer = 0; GOAL_MESSAGE_DURATION = 1.5
screen_flash_timer = 0
ball_was_on_ground = True; particles = [];
p1_can_headbutt = True; p2_can_headbutt = True
p1_body_collision_timer = 0; p2_body_collision_timer = 0
current_hit_count = 0

# --- Off-screen Arrow Function --- (as before)
def draw_offscreen_arrow(s, ball, p_pos): #...
    ar_sz = 15; pad = 25; is_off = False; tx, ty = ball.x, ball.y; ax = max(pad, min(ball.x, SCREEN_WIDTH - pad)); ay = max(pad, min(ball.y, SCREEN_HEIGHT - pad))
    if ball.x < 0 or ball.x > SCREEN_WIDTH: ax = pad if ball.x < 0 else SCREEN_WIDTH - pad; is_off = True
    if ball.y < 0 or ball.y > SCREEN_HEIGHT: ay = pad if ball.y < 0 else SCREEN_HEIGHT - pad; is_off = True
    if not is_off: return
    ang = math.atan2(ty - ay, tx - ax); p1 = (ar_sz, 0); p2 = (-ar_sz / 2, -ar_sz / 2); p3 = (-ar_sz / 2, ar_sz / 2)
    cos_a, sin_a = math.cos(ang), math.sin(ang); p1r = (p1[0] * cos_a - p1[1] * sin_a, p1[0] * sin_a + p1[1] * cos_a); p2r = (p2[0] * cos_a - p2[1] * sin_a, p2[0] * sin_a + p2[1] * cos_a); p3r = (p3[0] * cos_a - p3[1] * sin_a, p3[0] * sin_a + p3[1] * cos_a)
    pts = [(ax + p1r[0], ay + p1r[1]), (ax + p2r[0], ay + p2r[1]), (ax + p3r[0], ay + p3r[1])]; pygame.draw.polygon(s, ARROW_RED, [(int(p[0]), int(p[1])) for p in pts])

# --- Reset Function --- (as before)
def reset_after_goal(): #...
    global ball_was_on_ground, current_hit_count, p1_can_headbutt, p2_can_headbutt
    ball.x = SCREEN_WIDTH // 2; ball.y = SCREEN_HEIGHT // 3; ball.vx = 0; ball.vy = 0
    player1.x = SCREEN_WIDTH // 4; player1.y = GROUND_Y; player1.vx = 0; player1.vy = 0; player1.is_kicking = False; player1.on_other_player_head = False; player1.facing_direction = 1; player1.is_jumping = False;
    player2.x = SCREEN_WIDTH * 3 // 4; player2.y = GROUND_Y; player2.vx = 0; player2.vy = 0; player2.is_kicking = False; player2.on_other_player_head = False; player2.facing_direction = -1; player2.is_jumping = False;
    current_hit_count = 0; ball_was_on_ground = False
    p1_can_headbutt = True; p2_can_headbutt = True

# --- Collision Handling Function (Player-Ball) --- (Added sound triggers)
def handle_player_ball_collisions(player, ball, can_headbutt, body_collision_timer, is_ball_airborne): #...
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
                 ball.apply_force(kick_x, kick_y, hitter=player); kick_performed = True; kick_pt = local_kick_point
                 play_sound(loaded_sounds['kick'])
                 if is_ball_airborne: current_hit_count += 1; score_increase = True
    head_pos, head_radius = player.get_head_position_radius(); dist_x_head = ball.x - head_pos[0]; dist_y_head = ball.y - head_pos[1]
    dist_head_sq = dist_x_head**2 + dist_y_head**2; headbutt_cooldown_just_applied = False
    if dist_head_sq < (ball.radius + head_radius)**2:
        if can_headbutt:
            force_y = -HEADBUTT_UP_FORCE;
            if player.vy < 0: force_y -= abs(player.vy) * HEADBUTT_VY_MULTIPLIER
            force_x = player.vx * HEADBUTT_PLAYER_VX_FACTOR - dist_x_head * HEADBUTT_POS_X_FACTOR
            ball.apply_force(force_x, force_y, hitter=player); headbutt_cooldown_just_applied = True; headbutt_performed = True
            play_sound(loaded_sounds['headbutt'])
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
                 distance = math.sqrt(dist_sq_body); overlap = ball.radius - distance
                 collision_normal_x = delta_x / distance; collision_normal_y = delta_y / distance
                 push_amount = overlap + 0.2; ball.x += collision_normal_x * push_amount; ball.y += collision_normal_y * push_amount
                 rel_vx = ball.vx - player.vx; rel_vy = ball.vy - player.vy; vel_along_normal = rel_vx * collision_normal_x + rel_vy * collision_normal_y
                 if vel_along_normal < 0:
                     impulse_scalar = -(1 + PLAYER_BODY_BOUNCE) * vel_along_normal; bounce_vx = impulse_scalar * collision_normal_x; bounce_vy = impulse_scalar * collision_normal_y
                     bounce_vx += player.vx * PLAYER_VEL_TRANSFER; bounce_vy += player.vy * PLAYER_VEL_TRANSFER
                     new_vel_mag_sq = bounce_vx**2 + bounce_vy**2
                     if new_vel_mag_sq < MIN_BODY_BOUNCE_VEL**2:
                         if new_vel_mag_sq > 0: scale = MIN_BODY_BOUNCE_VEL / math.sqrt(new_vel_mag_sq); bounce_vx *= scale; bounce_vy *= scale
                         else: bounce_vx = collision_normal_x * MIN_BODY_BOUNCE_VEL; bounce_vy = collision_normal_y * MIN_BODY_BOUNCE_VEL
                     ball.vx = bounce_vx; ball.vy = bounce_vy
                     new_body_collision_timer = PLAYER_BODY_COLLISION_FRAMES
                     collision_occurred = True
             elif dist_sq_body == 0:
                  ball.y = player_rect.top - ball.radius - 0.1
                  if ball.vy > 0: ball.vy *= -PLAYER_BODY_BOUNCE
                  new_body_collision_timer = PLAYER_BODY_COLLISION_FRAMES
                  collision_occurred = True
             if collision_occurred:
                 play_sound(loaded_sounds['body_hit'])
    return score_increase, new_can_headbutt, new_body_collision_timer, kick_pt

# --- Main Game Loop ---
running = True
while running:
    dt = clock.tick(FPS) / 1000.0; dt = min(dt, 0.1)
    # --- Updates ---
    if p1_body_collision_timer > 0: p1_body_collision_timer -= 1 # ... (rest of updates as before) ...
    if p2_body_collision_timer > 0: p2_body_collision_timer -= 1
    if goal_message_timer > 0: goal_message_timer -= dt
    if screen_flash_timer > 0: screen_flash_timer -= dt
    for event in pygame.event.get(): # ... (event handling as before) ...
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT: player1.move(-1)
            elif event.key == pygame.K_RIGHT: player1.move(1)
            elif event.key == pygame.K_UP: player1.jump()
            elif event.key == pygame.K_DOWN: player1.start_kick()
            elif event.key == pygame.K_a: player2.move(-1)
            elif event.key == pygame.K_d: player2.move(1)
            elif event.key == pygame.K_w: player2.jump()
            elif event.key == pygame.K_s: player2.start_kick()
            elif event.key == pygame.K_ESCAPE: running = False
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT and player1.vx < 0: player1.stop_move()
            elif event.key == pygame.K_RIGHT and player1.vx > 0: player1.stop_move()
            elif event.key == pygame.K_a and player2.vx < 0: player2.stop_move()
            elif event.key == pygame.K_d and player2.vx > 0: player2.stop_move()
    player1.update(dt, player2)
    player2.update(dt, player1)
    ball_hit_ground_this_frame = ball.update(dt)
    particles = [p for p in particles if p.update(dt)]

    # --- Player-Player Collision --- (Added sound trigger)
    p1_rect = player1.get_body_rect(); p2_rect = player2.get_body_rect() #... (rest as before) ...
    if p1_rect.colliderect(p2_rect):
        p1_is_on_p2 = player1.on_other_player_head; p2_is_on_p1 = player2.on_other_player_head
        if p1_is_on_p2 and abs(player1.y - (player2.head_pos[1] - player2.head_radius)) > 10: p1_is_on_p2 = False
        if p2_is_on_p1 and abs(player2.y - (player1.head_pos[1] - player1.head_radius)) > 10: p2_is_on_p1 = False
        if not p1_is_on_p2 and not p2_is_on_p1:
            overlap_x = 0
            if player1.x < player2.x: overlap_x = p1_rect.right - p2_rect.left
            else: overlap_x = p2_rect.right - p1_rect.left
            if overlap_x > 0:
                play_sound(loaded_sounds['player_bump'])
                push = overlap_x / 2 + 0.1
                if player1.x < player2.x: player1.x -= push; player2.x += push;
                if player1.vx > 0: player1.vx = 0
                if player2.vx < 0: player2.vx = 0
                else: player1.x += push; player2.x -= push;
                if player1.vx < 0: player1.vx = 0
                if player2.vx > 0: player2.vx = 0

    # --- Goal Detection & Effects --- (Added 5th goal sound trigger)
    goal_scored = False; goal_pos_x = -1; scorer = 0
    if ball.x + ball.radius >= GOAL_LINE_X_RIGHT and ball.y > GOAL_Y_POS:
        player1_score += 1; scorer = 1; goal_message_timer = GOAL_MESSAGE_DURATION; goal_scored = True; goal_pos_x = SCREEN_WIDTH; print(f"GOAL! Player 1 Score: {player1_score}"); screen_flash_timer = SCREEN_FLASH_DURATION
    elif ball.x - ball.radius <= GOAL_LINE_X_LEFT and ball.y > GOAL_Y_POS:
        player2_score += 1; scorer = 2; goal_message_timer = GOAL_MESSAGE_DURATION; goal_scored = True; goal_pos_x = 0; print(f"GOAL! Player 2 Score: {player2_score}"); screen_flash_timer = SCREEN_FLASH_DURATION
    if goal_scored:
        if scorer == 1: play_sound(loaded_sounds['goal_p1'])
        elif scorer == 2: play_sound(loaded_sounds['goal_p2'])
        # Check for 5th goal milestone
        if (player1_score + player2_score) > 0 and (player1_score + player2_score) % 5 == 0:
            play_sound(loaded_sounds['combo']) # Play combo sound on 5th, 10th, etc., total goal
        goal_center_y = GOAL_Y_POS + GOAL_HEIGHT / 2
        for _ in range(GOAL_PARTICLE_COUNT): particles.append(Particle(goal_pos_x, goal_center_y, colors=GOAL_EXPLOSION_COLORS, speed_min=GOAL_PARTICLE_SPEED_MIN, speed_max=GOAL_PARTICLE_SPEED_MAX, lifespan=GOAL_PARTICLE_LIFESPAN))
        reset_after_goal(); continue

    # --- Combo Score Reset Logic --- (as before)
    is_ball_airborne = not ball.is_on_ground() # ... (rest as before) ...
    if not is_ball_airborne and ball_hit_ground_this_frame and not ball_was_on_ground: current_hit_count = 0
    ball_was_on_ground = not is_ball_airborne

    # --- Player-Ball Collisions --- (as before)
    p1_hit, p1_can_headbutt, p1_body_collision_timer, p1_kick_pt = handle_player_ball_collisions(player1, ball, p1_can_headbutt, p1_body_collision_timer, is_ball_airborne) # ... (rest as before) ...
    p2_hit, p2_can_headbutt, p2_body_collision_timer, p2_kick_pt = handle_player_ball_collisions(player2, ball, p2_can_headbutt, p2_body_collision_timer, is_ball_airborne)
    score_increased_this_frame = p1_hit or p2_hit
    last_kick_point = p1_kick_pt if p1_kick_pt else p2_kick_pt

    # --- Trigger Star Explosion (Combo effect) --- (Added sound trigger)
    if score_increased_this_frame and last_kick_point and current_hit_count > 0 and current_hit_count % 5 == 0: # ... (rest as before) ...
        play_sound(loaded_sounds['combo']) # <<< Combo sound for airborne hits
        num_kick_particles = PARTICLE_COUNT // 2
        for _ in range(num_kick_particles): particle_x = last_kick_point[0] + random.uniform(-5, 5); particle_y = last_kick_point[1] + random.uniform(-5, 5); particles.append(Particle(particle_x, particle_y))

    # --- Drawing ---
    screen.fill(SKY_BLUE); pygame.draw.rect(screen, GRASS_GREEN, (0, GROUND_Y, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y))
    draw_goal_isometric(screen, GOAL_LINE_X_LEFT, GOAL_Y_POS, GOAL_HEIGHT, -GOAL_DEPTH_X, GOAL_DEPTH_Y, GOAL_POST_THICKNESS, GOAL_COLOR, GOAL_NET_COLOR)
    draw_goal_isometric(screen, GOAL_LINE_X_RIGHT, GOAL_Y_POS, GOAL_HEIGHT, GOAL_DEPTH_X, GOAL_DEPTH_Y, GOAL_POST_THICKNESS, GOAL_COLOR, GOAL_NET_COLOR)
    if screen_flash_timer > 0: flash_surf = pygame.Surface(screen.get_size(), pygame.SRCALPHA); flash_alpha = int(255 * (screen_flash_timer / SCREEN_FLASH_DURATION)); flash_surf.fill((SCREEN_FLASH_COLOR[0], SCREEN_FLASH_COLOR[1], SCREEN_FLASH_COLOR[2], flash_alpha)); screen.blit(flash_surf, (0,0))
    for p in particles: p.draw(screen)
    player1.draw(screen); player2.draw(screen); ball.draw(screen); draw_offscreen_arrow(screen, ball, None)

    # --- Draw UI --- (Updated scoreboard call)
    draw_scoreboard(screen, player1_score, player2_score, font_large, font_medium, goal_message_timer > 0) # Pass font_medium for name
    if goal_message_timer > 0: goal_text_surf = font_goal.render("GOAL!", True, ITALY_RED); goal_text_rect = goal_text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)); bg_rect = goal_text_rect.inflate(20, 10); bg_surf = pygame.Surface(bg_rect.size, pygame.SRCALPHA); bg_surf.fill((WHITE[0], WHITE[1], WHITE[2], 180)); screen.blit(bg_surf, bg_rect.topleft); screen.blit(goal_text_surf, goal_text_rect)
    cooldown_radius = 5; indicator_offset_y = - player1.head_radius - cooldown_radius - 2
    if not p1_can_headbutt: cooldown_color = (255, 0, 0, 180); head_x, head_y = player1.head_pos; indicator_x = int(head_x); indicator_y = int(head_y + indicator_offset_y); temp_surf = pygame.Surface((cooldown_radius*2, cooldown_radius*2), pygame.SRCALPHA); pygame.draw.circle(temp_surf, cooldown_color, (cooldown_radius, cooldown_radius), cooldown_radius); screen.blit(temp_surf, (indicator_x - cooldown_radius, indicator_y - cooldown_radius))
    if not p2_can_headbutt: cooldown_color = (0, 0, 255, 180); head_x, head_y = player2.head_pos; indicator_x = int(head_x); indicator_y = int(head_y + indicator_offset_y); temp_surf = pygame.Surface((cooldown_radius*2, cooldown_radius*2), pygame.SRCALPHA); pygame.draw.circle(temp_surf, cooldown_color, (cooldown_radius, cooldown_radius), cooldown_radius); screen.blit(temp_surf, (indicator_x - cooldown_radius, indicator_y - cooldown_radius))
    timestamp_surf = font_timestamp.render(GENERATION_TIMESTAMP, True, TEXT_COLOR); timestamp_rect = timestamp_surf.get_rect(bottomright=(SCREEN_WIDTH - 10, SCREEN_HEIGHT - 10)); screen.blit(timestamp_surf, timestamp_rect)

    pygame.display.flip()

# Cleanup
pygame.quit(); sys.exit()