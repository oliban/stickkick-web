# -*- coding: utf-8 -*-
import pygame
import sys
import math
import random
from datetime import datetime

# --- Get Timestamp ---
GENERATION_TIMESTAMP = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# --- Constants ---
SCREEN_WIDTH = 800; SCREEN_HEIGHT = 600; FPS = 60
WHITE = (255, 255, 255); BLACK = (0, 0, 0); SKY_BLUE = (135, 206, 235)
ITALY_GREEN = (0, 146, 70); ITALY_WHITE = (241, 242, 241); ITALY_RED = (206, 43, 55)
GRASS_GREEN = (34, 139, 34); YELLOW = (255, 255, 0); TEXT_COLOR = (10, 10, 50)
ARROW_RED = (255, 50, 50); STAR_YELLOW = (255, 255, 100); STAR_ORANGE = (255, 180, 0)
DEBUG_BLUE = (0, 0, 255)
GOAL_COLOR = (220, 220, 220)
GOAL_NET_COLOR = (180, 180, 190)
DEBUG_KICK_ANGLES = False

# Physics
GRAVITY = 0.5; PLAYER_SPEED = 4; JUMP_POWER = -11
BASE_KICK_FORCE_X = 14; BASE_KICK_FORCE_Y = -13;
# Removed Charge Rate/Max/Min
KICK_FORCE_LEVEL = 1.5 # <<< Fixed strength multiplier for kicks
HEADBUTT_UP_FORCE = 15.0; HEADBUTT_VY_MULTIPLIER = 1.2
HEADBUTT_PLAYER_VX_FACTOR = 0.6; HEADBUTT_POS_X_FACTOR = 0.15
BALL_FRICTION = 0.99; BALL_BOUNCE = 0.7; GROUND_Y = SCREEN_HEIGHT - 50

# Collision Specific
PLAYER_BODY_BOUNCE = 0.65; PLAYER_VEL_TRANSFER = 0.25
MIN_BODY_BOUNCE_VEL = 1.5; PLAYER_BODY_COLLISION_FRAMES = 4
PLAYER_PUSH_FACTOR = 0.5

# Kick Collision Tweak
KICK_RADIUS_NORMAL = 13; KICK_RADIUS_FALLING_BONUS = 5
BALL_FALLING_VELOCITY_THRESHOLD = 5

# Goal Constants
GOAL_HEIGHT = 110; GOAL_POST_THICKNESS = 3; GOAL_Y_POS = GROUND_Y - GOAL_HEIGHT
GOAL_DEPTH_X = 30; GOAL_DEPTH_Y = -15
GOAL_LINE_X_LEFT = GOAL_POST_THICKNESS // 2; GOAL_LINE_X_RIGHT = SCREEN_WIDTH - (GOAL_POST_THICKNESS // 2)

# Animation
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

# Star Explosion
PARTICLE_LIFESPAN = 1.0; PARTICLE_SPEED = 150; PARTICLE_COUNT = 12; PARTICLE_SIZE = 6

# --- Helper Functions ---
def draw_polygon_shape(surface, color, center, size, sides, angle=0, width=0):
    points = []
    for i in range(sides):
        offset_angle = math.pi / sides if sides % 2 == 0 else math.pi / 2.0
        theta = offset_angle + (2.0 * math.pi * i / sides) + angle
        x = center[0] + size * math.cos(theta); y = center[1] + size * math.sin(theta)
        points.append((int(x), int(y)))
    pygame.draw.polygon(surface, color, points, width)
def draw_pentagon(surface, color, center, size, angle=0, width=0): draw_polygon_shape(surface, color, center, size, 5, angle, width)
def draw_hexagon(surface, color, center, size, angle=0, width=0): draw_polygon_shape(surface, color, center, size, 6, angle, width)
def normalize(v): mag_sq = v[0]**2 + v[1]**2; mag = math.sqrt(mag_sq) if mag_sq > 0 else 0; return (v[0]/mag, v[1]/mag) if mag > 0 else (0,0)
def draw_rotated_rectangle(surface, color, rect_center, width, height, angle_rad):
    half_w, half_h = width / 2, height / 2; corners = [(-half_w, -half_h), ( half_w, -half_h), ( half_w,  half_h), (-half_w,  half_h)]
    cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad); rotated_corners = []
    for x, y in corners: x_rot = x * cos_a - y * sin_a; y_rot = x * sin_a + y * cos_a; rotated_corners.append((rect_center[0] + x_rot, rect_center[1] + y_rot))
    pygame.draw.polygon(surface, color, rotated_corners, 0); pygame.draw.polygon(surface, BLACK, rotated_corners, 1)
