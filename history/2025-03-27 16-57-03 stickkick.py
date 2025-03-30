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
SCOREBOARD_BG_COLOR = (50, 50, 80, 180) # Semi-transparent dark blue/grey
SCOREBOARD_BORDER_COLOR = (200, 200, 220)
SCOREBOARD_TEXT_FLASH_COLOR = YELLOW
SCREEN_FLASH_COLOR = (255, 255, 255, 100) # Semi-transparent white
SCREEN_FLASH_DURATION = 0.15 # seconds
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
HEAD_PLATFORM_RADIUS_BUFFER = 5 # How far horizontally can feet be from head center to land

# Kick Collision Tweak
KICK_RADIUS_NORMAL = 16; KICK_RADIUS_FALLING_BONUS = 6
BALL_FALLING_VELOCITY_THRESHOLD = 5

# Goal Constants
GOAL_HEIGHT = 135; GOAL_POST_THICKNESS = 3; GOAL_Y_POS = GROUND_Y - GOAL_HEIGHT
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

# Star/Goal Explosion
PARTICLE_LIFESPAN = 1.0; PARTICLE_SPEED = 150; PARTICLE_COUNT = 12; PARTICLE_SIZE = 6
GOAL_PARTICLE_COUNT = 30; GOAL_PARTICLE_SPEED_MIN = 200
GOAL_PARTICLE_SPEED_MAX = 350; GOAL_PARTICLE_LIFESPAN = 1.2

# --- Helper Functions ---
def draw_polygon_shape(surface, color, center, size, sides, angle=0, width=0):
    points = []
    for i in range(sides): offset_angle = math.pi / sides if sides % 2 == 0 else math.pi / 2.0; theta = offset_angle + (2.0 * math.pi * i / sides) + angle; x = center[0] + size * math.cos(theta); y = center[1] + size * math.sin(theta); points.append((int(x), int(y)))
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

# --- New Scoreboard Function ---
def draw_scoreboard(surface, p1_score, p2_score, font, is_goal_active):
    score_text = f"{p1_score} - {p2_score}"
    text_color = SCOREBOARD_TEXT_FLASH_COLOR if is_goal_active else TEXT_COLOR
    score_surf = font.render(score_text, True, text_color)
    score_rect = score_surf.get_rect()

    # Panel dimensions
    panel_padding = 15
    panel_width = score_rect.width + panel_padding * 2
    panel_height = score_rect.height + panel_padding
    panel_rect = pygame.Rect(0, 0, panel_width, panel_height)
    panel_rect.centerx = SCREEN_WIDTH // 2
    panel_rect.top = 5 # Small margin from top

    # Center text on panel
    score_rect.center = panel_rect.center

    # Draw Panel
    panel_surf = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
    panel_surf.fill(SCOREBOARD_BG_COLOR)
    pygame.draw.rect(panel_surf, SCOREBOARD_BORDER_COLOR, panel_surf.get_rect(), 2) # Border
    surface.blit(panel_surf, panel_rect.topleft)

    # Draw Score Text
    surface.blit(score_surf, score_rect)

# --- Particle Class ---
class Particle:
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

