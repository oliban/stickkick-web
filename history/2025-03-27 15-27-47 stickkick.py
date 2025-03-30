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
DEBUG_BLUE = (0, 0, 255 STAR_YELLOW = (255, 255, 100); STAR_ORANGE = (255, 180, 0)
DEBUG_BLUE = (0, 0, 255)
GOAL_COLOR = (220, 220, 220) # Lighter grey for goal posts
GOAL_NET_COLOR = (180, 180, 190) # Slightly darker grey for net
DEBUG_KICK_ANGLES = False

# Physics
GRAVITY = 0.5)
GOAL_COLOR = (200, 200, 210) # Light grey for goals
DEBUG_KICK_ANGLES = False

# Physics
GRAVITY = 0.5; PLAYER_SPEED = 4; JUMP_POWER = -11; PLAYER_SPEED = 4; JUMP_POWER = -11
BASE_KICK_FORCE_X = 14; BASE_KICK_FORCE_Y = -13; CHARGE_RATE = 1.5
MAX_CHARGE_POWER = 2.0;
BASE_KICK_FORCE_X = 14; BASE_KICK_FORCE_Y = -13; CHARGE_RATE = 1.5
MAX_CHARGE_POWER = 2.0; MIN_CHARGE_POWER = 0.5
HEADBUTT_UP MIN_CHARGE_POWER = 0.5
HEADBUTT_UP_FORCE = 15.0; HEADBUTT_VY_MULTIPLIER = 1.2
HEADBUTT_PLAYER_VX_FACTOR = 0.6; HEADBUTT_POS_X_FACTOR = 0.15
BALL_FRICTION = 0.99; BALL_BOUNCE = 0.7; GROUND_Y = SCREEN_HEIGHT - 50

# Collision Specific
PLAYER_BODY_BOUNCE = 0.65; PLAYER_VEL_TRANSFER = 0_FORCE = 15.0; HEADBUTT_VY_MULTIPLIER = 1.2
HEADBUTT_PLAYER_VX_FACTOR = 0.6; HEADBUTT_POS_X_FACTOR = 0.15
BALL_FRICTION = 0.9.25
MIN_BODY_BOUNCE_VEL = 1.5; PLAYER_BODY_COLLISION_FRAMES = 4

# Kick Collision Tweak
KICK_RADIUS_NORMAL = 13; KICK_RADIUS_FALLING_BONUS = 5
BALL9; BALL_BOUNCE = 0.7; GROUND_Y = SCREEN_HEIGHT - 50

# Collision Specific
PLAYER_BODY_BOUNCE = 0.65; PLAYER_VEL_TRANSFER = 0.25
MIN_BODY_BOUNCE_VEL = 1_FALLING_VELOCITY_THRESHOLD = 5

# --- Isometric Goal Constants ---
GOAL_HEIGHT = 110 # Visual height
GOAL_POST_THICKNESS = 3 # Line thickness for posts/net
GOAL_Y_POS = GROUND_Y - GOAL_HEIGHT #.5; PLAYER_BODY_COLLISION_FRAMES = 4

# Kick Collision Tweak
KICK_RADIUS_NORMAL = 13; KICK_RADIUS_FALLING_BONUS = 5
BALL_FALLING_VELOCITY_THRESHOLD = 5