def draw_goal_isometric(surface, goal_line_x, goal_y, goal_height, depth_x, depth_y, thickness, post_color, net_color):
    is_left_goal = goal_line_x < SCREEN_WIDTH / 2; front_top = (goal_line_x, goal_y); front_bottom = (goal_line_x, goal_y + goal_height)
    back_x = goal_line_x + depth_x if is_left_goal else goal_line_x - depth_x; back_top_y = goal_y + depth_y; back_bottom_y = goal_y + goal_height + depth_y
    back_top = (back_x, back_top_y); back_bottom = (back_x, back_bottom_y)
    pygame.draw.line(surface, post_color, back_top, back_bottom, thickness); pygame.draw.line(surface, post_color, back_top, front_top, thickness); pygame.draw.line(surface, post_color, back_bottom, front_bottom, thickness)
    pygame.draw.line(surface, post_color, front_top, front_bottom, thickness)
    pygame.draw.line(surface, net_color, front_top, back_bottom, 1); pygame.draw.line(surface, net_color, front_bottom, back_top, 1)
    num_net_lines_back = 4
    for i in range(1, num_net_lines_back): lerp_factor = i / num_net_lines_back; y_pos = back_top_y + (back_bottom_y - back_top_y) * lerp_factor; pygame.draw.line(surface, net_color, (back_x, back_top_y), (back_x, y_pos), 1); pygame.draw.line(surface, net_color, (back_x, y_pos), (back_bottom[0], back_bottom[1]), 1)

# --- Particle Class ---
class Particle:
    def __init__(self, x, y):
        self.x = x; self.y = y; angle = random.uniform(0, 2 * math.pi); speed = random.uniform(PARTICLE_SPEED * 0.5, PARTICLE_SPEED * 1.5)
        self.vx = math.cos(angle) * speed; self.vy = math.sin(angle) * speed; self.lifespan = PARTICLE_LIFESPAN
        self.start_life = self.lifespan; self.size = PARTICLE_SIZE; self.color = random.choice([STAR_YELLOW, STAR_ORANGE, WHITE])
    def update(self, dt):
        self.x += self.vx * dt; self.y += self.vy * dt; self.vy += GRAVITY * 20 * dt; self.lifespan -= dt; self.size = PARTICLE_SIZE * (self.lifespan / self.start_life)
        return self.lifespan > 0 and self.size > 1
    def draw(self, screen):
        if self.size > 0: pygame.draw.rect(screen, self.color, (int(self.x - self.size/2), int(self.y - self.size/2), int(self.size), int(self.size)))