# --- Stick Man Class (Ciao) ---
class StickMan:
    def __init__(self, x, y, facing=1):
        self.x = x; self.y = y; self.base_y = y; self.width = 20; self.height = 80; self.vx = 0; self.vy = 0; self.is_jumping = False; self.is_kicking = False
        self.kick_timer = 0; self.kick_duration = 18; # Faster kick
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
    def move(self, direction):
        if not self.is_kicking:
            self.vx = direction * PLAYER_SPEED
            if direction != 0: self.facing_direction = direction
    def stop_move(self): self.vx = 0
    def jump(self):
        if not self.is_jumping or self.on_other_player_head:
            self.is_jumping = True; self.on_other_player_head = False; self.vy = JUMP_POWER; self.walk_cycle_timer = 0
    def start_kick(self): # No ball_x needed
        if not self.is_kicking:
            self.is_kicking = True; self.kick_timer = 0; self.vx = 0 # Stop horizontal movement when kicking

    def update(self, dt, other_player):
        time_ms = pygame.time.get_ticks()

        # --- Horizontal Movement ---
        # Apply velocity if not kicking
        if not self.is_kicking:
            self.x += self.vx
            # Clamp position to screen bounds
            self.x = max(self.limb_width / 2, min(self.x, SCREEN_WIDTH - self.limb_width / 2))
        # --- End Horizontal Movement ---

        # --- Vertical Movement & Platform Checks ---
        landed_on_head_this_frame = False
        landed_on_ground_this_frame = False

        # Determine potential platform Y (ground or other player's head)
        platform_y = self.base_y # Default to ground
        other_head_pos, other_head_radius = other_player.get_head_position_radius()
        head_top_y = other_head_pos[1] - other_head_radius
        dist_x_head = self.x - other_head_pos[0]

        # Check if horizontally aligned and vertically positioned to potentially land on head
        can_land_on_head = (
            abs(dist_x_head) < (other_head_radius + HEAD_PLATFORM_RADIUS_BUFFER) and # Within horizontal range?
            self.y >= head_top_y - 5 and # Feet near or slightly below head top? (Allows landing slightly before exact top)
            self.vy >= 0 # Must be moving downwards or stationary
        )

        if can_land_on_head:
            platform_y = head_top_y # Target platform is the other player's head

        # Apply Gravity (if not already treated as being on a head)
        next_y = self.y # Start with current y
        if not self.on_other_player_head:
            self.vy += GRAVITY
            next_y += self.vy # Calculate potential next y position

        # --- Landing / Falling Logic ---
        # Check for landing ON the determined platform (ground or head)
        if next_y >= platform_y and self.vy >= 0: # If moving down/still AND will be at or below platform
            if can_land_on_head and platform_y == head_top_y: # Landed specifically on head
                self.y = platform_y # Place feet exactly on head platform
                self.vy = 0
                self.is_jumping = False
                self.on_other_player_head = True # Now standing on head
                landed_on_head_this_frame = True
            elif platform_y == self.base_y: # Landed on ground
                self.y = self.base_y # Place feet exactly on ground
                self.vy = 0
                self.is_jumping = False
                self.on_other_player_head = False # Not on head if on ground
                landed_on_ground_this_frame = True
            else: # Still falling, haven't reached the determined platform (shouldn't happen often with this logic)
                 self.y = next_y
                 self.on_other_player_head = False # Ensure state is correct if falling past head
        # Handle falling OFF a head (lost horizontal alignment or jumped off)
        elif self.on_other_player_head and not can_land_on_head:
             self.on_other_player_head = False
             self.is_jumping = True # Considered jumping/falling now
             # Keep current vy (gravity was already applied if needed, or jump force exists)
             self.y = next_y # Apply gravity/velocity
        # Normal airborne movement (jumping up or falling freely)
        else: # (self.is_jumping or self.vy < 0 or not self.on_other_player_head)
            self.y = next_y
            # Ensure on_other_player_head is false if airborne
            if self.y < self.base_y and not landed_on_head_this_frame:
                self.on_other_player_head = False


        # Prevent falling through floor (final safety check)
        if self.y > self.base_y and not self.on_other_player_head:
             self.y = self.base_y
             if self.vy > 0: self.vy = 0 # Stop downward velocity if hitting ground
             self.is_jumping = False

        # --- End Vertical Movement ---

        # --- Animation Logic (Walk Cycle, Kicking, Jumping Poses) ---
        # Walk Cycle
        is_walking = abs(self.vx) > 0 and not self.is_jumping and not self.is_kicking and not self.on_other_player_head
        if is_walking: self.walk_cycle_timer += WALK_CYCLE_SPEED
        elif not self.is_jumping and not self.is_kicking: self.walk_cycle_timer *= 0.9 # Slow down walk cycle when stopping
        if abs(self.walk_cycle_timer) < 0.1: self.walk_cycle_timer = 0 # Snap to idle near zero

        # Kick Animation
        if self.is_kicking:
            self.walk_cycle_timer = 0 # Stop walk cycle during kick
            self.kick_timer += 1
            progress = min(self.kick_timer / self.kick_duration, 1.0)
            # Define kick phases
            windup_end = 0.20
            impact_start = 0.25
            impact_end = 0.50
            follow_end = 1.0
            # Calculate thigh angle based on progress
            if progress < windup_end: # Windup phase
                thigh_prog_angle = KICK_THIGH_WINDUP_ANGLE * (progress / windup_end)
            elif progress < impact_end: # Impact phase
                impact_progress = (progress - windup_end) / (impact_end - windup_end)
                thigh_prog_angle = KICK_THIGH_WINDUP_ANGLE + (KICK_THIGH_FOLLOW_ANGLE - KICK_THIGH_WINDUP_ANGLE) * impact_progress
            else: # Follow-through phase
                follow_progress = (progress - impact_end) / (follow_end - impact_end)
                ease_out_factor = 1.0 - follow_progress**1.5 # Ease out
                thigh_prog_angle = KICK_THIGH_FOLLOW_ANGLE * ease_out_factor
            # Calculate shin angle based on progress
            if progress < impact_start: # Windup phase (including thigh windup)
                 shin_prog_angle = KICK_SHIN_WINDUP_ANGLE * (progress / impact_start)
            elif progress < impact_end: # Impact phase
                impact_progress = (progress - impact_start) / (impact_end - impact_start)
                ease_in_factor = impact_progress ** 2 # Ease in quickly to impact
                shin_prog_angle = KICK_SHIN_WINDUP_ANGLE + (KICK_SHIN_IMPACT_ANGLE - KICK_SHIN_WINDUP_ANGLE) * ease_in_factor
            else: # Follow-through phase
                follow_progress = (progress - impact_end) / (follow_end - impact_end)
                shin_prog_angle = KICK_SHIN_IMPACT_ANGLE + (KICK_SHIN_FOLLOW_ANGLE - KICK_SHIN_IMPACT_ANGLE) * follow_progress

            if DEBUG_KICK_ANGLES: print(f"Kick Prog: {progress:.2f}, Thigh: {math.degrees(thigh_prog_angle):.1f}, Shin: {math.degrees(shin_prog_angle):.1f}")

            # Apply angles to correct legs based on facing direction
            kick_direction_multiplier = self.facing_direction
            if kick_direction_multiplier == 1: # Facing right, kick with right leg
                self.r_thigh_angle = thigh_prog_angle
                self.r_shin_angle = shin_prog_angle
                # Non-kicking leg moves slightly back
                self.l_thigh_angle = -thigh_prog_angle * 0.3
                self.l_shin_angle = 0.3
            else: # Facing left, kick with left leg
                self.l_thigh_angle = thigh_prog_angle * kick_direction_multiplier # Thigh angle needs direction flip
                self.l_shin_angle = shin_prog_angle
                # Non-kicking leg moves slightly back
                self.r_thigh_angle = -thigh_prog_angle * 0.3 * kick_direction_multiplier
                self.r_shin_angle = 0.3

            # Arm swing counterbalance during kick
            base_thigh_abs = abs(thigh_prog_angle)
            self.l_upper_arm_angle = -base_thigh_abs * 0.15 if self.facing_direction == 1 else base_thigh_abs * 0.12
            self.r_upper_arm_angle = base_thigh_abs * 0.12 if self.facing_direction == 1 else -base_thigh_abs * 0.15
            self.l_forearm_angle = 0.2 # Slightly bent
            self.r_forearm_angle = 0.2

            # End kick animation
            if self.kick_timer >= self.kick_duration:
                self.is_kicking = False; self.kick_timer = 0
                # Reset kick-specific angles (idle pose will take over)
                # self.r_thigh_angle = 0; self.l_thigh_angle = 0; self.r_shin_angle = 0; self.l_shin_angle = 0; self.l_upper_arm_angle = 0; self.r_upper_arm_angle = 0; self.l_forearm_angle = 0; self.r_forearm_angle = 0
        else: # Not kicking, handle walking or jumping pose
             if is_walking: # Walking animation
                 walk_sin = math.sin(self.walk_cycle_timer)
                 # Arms swing opposite to legs
                 self.l_upper_arm_angle = RUN_UPPER_ARM_SWING * walk_sin * self.facing_direction
                 self.r_upper_arm_angle = -RUN_UPPER_ARM_SWING * walk_sin * self.facing_direction
                 self.l_forearm_angle = RUN_FOREARM_SWING * math.sin(self.walk_cycle_timer - RUN_FOREARM_OFFSET_FACTOR) * self.facing_direction
                 self.r_forearm_angle = -RUN_FOREARM_SWING * math.sin(self.walk_cycle_timer - RUN_FOREARM_OFFSET_FACTOR) * self.facing_direction
                 # Legs swing
                 self.l_thigh_angle = -LEG_THIGH_SWING * walk_sin * self.facing_direction
                 self.r_thigh_angle = LEG_THIGH_SWING * walk_sin * self.facing_direction
                 # Shin bends when leg is moving back
                 shin_bend = LEG_SHIN_BEND_WALK * max(0, math.sin(self.walk_cycle_timer + LEG_SHIN_BEND_SHIFT))
                 self.l_shin_angle = shin_bend if self.l_thigh_angle * self.facing_direction < 0 else 0.1 # Bend left shin if left thigh moving back
                 self.r_shin_angle = shin_bend if self.r_thigh_angle * self.facing_direction < 0 else 0.1 # Bend right shin if right thigh moving back

             elif self.is_jumping and not self.on_other_player_head: # Jumping animation
                 # Arms raise based on upward velocity
                 base_up_angle = JUMP_UPPER_ARM_BASE - self.vy * JUMP_UPPER_ARM_VY_FACTOR
                 self.l_upper_arm_angle = base_up_angle
                 self.r_upper_arm_angle = base_up_angle
                 base_fore_angle = JUMP_FOREARM_BASE
                 self.l_forearm_angle = base_fore_angle
                 self.r_forearm_angle = base_fore_angle
                 # Legs tuck based on height relative to ground
                 jump_progress = max(0, min(1, 1 - (self.y / self.base_y))) # 0 on ground, 1 at peak (approx)
                 thigh_tuck = JUMP_THIGH_TUCK * jump_progress
                 shin_tuck = JUMP_SHIN_TUCK * jump_progress
                 self.l_thigh_angle = thigh_tuck
                 self.r_thigh_angle = thigh_tuck
                 self.l_shin_angle = shin_tuck
                 self.r_shin_angle = shin_tuck

             else: # Idle or on head pose
                 self.l_upper_arm_angle = 0; self.r_upper_arm_angle = 0; self.l_forearm_angle = 0; self.r_forearm_angle = 0
                 self.l_thigh_angle = 0; self.r_thigh_angle = 0; self.l_shin_angle = 0; self.r_shin_angle = 0
        # --- End Animation Logic ---


        # --- Calculate Joint Positions based on current angles ---
        current_y = self.y # Use the final calculated Y for this frame
        current_x = self.x # Use the final calculated X for this frame

        # Hip position is base for legs
        total_leg_visual_height = self.thigh_length + self.shin_length # Approximate resting height for hip calc
        self.hip_pos = (current_x, current_y - total_leg_visual_height)

        # Torso points up from hip
        upper_body_x = current_x # Keep torso centered for now
        self.neck_pos = (upper_body_x, self.hip_pos[1] - self.torso_length)
        self.head_pos = (upper_body_x, self.neck_pos[1] - self.head_radius)
        self.shoulder_pos = self.neck_pos # Shoulders are at neck level

        # Arms (Left)
        l_elbow_x = self.shoulder_pos[0] + self.upper_arm_length * math.sin(self.l_upper_arm_angle)
        l_elbow_y = self.shoulder_pos[1] + self.upper_arm_length * math.cos(self.l_upper_arm_angle)
        self.l_elbow_pos = (l_elbow_x, l_elbow_y)
        l_hand_angle_world = self.l_upper_arm_angle + self.l_forearm_angle
        l_hand_x = self.l_elbow_pos[0] + self.forearm_length * math.sin(l_hand_angle_world)
        l_hand_y = self.l_elbow_pos[1] + self.forearm_length * math.cos(l_hand_angle_world)
        self.l_hand_pos = (l_hand_x, l_hand_y)

        # Arms (Right)
        r_elbow_x = self.shoulder_pos[0] + self.upper_arm_length * math.sin(self.r_upper_arm_angle)
        r_elbow_y = self.shoulder_pos[1] + self.upper_arm_length * math.cos(self.r_upper_arm_angle)
        self.r_elbow_pos = (r_elbow_x, r_elbow_y)
        r_hand_angle_world = self.r_upper_arm_angle + self.r_forearm_angle
        r_hand_x = self.r_elbow_pos[0] + self.forearm_length * math.sin(r_hand_angle_world)
        r_hand_y = self.r_elbow_pos[1] + self.forearm_length * math.cos(r_hand_angle_world)
        self.r_hand_pos = (r_hand_x, r_hand_y)

        # Legs (Left)
        l_knee_x = self.hip_pos[0] + self.thigh_length * math.sin(self.l_thigh_angle)
        l_knee_y = self.hip_pos[1] + self.thigh_length * math.cos(self.l_thigh_angle)
        self.l_knee_pos = (l_knee_x, l_knee_y)
        l_foot_angle_world = self.l_thigh_angle + self.l_shin_angle
        l_foot_x = self.l_knee_pos[0] + self.shin_length * math.sin(l_foot_angle_world)
        l_foot_y = self.l_knee_pos[1] + self.shin_length * math.cos(l_foot_angle_world)
        self.l_foot_pos = (l_foot_x, l_foot_y)

        # Legs (Right)
        r_knee_x = self.hip_pos[0] + self.thigh_length * math.sin(self.r_thigh_angle)
        r_knee_y = self.hip_pos[1] + self.thigh_length * math.cos(self.r_thigh_angle)
        self.r_knee_pos = (r_knee_x, r_knee_y)
        r_foot_angle_world = self.r_thigh_angle + self.r_shin_angle
        r_foot_x = self.r_knee_pos[0] + self.shin_length * math.sin(r_foot_angle_world)
        r_foot_y = self.r_knee_pos[1] + self.shin_length * math.cos(r_foot_angle_world)
        self.r_foot_pos = (r_foot_x, r_foot_y)

        # Update Body Collision Rect (used for ball and player collisions)
        # Use neck and hip positions to define the main torso bounding box
        body_width = self.limb_width * 1.5 # Make rect slightly wider than limbs
        self.body_rect.width = int(body_width)
        self.body_rect.height = max(1, int(self.hip_pos[1] - self.neck_pos[1])) # Height from neck to hip
        self.body_rect.centerx = int(self.hip_pos[0]) # Center horizontally on hip/neck X
        self.body_rect.top = int(self.neck_pos[1]) # Top aligns with neck
        # --- End Joint Calculations ---


    # Getters
    def get_kick_impact_point(self):
        if self.is_kicking:
            impact_start = 0.25; impact_end = 0.6 # Timing window for kick impact
            progress = self.kick_timer / self.kick_duration
            if impact_start < progress < impact_end:
                # Return the position of the kicking foot
                return self.r_foot_pos if self.facing_direction == 1 else self.l_foot_pos
        return None
    def get_head_position_radius(self): return self.head_pos, self.head_radius
    def get_body_rect(self): return self.body_rect

    # Draw Method
    def draw(self, screen):
        # Head
        head_center_int = (int(self.head_pos[0]), int(self.head_pos[1]))
        pygame.draw.circle(screen, ITALY_WHITE, head_center_int, self.head_radius, 0)
        draw_pentagon(screen, BLACK, head_center_int, self.head_radius * 0.6, angle=0.1) # Soccer pattern
        draw_pentagon(screen, BLACK, head_center_int, self.head_radius * 0.3, angle=math.pi/5 + 0.1) # Soccer pattern inner
        pygame.draw.circle(screen, BLACK, head_center_int, self.head_radius, 1) # Outline
        # Nose
        nose_length = self.head_radius * 0.5
        nose_end_x = head_center_int[0] + nose_length * self.facing_direction
        nose_end_y = head_center_int[1] + 2 # Slightly down
        pygame.draw.line(screen, NOSE_COLOR, head_center_int, (int(nose_end_x), int(nose_end_y)), 2)

        # Torso (Stripes)
        torso_segment_height = self.torso_length / 3
        current_torso_y = self.neck_pos[1]
        for i in range(3):
            rect_center_x = self.neck_pos[0]
            rect_center_y = current_torso_y + torso_segment_height / 2
            # Use draw_rotated_rectangle (even with angle 0) for consistency and outline
            draw_rotated_rectangle(screen, self.torso_colors[i], (rect_center_x, rect_center_y), self.limb_width, torso_segment_height, 0)
            current_torso_y += torso_segment_height

        # Helper to draw limb segments as rotated rectangles
        def draw_limb_segment(start_pos, end_pos, length, color):
            center_x = (start_pos[0] + end_pos[0]) / 2
            center_y = (start_pos[1] + end_pos[1]) / 2
            dx = end_pos[0] - start_pos[0]
            dy = end_pos[1] - start_pos[1]
            # Calculate actual length and angle from start to end points
            draw_length = math.hypot(dx, dy)
            if draw_length < 1: draw_length = 1 # Avoid zero length
            angle = math.atan2(dy, dx) # Angle based on segment direction
            # Adjust angle for horizontal rectangle: add pi/2
            draw_rotated_rectangle(screen, color, (center_x, center_y), draw_length, self.limb_width, angle + math.pi/2)

        # Draw Limbs
        # Arms
        draw_limb_segment(self.shoulder_pos, self.l_elbow_pos, self.upper_arm_length, self.arm_colors[0]) # Left Upper Arm
        draw_limb_segment(self.l_elbow_pos, self.l_hand_pos, self.forearm_length, self.arm_colors[1])    # Left Forearm
        draw_limb_segment(self.shoulder_pos, self.r_elbow_pos, self.upper_arm_length, self.arm_colors[0]) # Right Upper Arm
        draw_limb_segment(self.r_elbow_pos, self.r_hand_pos, self.forearm_length, self.arm_colors[1])    # Right Forearm
        # Legs
        draw_limb_segment(self.hip_pos, self.l_knee_pos, self.thigh_length, self.leg_colors[0])          # Left Thigh
        draw_limb_segment(self.l_knee_pos, self.l_foot_pos, self.shin_length, self.leg_colors[1])        # Left Shin
        draw_limb_segment(self.hip_pos, self.r_knee_pos, self.thigh_length, self.leg_colors[0])          # Right Thigh
        draw_limb_segment(self.r_knee_pos, self.r_foot_pos, self.shin_length, self.leg_colors[1])        # Right Shin