# --- Goal Constants Y-coordinate of the crossbar
GOAL_DEPTH_X = 30 # How far back the goal goes horizontally
GOAL_DEPTH_Y = -15 # How far *up* the back bottom post starts relative to front
# Define precise goal line X coordinates
GOAL_LINE_X (Revised for Isometric Look) ---
GOAL_HEIGHT = 120
GOAL_POST_THICKNESS = 6 # Thinner posts
GOAL_Y_POS = GROUND_Y - GOAL_HEIGHT
GOAL_DEPTH = 40 # How far "back" the goal_LEFT = GOAL_POST_THICKNESS // 2
GOAL_LINE_X_RIGHT = SCREEN_WIDTH - (GOAL_POST_THICKNESS // 2)


# Animation (Constants remain the same)
WALK_CYCLE_SPEED = 0.25; BODY goes visually
GOAL_SIDE_OFFSET_X = 25 # Horizontal offset for back posts
GOAL_SIDE_OFFSET_Y = 15 # Vertical offset (downwards) for back posts (creates perspective)

# Animation
WALK_CYCLE_SPEED = 0.25;_WOBBLE_AMOUNT = 0
RUN_UPPER_ARM_SWING = math.pi / 6.0; RUN_UPPER_ARM_WOBBLE_AMP = 0; RUN_UPPER_ARM_WOBBLE_SPEED = 0
RUN_FOREARM_SWING = math.pi / 5.0; RUN_FOREARM_WOBBLE_AMP = 0; RUN_FOREARM_WOBBLE_SPEED = 0
RUN_FOREARM_OFFSET_FACTOR = 0.1; JUMP_UPPER_ARM_ BODY_WOBBLE_AMOUNT = 0
RUN_UPPER_ARM_SWING = math.pi / 6.0; RUN_UPPER_ARM_WOBBLE_AMP = 0; RUN_UPPER_ARM_WOBBLE_SPEED = 0
RUN_BASE = -math.pi * 0.1; JUMP_UPPER_ARM_WOBBLE_AMP = 0
JUMP_UPPER_ARM_WOBBLE_SPEED = 0; JUMP_UPPER_ARM_VY_FACTOR = 0.01;FOREARM_SWING = math.pi / 5.0; RUN_FOREARM_WOBBLE_AMP = 0; RUN_FOREARM_WOBBLE_SPEED = 0
RUN_FOREARM_OFFSET_FACTOR = 0.1; JUMP_UPPER_ARM JUMP_FOREARM_BASE = math.pi * 0.1
JUMP_FOREARM_WOBBLE_AMP = 0; JUMP_FOREARM_WOBBLE_SPEED = 0
LEG_THIGH_SWING = math.pi / 7.0; LEG_SHIN_BEND_WALK = math.pi / 8.0; LEG_SHIN_BEND_SHIFT = math.pi / 2.5
KICK_THIGH_WINDUP_ANGLE = -math.pi / 4.5; KICK__BASE = -math.pi * 0.1; JUMP_UPPER_ARM_WOBBLE_AMP = 0
JUMP_UPPER_ARM_WOBBLE_SPEED = 0; JUMP_UPPER_ARM_VY_FACTOR = 0.01; JUMP_FOREARM_BASE = math.pi * 0.1
JUMP_FOREARM_WOBBLE_AMP = 0; JUMP_FOREARM_WOBBLE_SPEED = 0
LEG_THIGH_SWING = math.pi / 7.0;THIGH_FOLLOW_ANGLE = math.pi * 0.7
KICK_SHIN_WINDUP_ANGLE = math.pi * 0.75; KICK_SHIN_IMPACT_ANGLE = -math.pi * 0.05
KICK_SH LEG_SHIN_BEND_WALK = math.pi / 8.0; LEG_SHIN_BEND_SHIFT = math.pi / 2.5
KICK_THIGH_WINDUP_ANGLE = -math.pi / 4.5; KICK_IN_FOLLOW_ANGLE = math.pi * 0.5
JUMP_THIGH_TUCK = math.pi * 0.1; JUMP_SHIN_TUCK = math.pi * 0.2

# Star Explosion
PARTICLE_LIFESPAN = 1.0; PARTICLE_SPEED = 150; PARTICLE_COUNT = 12; PARTICLE_SIZE = 6

# --- Helper Functions ---
def draw_polygon_shape(surface, color, center, size, sides, angle=0, width=0):
    THIGH_FOLLOW_ANGLE = math.pi * 0.7
KICK_SHIN_WINDUP_ANGLE = math.pi * 0.75; KICK_SHIN_IMPACT_ANGLE = -math.pi * 0.05
KICK_SHpoints = []
    for i in range(sides):
        offset_angle = math.pi / sides if sides % 2 == 0 else math.pi / 2.0
        theta = offset_angle + (2.0 * math.pi * i / sides) + angle
        IN_FOLLOW_ANGLE = math.pi * 0.5
JUMP_THIGH_TUCK = math.pi * 0.1; JUMP_SHIN_TUCK = math.pi * 0.2

# Star Explosion
PARTICLE_LIFESPAN = x = center[0] + size * math.cos(theta); y = center[1] + size * math.sin(theta)
        points.append((int(x), int(y)))
    pygame.draw.polygon(surface, color, points, width)
def draw_1.0; PARTICLE_SPEED = 150; PARTICLE_COUNT = 12; PARTICLE_SIZE = 6

# --- Helper Functions ---
def draw_polygon_shape(surface, color, center, size, sides, angle=0, width=0):
    pentagon(surface, color, center, size, angle=0, width=0): draw_polygon_shape(surface, color, center, size, 5, angle, width)
def draw_hexagon(surface, color, center, size, angle=0, width=0): draw_points = [];
    for i in range(sides): offset_angle = math.pi / sides if sides % 2 == 0 else math.pi / 2.0; theta = offset_angle + (2.0 * math.pi * i / sides) + angle; x = centerpolygon_shape(surface, color, center, size, 6, angle, width)
def normalize(v): mag_sq = v[0]**2 + v[1]**2; mag = math.sqrt(mag_sq) if mag_sq > 0 else 0; return (v[0]/mag, v[1]/mag) if mag > 0 else (0,0)
def draw_rotated_rectangle(surface, color, rect_center, width, height, angle_rad):
    half_w, half_h = width / 2,[0] + size * math.cos(theta); y = center[1] + size * math.sin(theta); points.append((int(x), int(y)))
    pygame.draw.polygon(surface, color, points, width)
def draw_pentagon(surface, height / 2; corners = [(-half_w, -half_h), ( half_w, -half_h), ( half_w,  half_h), (-half_w,  half_h)]
    cos_a, sin_a = math.cos(angle_ color, center, size, angle=0, width=0): draw_polygon_shape(surface, color, center, size, 5, angle, width)
def draw_hexagon(surface, color, center, size, angle=0, width=0): draw_polygon_shape(surfacerad), math.sin(angle_rad); rotated_corners = []
    for x, y in corners: x_rot = x * cos_a - y * sin_a; y_rot = x * sin_a + y * cos_a; rotated_corners.append((rect_, color, center, size, 6, angle, width)
def normalize(v): mag_sq = v[0]**2 + v[1]**2; mag = math.sqrt(mag_sq) if mag_sq > 0 else 0; return (v[0center[0] + x_rot, rect_center[1] + y_rot))
    pygame.draw.polygon(surface, color, rotated_corners, 0); pygame.draw.polygon(surface, BLACK, rotated_corners, 1)

# --- New Helper: Draw Isometric Goal]/mag, v[1]/mag) if mag > 0 else (0,0)
def draw_rotated_rectangle(surface, color, rect_center, width, height, angle_rad):
    half_w, half_h = width / 2, height / 2; corners = [ ---
def draw_goal_isometric(surface, goal_line_x, goal_y, goal_height, depth_x, depth_y, thickness, post_color, net_color):
    """Draws a goal with an isometric perspective using lines."""
    is_left_goal = goal_(-half_w, -half_h), ( half_w, -half_h), ( half_w,  half_h), (-half_w,  half_h)]
    cos_a, sin_a = math.cos(angle_rad), math.sin(angle_line_x < SCREEN_WIDTH / 2

    # Calculate Front Coordinates
    front_top = (goal_line_x, goal_y)
    front_bottom = (goal_line_x, goal_y + goal_height)

    # Calculate Back Coordinates (Offset based on siderad); rotated_corners = []
    for x, y in corners: x_rot = x * cos_a - y * sin_a; y_rot = x * sin_a + y * cos_a; rotated_corners.append((rect_center[0] + x_rot, rect_)
    back_x = goal_line_x + depth_x if is_left_goal else goal_line_x - depth_x
    back_top_y = goal_y + depth_y
    back_bottom_y = goal_y + goal_height + depth_ycenter[1] + y_rot))
    pygame.draw.polygon(surface, color, rotated_corners, 0); pygame.draw.polygon(surface, BLACK, rotated_corners, 1)

# --- Modified Draw Goal Function ---
def draw_goal(surface, goal_line
    back_top = (back_x, back_top_y)
    back_bottom = (back_x, back_bottom_y)

    # Draw Back Structure First (usually appears behind)
    pygame.draw.line(surface, post_color, back_top, back_bottom, thickness) # Back Post
    pygame.draw.line(surface, post_color, back_top, front_top, thickness)   # Top Side Bar
    pygame.draw.line(surface, post_color, back_bottom, front_bottom, thickness) # Bottom Side_x, goal_y, goal_height, depth, offset_x, offset_y, thickness, color):
    """Draws an isometric-style goal."""
    line_width = max(1, thickness // 2) # Use lines for perspective

    # Front posts and crossbar
     Bar

    # Draw Front Structure
    pygame.draw.line(surface, post_color, front_top, front_bottom, thickness) # Front Post
    # Crossbar is implicitly drawn by the connection to back_top

    # Draw Net Lines (Simple version)
    # Back verticalfront_top = goal_y
    front_bottom = goal_y + goal_height
    front_left_x = goal_line_x
    front_right_x = goal_line_x # For simplicity, assume posts are on the line

    # Calculate back corners based on offsets lines
    num_net_lines = 5
    for i in range(1, num_net_lines):
        y_lerp = i / num_net_lines
        top_y = back_top[1] + (back_bottom[1] - back_top[1])
    # Offset_x is positive for right goal, negative for left goal
    back_left_x = front_left_x + offset_x
    back_right_x = front_right_x + offset_x
    back_top_y = front_top + offset_y
     * y_lerp
        # Draw vertical lines on the back plane
        pygame.draw.line(surface, net_color, (back_top[0], top_y), (back_bottom[0], back_bottom_y), 1) #This seems wrong, should be vertical
        #back_bottom_y = front_bottom + offset_y

    # Define corner points
    ftl = (front_left_x, front_top)
    fbl = (front_left_x, front_bottom)
    # Note: Using goal_line_x directly for front Corrected: Draw vertical lines on the back plane
        pygame.draw.line(surface, net_color, (back_x, back_top_y + (back_bottom_y - back_top_y) * y_lerp), (back_x, back_bottom_y), 1) # Simplified vertical back net

    # Side net lines (diagonal)
    pygame.draw.line(surface, net_color, front_top, back_bottom, 1)
    pygame.draw.line(surface, net_color, front_bottom, back_top, posts
    btr = (back_right_x, back_top_y) # Back top right (relative to front right)
    bbr = (back_right_x, back_bottom_y) # Back bottom right

    # Draw using lines (aa for smoother look)
    # 1)
    # Add a couple more diagonals for density
    mid_front_y = (front_top[1] + front_bottom[1]) / 2
    mid_back_y = (back_top[1] + back_bottom[1]) / 2
    pygame.draw.line(surface, net_color, (front_top[0], mid_front_y), back_top, 1)
    pygame.draw.line(surface, net_color, (front_top[0], mid_front_y), back_bottom, 1) Front Frame (Posts slightly inside goal line for visual)
    pygame.draw.aaline(surface, color, (goal_line_x - thickness//2, front_top), (goal_line_x - thickness//2, front_bottom)) # Left Post
    pygame.draw.aaline


# --- Particle Class ---
class Particle:
    def __init__(self, x, y):
        self.x = x; self.y = y; angle = random.uniform(0, 2 * math.pi); speed = random.uniform(PARTICLE_SPEED * 0.(surface, color, (goal_line_x + thickness//2, front_top), (goal_line_x + thickness//2, front_bottom)) # Right Post (tiny overlap)
    pygame.draw.aaline(surface, color, (goal_line_x - thickness//25, PARTICLE_SPEED * 1.5)
        self.vx = math.cos(angle) * speed; self.vy = math.sin(angle) * speed; self.lifespan = PARTICLE_LIFESPAN
        self.start_life = self.lifespan; self.size = PARTICLE_SIZE; self.color = random.choice([STAR_YELLOW, STAR_ORANGE, WHITE])
    def update(self, dt):
        self.x += self.vx * dt; self.y += self.vy * dt; self.vy +=, front_top), (goal_line_x + thickness//2, front_top))       # Crossbar

    # Back frame (Use calculated back points) - needs adjustment based on side
    # Correct back top left/right needed
    back_top_left_x = front_left GRAVITY * 20 * dt; self.lifespan -= dt; self.size = PARTICLE_SIZE * (self.lifespan / self.start_life)
        return self.lifespan > 0 and self.size > 1
    def draw(self,_x + offset_x
    back_top_right_x = front_left_x + offset_x # Assume goal width is negligible for this style

    btl = (back_top_left_x, back_top_y)
    bbl = (back_top_left_ screen):
        if self.size > 0: pygame.draw.rect(screen, self.color, (int(self.x - self.size/2), int(self.y - self.size/2), int(self.size), int(self.size)))

# --- Stick Man Class (Ciao) ---
class StickMan:
    def __init__(self, x, y):
        self.x = x; self.y = y; self.base_y = y; self.width = 20; self.height = 80; self.x, back_bottom_y)

    # Connecting Lines (Perspective)
    pygame.draw.aaline(surface, color, (goal_line_x - thickness//2, front_top), btl) # Top Left connector
    pygame.draw.aaline(surface, color, (goal_vx = 0; self.vy = 0; self.is_jumping = False; self.is_kicking = False
        self.is_charging = False; self.kick_timer = 0; self.kick_duration = 20; self.charge_power = MIN_CHARGE_POWER; self.kick_charge_level = MIN_CHARGE_POWER
        self.walk_cycle_timer = 0.0; self.kick_side = 'right'; self.head_radius = 12; self.torso_length = 36; selfline_x + thickness//2, front_top), btl) # Top Right connector (Connects to same back point for simple look)
    pygame.draw.aaline(surface, color, (goal_line_x - thickness//2, front_bottom), bbl) # Bottom Left connector
    .limb_width = 10; self.upper_arm_length = 12
        self.forearm_length = 12; self.thigh_length = 14; self.shin_length = 14; self.torso_colors = [ITALY# Optional: Bottom right connector if you want a base bar
    # pygame.draw.aaline(surface, color, (goal_line_x + thickness//2, front_bottom), bbl)

    # Back Top Bar
    # pygame.draw.aaline(surface, color, b_GREEN, ITALY_WHITE, ITALY_RED]
        self.arm_colors = [ITALY_RED, ITALY_GREEN]; self.leg_colors = [ITALY_WHITE, ITALY_RED]; self.l_upper_arm_angle = 0; self.r_upper_arm_angle = 0; self.l_forearm_angle = 0
        self.r_forearm_angle = 0; self.l_thigh_angle = 0; self.r_thigh_angle = 0; self.l_shin_angle = 0;tl, btr) # If btr was calculated differently for width

    # Back Ground Line
    pygame.draw.aaline(surface, color, bbl, (bbl[0]+thickness, bbl[1]) ) # Short back line


# --- Particle Class ---
class Particle: self.r_shin_angle = 0; self.head_pos = (0, 0)
        self.neck_pos = (0, 0); self.hip_pos = (0, 0); self.shoulder_pos = (0, 0); self.l_elbow_pos = (0, 0); self.r_elbow_pos = (0, 0); self.l_hand_pos = (0, 0)
        self.r_hand_pos = (0, 0); self.l_knee_pos = (0, 
    def __init__(self, x, y):
        self.x = x; self.y = y; angle = random.uniform(0, 2 * math.pi); speed = random.uniform(PARTICLE_SPEED * 0.5, PARTICLE_SPEED * 1.5)0); self.r_knee_pos = (0, 0); self.l_foot_pos = (0, 0); self.r_foot_pos = (0, 0); self.body_rect = pygame.Rect(0,0,0,0)
    def move(
        self.vx = math.cos(angle) * speed; self.vy = math.sin(angle) * speed; self.lifespan = PARTICLE_LIFESPAN
        self.start_life = self.lifespan; self.size = PARTICLE_SIZE;self, direction):
        if not self.is_kicking: self.vx = direction * PLAYER_SPEED
    def stop_move(self): self.vx = 0
    def jump(self):
        if not self.is_jumping: self.is_jumping = True; self.color = random.choice([STAR_YELLOW, STAR_ORANGE, WHITE])
    def update(self, dt):
        self.x += self.vx * dt; self.y += self.vy * dt; self.vy += GRAVITY * 20 * dt; self self.vy = JUMP_POWER; self.walk_cycle_timer = 0
        if self.is_charging: self.is_charging = False; self.charge_power = MIN_CHARGE_POWER
    def start_charge(self):
        if not self.is_.lifespan -= dt; self.size = PARTICLE_SIZE * (self.lifespan / self.start_life)
        return self.lifespan > 0 and self.size > 1
    def draw(self, screen):
        if self.size > kicking and not self.is_charging: self.is_charging = True; self.charge_power = MIN_CHARGE_POWER
    def release_charge_and_kick(self, ball_x):
        if self.is_charging: self.is_charging = False; self0: pygame.draw.rect(screen, self.color, (int(self.x - self.size/2), int(self.y - self.size/2), int(self.size), int(self.size)))

# --- Stick Man Class (Ciao) ---
class Stick.kick_charge_level = self.charge_power; self.charge_power = MIN_CHARGE_POWER; self.vx = 0; self.kick_side = 'left' if ball_x < self.x else 'right'; self.start_kick()
    def start_kick(self):
        if not self.is_kicking: self.is_kicking = True; self.kick_timer = 0; self.vx = 0
    def update(self, dt):
        time_ms = pygame.time.get_ticks()
        Man:
    def __init__(self, x, y):
        self.x = x; self.y = y; self.base_y = y; self.width = 20; self.height = 80; self.vx = 0; self.vy = 0; selfif self.is_charging: self.charge_power = min(self.charge_power + CHARGE_RATE * dt, MAX_CHARGE_POWER)
        if not self.is_kicking: self.x += self.vx; self.x = max(self.limb_width.is_jumping = False; self.is_kicking = False
        self.is_charging = False; self.kick_timer = 0; self.kick_duration = 20; self.charge_power = MIN_CHARGE_POWER; self.kick_charge_level = / 2, min(self.x, SCREEN_WIDTH - self.limb_width / 2))
        if self.y < self.base_y or self.vy < 0: self.vy += GRAVITY; self.y += self.vy
        is_walking_on MIN_CHARGE_POWER
        self.walk_cycle_timer = 0.0; self.kick_side = 'right'; self.head_radius = 12; self.torso_length = 36; self.limb_width = 10; self.upper__ground = abs(self.vx) > 0 and not self.is_jumping and not self.is_kicking
        if is_walking_on_ground: self.walk_cycle_timer += WALK_CYCLE_SPEED
        elif not self.is_jumping and not self.is_karm_length = 12
        self.forearm_length = 12; self.thigh_length = 14; self.shin_length = 14; self.torso_colors = [ITALY_GREEN, ITALY_WHITE, ITALY_RED]
        icking: self.walk_cycle_timer *= 0.9
        if abs(self.walk_cycle_timer) < 0.1: self.walk_cycle_timer = 0
        if self.is_kicking:
            self.walk_cycle_timer = self.arm_colors = [ITALY_RED, ITALY_GREEN]; self.leg_colors = [ITALY_WHITE, ITALY_RED]; self.l_upper_arm_angle = 0; self.r_upper_arm_angle = 0; self.l_forearm0; self.kick_timer += 1; progress = min(self.kick_timer / self.kick_duration, 1.0)
            windup_end = 0.20; impact_start = 0.25; impact_end = 0.50; follow_end = 1.0
            if progress < windup_end: thigh_prog_angle = KICK_THIGH_WINDUP_ANGLE * (progress / windup_end)
            elif progress < impact_end: impact_progress = (progress - windup_end)_angle = 0
        self.r_forearm_angle = 0; self.l_thigh_angle = 0; self.r_thigh_angle = 0; self.l_shin_angle = 0; self.r_shin_angle = 0 / (impact_end - windup_end); thigh_prog_angle = KICK_THIGH_WINDUP_ANGLE + (KICK_THIGH_FOLLOW_ANGLE - KICK_THIGH_WINDUP_ANGLE) * impact_progress
            else: follow_progress =; self.head_pos = (0, 0)
        self.neck_pos = (0, 0); self.hip_pos = (0, 0); self.shoulder_pos = (0, 0); self.l_elbow_pos = (0, 0); (progress - impact_end) / (follow_end - impact_end); ease_out_factor = 1.0 - follow_progress**1.5; thigh_prog_angle = KICK_THIGH_FOLLOW_ANGLE * ease_out_factor
            if progress < impact_start: self.r_elbow_pos = (0, 0); self.l_hand_pos = (0, 0)
        self.r_hand_pos = (0, 0); self.l_knee_pos = (0, 0); self.r_knee_ shin_prog_angle = KICK_SHIN_WINDUP_ANGLE * (progress / impact_start)
            elif progress < impact_end: impact_progress = (progress - impact_start) / (impact_end - impact_start); ease_in_factor = impact_progress ** 2pos = (0, 0); self.l_foot_pos = (0, 0); self.r_foot_pos = (0, 0); self.body_rect = pygame.Rect(0,0,0,0)
    def move(self, direction):
        if not; shin_prog_angle = KICK_SHIN_WINDUP_ANGLE + (KICK_SHIN_IMPACT_ANGLE - KICK_SHIN_WINDUP_ANGLE) * ease_in_factor
            else: follow_progress = (progress - impact_end) self.is_kicking: self.vx = direction * PLAYER_SPEED
    def stop_move(self): self.vx = 0
    def jump(self):
        if not self.is_jumping: self.is_jumping = True; self.vy = JUMP_POWER / (follow_end - impact_end); shin_prog_angle = KICK_SHIN_IMPACT_ANGLE + (KICK_SHIN_FOLLOW_ANGLE - KICK_SHIN_IMPACT_ANGLE) * follow_progress
            if DEBUG_KICK_ANGLES: print(f; self.walk_cycle_timer = 0
        if self.is_charging: self.is_charging = False; self.charge_power = MIN_CHARGE_POWER
    def start_charge(self):
        if not self.is_kicking and not self.is_"Kick Prog: {progress:.2f}, Thigh: {math.degrees(thigh_prog_angle):.1f}, Shin: {math.degrees(shin_prog_angle):.1f}")
            if self.kick_side == 'right': self.r_thigh_angle = thigh_prog_angle; self.r_shin_angle = shin_prog_angle; self.l_thigh_angle = -thigh_prog_angle * 0.3; self.l_shin_angle = 0.3
            else: self.l_thcharging: self.is_charging = True; self.charge_power = MIN_CHARGE_POWER
    def release_charge_and_kick(self, ball_x):
        if self.is_charging: self.is_charging = False; self.kick_charge_level = self.charge_power; self.charge_power = MIN_CHARGE_POWER; self.vx = 0; self.kick_side = 'left' if ball_x < self.x else 'right'; self.start_kick()
    def start_kick(self):
        if notigh_angle = thigh_prog_angle; self.l_shin_angle = shin_prog_angle; self.r_thigh_angle = -thigh_prog_angle * 0.3; self.r_shin_angle = 0.3
            self.l_ self.is_kicking: self.is_kicking = True; self.kick_timer = 0; self.vx = 0

    def update(self, dt):
        time_ms = pygame.time.get_ticks()
        if self.is_charging: selfupper_arm_angle = -thigh_prog_angle * 0.15 if self.kick_side == 'right' else thigh_prog_angle * 0.12; self.r_upper_arm_angle = thigh_prog_angle * 0.12 if self.kick_side == 'right' else -thigh_prog_angle * 0.15
            self.l_forearm_angle = 0.2; self.r_forearm_angle = 0.2
            if self.kick_timer >= self.kick_.charge_power = min(self.charge_power + CHARGE_RATE * dt, MAX_CHARGE_POWER)
        if not self.is_kicking: self.x += self.vx; self.x = max(self.limb_width / 2, min(self.x, SCREENduration: self.is_kicking = False; self.kick_timer = 0; self.r_thigh_angle = 0; self.l_thigh_angle = 0; self.r_shin_angle = 0; self.l_shin_angle = _WIDTH - self.limb_width / 2))
        if self.y < self.base_y or self.vy < 0: self.vy += GRAVITY; self.y += self.vy
        is_walking_on_ground = abs(self.vx) > 0; self.l_upper_arm_angle = 0; self.r_upper_arm_angle = 0; self.l_forearm_angle = 0; self.r_forearm_angle = 0; self.kick_charge_level = MIN_CHARGE_0 and not self.is_jumping and not self.is_kicking
        if is_walking_on_ground: self.walk_cycle_timer += WALK_CYCLE_SPEED
        elif not self.is_jumping and not self.is_kicking: self.walk_cycle_POWER
        else:
             if is_walking_on_ground: walk_sin = math.sin(self.walk_cycle_timer); self.l_upper_arm_angle = RUN_UPPER_ARM_SWING * walk_sin; self.r_upper_arm_angle = -timer *= 0.9
        if abs(self.walk_cycle_timer) < 0.1: self.walk_cycle_timer = 0
        if self.is_kicking:
            self.walk_cycle_timer = 0; self.kick_timer +=RUN_UPPER_ARM_SWING * walk_sin; self.l_forearm_angle = RUN_FOREARM_SWING * math.sin(self.walk_cycle_timer - RUN_FOREARM_OFFSET_FACTOR); self.r_forearm_angle = -RUN_FOREARM_SWING * math.sin(self.walk_cycle_timer - RUN_FOREARM_OFFSET_FACTOR); self.l_thigh_angle = -LEG_THIGH_SWING * walk_sin; self.r_thigh_angle = LEG_THIGH_SW 1; progress = min(self.kick_timer / self.kick_duration, 1.0)
            windup_end = 0.20; impact_start = 0.25; impact_end = 0.50; follow_end = 1.ING * walk_sin; shin_bend = LEG_SHIN_BEND_WALK * max(0, math.sin(self.walk_cycle_timer + LEG_SHIN_BEND_SHIFT)); self.l_shin_angle = shin_bend if self.l_th0
            if progress < windup_end: thigh_prog_angle = KICK_THIGH_WINDUP_ANGLE * (progress / windup_end)
            elif progress < impact_end: impact_progress = (progress - windup_end) / (impact_end - windupigh_angle < 0 else 0.1; self.r_shin_angle = shin_bend if self.r_thigh_angle < 0 else 0.1
             elif self.is_jumping: base_up_angle = JUMP_UPPER_ARM_BASE_end); thigh_prog_angle = KICK_THIGH_WINDUP_ANGLE + (KICK_THIGH_FOLLOW_ANGLE - KICK_THIGH_WINDUP_ANGLE) * impact_progress
            else: follow_progress = (progress - impact_end) / - self.vy * JUMP_UPPER_ARM_VY_FACTOR; self.l_upper_arm_angle = base_up_angle; self.r_upper_arm_angle = base_up_angle; base_fore_angle = JUMP_FOREARM_BASE; self.l (follow_end - impact_end); ease_out_factor = 1.0 - follow_progress**1.5; thigh_prog_angle = KICK_THIGH_FOLLOW_ANGLE * ease_out_factor
            if progress < impact_start: shin_prog_angle = K_forearm_angle = base_fore_angle; self.r_forearm_angle = base_fore_angle; jump_progress = max(0, min(1, 1 - (self.y / self.base_y))); thigh_tuck = JUMP_THIGH_TUCK * jump_progress; shin_tuck = JUMP_SHIN_TUCK * jump_progress; self.l_thigh_angle = thigh_tuck; self.r_thigh_angle = thigh_tuck; self.l_shin_angle = shin_tICK_SHIN_WINDUP_ANGLE * (progress / impact_start)
            elif progress < impact_end: impact_progress = (progress - impact_start) / (impact_end - impact_start); ease_in_factor = impact_progress ** 2; shin_prog_angle =uck; self.r_shin_angle = shin_tuck
             elif self.is_charging: charge_crouch = (self.charge_power - MIN_CHARGE_POWER) / (MAX_CHARGE_POWER - MIN_CHARGE_POWER); squat_angle = math.pi * KICK_SHIN_WINDUP_ANGLE + (KICK_SHIN_IMPACT_ANGLE - KICK_SHIN_WINDUP_ANGLE) * ease_in_factor
            else: follow_progress = (progress - impact_end) / (follow_end - impact_end); 0.05 * charge_crouch; self.l_thigh_angle = squat_angle; self.r_thigh_angle = squat_angle; self.l_shin_angle = squat_angle * 1.5; self.r_shin_angle = squat shin_prog_angle = KICK_SHIN_IMPACT_ANGLE + (KICK_SHIN_FOLLOW_ANGLE - KICK_SHIN_IMPACT_ANGLE) * follow_progress
            if DEBUG_KICK_ANGLES: print(f"Kick Prog: {progress:.2_angle * 1.5; self.l_upper_arm_angle = squat_angle; self.r_upper_arm_angle = squat_angle; self.l_forearm_angle = math.pi * 0.1; self.r_forearm_angle = mathf}, Thigh: {math.degrees(thigh_prog_angle):.1f}, Shin: {math.degrees(shin_prog_angle):.1f}")
            if self.kick_side == 'right': self.r_thigh_angle = thigh_prog_angle; self.pi * 0.1
             else: self.l_upper_arm_angle = 0; self.r_upper_arm_angle = 0; self.l_forearm_angle = 0; self.r_forearm_angle = 0; self.l.r_shin_angle = shin_prog_angle; self.l_thigh_angle = -thigh_prog_angle * 0.3; self.l_shin_angle = 0.3
            else: self.l_thigh_angle = thigh_prog__thigh_angle = 0; self.r_thigh_angle = 0; self.l_shin_angle = 0; self.r_shin_angle = 0
        current_y = self.y; current_x = self.x; wobble_offset =angle; self.l_shin_angle = shin_prog_angle; self.r_thigh_angle = -thigh_prog_angle * 0.3; self.r_shin_angle = 0.3
            self.l_upper_arm_angle = -th 0; total_leg_visual_height = self.thigh_length + self.shin_length; self.hip_pos = (current_x, current_y - total_leg_visual_height); upper_body_x = current_x + wobble_offset; self.neck_pos = (upper_body_x, self.hip_pos[1] - self.torso_length); self.head_pos = (upper_body_x, self.neck_pos[1] - self.head_radius); self.shoulder_pos = self.neck_igh_prog_angle * 0.15 if self.kick_side == 'right' else thigh_prog_angle * 0.12; self.r_upper_arm_angle = thigh_prog_angle * 0.12 if self.kick_side == 'right'pos; l_elbow_x = self.shoulder_pos[0] + self.upper_arm_length * math.sin(self.l_upper_arm_angle); l_elbow_y = self.shoulder_pos[1] + self.upper_arm_length * math. else -thigh_prog_angle * 0.15
            self.l_forearm_angle = 0.2; self.r_forearm_angle = 0.2
            if self.kick_timer >= self.kick_duration: self.is_kickingcos(self.l_upper_arm_angle); self.l_elbow_pos = (l_elbow_x, l_elbow_y); l_hand_angle_world = self.l_upper_arm_angle + self.l_forearm_angle; l_hand_ = False; self.kick_timer = 0; self.r_thigh_angle = 0; self.l_thigh_angle = 0; self.r_shin_angle = 0; self.l_shin_angle = 0; self.l_upper_x = self.l_elbow_pos[0] + self.forearm_length * math.sin(l_hand_angle_world); l_hand_y = self.l_elbow_pos[1] + self.forearm_length * math.cos(l_hand_arm_angle = 0; self.r_upper_arm_angle = 0; self.l_forearm_angle = 0; self.r_forearm_angle = 0; self.kick_charge_level = MIN_CHARGE_POWER
        else:
             ifangle_world); self.l_hand_pos = (l_hand_x, l_hand_y); r_elbow_x = self.shoulder_pos[0] + self.upper_arm_length * math.sin(self.r_upper_arm_angle); r_elbow_ is_walking_on_ground: walk_sin = math.sin(self.walk_cycle_timer); self.l_upper_arm_angle = RUN_UPPER_ARM_SWING * walk_sin; self.r_upper_arm_angle = -RUN_UPPER_ARM_SWy = self.shoulder_pos[1] + self.upper_arm_length * math.cos(self.r_upper_arm_angle); self.r_elbow_pos = (r_elbow_x, r_elbow_y); r_hand_angle_world = self.r_upperING * walk_sin; self.l_forearm_angle = RUN_FOREARM_SWING * math.sin(self.walk_cycle_timer - RUN_FOREARM_OFFSET_FACTOR); self.r_forearm_angle = -RUN_FOREARM_SWING * math._arm_angle + self.r_forearm_angle; r_hand_x = self.r_elbow_pos[0] + self.forearm_length * math.sin(r_hand_angle_world); r_hand_y = self.r_elbow_pos[1] +sin(self.walk_cycle_timer - RUN_FOREARM_OFFSET_FACTOR); self.l_thigh_angle = -LEG_THIGH_SWING * walk_sin; self.r_thigh_angle = LEG_THIGH_SWING * walk_sin; shin_ self.forearm_length * math.cos(r_hand_angle_world); self.r_hand_pos = (r_hand_x, r_hand_y); l_knee_x = self.hip_pos[0] + self.thigh_length * math.sin(self.l_thigh_angle); l_knee_y = self.hip_pos[1] + self.thigh_length * math.cos(self.l_thigh_angle); self.l_knee_pos = (l_knee_x, l_kneebend = LEG_SHIN_BEND_WALK * max(0, math.sin(self.walk_cycle_timer + LEG_SHIN_BEND_SHIFT)); self.l_shin_angle = shin_bend if self.l_thigh_angle < 0 else _y); l_foot_angle_world = self.l_thigh_angle + self.l_shin_angle; l_foot_x = self.l_knee_pos[0] + self.shin_length * math.sin(l_foot_angle_world); l0.1; self.r_shin_angle = shin_bend if self.r_thigh_angle < 0 else 0.1
             elif self.is_jumping: base_up_angle = JUMP_UPPER_ARM_BASE - self.vy * JUMP__foot_y = self.l_knee_pos[1] + self.shin_length * math.cos(l_foot_angle_world); r_knee_x = self.hip_pos[0] + self.thigh_length * math.sin(self.r_UPPER_ARM_VY_FACTOR; self.l_upper_arm_angle = base_up_angle; self.r_upper_arm_angle = base_up_angle; base_fore_angle = JUMP_FOREARM_BASE; self.l_forearm_angle = base_thigh_angle); r_knee_y = self.hip_pos[1] + self.thigh_length * math.cos(self.r_thigh_angle); self.r_knee_pos = (r_knee_x, r_knee_y); r_foot_anglefore_angle; self.r_forearm_angle = base_fore_angle; jump_progress = max(0, min(1, 1 - (self.y / self.base_y))); thigh_tuck = JUMP_THIGH_TUCK * jump_progress; shin_world = self.r_thigh_angle + self.r_shin_angle; r_foot_x = self.r_knee_pos[0] + self.shin_length * math.sin(r_foot_angle_world); r_foot_y = self.r_tuck = JUMP_SHIN_TUCK * jump_progress; self.l_thigh_angle = thigh_tuck; self.r_thigh_angle = thigh_tuck; self.l_shin_angle = shin_tuck; self.r_shin__knee_pos[1] + self.shin_length * math.cos(r_foot_angle_world)
        body_width = self.limb_width * 1.5; self.body_rect.width = int(body_width); self.body_rect.heightangle = shin_tuck
             elif self.is_charging: charge_crouch = (self.charge_power - MIN_CHARGE_POWER) / (MAX_CHARGE_POWER - MIN_CHARGE_POWER); squat_angle = math.pi * 0.05 * charge_ = int(self.hip_pos[1] - self.neck_pos[1]); self.body_rect.centerx = int(self.hip_pos[0]); self.body_rect.top = int(self.neck_pos[1])
        ground = self.basecrouch; self.l_thigh_angle = squat_angle; self.r_thigh_angle = squat_angle; self.l_shin_angle = squat_angle * 1.5; self.r_shin_angle = squat_angle * 1.5;_y; lowest_foot_y = max(l_foot_y, r_foot_y)
        if self.y >= ground and self.vy >= 0:
             if not self.is_kicking: self.y = ground; self.is_jumping = False; self.vy = 0; l_knee_x = self.hip_pos[0] + self.thigh_length * math.sin(self.l_thigh_angle); l_knee_y = self.hip_pos[1] + self.thigh_length * math.cos self.l_upper_arm_angle = squat_angle; self.r_upper_arm_angle = squat_angle; self.l_forearm_angle = math.pi * 0.1; self.r_forearm_angle = math.pi * 0.1
(self.l_thigh_angle); l_foot_angle_world = self.l_thigh_angle + self.l_shin_angle; l_foot_x = l_knee_x + self.shin_length * math.sin(l_foot_angle_world); r             else: self.l_upper_arm_angle = 0; self.r_upper_arm_angle = 0; self.l_forearm_angle = 0; self.r_forearm_angle = 0; self.l_thigh_angle = 0_knee_x = self.hip_pos[0] + self.thigh_length * math.sin(self.r_thigh_angle); r_knee_y = self.hip_pos[1] + self.thigh_length * math.cos(self.r_; self.r_thigh_angle = 0; self.l_shin_angle = 0; self.r_shin_angle = 0
        current_y = self.y; current_x = self.x; wobble_offset = 0; total_leg_visualthigh_angle); r_foot_angle_world = self.r_thigh_angle + self.r_shin_angle; r_foot_x = r_knee_x + self.shin_length * math.sin(r_foot_angle_world); self.l_foot_height = self.thigh_length + self.shin_length; self.hip_pos = (current_x, current_y - total_leg_visual_height); upper_body_x = current_x + wobble_offset; self.neck_pos = (upper_body__pos = (l_foot_x, ground); self.r_foot_pos = (r_foot_x, ground)
        else: self.l_foot_pos = (l_foot_x, l_foot_y); self.r_foot_pos = (rx, self.hip_pos[1] - self.torso_length); self.head_pos = (upper_body_x, self.neck_pos[1] - self.head_radius); self.shoulder_pos = self.neck_pos; l_elbow_x =_foot_x, r_foot_y)

    # Getters
    def get_kick_impact_point(self):
        if self.is_kicking:
            impact_start = 0.25; impact_end = 0.6; progress = self. self.shoulder_pos[0] + self.upper_arm_length * math.sin(self.l_upper_arm_angle); l_elbow_y = self.shoulder_pos[1] + self.upper_arm_length * math.cos(self.l_upper_kick_timer / self.kick_duration
            if impact_start < progress < impact_end:
                return self.l_foot_pos if self.kick_side == 'left' else self.r_foot_pos
        return None
    def get_head_position_radius(self):arm_angle); self.l_elbow_pos = (l_elbow_x, l_elbow_y); l_hand_angle_world = self.l_upper_arm_angle + self.l_forearm_angle; l_hand_x = self.l_elbow_ return self.head_pos, self.head_radius
    def get_body_rect(self): return self.body_rect

    # Draw Method
    def draw(self, screen):
        if self.is_charging: bar_width = 50; bar_height =pos[0] + self.forearm_length * math.sin(l_hand_angle_world); l_hand_y = self.l_elbow_pos[1] + self.forearm_length * math.cos(l_hand_angle_world); self.l_ 8; bar_x = self.head_pos[0] - bar_width / 2; bar_y = self.head_pos[1] - self.head_radius - bar_height - 5; fill_ratio = (self.charge_power - MIN_CHARGE_POWER)hand_pos = (l_hand_x, l_hand_y); r_elbow_x = self.shoulder_pos[0] + self.upper_arm_length * math.sin(self.r_upper_arm_angle); r_elbow_y = self.shoulder_ / (MAX_CHARGE_POWER - MIN_CHARGE_POWER); fill_width = bar_width * max(0, min(1, fill_ratio)); pygame.draw.rect(screen, BLACK, (bar_x - 1, bar_y - 1, bar_width + 2, bar_height + 2), 1); pygame.draw.rect(screen, YELLOW, (bar_x, bar_y, fill_width, bar_height))
        head_center_int = (int(self.head_pos[0]), int(self.head_pos[1pos[1] + self.upper_arm_length * math.cos(self.r_upper_arm_angle); self.r_elbow_pos = (r_elbow_x, r_elbow_y); r_hand_angle_world = self.r_upper_arm_])); pygame.draw.circle(screen, ITALY_WHITE, head_center_int, self.head_radius, 0); draw_pentagon(screen, BLACK, head_center_int, self.head_radius * 0.6, angle=0.1); draw_pentagon(screenangle + self.r_forearm_angle; r_hand_x = self.r_elbow_pos[0] + self.forearm_length * math.sin(r_hand_angle_world); r_hand_y = self.r_elbow_pos[1] +, BLACK, head_center_int, self.head_radius * 0.3, angle=math.pi/5 + 0.1); pygame.draw.circle(screen, BLACK, head_center_int, self.head_radius, 1); torso_segment_height = self.forearm_length * math.cos(r_hand_angle_world); self.r_hand_pos = (r_hand_x, r_hand_y); l_knee_x = self.hip_pos[0] + self.thigh_length * math. self.torso_length / 3; current_torso_y = self.neck_pos[1]
        for i in range(3): rect_center_x = self.neck_pos[0]; rect_center_y = current_torso_y + torso_segment_height /sin(self.l_thigh_angle); l_knee_y = self.hip_pos[1] + self.thigh_length * math.cos(self.l_thigh_angle); self.l_knee_pos = (l_knee_x, l_knee 2; draw_rotated_rectangle(screen, self.torso_colors[i], (rect_center_x, rect_center_y), self.limb_width, torso_segment_height, 0); current_torso_y += torso_segment_height
        def draw__y); l_foot_angle_world = self.l_thigh_angle + self.l_shin_angle; l_foot_x = self.l_knee_pos[0] + self.shin_length * math.sin(l_foot_angle_world); llimb_segment(start_pos, end_pos, length, color):
            center_x = (start_pos[0] + end_pos[0]) / 2; center_y = (start_pos[1] + end_pos[1]) / 2
            dx_foot_y = self.l_knee_pos[1] + self.shin_length * math.cos(l_foot_angle_world); r_knee_x = self.hip_pos[0] + self.thigh_length * math.sin(self.r_ = end_pos[0] - start_pos[0]; dy = end_pos[1] - start_pos[1]
            draw_length = math.hypot(dx, dy)
            if draw_length < 1: draw_length = 1
            angle =thigh_angle); r_knee_y = self.hip_pos[1] + self.thigh_length * math.cos(self.r_thigh_angle); self.r_knee_pos = (r_knee_x, r_knee_y); r_foot_angle math.atan2(dy, dx)
            draw_rotated_rectangle(screen, color, (center_x, center_y), draw_length, self.limb_width, angle)
        draw_limb_segment(self.shoulder_pos, self.l_elbow_pos, self.upper_arm_length, self.arm_colors[0]); draw_limb_segment(self.l_elbow_pos, self.l_hand_pos, self.forearm_length, self.arm_colors[1])
        draw_limb_segment(self.shoulder_world = self.r_thigh_angle + self.r_shin_angle; r_foot_x = self.r_knee_pos[0] + self.shin_length * math.sin(r_foot_angle_world); r_foot_y = self.r_pos, self.r_elbow_pos, self.upper_arm_length, self.arm_colors[0]); draw_limb_segment(self.r_elbow_pos, self.r_hand_pos, self.forearm_length, self.arm_colors[1])_knee_pos[1] + self.shin_length * math.cos(r_foot_angle_world)
        body_width = self.limb_width * 1.5; self.body_rect.width = int(body_width); self.body_rect.height
        draw_limb_segment(self.hip_pos, self.l_knee_pos, self.thigh_length, self.leg_colors[0]); draw_limb_segment(self.l_knee_pos, self.l_foot_pos, self.shin_length = int(self.hip_pos[1] - self.neck_pos[1]); self.body_rect.centerx = int(self.hip_pos[0]); self.body_rect.top = int(self.neck_pos[1])
        ground = self.base, self.leg_colors[1])
        draw_limb_segment(self.hip_pos, self.r_knee_pos, self.thigh_length, self.leg_colors[0]); draw_limb_segment(self.r_knee_pos, self.r__y; lowest_foot_y = max(l_foot_y, r_foot_y)
        if self.y >= ground and self.vy >= 0:
             if not self.is_kicking: self.y = ground; self.is_jumping = False;foot_pos, self.shin_length, self.leg_colors[1])

# --- Ball Class ---
class Ball:
    def __init__(self, x, y, radius): self.x = x; self.y = y; self.radius = radius; self.vx = 0; self.vy = 0; l_knee_x = self.hip_pos[0] + self.thigh_length * math.sin(self.l_thigh_angle); l_knee_y = self.hip_pos[1] + self.thigh_length * self.vy = 0; self.last_hit_by = None; self.rotation_angle = 0
    def apply_force(self, force_x, force_y, hitter='player'): self.vx += force_x; self.vy += force_y; self. math.cos(self.l_thigh_angle); l_foot_angle_world = self.l_thigh_angle + self.l_shin_angle; l_foot_x = l_knee_x + self.shin_length * math.sin(l_foot_anglelast_hit_by = hitter
    def update(self, dt):
        self.rotation_angle += self.vx * 0.015; self.rotation_angle %= (2 * math.pi); self.vy += GRAVITY; self.vx *= BALL_FRICTION;_world); r_knee_x = self.hip_pos[0] + self.thigh_length * math.sin(self.r_thigh_angle); r_knee_y = self.hip_pos[1] + self.thigh_length * math.cos( self.x += self.vx; self.y += self.vy
        hit_ground = False
        if self.y + self.radius >= GROUND_Y:
            if self.vy >= 0: hit_ground = True
            self.y = GROUND_Y - self.radius; self.vy *= -BALL_BOUNCE; self.vx *= 0.9
            if abs(self.vy) < 1: self.vy = 0
        if self.x + self.radius >= SCREEN_WIDTH: self.x = SCREEN_WIDTH - self.self.r_thigh_angle); r_foot_angle_world = self.r_thigh_angle + self.r_shin_angle; r_foot_x = r_knee_x + self.shin_length * math.sin(r_foot_angle_world); self.radius; self.vx *= -BALL_BOUNCE * 0.8
        elif self.x - self.radius <= 0: self.x = self.radius; self.vx *= -BALL_BOUNCE * 0.8
        if abs(self.vx) <l_foot_pos = (l_foot_x, ground); self.r_foot_pos = (r_foot_x, ground)
        else: self.l_foot_pos = (l_foot_x, l_foot_y); self.r_foot_pos 0.1 and self.is_on_ground(): self.vx = 0
        return hit_ground
    def is_on_ground(self): return self.y + self.radius >= GROUND_Y - 0.5
    def draw(self, screen):
         = (r_foot_x, r_foot_y)

    # Getters
    def get_kick_impact_point(self):
        if self.is_kicking:
            impact_start = 0.25; impact_end = 0.6; progresscenter_tuple = (int(self.x), int(self.y)); pygame.draw.circle(screen, WHITE, center_tuple, self.radius)
        pent_size = self.radius * 0.40; hex_size = self.radius * 0.42; dist = self.kick_timer / self.kick_duration
            if impact_start < progress < impact_end:
                return self.l_foot_pos if self.kick_side == 'left' else self.r_foot_pos
        return None
    def get_head_position__factor = 0.65; num_around = 5; angle_step = 2 * math.pi / num_around
        draw_pentagon(screen, BLACK, center_tuple, pent_size, self.rotation_angle)
        for i in range(num_around):radius(self): return self.head_pos, self.head_radius
    def get_body_rect(self): return self.body_rect

    # Draw Method
    def draw(self, screen):
        if self.is_charging: bar_width = 50;
            angle = self.rotation_angle + (i * angle_step) + angle_step / 2
            shape_center_x = center_tuple[0] + self.radius * dist_factor * math.cos(angle)
            shape_center_y = center_tuple[ bar_height = 8; bar_x = self.head_pos[0] - bar_width / 2; bar_y = self.head_pos[1] - self.head_radius - bar_height - 5; fill_ratio = (self.charge_power - MIN_1] + self.radius * dist_factor * math.sin(angle)
            shape_center = (shape_center_x, shape_center_y)
            if i % 2 == 0: draw_hexagon(screen, BLACK, shape_center, hex_size, angleCHARGE_POWER) / (MAX_CHARGE_POWER - MIN_CHARGE_POWER); fill_width = bar_width * max(0, min(1, fill_ratio)); pygame.draw.rect(screen, BLACK, (bar_x - 1, bar_y - 1, bar + self.rotation_angle * 0.5, width=1)
            else: draw_pentagon(screen, BLACK, shape_center, pent_size, angle + self.rotation_angle * 0.5)
        pygame.draw.circle(screen, BLACK, center__width + 2, bar_height + 2), 1); pygame.draw.rect(screen, YELLOW, (bar_x, bar_y, fill_width, bar_height))
        head_center_int = (int(self.head_pos[0]), int(tuple, self.radius, 1)

# --- Game Setup ---
pygame.init(); screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ciao Kick!"); clock = pygame.time.Clock()
player = StickMan(SCREEN_WIDTH // 4, GROUND_Y); ball = Ball(SCREEN_WIDTH // 2, GROUND_Y - 20, 15)
font_large = pygame.font.Font(None, 50); font_medium = pygame.font.Font(None, self.head_pos[1])); pygame.draw.circle(screen, ITALY_WHITE, head_center_int, self.head_radius, 0); draw_pentagon(screen, BLACK, head_center_int, self.head_radius * 0.6, angle=036); font_small = pygame.font.Font(None, 28)
font_timestamp = pygame.font.Font(None, 20); font_goal = pygame.font.Font(None, 80)

# --- Score & State Variables ---
player_score.1); draw_pentagon(screen, BLACK, head_center_int, self.head_radius * 0.3, angle=math.pi/5 + 0.1); pygame.draw.circle(screen, BLACK, head_center_int, self.head_radius, = 0; opponent_score = 0; goal_message_timer = 0; GOAL_MESSAGE_DURATION = 1.5
current_max_height = 0.0; current_hit_count = 0; high_score = 0
high_score_max 1); torso_segment_height = self.torso_length / 3; current_torso_y = self.neck_pos[1]
        for i in range(3): rect_center_x = self.neck_pos[0]; rect_center_y = current_height = 0.0; high_score_hit_count = 0
ball_was_on_ground = True; particles = []; can_headbutt = True
player_body_collision_timer = 0

# --- Off-screen Arrow Function ---
def draw_offscreen_arrow_torso_y + torso_segment_height / 2; draw_rotated_rectangle(screen, self.torso_colors[i], (rect_center_x, rect_center_y), self.limb_width, torso_segment_height, 0); current_torso(s, ball, p_pos):
    ar_sz = 15; pad = 25; is_off = False; tx, ty = ball.x, ball.y; ax = max(pad, min(ball.x, SCREEN_WIDTH - pad)); ay = max_y += torso_segment_height

        # Correctly indented nested function
        def draw_limb_segment(start_pos, end_pos, length, color):
            center_x = (start_pos[0] + end_pos[0]) / 2
            center_y = ((pad, min(ball.y, SCREEN_HEIGHT - pad))
    if ball.x < 0 or ball.x > SCREEN_WIDTH: ax = pad if ball.x < 0 else SCREEN_WIDTH - pad; is_off = True
    if ball.y < 0start_pos[1] + end_pos[1]) / 2
            dx = end_pos[0] - start_pos[0]; dy = end_pos[1] - start_pos[1]
            draw_length = math.hypot(dx, dy)
            if draw or ball.y > SCREEN_HEIGHT: ay = pad if ball.y < 0 else SCREEN_HEIGHT - pad; is_off = True
    if not is_off: return
    ang = math.atan2(ty - ay, tx - ax); p1 = (ar_sz_length < 1: draw_length = 1
            angle = math.atan2(dy, dx)
            draw_rotated_rectangle(screen, color, (center_x, center_y), draw_length, self.limb_width, angle)

        draw_limb_, 0); p2 = (-ar_sz / 2, -ar_sz / 2); p3 = (-ar_sz / 2, ar_sz / 2)
    cos_a, sin_a = math.cos(ang), math.sin(ang); p1r = (p1[0] * cos_a - p1[1] * sin_a, p1[0] * sin_a + p1[1] * cos_a); p2r = (p2[0] * cos_a - p2[1]segment(self.shoulder_pos, self.l_elbow_pos, self.upper_arm_length, self.arm_colors[0]); draw_limb_segment(self.l_elbow_pos, self.l_hand_pos, self.forearm_length, self.arm * sin_a, p2[0] * sin_a + p2[1] * cos_a); p3r = (p3[0] * cos_a - p3[1] * sin_a, p3[0] * sin_a + p3[1_colors[1])
        draw_limb_segment(self.shoulder_pos, self.r_elbow_pos, self.upper_arm_length, self.arm_colors[0]); draw_limb_segment(self.r_elbow_pos, self.r_hand_pos] * cos_a)
    pts = [(ax + p1r[0], ay + p1r[1]), (ax + p2r[0], ay + p2r[1]), (ax + p3r[0], ay + p3r[1])]; pygame., self.forearm_length, self.arm_colors[1])
        draw_limb_segment(self.hip_pos, self.l_knee_pos, self.thigh_length, self.leg_colors[0]); draw_limb_segment(self.l_kneedraw.polygon(s, ARROW_RED, [(int(p[0]), int(p[1])) for p in pts])

# --- Reset Function ---
def reset_after_goal():
    global current_max_height, current_hit_count, ball_was_on__pos, self.l_foot_pos, self.shin_length, self.leg_colors[1])
        draw_limb_segment(self.hip_pos, self.r_knee_pos, self.thigh_length, self.leg_colors[0]); draw_ground
    ball.x = SCREEN_WIDTH // 2; ball.y = SCREEN_HEIGHT // 3; ball.vx = 0; ball.vy = 0
    player.x = SCREEN_WIDTH // 4; player.y = GROUND_Y; player.vx = limb_segment(self.r_knee_pos, self.r_foot_pos, self.shin_length, self.leg_colors[1])

# --- Ball Class ---
class Ball:
    def __init__(self, x, y, radius): self.x = x; self.y0; player.vy = 0
    player.is_kicking = False; player.is_charging = False
    current_max_height = 0.0; current_hit_count = 0; ball_was_on_ground = False

# --- Main Game Loop --- = y; self.radius = radius; self.vx = 0; self.vy = 0; self.last_hit_by = None; self.rotation_angle = 0
    def apply_force(self, force_x, force_y, hitter='player'): self.
running = True
while running:
    dt = clock.tick(FPS) / 1000.0; dt = min(dt, 0.1)
    if player_body_collision_timer > 0: player_body_collision_timer -= 1
    vx += force_x; self.vy += force_y; self.last_hit_by = hitter

    # Correctly Formatted Update
    def update(self, dt):
        self.rotation_angle += self.vx * 0.015
        self.rotation_if goal_message_timer > 0: goal_message_timer -= dt

    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN:
            if event.keyangle %= (2 * math.pi)
        self.vy += GRAVITY
        self.vx *= BALL_FRICTION
        self.x += self.vx
        self.y += self.vy
        hit_ground = False
        if self.y + self.radius >= GROUND == pygame.K_LEFT: player.move(-1)
            elif event.key == pygame.K_RIGHT: player.move(1)
            elif event.key == pygame.K_UP: player.jump()
            elif event.key == pygame.K_SPACE: player.start_charge()
            elif event.key == pygame.K_ESCAPE: running = False
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT and player.vx < 0: player.stop_move()
            elif event.key_Y:
            if self.vy >= 0: hit_ground = True
            self.y = GROUND_Y - self.radius
            self.vy *= -BALL_BOUNCE
            self.vx *= 0.9
            if abs(self.vy) <  == pygame.K_RIGHT and player.vx > 0: player.stop_move()
            elif event.key == pygame.K_SPACE: player.release_charge_and_kick(ball.x)

    # Updates
    player.update(dt); ball_hit_ground1: self.vy = 0
        if self.x + self.radius >= SCREEN_WIDTH: self.x = SCREEN_WIDTH - self.radius; self.vx *= -BALL_BOUNCE * 0.8
        elif self.x - self.radius <= 0:_this_frame = ball.update(dt); particles = [p for p in particles if p.update(dt)]

    # --- Goal Detection ---
    goal_scored = False
    if ball.x + ball.radius >= GOAL_LINE_X_RIGHT and ball.y > self.x = self.radius; self.vx *= -BALL_BOUNCE * 0.8
        if abs(self.vx) < 0.1 and self.is_on_ground(): self.vx = 0
        return hit_ground

    def is_on GOAL_Y_POS: # Use constant
        player_score += 1; goal_message_timer = GOAL_MESSAGE_DURATION; goal_scored = True; print(f"GOAL! Player Score: {player_score}")
    elif ball.x - ball.radius <= GOAL_ground(self): return self.y + self.radius >= GROUND_Y - 0.5

    # Correctly Formatted Draw
    def draw(self, screen):
        center_tuple = (int(self.x), int(self.y))
        pygame.draw._LINE_X_LEFT and ball.y > GOAL_Y_POS: # Use constant
        opponent_score += 1; goal_message_timer = GOAL_MESSAGE_DURATION; goal_scored = True; print(f"GOAL! Opponent Score: {opponent_score}")
circle(screen, WHITE, center_tuple, self.radius)
        pent_size = self.radius * 0.40; hex_size = self.radius * 0.42; dist_factor = 0.65; num_around = 5; angle_step    if goal_scored: reset_after_goal(); continue

    # Score / Height Tracking Logic
    is_ball_airborne = not ball.is_on_ground();
    if is_ball_airborne: current_height_pixels = max(0, GROUND_Y - ( = 2 * math.pi / num_around
        draw_pentagon(screen, BLACK, center_tuple, pent_size, self.rotation_angle)
        for i in range(num_around):
            angle = self.rotation_angle + (i * angle_step)ball.y + ball.radius)); current_max_height = max(current_max_height, current_height_pixels); ball_was_on_ground = False
    elif ball_hit_ground_this_frame:
        if not ball_was_on_ground:
            final_sequence + angle_step / 2
            shape_center_x = center_tuple[0] + self.radius * dist_factor * math.cos(angle)
            shape_center_y = center_tuple[1] + self.radius * dist_factor * math.sin(angle_score = int(current_max_height * current_hit_count)
            if final_sequence_score > high_score:
                high_score = final_sequence_score; high_score_max_height = current_max_height; high_score_hit_count =)
            shape_center = (shape_center_x, shape_center_y)
            if i % 2 == 0: draw_hexagon(screen, BLACK, shape_center, hex_size, angle + self.rotation_angle * 0.5, width=1) current_hit_count
            current_max_height = 0.0 # Correct indentation
            current_hit_count = 0 # Correct indentation
        ball_was_on_ground = True
    display_height_score = int(current_max_height * current_hit_count
            else: draw_pentagon(screen, BLACK, shape_center, pent_size, angle + self.rotation_angle * 0.5)
        pygame.draw.circle(screen, BLACK, center_tuple, self.radius, 1)

# --- Game Setup ---
)

    # --- Collision Detection & Resolution ---
    kick_performed_this_frame = False; headbutt_performed_this_frame = False; score_increased_this_frame = False

    # 1. Kick Collision
    kick_point = player.get_kick_impact_pygame.init(); screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ciao Kick!"); clock = pygame.time.Clock()
player = StickMan(SCREEN_WIDTH // 4, GROUND_Y); ball = Ball(SCREENpoint()
    if kick_point:
        dist_x = kick_point[0] - ball.x; dist_y = kick_point[1] - ball.y; dist_sq = dist_x**2 + dist_y**2
        effective_kick_rad = KICK__WIDTH // 2, GROUND_Y - 20, 15)
font_large = pygame.font.Font(None, 50); font_medium = pygame.font.Font(None, 36); font_small = pygame.font.Font(None, RADIUS_NORMAL
        if ball.vy > BALL_FALLING_VELOCITY_THRESHOLD: effective_kick_rad += KICK_RADIUS_FALLING_BONUS
        if dist_sq < (ball.radius + effective_kick_rad)**2:
             progress = player.kick_timer /28)
font_timestamp = pygame.font.Font(None, 20); font_goal = pygame.font.Font(None, 80)

# --- Score & State Variables ---
player_score = 0; opponent_score = 0; goal_message_timer player.kick_duration
             if 0.25 < progress < 0.6:
                 kick_x_base = BASE_KICK_FORCE_X
                 if player.kick_side == "left": kick_x_base = -kick_x_base
                 kick_x = 0; GOAL_MESSAGE_DURATION = 1.5
current_max_height = 0.0; current_hit_count = 0; high_score = 0
high_score_max_height = 0.0; high_score_hit_count = = kick_x_base * player.kick_charge_level; kick_y = BASE_KICK_FORCE_Y * player.kick_charge_level
                 if player.vy < 0: kick_y += player.vy * 0.3
                 ball.apply_force(kick_x, kick_y); kick_performed_this_frame = True
                 if is_ball_airborne: current_hit_count += 1

    # 2. Headbutt Collision
    head_pos, head_radius = player.get_head_position_radius(); 0
ball_was_on_ground = True; particles = []; can_headbutt = True
player_body_collision_timer = 0

# --- Off-screen Arrow Function ---
def draw_offscreen_arrow(s, ball, p_pos):
    ar_sz = 15; pad = 25; is_off = False; tx, ty = ball.x, ball.y; ax = max(pad, min(ball.x, SCREEN_WIDTH - pad)); ay = max(pad, min(ball.y, SCREEN_HEIGHT - pad dist_x_head = ball.x - head_pos[0]; dist_y_head = ball.y - head_pos[1]
    dist_head_sq = dist_x_head**2 + dist_y_head**2; headbutt_cooldown_applied = False
    if dist_head_sq < (ball.radius + head_radius)**2:
        if can_headbutt:
            force_y = -HEADBUTT_UP_FORCE
            if player.vy < 0: force_y -= abs(player.vy) *))
    if ball.x < 0 or ball.x > SCREEN_WIDTH: ax = pad if ball.x < 0 else SCREEN_WIDTH - pad; is_off = True
    if ball.y < 0 or ball.y > SCREEN_HEIGHT: ay = pad if ball.y < HEADBUTT_VY_MULTIPLIER
            force_x = player.vx * HEADBUTT_PLAYER_VX_FACTOR - dist_x_head * HEADBUTT_POS_X_FACTOR
            ball.apply_force(force_x, force_y); can_headbutt 0 else SCREEN_HEIGHT - pad; is_off = True
    if not is_off: return
    ang = math.atan2(ty - ay, tx - ax); p1 = (ar_sz, 0); p2 = (-ar_sz / 2, -ar = False; headbutt_cooldown_applied = True; headbutt_performed_this_frame = True
            if is_ball_airborne: current_hit_count += 1
    if not headbutt_cooldown_applied:
        if dist_head_sq > (ball.radius_sz / 2); p3 = (-ar_sz / 2, ar_sz / 2)
    cos_a, sin_a = math.cos(ang), math.sin(ang); p1r = (p1[0] * cos_a - p1[ + head_radius + 15) ** 2: can_headbutt = True

    # --- 3. Player Body Collision (with Cooldown) ---
    if not kick_performed_this_frame and not headbutt_performed_this_frame and player_body_collision_timer == 01] * sin_a, p1[0] * sin_a + p1[1] * cos_a); p2r = (p2[0] * cos_a - p2[1] * sin_a, p2[0] * sin_a + p2:
        player_rect = player.get_body_rect()
        closest_x = max(player_rect.left, min(ball.x, player_rect.right)); closest_y = max(player_rect.top, min(ball.y, player_rect.bottom))[1] * cos_a); p3r = (p3[0] * cos_a - p3[1] * sin_a, p3[0] * sin_a + p3[1] * cos_a)
    pts = [(ax + p1r[0
        delta_x = ball.x - closest_x; delta_y = ball.y - closest_y; dist_sq_body = delta_x**2 + delta_y**2
        if dist_sq_body < ball.radius**2 and dist_sq_body > 0:], ay + p1r[1]), (ax + p2r[0], ay + p2r[1]), (ax + p3r[0], ay + p3r[1])]; pygame.draw.polygon(s, ARROW_RED, [(int(p[0]),
            distance = math.sqrt(dist_sq_body); overlap = ball.radius - distance
            collision_normal_x = delta_x / distance; collision_normal_y = delta_y / distance
            push_amount = overlap + 0.2; ball.x += collision_normal_x * push_amount; ball.y += collision_normal_y * push_amount
            rel_vx = ball.vx - player.vx; rel_vy = ball.vy - player.vy; vel_along_normal = rel_vx * collision_normal_x + rel_vy int(p[1])) for p in pts])

# --- Reset Function ---
def reset_after_goal():
    global current_max_height, current_hit_count, ball_was_on_ground
    ball.x = SCREEN_WIDTH // 2; ball.y = SCREEN_HEIGHT // 3; ball.vx = 0; ball.vy = 0
    player.x = SCREEN_WIDTH // 4; player.y = GROUND_Y; player.vx = 0; player.vy = 0
    player.is_kicking = False; player * collision_normal_y
            if vel_along_normal < 0:
                impulse_scalar = -(1 + PLAYER_BODY_BOUNCE) * vel_along_normal; bounce_vx = impulse_scalar * collision_normal_x; bounce_vy = impulse_scalar.is_charging = False
    current_max_height = 0.0; current_hit_count = 0; ball_was_on_ground = False

# --- Main Game Loop ---
running = True
while running:
    dt = clock.tick(FPS) / 100 * collision_normal_y
                bounce_vx += player.vx * PLAYER_VEL_TRANSFER; bounce_vy += player.vy * PLAYER_VEL_TRANSFER
                new_vel_mag_sq = bounce_vx**2 + bounce_vy**2
                if new_vel_mag_sq < MIN_BODY_BOUNCE_VEL**2:
                    if new_vel_mag_sq > 0: scale = MIN_BODY_BOUNCE_VEL / math.sqrt(new_vel_mag_sq); bounce_vx *= scale; bounce_vy *= scale0.0; dt = min(dt, 0.1)
    if player_body_collision_timer > 0: player_body_collision_timer -= 1
    if goal_message_timer > 0: goal_message_timer -= dt

    # Event Handling
    for
                    else: bounce_vx = collision_normal_x * MIN_BODY_BOUNCE_VEL; bounce_vy = collision_normal_y * MIN_BODY_BOUNCE_VEL
                ball.vx = bounce_vx; ball.vy = bounce_vy
                player_body_collision event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT: player.move(-1)
            elif event.key == pygame.K_RIGHT_timer = PLAYER_BODY_COLLISION_FRAMES
        elif dist_sq_body == 0: # Corrected Indentation Block
             ball.y = player_rect.top - ball.radius - 0.1
             if ball.vy > 0:
                 ball.vy *=: player.move(1)
            elif event.key == pygame.K_UP: player.jump()
            elif event.key == pygame.K_SPACE: player.start_charge()
            elif event.key == pygame.K_ESCAPE: running = False
        if event. -PLAYER_BODY_BOUNCE
                 player_body_collision_timer = PLAYER_BODY_COLLISION_FRAMES
    # --- END BODY COLLISION ---

    # --- Score Increase Check ---
    if kick_performed_this_frame or headbutt_performed_this_frame: score_type == pygame.KEYUP:
            if event.key == pygame.K_LEFT and player.vx < 0: player.stop_move()
            elif event.key == pygame.K_RIGHT and player.vx > 0: player.stop_move()
            elif event.increased_this_frame = True

    # Trigger Star Explosion
    if score_increased_this_frame and kick_point and current_hit_count > 0 and current_hit_count % 5 == 0:
        num_kick_particles = PARTICLE_COUNT // 2key == pygame.K_SPACE: player.release_charge_and_kick(ball.x)

    # Updates
    player.update(dt); ball_hit_ground_this_frame = ball.update(dt); particles = [p for p in particles if p.update(dt
        for _ in range(num_kick_particles): particle_x = kick_point[0] + random.uniform(-5, 5); particle_y = kick_point[1] + random.uniform(-5, 5); particles.append(Particle(particle_x, particle)]

    # --- Goal Detection ---
    goal_scored = False
    if ball.x + ball.radius >= SCREEN_WIDTH and ball.y > GOAL_Y_POS: player_score += 1; goal_message_timer = GOAL_MESSAGE_DURATION; goal_scored_y))

    # --- Drawing ---
    screen.fill(SKY_BLUE); pygame.draw.rect(screen, GRASS_GREEN, (0, GROUND_Y, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y))
    # Draw Isometric Goals
    draw_goal_isometric = True; print(f"GOAL! Player Score: {player_score}")
    elif ball.x - ball.radius <= 0 and ball.y > GOAL_Y_POS: opponent_score += 1; goal_message_timer = GOAL_MESSAGE_DURATION; goal(screen, GOAL_LINE_X_LEFT, GOAL_Y_POS, GOAL_HEIGHT, GOAL_DEPTH_X, GOAL_DEPTH_Y, GOAL_POST_THICKNESS, GOAL_COLOR, GOAL_NET_COLOR)
    draw_goal_isometric(_scored = True; print(f"GOAL! Opponent Score: {opponent_score}")
    if goal_scored: reset_after_goal(); continue

    # Score / Height Tracking Logic
    is_ball_airborne = not ball.is_on_ground();
    if isscreen, GOAL_LINE_X_RIGHT, GOAL_Y_POS, GOAL_HEIGHT, GOAL_DEPTH_X, GOAL_DEPTH_Y, GOAL_POST_THICKNESS, GOAL_COLOR, GOAL_NET_COLOR)
    for p in particles: p._ball_airborne: current_height_pixels = max(0, GROUND_Y - (ball.y + ball.radius)); current_max_height = max(current_max_height, current_height_pixels); ball_was_on_ground = False
    elif ball_hitdraw(screen)
    player.draw(screen); ball.draw(screen); draw_offscreen_arrow(screen, ball, (player.x, player.y))
    # Scores (Player vs Opponent)
    score_text = f"{player_score} - {opponent_score}"; score_surf = font_large.render(score_text, True, TEXT_COLOR); score_rect = score_surf.get_rect(centerx=SCREEN_WIDTH // 2, top=10); screen.blit(score_surf, score_rect)
    # Draw GO_ground_this_frame:
        if not ball_was_on_ground: # Just hit ground
            final_sequence_score = int(current_max_height * current_hit_count)
            # Correctly Indented High Score Logic
            if final_sequence_score > high_scoreAL! Message
    if goal_message_timer > 0:
        goal_text_surf = font_goal.render("GOAL!", True, ITALY_RED); goal_text_rect = goal_text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT //: # Update high score details
                high_score = final_sequence_score
                high_score_max_height = current_max_height
                high_score_hit_count = current_hit_count
            # Reset happens regardless of high score check
            current_max_height = 3))
        bg_rect = goal_text_rect.inflate(20, 10); bg_surf = pygame.Surface(bg_rect.size, pygame.SRCALPHA); bg_surf.fill((WHITE[0], WHITE[1], WHITE[2], 1 0.0
            current_hit_count = 0
        ball_was_on_ground = True
    display_height_score = int(current_max_height * current_hit_count)

    # --- Collision Detection & Resolution ---
    kick_performed_this_80)); screen.blit(bg_surf, bg_rect.topleft); screen.blit(goal_text_surf, goal_text_rect)
    # Cooldown
    if not can_headbutt: cooldown_color = (255, 0, 0, 18frame = False; headbutt_performed_this_frame = False; score_increased_this_frame = False

    # 1. Kick Collision
    kick_point = player.get_kick_impact_point()
    if kick_point:
        dist_x = kick_point0); cooldown_radius = 5; head_x, head_y = player.head_pos; indicator_x = int(head_x); indicator_y = int(head_y - player.head_radius - cooldown_radius - 2); temp_surf = pygame.Surface((cooldown[0] - ball.x; dist_y = kick_point[1] - ball.y; dist_sq = dist_x**2 + dist_y**2
        effective_kick_rad = KICK_RADIUS_NORMAL
        if ball.vy > BALL_FALLING_VELOCITY__radius*2, cooldown_radius*2), pygame.SRCALPHA); pygame.draw.circle(temp_surf, cooldown_color, (cooldown_radius, cooldown_radius), cooldown_radius); screen.blit(temp_surf, (indicator_x - cooldown_radius, indicator_THRESHOLD: effective_kick_rad += KICK_RADIUS_FALLING_BONUS
        if dist_sq < (ball.radius + effective_kick_rad)**2:
             progress = player.kick_timer / player.kick_duration
             if 0.25 < progress <y - cooldown_radius))
    # Timestamp
    timestamp_surf = font_timestamp.render(GENERATION_TIMESTAMP, True, TEXT_COLOR); timestamp_rect = timestamp_surf.get_rect(bottomright=(SCREEN_WIDTH - 10, SCREEN_HEIGHT - 10)); screen.blit(timestamp_surf, timestamp_rect)
    pygame.display.flip()

# Cleanup
pygame.quit(); sys.exit()