# --- Stick Man Class (Ciao - No Charging) ---
class StickMan:
    def __init__(self, x, y, facing=1):
        self.x = x; self.y = y; self.base_y = y; self.width = 20; self.height = 80; self.vx = 0; self.vy = 0; self.is_jumping = False; self.is_kicking = False
        # Removed is_charging, charge_power, kick_charge_level
        self.kick_timer = 0; self.kick_duration = 20;
        self.walk_cycle_timer = 0.0; self.kick_side = 'right'; self.head_radius = 12; self.torso_length = 36; self.limb_width = 10; self.upper_arm_length = 12
        self.forearm_length = 12; self.thigh_length = 14; self.shin_length = 14; self.torso_colors = [ITALY_GREEN, ITALY_WHITE, ITALY_RED]
        self.arm_colors = [ITALY_RED, ITALY_GREEN]; self.leg_colors = [ITALY_WHITE, ITALY_RED]; self.l_upper_arm_angle = 0; self.r_upper_arm_angle = 0; self.l_forearm_angle = 0
        self.r_forearm_angle = 0; self.l_thigh_angle = 0; self.r_thigh_angle = 0; self.l_shin_angle = 0; self.r_shin_angle = 0; self.head_pos = (0, 0)
        self.neck_pos = (0, 0); self.hip_pos = (0, 0); self.shoulder_pos = (0, 0); self.l_elbow_pos = (0, 0); self.r_elbow_pos = (0, 0); self.l_hand_pos = (0, 0)
        self.r_hand_pos = (0, 0); self.l_knee_pos = (0, 0); self.r_knee_pos = (0, 0); self.l_foot_pos = (0, 0); self.r_foot_pos = (0, 0); self.body_rect = pygame.Rect(0,0,0,0)
        self.facing_direction = facing
    # Correctly Formatted Move
    def move(self, direction):
        if not self.is_kicking:
            self.vx = direction * PLAYER_SPEED
            if direction != 0:
                self.facing_direction = direction
    def stop_move(self): self.vx = 0
    def jump(self):
        if not self.is_jumping: self.is_jumping = True; self.vy = JUMP_POWER; self.walk_cycle_timer = 0
    # Removed start_charge and release_charge_and_kick related to charging
    # Modified start_kick
    def start_kick(self, ball_x):
        if not self.is_kicking:
            self.is_kicking = True; self.kick_timer = 0; self.vx = 0
            self.kick_side = 'left' if ball_x < self.x else 'right'

    def update(self, dt):
        time_ms = pygame.time.get_ticks()
        # No charging update
        if not self.is_kicking: self.x += self.vx; self.x = max(self.limb_width / 2, min(self.x, SCREEN_WIDTH - self.limb_width / 2))
        if self.y < self.base_y or self.vy < 0: self.vy += GRAVITY; self.y += self.vy
        is_walking_on_ground = abs(self.vx) > 0 and not self.is_jumping and not self.is_kicking
        if is_walking_on_ground: self.walk_cycle_timer += WALK_CYCLE_SPEED
        elif not self.is_jumping and not self.is_kicking: self.walk_cycle_timer *= 0.9
        if abs(self.walk_cycle_timer) < 0.1: self.walk_cycle_timer = 0
        if self.is_kicking:
            self.walk_cycle_timer = 0; self.kick_timer += 1; progress = min(self.kick_timer / self.kick_duration, 1.0)
            windup_end = 0.20; impact_start = 0.25; impact_end = 0.50; follow_end = 1.0
            if progress < windup_end: thigh_prog_angle = KICK_THIGH_WINDUP_ANGLE * (progress / windup_end)
            elif progress < impact_end: impact_progress = (progress - windup_end) / (impact_end - windup_end); thigh_prog_angle = KICK_THIGH_WINDUP_ANGLE + (KICK_THIGH_FOLLOW_ANGLE - KICK_THIGH_WINDUP_ANGLE) * impact_progress
            else: follow_progress = (progress - impact_end) / (follow_end - impact_end); ease_out_factor = 1.0 - follow_progress**1.5; thigh_prog_angle = KICK_THIGH_FOLLOW_ANGLE * ease_out_factor
            if progress < impact_start: shin_prog_angle = KICK_SHIN_WINDUP_ANGLE * (progress / impact_start)
            elif progress < impact_end: impact_progress = (progress - impact_start) / (impact_end - impact_start); ease_in_factor = impact_progress ** 2; shin_prog_angle = KICK_SHIN_WINDUP_ANGLE + (KICK_SHIN_IMPACT_ANGLE - KICK_SHIN_WINDUP_ANGLE) * ease_in_factor
            else: follow_progress = (progress - impact_end) / (follow_end - impact_end); shin_prog_angle = KICK_SHIN_IMPACT_ANGLE + (KICK_SHIN_FOLLOW_ANGLE - KICK_SHIN_IMPACT_ANGLE) * follow_progress
            if DEBUG_KICK_ANGLES: print(f"Kick Prog: {progress:.2f}, Thigh: {math.degrees(thigh_prog_angle):.1f}, Shin: {math.degrees(shin_prog_angle):.1f}")
            if self.kick_side == 'right': self.r_thigh_angle = thigh_prog_angle; self.r_shin_angle = shin_prog_angle; self.l_thigh_angle = -thigh_prog_angle * 0.3; self.l_shin_angle = 0.3
            else: self.l_thigh_angle = thigh_prog_angle; self.l_shin_angle = shin_prog_angle; self.r_thigh_angle = -thigh_prog_angle * 0.3; self.r_shin_angle = 0.3
            self.l_upper_arm_angle = -thigh_prog_angle * 0.15 if self.kick_side == 'right' else thigh_prog_angle * 0.12; self.r_upper_arm_angle = thigh_prog_angle * 0.12 if self.kick_side == 'right' else -thigh_prog_angle * 0.15
            self.l_forearm_angle = 0.2; self.r_forearm_angle = 0.2
            if self.kick_timer >= self.kick_duration: self.is_kicking = False; self.kick_timer = 0; self.r_thigh_angle = 0; self.l_thigh_angle = 0; self.r_shin_angle = 0; self.l_shin_angle = 0; self.l_upper_arm_angle = 0; self.r_upper_arm_angle = 0; self.l_forearm_angle = 0; self.r_forearm_angle = 0
        else:
             if is_walking_on_ground: walk_sin = math.sin(self.walk_cycle_timer); self.l_upper_arm_angle = RUN_UPPER_ARM_SWING * walk_sin * self.facing_direction; self.r_upper_arm_angle = -RUN_UPPER_ARM_SWING * walk_sin * self.facing_direction; self.l_forearm_angle = RUN_FOREARM_SWING * math.sin(self.walk_cycle_timer - RUN_FOREARM_OFFSET_FACTOR) * self.facing_direction; self.r_forearm_angle = -RUN_FOREARM_SWING * math.sin(self.walk_cycle_timer - RUN_FOREARM_OFFSET_FACTOR) * self.facing_direction; self.l_thigh_angle = -LEG_THIGH_SWING * walk_sin * self.facing_direction; self.r_thigh_angle = LEG_THIGH_SWING * walk_sin * self.facing_direction; shin_bend = LEG_SHIN_BEND_WALK * max(0, math.sin(self.walk_cycle_timer + LEG_SHIN_BEND_SHIFT)); self.l_shin_angle = shin_bend if self.l_thigh_angle * self.facing_direction < 0 else 0.1; self.r_shin_angle = shin_bend if self.r_thigh_angle * self.facing_direction < 0 else 0.1
             elif self.is_jumping: base_up_angle = JUMP_UPPER_ARM_BASE - self.vy * JUMP_UPPER_ARM_VY_FACTOR; self.l_upper_arm_angle = base_up_angle; self.r_upper_arm_angle = base_up_angle; base_fore_angle = JUMP_FOREARM_BASE; self.l_forearm_angle = base_fore_angle; self.r_forearm_angle = base_fore_angle; jump_progress = max(0, min(1, 1 - (self.y / self.base_y))); thigh_tuck = JUMP_THIGH_TUCK * jump_progress; shin_tuck = JUMP_SHIN_TUCK * jump_progress; self.l_thigh_angle = thigh_tuck; self.r_thigh_angle = thigh_tuck; self.l_shin_angle = shin_tuck; self.r_shin_angle = shin_tuck
             else: self.l_upper_arm_angle = 0; self.r_upper_arm_angle = 0; self.l_forearm_angle = 0; self.r_forearm_angle = 0; self.l_thigh_angle = 0; self.r_thigh_angle = 0; self.l_shin_angle = 0; self.r_shin_angle = 0
        current_y = self.y; current_x = self.x; wobble_offset = 0; total_leg_visual_height = self.thigh_length + self.shin_length; self.hip_pos = (current_x, current_y - total_leg_visual_height); upper_body_x = current_x + wobble_offset; self.neck_pos = (upper_body_x, self.hip_pos[1] - self.torso_length); self.head_pos = (upper_body_x, self.neck_pos[1] - self.head_radius); self.shoulder_pos = self.neck_pos; l_elbow_x = self.shoulder_pos[0] + self.upper_arm_length * math.sin(self.l_upper_arm_angle); l_elbow_y = self.shoulder_pos[1] + self.upper_arm_length * math.cos(self.l_upper_arm_angle); self.l_elbow_pos = (l_elbow_x, l_elbow_y); l_hand_angle_world = self.l_upper_arm_angle + self.l_forearm_angle; l_hand_x = self.l_elbow_pos[0] + self.forearm_length * math.sin(l_hand_angle_world); l_hand_y = self.l_elbow_pos[1] + self.forearm_length * math.cos(l_hand_angle_world); self.l_hand_pos = (l_hand_x, l_hand_y); r_elbow_x = self.shoulder_pos[0] + self.upper_arm_length * math.sin(self.r_upper_arm_angle); r_elbow_y = self.shoulder_pos[1] + self.upper_arm_length * math.cos(self.r_upper_arm_angle); self.r_elbow_pos = (r_elbow_x, r_elbow_y); r_hand_angle_world = self.r_upper_arm_angle + self.r_forearm_angle; r_hand_x = self.r_elbow_pos[0] + self.forearm_length * math.sin(r_hand_angle_world); r_hand_y = self.r_elbow_pos[1] + self.forearm_length * math.cos(r_hand_angle_world); self.r_hand_pos = (r_hand_x, r_hand_y); l_knee_x = self.hip_pos[0] + self.thigh_length * math.sin(self.l_thigh_angle); l_knee_y = self.hip_pos[1] + self.thigh_length * math.cos(self.l_thigh_angle); self.l_knee_pos = (l_knee_x, l_knee_y); l_foot_angle_world = self.l_thigh_angle + self.l_shin_angle; l_foot_x = self.l_knee_pos[0] + self.shin_length * math.sin(l_foot_angle_world); l_foot_y = self.l_knee_pos[1] + self.shin_length * math.cos(l_foot_angle_world); r_knee_x = self.hip_pos[0] + self.thigh_length * math.sin(self.r_thigh_angle); r_knee_y = self.hip_pos[1] + self.thigh_length * math.cos(self.r_thigh_angle); self.r_knee_pos = (r_knee_x, r_knee_y); r_foot_angle_world = self.r_thigh_angle + self.r_shin_angle; r_foot_x = self.r_knee_pos[0] + self.shin_length * math.sin(r_foot_angle_world); r_foot_y = self.r_knee_pos[1] + self.shin_length * math.cos(r_foot_angle_world)
        body_width = self.limb_width * 1.5; self.body_rect.width = int(body_width); self.body_rect.height = int(self.hip_pos[1] - self.neck_pos[1]); self.body_rect.centerx = int(self.hip_pos[0]); self.body_rect.top = int(self.neck_pos[1])
        ground = self.base_y; lowest_foot_y = max(l_foot_y, r_foot_y)
        if self.y >= ground and self.vy >= 0:
             if not self.is_kicking: self.y = ground; self.is_jumping = False; self.vy = 0; l_knee_x = self.hip_pos[0] + self.thigh_length * math.sin(self.l_thigh_angle); l_knee_y = self.hip_pos[1] + self.thigh_length * math.cos(self.l_thigh_angle); l_foot_angle_world = self.l_thigh_angle + self.l_shin_angle; l_foot_x = l_knee_x + self.shin_length * math.sin(l_foot_angle_world); r_knee_x = self.hip_pos[0] + self.thigh_length * math.sin(self.r_thigh_angle); r_knee_y = self.hip_pos[1] + self.thigh_length * math.cos(self.r_thigh_angle); r_foot_angle_world = self.r_thigh_angle + self.r_shin_angle; r_foot_x = r_knee_x + self.shin_length * math.sin(r_foot_angle_world); self.l_foot_pos = (l_foot_x, ground); self.r_foot_pos = (r_foot_x, ground)
        else: self.l_foot_pos = (l_foot_x, l_foot_y); self.r_foot_pos = (r_foot_x, r_foot_y)

    # Getters
    def get_kick_impact_point(self):
        if self.is_kicking:
            impact_start = 0.25; impact_end = 0.6; progress = self.kick_timer / self.kick_duration
            if impact_start < progress < impact_end: return self.l_foot_pos if self.kick_side == 'left' else self.r_foot_pos
        return None
    def get_head_position_radius(self): return self.head_pos, self.head_radius
    def get_body_rect(self): return self.body_rect

    # Draw Method
    def draw(self, screen):
        # No charge bar
        head_center_int = (int(self.head_pos[0]), int(self.head_pos[1])); pygame.draw.circle(screen, ITALY_WHITE, head_center_int, self.head_radius, 0); draw_pentagon(screen, BLACK, head_center_int, self.head_radius * 0.6, angle=0.1); draw_pentagon(screen, BLACK, head_center_int, self.head_radius * 0.3, angle=math.pi/5 + 0.1); pygame.draw.circle(screen, BLACK, head_center_int, self.head_radius, 1); torso_segment_height = self.torso_length / 3; current_torso_y = self.neck_pos[1]
        for i in range(3): rect_center_x = self.neck_pos[0]; rect_center_y = current_torso_y + torso_segment_height / 2; draw_rotated_rectangle(screen, self.torso_colors[i], (rect_center_x, rect_center_y), self.limb_width, torso_segment_height, 0); current_torso_y += torso_segment_height
        def draw_limb_segment(start_pos, end_pos, length, color):
            center_x = (start_pos[0] + end_pos[0]) / 2; center_y = (start_pos[1] + end_pos[1]) / 2
            dx = end_pos[0] - start_pos[0]; dy = end_pos[1] - start_pos[1]; draw_length = math.hypot(dx, dy);
            if draw_length < 1: draw_length = 1
            angle = math.atan2(dy, dx); draw_rotated_rectangle(screen, color, (center_x, center_y), draw_length, self.limb_width, angle)
        draw_limb_segment(self.shoulder_pos, self.l_elbow_pos, self.upper_arm_length, self.arm_colors[0]); draw_limb_segment(self.l_elbow_pos, self.l_hand_pos, self.forearm_length, self.arm_colors[1])
        draw_limb_segment(self.shoulder_pos, self.r_elbow_pos, self.upper_arm_length, self.arm_colors[0]); draw_limb_segment(self.r_elbow_pos, self.r_hand_pos, self.forearm_length, self.arm_colors[1])
        draw_limb_segment(self.hip_pos, self.l_knee_pos, self.thigh_length, self.leg_colors[0]); draw_limb_segment(self.l_knee_pos, self.l_foot_pos, self.shin_length, self.leg_colors[1])
        draw_limb_segment(self.hip_pos, self.r_knee_pos, self.thigh_length, self.leg_colors[0]); draw_limb_segment(self.r_knee_pos, self.r_foot_pos, self.shin_length, self.leg_colors[1])