# --- Ball Class ---
class Ball:
    def __init__(self, x, y, radius): self.x = x; self.y = y; self.radius = radius; self.vx = 0; self.vy = 0; self.last_hit_by = None; self.rotation_angle = 0
    def apply_force(self, force_x, force_y, hitter='player'): self.vx += force_x; self.vy += force_y; self.last_hit_by = hitter
    def update(self, dt):
        self.rotation_angle += self.vx * 0.015; self.rotation_angle %= (2 * math.pi); self.vy += GRAVITY; self.vx *= BALL_FRICTION; self.x += self.vx; self.y += self.vy
        hit_ground = False
        if self.y + self.radius >= GROUND_Y:
            if self.vy >= 0: hit_ground = True # Check if it was moving downwards when hitting
            self.y = GROUND_Y - self.radius; self.vy *= -BALL_BOUNCE; self.vx *= 0.9 # Bounce and friction
            if abs(self.vy) < 1: self.vy = 0 # Rest on ground
        if self.x + self.radius >= SCREEN_WIDTH: self.x = SCREEN_WIDTH - self.radius; self.vx *= -BALL_BOUNCE * 0.8 # Side wall bounce
        elif self.x - self.radius <= 0: self.x = self.radius; self.vx *= -BALL_BOUNCE * 0.8 # Side wall bounce
        if abs(self.vx) < 0.1 and self.is_on_ground(): self.vx = 0 # Stop rolling friction
        return hit_ground
    def is_on_ground(self): return self.y + self.radius >= GROUND_Y - 0.5
    def draw(self, screen):
        center_tuple = (int(self.x), int(self.y)); pygame.draw.circle(screen, WHITE, center_tuple, self.radius)
        # Draw soccer pattern (simplified)
        pent_size = self.radius * 0.40; hex_size = self.radius * 0.42; dist_factor = 0.65; num_around = 5; angle_step = 2 * math.pi / num_around
        draw_pentagon(screen, BLACK, center_tuple, pent_size, self.rotation_angle) # Center pentagon
        for i in range(num_around): # Surrounding shapes
            angle = self.rotation_angle + (i * angle_step) + angle_step / 2; shape_center_x = center_tuple[0] + self.radius * dist_factor * math.cos(angle)
            shape_center_y = center_tuple[1] + self.radius * dist_factor * math.sin(angle); shape_center = (shape_center_x, shape_center_y)
            # Alternate pattern (approximate)
            if i % 2 == 0: draw_hexagon(screen, BLACK, shape_center, hex_size, angle + self.rotation_angle * 0.5, width=1)
            else: draw_pentagon(screen, BLACK, shape_center, pent_size, angle + self.rotation_angle * 0.5)
        pygame.draw.circle(screen, BLACK, center_tuple, self.radius, 1) # Outline

# --- Game Setup ---
pygame.init(); screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ciao Kick!"); clock = pygame.time.Clock()
player1 = StickMan(SCREEN_WIDTH // 4, GROUND_Y, facing=1); player2 = StickMan(SCREEN_WIDTH * 3 // 4, GROUND_Y, facing=-1)
# Set Player 1 colors
player1.torso_colors = [P1_COLOR_MAIN, P1_COLOR_ACCENT, P1_COLOR_MAIN]; player1.arm_colors = [P1_COLOR_ACCENT, P1_COLOR_MAIN]; player1.leg_colors = [P1_COLOR_MAIN, P1_COLOR_ACCENT]
ball = Ball(SCREEN_WIDTH // 2, GROUND_Y - 20, 15)
# Fonts
font_large = pygame.font.Font(None, 50); font_medium = pygame.font.Font(None, 36); font_small = pygame.font.Font(None, 28)
font_timestamp = pygame.font.Font(None, 20); font_goal = pygame.font.Font(None, 80)

# --- Score & State Variables ---
player1_score = 0; player2_score = 0; goal_message_timer = 0; GOAL_MESSAGE_DURATION = 1.5
screen_flash_timer = 0 # For goal flash effect
ball_was_on_ground = True; particles = [];
p1_can_headbutt = True; p2_can_headbutt = True # Cooldown for ball headbutt
p1_body_collision_timer = 0; p2_body_collision_timer = 0 # Cooldown for ball body collision bounce
current_hit_count = 0 # For combo effect

# --- Off-screen Arrow Function ---
def draw_offscreen_arrow(s, ball, p_pos): # p_pos unused currently
    ar_sz = 15; pad = 25; is_off = False
    tx, ty = ball.x, ball.y # Target position (ball)
    # Clamp arrow position to screen bounds with padding
    ax = max(pad, min(ball.x, SCREEN_WIDTH - pad)); ay = max(pad, min(ball.y, SCREEN_HEIGHT - pad))
    # Check if ball is actually off-screen to determine if arrow should draw
    if ball.x < 0 or ball.x > SCREEN_WIDTH: ax = pad if ball.x < 0 else SCREEN_WIDTH - pad; is_off = True
    if ball.y < 0 or ball.y > SCREEN_HEIGHT: ay = pad if ball.y < 0 else SCREEN_HEIGHT - pad; is_off = True
    if not is_off: return # Don't draw if ball is on screen
    # Calculate angle from arrow position to ball position
    ang = math.atan2(ty - ay, tx - ax)
    # Define arrow shape points relative to origin (pointing right)
    p1 = (ar_sz, 0); p2 = (-ar_sz / 2, -ar_sz / 2); p3 = (-ar_sz / 2, ar_sz / 2)
    # Rotate points by the calculated angle
    cos_a, sin_a = math.cos(ang), math.sin(ang)
    p1r = (p1[0] * cos_a - p1[1] * sin_a, p1[0] * sin_a + p1[1] * cos_a)
    p2r = (p2[0] * cos_a - p2[1] * sin_a, p2[0] * sin_a + p2[1] * cos_a)
    p3r = (p3[0] * cos_a - p3[1] * sin_a, p3[0] * sin_a + p3[1] * cos_a)
    # Translate points to the clamped arrow position
    pts = [(ax + p1r[0], ay + p1r[1]), (ax + p2r[0], ay + p2r[1]), (ax + p3r[0], ay + p3r[1])]
    # Draw the arrow polygon
    pygame.draw.polygon(s, ARROW_RED, [(int(p[0]), int(p[1])) for p in pts])

# --- Reset Function ---
def reset_after_goal():
    global ball_was_on_ground, current_hit_count, p1_can_headbutt, p2_can_headbutt
    # Reset ball
    ball.x = SCREEN_WIDTH // 2; ball.y = SCREEN_HEIGHT // 3; ball.vx = 0; ball.vy = 0
    # Reset players
    player1.x = SCREEN_WIDTH // 4; player1.y = GROUND_Y; player1.vx = 0; player1.vy = 0; player1.is_kicking = False; player1.on_other_player_head = False; player1.facing_direction = 1
    player2.x = SCREEN_WIDTH * 3 // 4; player2.y = GROUND_Y; player2.vx = 0; player2.vy = 0; player2.is_kicking = False; player2.on_other_player_head = False; player2.facing_direction = -1
    # Reset states
    current_hit_count = 0; ball_was_on_ground = False # Assume starts airborne
    p1_can_headbutt = True; p2_can_headbutt = True # Reset headbutt cooldown

# --- Collision Handling Function (Player-Ball) ---
def handle_player_ball_collisions(player, ball, can_headbutt, body_collision_timer, is_ball_airborne):
    global current_hit_count
    kick_performed = False; headbutt_performed = False; score_increase = False; kick_pt = None
    # 1. Kick Collision
    local_kick_point = player.get_kick_impact_point() # Get foot position during kick animation
    if local_kick_point:
        dist_x = local_kick_point[0] - ball.x; dist_y = local_kick_point[1] - ball.y; dist_sq = dist_x**2 + dist_y**2
        # Dynamic kick radius: larger if ball is falling fast towards foot
        eff_kick_rad = KICK_RADIUS_NORMAL + (KICK_RADIUS_FALLING_BONUS if ball.vy > BALL_FALLING_VELOCITY_THRESHOLD else 0)
        # Check distance squared
        if dist_sq < (ball.radius + eff_kick_rad)**2:
             # Check if kick animation is in the impact phase
             progress = player.kick_timer / player.kick_duration
             if 0.25 < progress < 0.6: # Impact window
                 # Apply kick force based on facing direction
                 kick_x = BASE_KICK_FORCE_X * KICK_FORCE_LEVEL * player.facing_direction
                 kick_y = BASE_KICK_FORCE_Y * KICK_FORCE_LEVEL
                 if player.vy < 0: kick_y += player.vy * 0.4 # Add some upward force if jumping
                 ball.apply_force(kick_x, kick_y, hitter=player); kick_performed = True; kick_pt = local_kick_point
                 if is_ball_airborne: current_hit_count += 1; score_increase = True # Increment combo only if airborne

    # 2. Headbutt Collision
    head_pos, head_radius = player.get_head_position_radius(); dist_x_head = ball.x - head_pos[0]; dist_y_head = ball.y - head_pos[1]
    dist_head_sq = dist_x_head**2 + dist_y_head**2; headbutt_cooldown_just_applied = False
    if dist_head_sq < (ball.radius + head_radius)**2: # Collision with head
        if can_headbutt: # Check cooldown
            # Apply headbutt force (mostly upwards)
            force_y = -HEADBUTT_UP_FORCE
            if player.vy < 0: force_y -= abs(player.vy) * HEADBUTT_VY_MULTIPLIER # More force if moving up
            force_x = player.vx * HEADBUTT_PLAYER_VX_FACTOR - dist_x_head * HEADBUTT_POS_X_FACTOR # Slight horizontal influence
            ball.apply_force(force_x, force_y, hitter=player); headbutt_cooldown_just_applied = True; headbutt_performed = True
            if is_ball_airborne: current_hit_count += 1; score_increase = True # Increment combo
    # Headbutt cooldown logic
    new_can_headbutt = can_headbutt
    if headbutt_cooldown_just_applied: new_can_headbutt = False # Apply cooldown
    elif not new_can_headbutt and dist_head_sq > (ball.radius + head_radius + 15)**2: new_can_headbutt = True # Reset cooldown when ball is far enough

    # 3. Body Collision (if not kicked or headbutted, and cooldown allows)
    new_body_collision_timer = body_collision_timer
    if not kick_performed and not headbutt_performed and body_collision_timer == 0:
        player_rect = player.get_body_rect()
        # Find closest point on player rect to ball center
        closest_x = max(player_rect.left, min(ball.x, player_rect.right)); closest_y = max(player_rect.top, min(ball.y, player_rect.bottom))
        delta_x = ball.x - closest_x; delta_y = ball.y - closest_y; dist_sq_body = delta_x**2 + delta_y**2

        if dist_sq_body < ball.radius**2: # Collision detected
             if dist_sq_body > 0: # Normal collision
                 distance = math.sqrt(dist_sq_body); overlap = ball.radius - distance
                 # Calculate collision normal
                 collision_normal_x = delta_x / distance; collision_normal_y = delta_y / distance
                 # Push ball out of player rect
                 push_amount = overlap + 0.2; ball.x += collision_normal_x * push_amount; ball.y += collision_normal_y * push_amount
                 # Calculate relative velocity
                 rel_vx = ball.vx - player.vx; rel_vy = ball.vy - player.vy
                 vel_along_normal = rel_vx * collision_normal_x + rel_vy * collision_normal_y
                 # Apply bounce only if moving towards each other
                 if vel_along_normal < 0:
                     # Calculate impulse scalar (bounce effect)
                     impulse_scalar = -(1 + PLAYER_BODY_BOUNCE) * vel_along_normal
                     bounce_vx = impulse_scalar * collision_normal_x; bounce_vy = impulse_scalar * collision_normal_y
                     # Add some velocity transfer from player
                     bounce_vx += player.vx * PLAYER_VEL_TRANSFER; bounce_vy += player.vy * PLAYER_VEL_TRANSFER
                     # Ensure minimum bounce velocity
                     new_vel_mag_sq = bounce_vx**2 + bounce_vy**2
                     if new_vel_mag_sq < MIN_BODY_BOUNCE_VEL**2:
                         if new_vel_mag_sq > 0: scale = MIN_BODY_BOUNCE_VEL / math.sqrt(new_vel_mag_sq); bounce_vx *= scale; bounce_vy *= scale
                         else: bounce_vx = collision_normal_x * MIN_BODY_BOUNCE_VEL; bounce_vy = collision_normal_y * MIN_BODY_BOUNCE_VEL # Failsafe
                     # Apply final velocity to ball
                     ball.vx = bounce_vx; ball.vy = bounce_vy
                     new_body_collision_timer = PLAYER_BODY_COLLISION_FRAMES # Apply cooldown
             elif dist_sq_body == 0: # Ball center exactly on edge/corner (rare)
                  # Push ball slightly away, primarily vertically upwards if possible
                  ball.y = player_rect.top - ball.radius - 0.1
                  if ball.vy > 0: ball.vy *= -PLAYER_BODY_BOUNCE # Bounce if moving down
                  new_body_collision_timer = PLAYER_BODY_COLLISION_FRAMES # Apply cooldown

    return score_increase, new_can_headbutt, new_body_collision_timer, kick_pt

# --- Main Game Loop ---
running = True
while running:
    # Delta time calculation
    dt = clock.tick(FPS) / 1000.0; dt = min(dt, 0.1) # Cap dt to prevent large steps

    # Update Cooldowns
    if p1_body_collision_timer > 0: p1_body_collision_timer -= 1
    if p2_body_collision_timer > 0: p2_body_collision_timer -= 1
    if goal_message_timer > 0: goal_message_timer -= dt
    if screen_flash_timer > 0: screen_flash_timer -= dt

    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        # Keyboard Down Events
        if event.type == pygame.KEYDOWN:
            # Player 1 Controls
            if event.key == pygame.K_LEFT: player1.move(-1)
            elif event.key == pygame.K_RIGHT: player1.move(1)
            elif event.key == pygame.K_UP: player1.jump()
            elif event.key == pygame.K_DOWN: player1.start_kick()
            # Player 2 Controls
            elif event.key == pygame.K_a: player2.move(-1)
            elif event.key == pygame.K_d: player2.move(1)
            elif event.key == pygame.K_w: player2.jump()
            elif event.key == pygame.K_s: player2.start_kick()
            # General Controls
            elif event.key == pygame.K_ESCAPE: running = False
        # Keyboard Up Events (Stop movement)
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT and player1.vx < 0: player1.stop_move()
            elif event.key == pygame.K_RIGHT and player1.vx > 0: player1.stop_move()
            elif event.key == pygame.K_a and player2.vx < 0: player2.stop_move()
            elif event.key == pygame.K_d and player2.vx > 0: player2.stop_move()

    # --- Updates ---
    # Update players (physics and animation) - Pass the *other* player for head collision checks
    player1.update(dt, player2)
    player2.update(dt, player1)
    # Update ball physics
    ball_hit_ground_this_frame = ball.update(dt)
    # Update particles
    particles = [p for p in particles if p.update(dt)] # Keep active particles

    # --- Player-Player Collision (REVISED BLOCK v2) ---
    p1_rect = player1.get_body_rect()
    p2_rect = player2.get_body_rect()

    if p1_rect.colliderect(p2_rect):

        # Get vertical positions for head-stand check
        # Using foot position (self.y) and head top position
        p1_head_pos, p1_head_rad = player1.get_head_position_radius()
        p2_head_pos, p2_head_rad = player2.get_head_position_radius()
        p1_head_top_y = p1_head_pos[1] - p1_head_rad
        p2_head_top_y = p2_head_pos[1] - p2_head_rad
        p1_feet_y = player1.y
        p2_feet_y = player2.y

        # --- Head-Stand Check ---
        # Check if p1 is potentially landing/standing on p2
        p1_on_p2_check = (
            abs(player1.x - p2_head_pos[0]) < (p2_head_rad + HEAD_PLATFORM_RADIUS_BUFFER) and # Horizontally aligned?
            p1_feet_y >= p2_head_top_y - 10 and # Feet near or slightly below head top? (Tolerance for landing)
            p1_feet_y < p2_head_top_y + player1.height * 0.5 # Feet not way below head? (Avoids side-by-side body rects triggering this)
        )
        # Check if p2 is potentially landing/standing on p1
        p2_on_p1_check = (
            abs(player2.x - p1_head_pos[0]) < (p1_head_rad + HEAD_PLATFORM_RADIUS_BUFFER) and # Horizontally aligned?
            p2_feet_y >= p1_head_top_y - 10 and # Feet near or slightly below head top?
            p2_feet_y < p1_head_top_y + player2.height * 0.5 # Feet not way below head?
        )

        # --- Collision Resolution ---
        # If neither player seems to be standing on the other, resolve as horizontal body collision
        if not p1_on_p2_check and not p2_on_p1_check:

            # Calculate horizontal overlap using rect edges
            overlap_x = 0
            if player1.x < player2.x: # p1 is left, p2 is right
                overlap_x = p1_rect.right - p2_rect.left
            else: # p1 is right, p2 is left
                overlap_x = p2_rect.right - p1_rect.left

            # Ensure positive overlap before resolving
            if overlap_x > 0:
                push = overlap_x / 2 + 0.1 # Gentle positional push based on overlap

                # Apply positional correction
                if player1.x < player2.x: # p1 is left, p2 is right
                    player1.x -= push
                    player2.x += push
                    # Stop players from moving further into each other
                    if player1.vx > 0: player1.vx = 0
                    if player2.vx < 0: player2.vx = 0
                else: # p1 is right, p2 is left
                    player1.x += push
                    player2.x -= push
                    # Stop players from moving further into each other
                    if player1.vx < 0: player1.vx = 0
                    if player2.vx > 0: player2.vx = 0

        # --- (End of horizontal body collision resolution) ---
        # If it *was* a potential head-stand situation (p1_on_p2_check or p2_on_p1_check is True),
        # we simply do nothing here in the main loop's collision block.
        # The StickMan.update() method's vertical platform logic should handle the landing/standing.
        # This prevents the horizontal push from interfering with the vertical landing.

    # --- (End of Player-Player Collision Block) ---


    # --- Goal Detection & Effects ---
    goal_scored = False; goal_pos_x = -1 # Store which goal line was crossed
    # Check Player 1 goal (right side)
    if ball.x + ball.radius >= GOAL_LINE_X_RIGHT and ball.y > GOAL_Y_POS:
        player1_score += 1; goal_message_timer = GOAL_MESSAGE_DURATION; goal_scored = True; goal_pos_x = SCREEN_WIDTH; print(f"GOAL! Player 1 Score: {player1_score}")
        screen_flash_timer = SCREEN_FLASH_DURATION # Trigger screen flash
    # Check Player 2 goal (left side)
    elif ball.x - ball.radius <= GOAL_LINE_X_LEFT and ball.y > GOAL_Y_POS:
        player2_score += 1; goal_message_timer = GOAL_MESSAGE_DURATION; goal_scored = True; goal_pos_x = 0; print(f"GOAL! Player 2 Score: {player2_score}")
        screen_flash_timer = SCREEN_FLASH_DURATION # Trigger screen flash

    # If a goal was scored in this frame
    if goal_scored:
        # Create goal explosion particles
        goal_center_y = GOAL_Y_POS + GOAL_HEIGHT / 2
        for _ in range(GOAL_PARTICLE_COUNT): particles.append(Particle(goal_pos_x, goal_center_y, colors=GOAL_EXPLOSION_COLORS, speed_min=GOAL_PARTICLE_SPEED_MIN, speed_max=GOAL_PARTICLE_SPEED_MAX, lifespan=GOAL_PARTICLE_LIFESPAN))
        # Reset positions and ball state
        reset_after_goal()
        continue # Skip the rest of the loop for this frame to avoid physics issues post-reset

    # --- Combo Score Reset Logic ---
    is_ball_airborne = not ball.is_on_ground()
    # Reset combo count if the ball hits the ground *this frame* and it *was* airborne previously
    if not is_ball_airborne and ball_hit_ground_this_frame and not ball_was_on_ground:
        current_hit_count = 0
    # Update the ball's ground status for the next frame's check
    ball_was_on_ground = not is_ball_airborne

    # --- Player-Ball Collisions ---
    # Handle collisions and get results (did score increase, can headbutt, body timer, kick point)
    p1_hit, p1_can_headbutt, p1_body_collision_timer, p1_kick_pt = handle_player_ball_collisions(player1, ball, p1_can_headbutt, p1_body_collision_timer, is_ball_airborne)
    p2_hit, p2_can_headbutt, p2_body_collision_timer, p2_kick_pt = handle_player_ball_collisions(player2, ball, p2_can_headbutt, p2_body_collision_timer, is_ball_airborne)
    # Check if combo score increased this frame
    score_increased_this_frame = p1_hit or p2_hit
    # Find the location of the kick if one happened
    last_kick_point = p1_kick_pt if p1_kick_pt else p2_kick_pt

    # Trigger Star Explosion (Combo effect) on kick
    if score_increased_this_frame and last_kick_point and current_hit_count > 0 and current_hit_count % 5 == 0: # Every 5 airborne hits
        num_kick_particles = PARTICLE_COUNT // 2
        for _ in range(num_kick_particles):
            particle_x = last_kick_point[0] + random.uniform(-5, 5)
            particle_y = last_kick_point[1] + random.uniform(-5, 5)
            particles.append(Particle(particle_x, particle_y)) # Default star particles

    # --- Drawing ---
    # Background
    screen.fill(SKY_BLUE)
    pygame.draw.rect(screen, GRASS_GREEN, (0, GROUND_Y, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y))

    # Draw Goals (behind players/ball)
    draw_goal_isometric(screen, GOAL_LINE_X_LEFT, GOAL_Y_POS, GOAL_HEIGHT, -GOAL_DEPTH_X, GOAL_DEPTH_Y, GOAL_POST_THICKNESS, GOAL_COLOR, GOAL_NET_COLOR) # Left goal, depth towards left
    draw_goal_isometric(screen, GOAL_LINE_X_RIGHT, GOAL_Y_POS, GOAL_HEIGHT, GOAL_DEPTH_X, GOAL_DEPTH_Y, GOAL_POST_THICKNESS, GOAL_COLOR, GOAL_NET_COLOR) # Right goal, depth towards right

    # Draw Screen Flash (if active) - draw semi-transparent overlay
    if screen_flash_timer > 0:
        flash_surf = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        flash_alpha = int(255 * (screen_flash_timer / SCREEN_FLASH_DURATION)) # Fade out effect
        flash_surf.fill((SCREEN_FLASH_COLOR[0], SCREEN_FLASH_COLOR[1], SCREEN_FLASH_COLOR[2], flash_alpha))
        screen.blit(flash_surf, (0,0))

    # Draw Game Elements
    for p in particles: p.draw(screen) # Draw particles
    player1.draw(screen); player2.draw(screen); ball.draw(screen)
    draw_offscreen_arrow(screen, ball, None) # Draw arrow if ball is off-screen

    # Draw UI Elements (Scoreboard, Goal Message, Cooldowns)
    # Scoreboard
    draw_scoreboard(screen, player1_score, player2_score, font_large, goal_message_timer > 0)
    # GOAL! Message
    if goal_message_timer > 0:
        goal_text_surf = font_goal.render("GOAL!", True, ITALY_RED)
        goal_text_rect = goal_text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        # Simple background for text
        bg_rect = goal_text_rect.inflate(20, 10)
        bg_surf = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        bg_surf.fill((WHITE[0], WHITE[1], WHITE[2], 180))
        screen.blit(bg_surf, bg_rect.topleft)
        screen.blit(goal_text_surf, goal_text_rect)

    # Headbutt Cooldown Indicators (small circle above head)
    cooldown_radius = 5
    indicator_offset_y = - player1.head_radius - cooldown_radius - 2 # Above head
    if not p1_can_headbutt:
        cooldown_color = (255, 0, 0, 180) # Red semi-transparent
        head_x, head_y = player1.head_pos
        indicator_x = int(head_x); indicator_y = int(head_y + indicator_offset_y)
        # Draw using a temporary surface for alpha blending
        temp_surf = pygame.Surface((cooldown_radius*2, cooldown_radius*2), pygame.SRCALPHA)
        pygame.draw.circle(temp_surf, cooldown_color, (cooldown_radius, cooldown_radius), cooldown_radius)
        screen.blit(temp_surf, (indicator_x - cooldown_radius, indicator_y - cooldown_radius))
    if not p2_can_headbutt:
        cooldown_color = (0, 0, 255, 180) # Blue semi-transparent (distinguish players)
        head_x, head_y = player2.head_pos
        indicator_x = int(head_x); indicator_y = int(head_y + indicator_offset_y)
        temp_surf = pygame.Surface((cooldown_radius*2, cooldown_radius*2), pygame.SRCALPHA)
        pygame.draw.circle(temp_surf, cooldown_color, (cooldown_radius, cooldown_radius), cooldown_radius)
        screen.blit(temp_surf, (indicator_x - cooldown_radius, indicator_y - cooldown_radius))

    # Timestamp (Bottom Right)
    timestamp_surf = font_timestamp.render(GENERATION_TIMESTAMP, True, TEXT_COLOR)
    timestamp_rect = timestamp_surf.get_rect(bottomright=(SCREEN_WIDTH - 10, SCREEN_HEIGHT - 10))
    screen.blit(timestamp_surf, timestamp_rect)

    # Update the display
    pygame.display.flip()

# Cleanup
pygame.quit(); sys.exit()