# --- Ball Class ---
class Ball:
    def __init__(self, x, y, radius): self.x = x; self.y = y; self.radius = radius; self.vx = 0; self.vy = 0; self.last_hit_by = None; self.rotation_angle = 0
    def apply_force(self, force_x, force_y, hitter='player'): self.vx += force_x; self.vy += force_y; self.last_hit_by = hitter
    def update(self, dt):
        self.rotation_angle += self.vx * 0.015; self.rotation_angle %= (2 * math.pi); self.vy += GRAVITY; self.vx *= BALL_FRICTION; self.x += self.vx; self.y += self.vy
        hit_ground = False
        if self.y + self.radius >= GROUND_Y:
            if self.vy >= 0: hit_ground = True
            self.y = GROUND_Y - self.radius; self.vy *= -BALL_BOUNCE; self.vx *= 0.9
            if abs(self.vy) < 1: self.vy = 0
        if self.x + self.radius >= SCREEN_WIDTH: self.x = SCREEN_WIDTH - self.radius; self.vx *= -BALL_BOUNCE * 0.8
        elif self.x - self.radius <= 0: self.x = self.radius; self.vx *= -BALL_BOUNCE * 0.8
        if abs(self.vx) < 0.1 and self.is_on_ground(): self.vx = 0
        return hit_ground
    def is_on_ground(self): return self.y + self.radius >= GROUND_Y - 0.5
    def draw(self, screen):
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
pygame.init(); screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ciao Kick!"); clock = pygame.time.Clock()
player1 = StickMan(SCREEN_WIDTH // 4, GROUND_Y, facing=1); player2 = StickMan(SCREEN_WIDTH * 3 // 4, GROUND_Y, facing=-1)
ball = Ball(SCREEN_WIDTH // 2, GROUND_Y - 20, 15)
font_large = pygame.font.Font(None, 50); font_medium = pygame.font.Font(None, 36); font_small = pygame.font.Font(None, 28)
font_timestamp = pygame.font.Font(None, 20); font_goal = pygame.font.Font(None, 80)

# --- Score & State Variables ---
player1_score = 0; player2_score = 0; goal_message_timer = 0; GOAL_MESSAGE_DURATION = 1.5
ball_was_on_ground = True; particles = [];
p1_can_headbutt = True; p2_can_headbutt = True
p1_body_collision_timer = 0; p2_body_collision_timer = 0
current_hit_count = 0 # Re-added for particle effect trigger

# --- Off-screen Arrow Function ---
def draw_offscreen_arrow(s, ball, p_pos): # p_pos unused
    ar_sz = 15; pad = 25; is_off = False; tx, ty = ball.x, ball.y; ax = max(pad, min(ball.x, SCREEN_WIDTH - pad)); ay = max(pad, min(ball.y, SCREEN_HEIGHT - pad))
    if ball.x < 0 or ball.x > SCREEN_WIDTH: ax = pad if ball.x < 0 else SCREEN_WIDTH - pad; is_off = True
    if ball.y < 0 or ball.y > SCREEN_HEIGHT: ay = pad if ball.y < 0 else SCREEN_HEIGHT - pad; is_off = True
    if not is_off: return
    ang = math.atan2(ty - ay, tx - ax); p1 = (ar_sz, 0); p2 = (-ar_sz / 2, -ar_sz / 2); p3 = (-ar_sz / 2, ar_sz / 2)
    cos_a, sin_a = math.cos(ang), math.sin(ang); p1r = (p1[0] * cos_a - p1[1] * sin_a, p1[0] * sin_a + p1[1] * cos_a); p2r = (p2[0] * cos_a - p2[1] * sin_a, p2[0] * sin_a + p2[1] * cos_a); p3r = (p3[0] * cos_a - p3[1] * sin_a, p3[0] * sin_a + p3[1] * cos_a)
    pts = [(ax + p1r[0], ay + p1r[1]), (ax + p2r[0], ay + p2r[1]), (ax + p3r[0], ay + p3r[1])]; pygame.draw.polygon(s, ARROW_RED, [(int(p[0]), int(p[1])) for p in pts])

# --- Reset Function ---
def reset_after_goal():
    global ball_was_on_ground, current_hit_count
    ball.x = SCREEN_WIDTH // 2; ball.y = SCREEN_HEIGHT // 3; ball.vx = 0; ball.vy = 0
    player1.x = SCREEN_WIDTH // 4; player1.y = GROUND_Y; player1.vx = 0; player1.vy = 0; player1.is_kicking = False; player1.is_charging = False; player1.facing_direction = 1
    player2.x = SCREEN_WIDTH * 3 // 4; player2.y = GROUND_Y; player2.vx = 0; player2.vy = 0; player2.is_kicking = False; player2.is_charging = False; player2.facing_direction = -1
    current_hit_count = 0; ball_was_on_ground = False

# --- Collision Handling Function ---
def handle_player_ball_collisions(player, ball, can_headbutt, body_collision_timer, is_ball_airborne):
    global current_hit_count
    kick_performed = False; headbutt_performed = False; score_increase = False; kick_pt = None
    # 1. Kick
    local_kick_point = player.get_kick_impact_point()
    if local_kick_point:
        dist_x = local_kick_point[0] - ball.x; dist_y = local_kick_point[1] - ball.y; dist_sq = dist_x**2 + dist_y**2
        eff_kick_rad = KICK_RADIUS_NORMAL + (KICK_RADIUS_FALLING_BONUS if ball.vy > BALL_FALLING_VELOCITY_THRESHOLD else 0)
        if dist_sq < (ball.radius + eff_kick_rad)**2:
             progress = player.kick_timer / player.kick_duration
             if 0.25 < progress < 0.6:
                 kick_x_base = BASE_KICK_FORCE_X if player.kick_side == 'right' else -BASE_KICK_FORCE_X
                 kick_x = kick_x_base * KICK_FORCE_LEVEL # Use fixed force
                 kick_y = BASE_KICK_FORCE_Y * KICK_FORCE_LEVEL # Use fixed force
                 if player.vy < 0: kick_y += player.vy * 0.3
                 ball.apply_force(kick_x, kick_y, hitter=player); kick_performed = True; kick_pt = local_kick_point
                 if is_ball_airborne: current_hit_count += 1; score_increase = True # Increment combo count
    # 2. Headbutt
    head_pos, head_radius = player.get_head_position_radius(); dist_x_head = ball.x - head_pos[0]; dist_y_head = ball.y - head_pos[1]
    dist_head_sq = dist_x_head**2 + dist_y_head**2; headbutt_cooldown_just_applied = False
    if dist_head_sq < (ball.radius + head_radius)**2:
        if can_headbutt:
            force_y = -HEADBUTT_UP_FORCE
            if player.vy < 0: force_y -= abs(player.vy) * HEADBUTT_VY_MULTIPLIER
            force_x = player.vx * HEADBUTT_PLAYER_VX_FACTOR - dist_x_head * HEADBUTT_POS_X_FACTOR
            ball.apply_force(force_x, force_y, hitter=player); headbutt_cooldown_just_applied = True; headbutt_performed = True
            if is_ball_airborne: current_hit_count += 1; score_increase = True # Increment combo count
    new_can_headbutt = can_headbutt
    if headbutt_cooldown_just_applied: new_can_headbutt = False
    elif not new_can_headbutt and dist_head_sq > (ball.radius + head_radius + 15)**2: new_can_headbutt = True
    # 3. Body Collision
    new_body_collision_timer = body_collision_timer
    if not kick_performed and not headbutt_performed and body_collision_timer == 0:
        player_rect = player.get_body_rect()
        closest_x = max(player_rect.left, min(ball.x, player_rect.right)); closest_y = max(player_rect.top, min(ball.y, player_rect.bottom))
        delta_x = ball.x - closest_x; delta_y = ball.y - closest_y; dist_sq_body = delta_x**2 + delta_y**2
        if dist_sq_body < ball.radius**2 and dist_sq_body > 0:
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
        elif dist_sq_body == 0:
             ball.y = player_rect.top - ball.radius - 0.1
             if ball.vy > 0:
                 ball.vy *= -PLAYER_BODY_BOUNCE
                 new_body_collision_timer = PLAYER_BODY_COLLISION_FRAMES
    return score_increase, new_can_headbutt, new_body_collision_timer, kick_pt

# --- Main Game Loop ---
running = True
while running:
    dt = clock.tick(FPS) / 1000.0; dt = min(dt, 0.1)
    if p1_body_collision_timer > 0: p1_body_collision_timer -= 1
    if p2_body_collision_timer > 0: p2_body_collision_timer -= 1
    if goal_message_timer > 0: goal_message_timer -= dt

    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT: player1.move(-1)
            elif event.key == pygame.K_RIGHT: player1.move(1)
            elif event.key == pygame.K_UP: player1.jump()
            elif event.key == pygame.K_DOWN: player1.start_kick(ball.x) # P1 Kick
            elif event.key == pygame.K_a: player2.move(-1)
            elif event.key == pygame.K_d: player2.move(1)
            elif event.key == pygame.K_w: player2.jump()
            elif event.key == pygame.K_s: player2.start_kick(ball.x) # P2 Kick
            elif event.key == pygame.K_ESCAPE: running = False
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT and player1.vx < 0: player1.stop_move()
            elif event.key == pygame.K_RIGHT and player1.vx > 0: player1.stop_move()
            elif event.key == pygame.K_a and player2.vx < 0: player2.stop_move()
            elif event.key == pygame.K_d and player2.vx > 0: player2.stop_move()

    # Updates
    player1.update(dt); player2.update(dt); ball_hit_ground_this_frame = ball.update(dt); particles = [p for p in particles if p.update(dt)]

    # Player-Player Collision
    p1_rect = player1.get_body_rect(); p2_rect = player2.get_body_rect()
    if p1_rect.colliderect(p2_rect):
        dx = player2.x - player1.x; overlap = (p1_rect.width / 2 + p2_rect.width / 2) - abs(dx)
        if overlap > 0:
            push = overlap / 2 + 0.1;
            if dx > 0: player1.x -= push; player2.x += push
            else: player1.x += push; player2.x -= push
            player1.vx *= -0.1; player2.vx *= -0.1

    # Goal Detection
    goal_scored = False
    if ball.x + ball.radius >= GOAL_LINE_X_RIGHT and ball.y > GOAL_Y_POS: player1_score += 1; goal_message_timer = GOAL_MESSAGE_DURATION; goal_scored = True; print(f"GOAL! Player 1 Score: {player1_score}")
    elif ball.x - ball.radius <= GOAL_LINE_X_LEFT and ball.y > GOAL_Y_POS: player2_score += 1; goal_message_timer = GOAL_MESSAGE_DURATION; goal_scored = True; print(f"GOAL! Player 2 Score: {player2_score}")
    if goal_scored: reset_after_goal(); continue

    # Combo Score Reset Logic
    is_ball_airborne = not ball.is_on_ground()
    if not is_ball_airborne and ball_hit_ground_this_frame and not ball_was_on_ground:
        current_hit_count = 0
    ball_was_on_ground = not is_ball_airborne

    # --- Player-Ball Collisions ---
    p1_hit, p1_can_headbutt, p1_body_collision_timer, p1_kick_pt = handle_player_ball_collisions(player1, ball, p1_can_headbutt, p1_body_collision_timer, is_ball_airborne)
    p2_hit, p2_can_headbutt, p2_body_collision_timer, p2_kick_pt = handle_player_ball_collisions(player2, ball, p2_can_headbutt, p2_body_collision_timer, is_ball_airborne)
    score_increased_this_frame = p1_hit or p2_hit
    last_kick_point = p1_kick_pt if p1_kick_pt else p2_kick_pt

    # Trigger Star Explosion (Using current_hit_count)
    if score_increased_this_frame and last_kick_point and current_hit_count > 0 and current_hit_count % 5 == 0:
        num_kick_particles = PARTICLE_COUNT // 2
        for _ in range(num_kick_particles): particle_x = last_kick_point[0] + random.uniform(-5, 5); particle_y = last_kick_point[1] + random.uniform(-5, 5); particles.append(Particle(particle_x, particle_y))

    # --- Drawing ---
    screen.fill(SKY_BLUE); pygame.draw.rect(screen, GRASS_GREEN, (0, GROUND_Y, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y))
    draw_goal_isometric(screen, GOAL_LINE_X_LEFT, GOAL_Y_POS, GOAL_HEIGHT, GOAL_DEPTH_X, GOAL_DEPTH_Y, GOAL_POST_THICKNESS, GOAL_COLOR, GOAL_NET_COLOR)
    draw_goal_isometric(screen, GOAL_LINE_X_RIGHT, GOAL_Y_POS, GOAL_HEIGHT, GOAL_DEPTH_X, GOAL_DEPTH_Y, GOAL_POST_THICKNESS, GOAL_COLOR, GOAL_NET_COLOR)
    for p in particles: p.draw(screen)
    player1.draw(screen); player2.draw(screen); ball.draw(screen); draw_offscreen_arrow(screen, ball, None)
    # Scores
    score_text = f"{player2_score} - {player1_score}"; score_surf = font_large.render(score_text, True, TEXT_COLOR); score_rect = score_surf.get_rect(centerx=SCREEN_WIDTH // 2, top=10); screen.blit(score_surf, score_rect)
    # Draw GOAL! Message
    if goal_message_timer > 0:
        goal_text_surf = font_goal.render("GOAL!", True, ITALY_RED); goal_text_rect = goal_text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        bg_rect = goal_text_rect.inflate(20, 10); bg_surf = pygame.Surface(bg_rect.size, pygame.SRCALPHA); bg_surf.fill((WHITE[0], WHITE[1], WHITE[2], 180)); screen.blit(bg_surf, bg_rect.topleft); screen.blit(goal_text_surf, goal_text_rect)
    # Cooldown Indicators
    if not p1_can_headbutt: cooldown_color = (255, 0, 0, 180); cooldown_radius = 5; head_x, head_y = player1.head_pos; indicator_x = int(head_x); indicator_y = int(head_y - player1.head_radius - cooldown_radius - 2); temp_surf = pygame.Surface((cooldown_radius*2, cooldown_radius*2), pygame.SRCALPHA); pygame.draw.circle(temp_surf, cooldown_color, (cooldown_radius, cooldown_radius), cooldown_radius); screen.blit(temp_surf, (indicator_x - cooldown_radius, indicator_y - cooldown_radius))
    if not p2_can_headbutt: cooldown_color = (0, 0, 255, 180); cooldown_radius = 5; head_x, head_y = player2.head_pos; indicator_x = int(head_x); indicator_y = int(head_y - player2.head_radius - cooldown_radius - 2); temp_surf = pygame.Surface((cooldown_radius*2, cooldown_radius*2), pygame.SRCALPHA); pygame.draw.circle(temp_surf, cooldown_color, (cooldown_radius, cooldown_radius), cooldown_radius); screen.blit(temp_surf, (indicator_x - cooldown_radius, indicator_y - cooldown_radius))
    # Timestamp
    timestamp_surf = font_timestamp.render(GENERATION_TIMESTAMP, True, TEXT_COLOR); timestamp_rect = timestamp_surf.get_rect(bottomright=(SCREEN_WIDTH - 10, SCREEN_HEIGHT - 10)); screen.blit(timestamp_surf, timestamp_rect)
    pygame.display.flip()

# Cleanup
pygame.quit(); sys.exit()