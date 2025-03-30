# -*- coding: utf-8 -*-
import pygame
import sys
import math
import random

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (135, 206, 235)
# Italian Flag Colors for Ciao
ITALY_GREEN = (0, 146, 70)
ITALY_WHITE = (241, 242, 241)
ITALY_RED = (206, 43, 55)
# Other colors remain the same
GRASS_GREEN = (34, 139, 34) # Keeping original grass
YELLOW = (255, 255, 0)
TEXT_COLOR = (10, 10, 50)
ARROW_RED = (255, 50, 50)
STAR_YELLOW = (255, 255, 100)
STAR_ORANGE = (255, 180, 0)
DEBUG_BLUE = (0, 0, 255)

# Physics (Mostly unchanged, but Ciao might feel heavier/stiffer)
GRAVITY = 0.5
PLAYER_SPEED = 4 # Slightly slower to feel blockier
JUMP_POWER = -11 # Slightly weaker jump
BASE_KICK_FORCE_X = 14
BASE_KICK_FORCE_Y = -13
CHARGE_RATE = 1.5
MAX_CHARGE_POWER = 2.0
MIN_CHARGE_POWER = 0.5
HEADBUTT_UP_FORCE = 15.0
HEADBUTT_VY_MULTIPLIER = 1.2
HEADBUTT_PLAYER_VX_FACTOR = 0.6
HEADBUTT_POS_X_FACTOR = 0.15
BALL_FRICTION = 0.99
BALL_BOUNCE = 0.7
GROUND_Y = SCREEN_HEIGHT - 50

# Animation (Reduced swing/wobble for stiffness)
WALK_CYCLE_SPEED = 0.25 # Slower cycle
BODY_WOBBLE_AMOUNT = 0 # Ciao is rigid!

# Arms (Reduced swing)
RUN_UPPER_ARM_SWING = math.pi / 6.0; RUN_UPPER_ARM_WOBBLE_AMP = 0; RUN_UPPER_ARM_WOBBLE_SPEED = 0
RUN_FOREARM_SWING = math.pi / 5.0; RUN_FOREARM_WOBBLE_AMP = 0; RUN_FOREARM_WOBBLE_SPEED = 0
RUN_FOREARM_OFFSET_FACTOR = 0.1; JUMP_UPPER_ARM_BASE = -math.pi * 0.1; JUMP_UPPER_ARM_WOBBLE_AMP = 0
JUMP_UPPER_ARM_WOBBLE_SPEED = 0; JUMP_UPPER_ARM_VY_FACTOR = 0.01; JUMP_FOREARM_BASE = math.pi * 0.1
JUMP_FOREARM_WOBBLE_AMP = 0; JUMP_FOREARM_WOBBLE_SPEED = 0
# Legs (Reduced swing)
LEG_THIGH_SWING = math.pi / 7.0; LEG_SHIN_BEND_WALK = math.pi / 8.0; LEG_SHIN_BEND_SHIFT = math.pi / 2.5
KICK_THIGH_WINDUP_ANGLE = -math.pi / 4.0; KICK_THIGH_FOLLOW_ANGLE = math.pi * 0.6; KICK_SHIN_WINDUP_ANGLE = math.pi * 0.5
KICK_SHIN_IMPACT_ANGLE = -math.pi * 0.05; KICK_SHIN_FOLLOW_ANGLE = math.pi * 0.2; JUMP_THIGH_TUCK = math.pi * 0.1; JUMP_SHIN_TUCK = math.pi * 0.2

# Star Explosion (Unchanged)
PARTICLE_LIFESPAN = 1.0; PARTICLE_SPEED = 150; PARTICLE_COUNT = 12; PARTICLE_SIZE = 6

# --- Helper Functions ---
def draw_pentagon(surface, color, center, size, angle=0):
    points = [];
    for i in range(5): theta=math.pi/2.0+(2.0*math.pi*i/5.0)+angle; x=center[0]+size*math.cos(theta); y=center[1]+size*math.sin(theta); points.append((int(x),int(y)))
    pygame.draw.polygon(surface, color, points)

def normalize(v):
    mag_sq = v[0]**2 + v[1]**2;
    if mag_sq == 0: return (0,0)
    mag = math.sqrt(mag_sq); return (v[0]/mag, v[1]/mag)

def draw_rotated_rectangle(surface, color, rect_center, width, height, angle_rad):
    """Draws a filled rectangle rotated around its center using polygons."""
    # Calculate corners relative to center (0,0) before rotation
    # Note: We treat 'width' as the dimension along the angle, 'height' as perpendicular thickness
    half_w, half_h = width / 2, height / 2
    corners = [
        (-half_w, -half_h), ( half_w, -half_h),
        ( half_w,  half_h), (-half_w,  half_h)
    ]

    # Rotate and translate corners
    cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad)
    rotated_corners = []
    for x, y in corners:
        # Rotate point around origin (0,0)
        x_rot = x * cos_a - y * sin_a
        y_rot = x * sin_a + y * cos_a
        # Translate to the final center position
        rotated_corners.append((rect_center[0] + x_rot, rect_center[1] + y_rot))

    # Draw the polygon
    pygame.draw.polygon(surface, color, rotated_corners, 0) # Filled
    pygame.draw.polygon(surface, BLACK, rotated_corners, 1) # Outline

# --- Particle Class (Unchanged) ---
class Particle:
    def __init__(self, x, y):
        self.x = x; self.y = y; angle = random.uniform(0, 2 * math.pi); speed = random.uniform(PARTICLE_SPEED * 0.5, PARTICLE_SPEED * 1.5)
        self.vx = math.cos(angle) * speed; self.vy = math.sin(angle) * speed; self.lifespan = PARTICLE_LIFESPAN
        self.start_life = self.lifespan; self.size = PARTICLE_SIZE; self.color = random.choice([STAR_YELLOW, STAR_ORANGE, WHITE])
    def update(self, dt):
        self.x += self.vx * dt; self.y += self.vy * dt; self.vy += GRAVITY * 20 * dt
        self.lifespan -= dt; self.size = PARTICLE_SIZE * (self.lifespan / self.start_life)
        return self.lifespan > 0 and self.size > 1
    def draw(self, screen):
        if self.size > 0: pygame.draw.rect(screen, self.color, (int(self.x - self.size/2), int(self.y - self.size/2), int(self.size), int(self.size)))

# --- Stick Man Class (Modified for Ciao) ---
class StickMan:
    def __init__(self, x, y):
        self.x = x; self.y = y; self.base_y = y
        self.width = 20; self.height = 80 # Used for boundary checks, less relevant for drawing now
        self.vx = 0; self.vy = 0
        self.is_jumping = False; self.is_kicking = False; self.is_charging = False
        self.kick_timer = 0; self.kick_duration = 23
        self.charge_power = MIN_CHARGE_POWER; self.kick_charge_level = MIN_CHARGE_POWER
        self.walk_cycle_timer = 0.0
        self.kick_side = 'right'

        # --- Ciao Specific Appearance ---
        self.head_radius = 12 # Slightly larger head
        self.torso_length = 36 # Longer torso
        self.limb_width = 10   # Thickness of the blocks
        # Shorter, chunkier limbs
        self.upper_arm_length = 12
        self.forearm_length = 12
        self.thigh_length = 14
        self.shin_length = 14
        # Colors
        self.torso_colors = [ITALY_GREEN, ITALY_WHITE, ITALY_RED]
        # Define color patterns for limbs (can be adjusted)
        self.arm_colors = [ITALY_RED, ITALY_GREEN] # e.g., Upper=Red, Fore=Green
        self.leg_colors = [ITALY_WHITE, ITALY_RED]   # e.g., Thigh=White, Shin=Red
        # --- End Ciao Specific ---

        # Limb angles (in radians) - Same logic as before
        self.l_upper_arm_angle = 0; self.r_upper_arm_angle = 0
        self.l_forearm_angle = 0; self.r_forearm_angle = 0
        self.l_thigh_angle = 0; self.r_thigh_angle = 0
        self.l_shin_angle = 0; self.r_shin_angle = 0

        # Joint positions (calculated in update()) - Same logic as before
        self.head_pos = (0, 0); self.neck_pos = (0, 0); self.hip_pos = (0, 0)
        self.shoulder_pos = (0, 0); self.l_elbow_pos = (0, 0); self.r_elbow_pos = (0, 0)
        self.l_hand_pos = (0, 0); self.r_hand_pos = (0, 0); self.l_knee_pos = (0, 0)
        self.r_knee_pos = (0, 0); self.l_foot_pos = (0, 0); self.r_foot_pos = (0, 0)

    # --- Methods (move, stop_move, jump, start_charge, release_charge_and_kick, start_kick) ---
    # These remain functionally the same as before
    def move(self, direction):
        if not self.is_kicking: self.vx = direction * PLAYER_SPEED
    def stop_move(self): self.vx = 0
    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True; self.vy = JUMP_POWER; self.walk_cycle_timer = 0
        if self.is_charging: self.is_charging = False; self.charge_power = MIN_CHARGE_POWER
    def start_charge(self):
        if not self.is_kicking and not self.is_charging:
            self.is_charging = True; self.charge_power = MIN_CHARGE_POWER
    def release_charge_and_kick(self, ball_x):
        if self.is_charging:
            self.is_charging = False; self.kick_charge_level = self.charge_power
            self.charge_power = MIN_CHARGE_POWER; self.vx = 0
            self.kick_side = 'left' if ball_x < self.x else 'right'; self.start_kick()
    def start_kick(self):
        if not self.is_kicking:
            self.is_kicking = True; self.kick_timer = 0; self.vx = 0

    # --- Update Method ---
    # Calculation logic for angles and joint positions remains the same
    def update(self, dt):
        time_ms = pygame.time.get_ticks()
        if self.is_charging: self.charge_power = min(self.charge_power + CHARGE_RATE * dt, MAX_CHARGE_POWER)
        if not self.is_kicking: self.x += self.vx; self.x = max(self.limb_width / 2, min(self.x, SCREEN_WIDTH - self.limb_width / 2)) # Use limb_width for boundary
        if self.y < self.base_y or self.vy < 0: self.vy += GRAVITY; self.y += self.vy

        is_walking_on_ground = abs(self.vx) > 0 and not self.is_jumping and not self.is_kicking
        if is_walking_on_ground: self.walk_cycle_timer += WALK_CYCLE_SPEED
        elif not self.is_jumping and not self.is_kicking: self.walk_cycle_timer *= 0.9
        if abs(self.walk_cycle_timer) < 0.1: self.walk_cycle_timer = 0

        # --- Limb Angle Calculations (Using adjusted constants) ---
        if self.is_kicking:
            self.walk_cycle_timer = 0; self.kick_timer += 1; progress = min(self.kick_timer / self.kick_duration, 1.0)
            if progress < 0.3: thigh_prog_angle = KICK_THIGH_WINDUP_ANGLE * (progress / 0.3)
            elif progress < 0.6: thigh_prog_angle = KICK_THIGH_WINDUP_ANGLE + (KICK_THIGH_FOLLOW_ANGLE - KICK_THIGH_WINDUP_ANGLE) * ((progress - 0.3) / 0.3)
            else: thigh_prog_angle = KICK_THIGH_FOLLOW_ANGLE * (1.0 - (progress - 0.6) / 0.4)
            if progress < 0.4: shin_prog_angle = KICK_SHIN_WINDUP_ANGLE * (progress / 0.4)
            elif progress < 0.65: shin_prog_angle = KICK_SHIN_WINDUP_ANGLE + (KICK_SHIN_IMPACT_ANGLE - KICK_SHIN_WINDUP_ANGLE) * ((progress - 0.4) / 0.25)
            else: shin_prog_angle = KICK_SHIN_IMPACT_ANGLE + (KICK_SHIN_FOLLOW_ANGLE - KICK_SHIN_IMPACT_ANGLE) * ((progress - 0.65) / 0.35)
            if self.kick_side == 'right':
                self.r_thigh_angle = thigh_prog_angle; self.r_shin_angle = shin_prog_angle
                self.l_thigh_angle = -thigh_prog_angle * 0.1; self.l_shin_angle = 0.1
            else:
                self.l_thigh_angle = thigh_prog_angle; self.l_shin_angle = shin_prog_angle
                self.r_thigh_angle = -thigh_prog_angle * 0.1; self.r_shin_angle = 0.1
            self.l_upper_arm_angle = -thigh_prog_angle * 0.05 if self.kick_side == 'right' else thigh_prog_angle * 0.03
            self.r_upper_arm_angle = thigh_prog_angle * 0.03 if self.kick_side == 'right' else -thigh_prog_angle * 0.05
            self.l_forearm_angle = 0.1; self.r_forearm_angle = 0.1
            if self.kick_timer >= self.kick_duration:
                self.is_kicking = False; self.kick_timer = 0; self.r_thigh_angle = 0; self.l_thigh_angle = 0
                self.r_shin_angle = 0; self.l_shin_angle = 0; self.l_upper_arm_angle = 0; self.r_upper_arm_angle = 0
                self.l_forearm_angle = 0; self.r_forearm_angle = 0; self.kick_charge_level = MIN_CHARGE_POWER
        else:
            if is_walking_on_ground:
                walk_sin = math.sin(self.walk_cycle_timer)
                self.l_upper_arm_angle = RUN_UPPER_ARM_SWING * walk_sin
                self.r_upper_arm_angle = -RUN_UPPER_ARM_SWING * walk_sin
                self.l_forearm_angle = RUN_FOREARM_SWING * math.sin(self.walk_cycle_timer - RUN_FOREARM_OFFSET_FACTOR)
                self.r_forearm_angle = -RUN_FOREARM_SWING * math.sin(self.walk_cycle_timer - RUN_FOREARM_OFFSET_FACTOR)
                self.l_thigh_angle = -LEG_THIGH_SWING * walk_sin
                self.r_thigh_angle = LEG_THIGH_SWING * walk_sin
                shin_bend = LEG_SHIN_BEND_WALK * max(0, math.sin(self.walk_cycle_timer + LEG_SHIN_BEND_SHIFT))
                self.l_shin_angle = shin_bend if self.l_thigh_angle < 0 else 0.1
                self.r_shin_angle = shin_bend if self.r_thigh_angle < 0 else 0.1
            elif self.is_jumping:
                base_up_angle = JUMP_UPPER_ARM_BASE - self.vy * JUMP_UPPER_ARM_VY_FACTOR
                self.l_upper_arm_angle = base_up_angle; self.r_upper_arm_angle = base_up_angle
                base_fore_angle = JUMP_FOREARM_BASE
                self.l_forearm_angle = base_fore_angle; self.r_forearm_angle = base_fore_angle
                jump_progress = max(0, min(1, 1 - (self.y / self.base_y)))
                thigh_tuck = JUMP_THIGH_TUCK * jump_progress; shin_tuck = JUMP_SHIN_TUCK * jump_progress
                self.l_thigh_angle = thigh_tuck; self.r_thigh_angle = thigh_tuck
                self.l_shin_angle = shin_tuck; self.r_shin_angle = shin_tuck
            elif self.is_charging:
                 charge_crouch = (self.charge_power - MIN_CHARGE_POWER) / (MAX_CHARGE_POWER - MIN_CHARGE_POWER)
                 squat_angle = math.pi * 0.05 * charge_crouch; self.l_thigh_angle = squat_angle; self.r_thigh_angle = squat_angle
                 self.l_shin_angle = squat_angle * 1.5; self.r_shin_angle = squat_angle * 1.5
                 self.l_upper_arm_angle = squat_angle; self.r_upper_arm_angle = squat_angle
                 self.l_forearm_angle = math.pi * 0.1; self.r_forearm_angle = math.pi * 0.1
            else: # Idle
                 self.l_upper_arm_angle = 0; self.r_upper_arm_angle = 0; self.l_forearm_angle = 0; self.r_forearm_angle = 0
                 self.l_thigh_angle = 0; self.r_thigh_angle = 0; self.l_shin_angle = 0; self.r_shin_angle = 0

        # --- Calculate Joint Positions (Mostly unchanged logic) ---
        current_y = self.y; current_x = self.x; wobble_offset = 0
        # Ciao-specific adjustment: Calculate hip based on actual leg block position
        # Assuming foot_y is the lowest point, calculate hip based on that + total leg length
        total_leg_visual_height = self.thigh_length + self.shin_length # Approx vertical height when standing straight
        self.hip_pos = (current_x, current_y - total_leg_visual_height) # Adjust hip based on visual leg height
        upper_body_x = current_x + wobble_offset # Wobble is 0 now
        self.neck_pos = (upper_body_x, self.hip_pos[1] - self.torso_length)
        self.head_pos = (upper_body_x, self.neck_pos[1] - self.head_radius)
        self.shoulder_pos = self.neck_pos # Shoulders same as neck

        # Left arm
        l_elbow_x = self.shoulder_pos[0] + self.upper_arm_length * math.sin(self.l_upper_arm_angle)
        l_elbow_y = self.shoulder_pos[1] + self.upper_arm_length * math.cos(self.l_upper_arm_angle)
        self.l_elbow_pos = (l_elbow_x, l_elbow_y)
        l_hand_angle_world = self.l_upper_arm_angle + self.l_forearm_angle
        l_hand_x = self.l_elbow_pos[0] + self.forearm_length * math.sin(l_hand_angle_world)
        l_hand_y = self.l_elbow_pos[1] + self.forearm_length * math.cos(l_hand_angle_world)
        self.l_hand_pos = (l_hand_x, l_hand_y)
        # Right arm
        r_elbow_x = self.shoulder_pos[0] + self.upper_arm_length * math.sin(self.r_upper_arm_angle)
        r_elbow_y = self.shoulder_pos[1] + self.upper_arm_length * math.cos(self.r_upper_arm_angle)
        self.r_elbow_pos = (r_elbow_x, r_elbow_y)
        r_hand_angle_world = self.r_upper_arm_angle + self.r_forearm_angle
        r_hand_x = self.r_elbow_pos[0] + self.forearm_length * math.sin(r_hand_angle_world)
        r_hand_y = self.r_elbow_pos[1] + self.forearm_length * math.cos(r_hand_angle_world)
        self.r_hand_pos = (r_hand_x, r_hand_y)
        # Left leg
        l_knee_x = self.hip_pos[0] + self.thigh_length * math.sin(self.l_thigh_angle)
        l_knee_y = self.hip_pos[1] + self.thigh_length * math.cos(self.l_thigh_angle)
        self.l_knee_pos = (l_knee_x, l_knee_y)
        l_foot_angle_world = self.l_thigh_angle + self.l_shin_angle
        l_foot_x = self.l_knee_pos[0] + self.shin_length * math.sin(l_foot_angle_world)
        l_foot_y = self.l_knee_pos[1] + self.shin_length * math.cos(l_foot_angle_world)
        # Right leg
        r_knee_x = self.hip_pos[0] + self.thigh_length * math.sin(self.r_thigh_angle)
        r_knee_y = self.hip_pos[1] + self.thigh_length * math.cos(self.r_thigh_angle)
        self.r_knee_pos = (r_knee_x, r_knee_y)
        r_foot_angle_world = self.r_thigh_angle + self.r_shin_angle
        r_foot_x = self.r_knee_pos[0] + self.shin_length * math.sin(r_foot_angle_world)
        r_foot_y = self.r_knee_pos[1] + self.shin_length * math.cos(r_foot_angle_world)

        # Grounding Logic (Adjusted slightly for Ciao's block feet)
        ground = self.base_y
        lowest_foot_y = max(l_foot_y, r_foot_y) # Find the lower foot

        if self.y >= ground and self.vy >= 0: # If feet are potentially below ground and falling/still
             if not self.is_kicking: # Don't interrupt kick landing
                 y_offset = lowest_foot_y - ground # How much feet are below ground
                 self.y -= y_offset # Move entire body up
                 # Recalculate all joint positions after adjusting self.y
                 # (This might ideally be done iteratively, but a single adjustment is simpler)
                 # Or simply snap y to ground and recalculate next frame. Let's snap.
                 self.y = ground
                 self.is_jumping = False; self.vy = 0
                 # Re-calculate foot positions based on grounded self.y and angles
                 l_knee_x = self.hip_pos[0] + self.thigh_length * math.sin(self.l_thigh_angle)
                 l_knee_y = self.hip_pos[1] + self.thigh_length * math.cos(self.l_thigh_angle)
                 l_foot_angle_world = self.l_thigh_angle + self.l_shin_angle
                 l_foot_x = l_knee_x + self.shin_length * math.sin(l_foot_angle_world)
                 l_foot_y = l_knee_y + self.shin_length * math.cos(l_foot_angle_world)
                 r_knee_x = self.hip_pos[0] + self.thigh_length * math.sin(self.r_thigh_angle)
                 r_knee_y = self.hip_pos[1] + self.thigh_length * math.cos(self.r_thigh_angle)
                 r_foot_angle_world = self.r_thigh_angle + self.r_shin_angle
                 r_foot_x = r_knee_x + self.shin_length * math.sin(r_foot_angle_world)
                 r_foot_y = r_knee_y + self.shin_length * math.cos(r_foot_angle_world)
                 self.l_foot_pos = (l_foot_x, ground) # Snap feet to ground visually
                 self.r_foot_pos = (r_foot_x, ground)
        else:
             # Keep calculated foot positions if airborne
             self.l_foot_pos = (l_foot_x, l_foot_y)
             self.r_foot_pos = (r_foot_x, r_foot_y)


    # --- Getters (Unchanged) ---
    def get_kick_impact_point(self):
        if self.is_kicking:
            progress = self.kick_timer / self.kick_duration
            if 0.4 < progress < 0.65:
                return self.l_foot_pos if self.kick_side == 'left' else self.r_foot_pos
        return None
    def get_head_position_radius(self):
        return self.head_pos, self.head_radius

    # --- Draw Method (Completely Rewritten for Ciao) ---
    def draw(self, screen):
        # Charge Bar (Draw first)
        if self.is_charging:
            bar_width = 50; bar_height = 8
            bar_x = self.head_pos[0] - bar_width / 2
            bar_y = self.head_pos[1] - self.head_radius - bar_height - 5
            fill_ratio = (self.charge_power - MIN_CHARGE_POWER) / (MAX_CHARGE_POWER - MIN_CHARGE_POWER)
            fill_width = bar_width * max(0, min(1, fill_ratio))
            pygame.draw.rect(screen, BLACK, (bar_x - 1, bar_y - 1, bar_width + 2, bar_height + 2), 1)
            pygame.draw.rect(screen, YELLOW, (bar_x, bar_y, fill_width, bar_height))

        # --- Draw Head (Soccer Ball) ---
        head_center_int = (int(self.head_pos[0]), int(self.head_pos[1]))
        pygame.draw.circle(screen, ITALY_WHITE, head_center_int, self.head_radius, 0)
        # Draw some pentagons (adjust size/angle as needed)
        draw_pentagon(screen, BLACK, head_center_int, self.head_radius * 0.6, angle=0.1)
        draw_pentagon(screen, BLACK, head_center_int, self.head_radius * 0.3, angle=math.pi/5 + 0.1) # Rotated slightly
        pygame.draw.circle(screen, BLACK, head_center_int, self.head_radius, 1) # Outline

        # --- Draw Torso (3 Colored Rectangles) ---
        torso_segment_height = self.torso_length / 3
        current_torso_y = self.neck_pos[1]
        for i in range(3):
            rect_center_x = self.neck_pos[0] # Torso doesn't rotate
            rect_center_y = current_torso_y + torso_segment_height / 2
            # Use the helper function (width = limb_width, height = segment_height, angle = 0)
            draw_rotated_rectangle(screen, self.torso_colors[i],
                                  (rect_center_x, rect_center_y),
                                  self.limb_width, torso_segment_height, 0)
            current_torso_y += torso_segment_height

        # --- Draw Limbs using Rotated Rectangles ---
        # Helper function to draw one limb segment
        def draw_limb_segment(start_pos, end_pos, length, color):
            center_x = (start_pos[0] + end_pos[0]) / 2
            center_y = (start_pos[1] + end_pos[1]) / 2
            dx = end_pos[0] - start_pos[0]
            dy = end_pos[1] - start_pos[1]
            # Use actual calculated length for drawing robustness
            draw_length = math.hypot(dx, dy)
            if draw_length < 1: draw_length = 1 # Avoid zero division/size
            angle = math.atan2(dy, dx) # Angle relative to horizontal right

            # Call the main draw function (length along angle, width is thickness)
            draw_rotated_rectangle(screen, color,
                                  (center_x, center_y),
                                  draw_length, self.limb_width, angle)

        # Arms
        draw_limb_segment(self.shoulder_pos, self.l_elbow_pos, self.upper_arm_length, self.arm_colors[0]) # Left Upper
        draw_limb_segment(self.l_elbow_pos, self.l_hand_pos, self.forearm_length, self.arm_colors[1])    # Left Forearm
        draw_limb_segment(self.shoulder_pos, self.r_elbow_pos, self.upper_arm_length, self.arm_colors[0]) # Right Upper
        draw_limb_segment(self.r_elbow_pos, self.r_hand_pos, self.forearm_length, self.arm_colors[1])    # Right Forearm

        # Legs
        draw_limb_segment(self.hip_pos, self.l_knee_pos, self.thigh_length, self.leg_colors[0])      # Left Thigh
        draw_limb_segment(self.l_knee_pos, self.l_foot_pos, self.shin_length, self.leg_colors[1])       # Left Shin
        draw_limb_segment(self.hip_pos, self.r_knee_pos, self.thigh_length, self.leg_colors[0])      # Right Thigh
        draw_limb_segment(self.r_knee_pos, self.r_foot_pos, self.shin_length, self.leg_colors[1])       # Right Shin


# --- Ball Class (Unchanged from previous working version) ---
class Ball:
    def __init__(self, x, y, radius):
        self.x = x; self.y = y; self.radius = radius
        self.vx = 0; self.vy = 0
        self.last_hit_by = None; self.rotation_angle = 0
    def apply_force(self, force_x, force_y, hitter='player'):
        self.vx += force_x; self.vy += force_y
        self.last_hit_by = hitter
    def update(self, dt):
        self.rotation_angle += self.vx * 0.02; self.rotation_angle %= (2 * math.pi)
        self.vy += GRAVITY; self.vx *= BALL_FRICTION
        self.x += self.vx; self.y += self.vy
        hit_ground = False # Flag to return if ground was hit *this frame*
        if self.y + self.radius >= GROUND_Y:
            if self.vy >= 0: # Only bounce/stop if moving downwards or resting
                 hit_ground = True
            self.y = GROUND_Y - self.radius; self.vy *= -BALL_BOUNCE; self.vx *= 0.9
            if abs(self.vy) < 1: self.vy = 0 # Stop bouncing if speed is low
        if self.x + self.radius >= SCREEN_WIDTH: self.x = SCREEN_WIDTH-self.radius; self.vx *= -BALL_BOUNCE*0.8
        elif self.x - self.radius <= 0: self.x = self.radius; self.vx *= -BALL_BOUNCE*0.8
        if abs(self.vx) < 0.1 and self.y + self.radius >= GROUND_Y - 1: self.vx = 0 # Stop sliding
        return hit_ground # Return the flag

    def is_on_ground(self):
        """Checks if the ball is resting on or very close to the ground."""
        return self.y + self.radius >= GROUND_Y - 0.5 # Use a small tolerance

    def draw(self, screen):
        center=(int(self.x), int(self.y))
        pygame.draw.circle(screen, WHITE, center, self.radius) # Use standard white for ball
        pent_sz=self.radius*0.45; off_d=self.radius*0.6
        for i in range(3):
            a=self.rotation_angle+(i*2*math.pi/3); px=center[0]+off_d*math.cos(a); py=center[1]+off_d*math.sin(a)
            draw_pentagon(screen,BLACK,(px,py),pent_sz,self.rotation_angle*1.5)
        pygame.draw.circle(screen,BLACK,center,self.radius,1)


# --- Game Setup ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ciao Kick!") # Updated Caption
clock = pygame.time.Clock()
player = StickMan(SCREEN_WIDTH // 4, GROUND_Y)
ball = Ball(SCREEN_WIDTH // 2, GROUND_Y - 20, 15)
font_large = pygame.font.Font(None, 50)
font_medium = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 28)

# --- Score Variables (Unchanged) ---
current_max_height = 0.0
current_hit_count = 0
high_score = 0
high_score_max_height = 0.0
high_score_hit_count = 0
ball_was_on_ground = True

particles = []
can_headbutt = True

# --- Off-screen Arrow Function (Unchanged) ---
def draw_offscreen_arrow(s, ball, p_pos):
    ar_sz = 15; pad = 25; is_off = False
    tx, ty = ball.x, ball.y
    ax = max(pad, min(ball.x, SCREEN_WIDTH - pad))
    ay = max(pad, min(ball.y, SCREEN_HEIGHT - pad))
    if ball.x < 0 or ball.x > SCREEN_WIDTH: ax = pad if ball.x < 0 else SCREEN_WIDTH - pad; is_off = True
    if ball.y < 0 or ball.y > SCREEN_HEIGHT: ay = pad if ball.y < 0 else SCREEN_HEIGHT - pad; is_off = True
    if not is_off: return
    ang = math.atan2(ty - ay, tx - ax)
    p1 = (ar_sz, 0); p2 = (-ar_sz / 2, -ar_sz / 2); p3 = (-ar_sz / 2, ar_sz / 2)
    cos_a, sin_a = math.cos(ang), math.sin(ang)
    p1r = (p1[0] * cos_a - p1[1] * sin_a, p1[0] * sin_a + p1[1] * cos_a)
    p2r = (p2[0] * cos_a - p2[1] * sin_a, p2[0] * sin_a + p2[1] * cos_a)
    p3r = (p3[0] * cos_a - p3[1] * sin_a, p3[0] * sin_a + p3[1] * cos_a)
    pts = [(ax + p1r[0], ay + p1r[1]), (ax + p2r[0], ay + p2r[1]), (ax + p3r[0], ay + p3r[1])]
    pygame.draw.polygon(s, ARROW_RED, [(int(p[0]), int(p[1])) for p in pts])

# --- Main Game Loop ---
running = True
while running:
    dt = clock.tick(FPS) / 1000.0
    dt = min(dt, 0.1)
    # Event Handling (Unchanged)
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT: player.move(-1)
            elif event.key == pygame.K_RIGHT: player.move(1)
            elif event.key == pygame.K_UP: player.jump()
            elif event.key == pygame.K_SPACE: player.start_charge()
            elif event.key == pygame.K_ESCAPE: running = False
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT and player.vx < 0: player.stop_move()
            elif event.key == pygame.K_RIGHT and player.vx > 0: player.stop_move()
            elif event.key == pygame.K_SPACE: player.release_charge_and_kick(ball.x)

    # Updates (Unchanged)
    player.update(dt)
    ball_hit_ground_this_frame = ball.update(dt)
    particles = [p for p in particles if p.update(dt)]

    # Score / Height Tracking Logic (Unchanged)
    is_ball_airborne = not ball.is_on_ground()
    if is_ball_airborne:
        current_height_pixels = max(0, GROUND_Y - (ball.y + ball.radius))
        current_max_height = max(current_max_height, current_height_pixels)
        ball_was_on_ground = False
    elif ball_hit_ground_this_frame:
        if not ball_was_on_ground:
            final_sequence_score = int(current_max_height * current_hit_count)
            if final_sequence_score > high_score:
                high_score = final_sequence_score
                high_score_max_height = current_max_height
                high_score_hit_count = current_hit_count
            current_max_height = 0.0; current_hit_count = 0
        ball_was_on_ground = True
    display_score = int(current_max_height * current_hit_count)

    # Collision & Score (Unchanged)
    score_increased_this_frame = False
    kick_point = player.get_kick_impact_point()
    if kick_point:
        dist_x = kick_point[0] - ball.x; dist_y = kick_point[1] - ball.y
        dist_sq = dist_x**2 + dist_y**2; kick_rad = 13 # Kick radius might need tuning
        if dist_sq < (ball.radius + kick_rad)**2:
             if player.kick_timer < (player.kick_duration * 0.65):
                 kick_x_base = BASE_KICK_FORCE_X
                 if player.kick_side == "left": kick_x_base = -kick_x_base
                 kick_x = kick_x_base * player.kick_charge_level
                 kick_y = BASE_KICK_FORCE_Y * player.kick_charge_level
                 if player.vy < 0: kick_y += player.vy * 0.3
                 ball.apply_force(kick_x, kick_y)
                 if is_ball_airborne: current_hit_count += 1; score_increased_this_frame = True
    head_pos, head_radius = player.get_head_position_radius()
    dist_x_head = ball.x - head_pos[0]; dist_y_head = ball.y - head_pos[1]
    dist_head_sq = dist_x_head**2 + dist_y_head**2
    headbutt_cooldown_applied = False
    if dist_head_sq < (ball.radius + head_radius)**2:
        if can_headbutt:
            force_y = -HEADBUTT_UP_FORCE
            if player.vy < 0: force_y -= abs(player.vy) * HEADBUTT_VY_MULTIPLIER
            force_x = player.vx * HEADBUTT_PLAYER_VX_FACTOR - dist_x_head * HEADBUTT_POS_X_FACTOR
            ball.apply_force(force_x, force_y)
            can_headbutt = False; headbutt_cooldown_applied = True
            if is_ball_airborne: current_hit_count += 1; score_increased_this_frame = True
    if not headbutt_cooldown_applied:
        if dist_head_sq > (ball.radius + head_radius + 15) ** 2: can_headbutt = True

    # Trigger Star Explosion (Use Particle Class)
    if score_increased_this_frame and kick_point and current_hit_count > 0 and current_hit_count % 5 == 0:
        num_kick_particles = PARTICLE_COUNT // 2 # Fewer particles for blocky style maybe?
        for _ in range(num_kick_particles):
            particle_x = kick_point[0] + random.uniform(-5, 5)
            particle_y = kick_point[1] + random.uniform(-5, 5)
            particles.append(Particle(particle_x, particle_y)) # Use the Particle class

    # --- Drawing ---
    screen.fill(SKY_BLUE)
    pygame.draw.rect(screen, GRASS_GREEN, (0, GROUND_Y, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y))
    for p in particles: p.draw(screen)
    # Draw Ciao!
    player.draw(screen)
    ball.draw(screen)
    draw_offscreen_arrow(screen, ball, (player.x, player.y))

    # Draw Scores (Unchanged)
    score_text = f"{display_score}"; score_surf = font_large.render(score_text, True, TEXT_COLOR); score_rect = score_surf.get_rect(centerx=SCREEN_WIDTH // 2, top=10); screen.blit(score_surf, score_rect)
    if high_score > 0: high_score_text = f"Best: {high_score} ({high_score_max_height:.0f}px * {high_score_hit_count} hits)"
    else: high_score_text = f"Best: {high_score}"
    high_score_surf = font_medium.render(high_score_text, True, TEXT_COLOR); high_score_rect = high_score_surf.get_rect(topright=(SCREEN_WIDTH - 15, 10)); screen.blit(high_score_surf, high_score_rect)
    height_text = f"Max H: {current_max_height:.0f}"; height_surf = font_small.render(height_text, True, TEXT_COLOR); height_rect = height_surf.get_rect(topleft=(15, 10)); screen.blit(height_surf, height_rect)
    hits_text = f"Hits: {current_hit_count}"; hits_surf = font_small.render(hits_text, True, TEXT_COLOR); hits_rect = hits_surf.get_rect(topleft=(15, 10 + height_rect.height + 2)); screen.blit(hits_surf, hits_rect)

    # Headbutt Cooldown Indicator (Draw last)
    if not can_headbutt:
        cooldown_color = (255, 0, 0, 180) # Semi-transparent red
        cooldown_radius = 5
        head_x, head_y = player.head_pos
        indicator_x = int(head_x)
        indicator_y = int(head_y - player.head_radius - cooldown_radius - 2)
        # Draw a simple circle, could be improved
        temp_surf = pygame.Surface((cooldown_radius*2, cooldown_radius*2), pygame.SRCALPHA)
        pygame.draw.circle(temp_surf, cooldown_color, (cooldown_radius, cooldown_radius), cooldown_radius)
        screen.blit(temp_surf, (indicator_x - cooldown_radius, indicator_y - cooldown_radius))


    pygame.display.flip()

# Cleanup
pygame.quit()
sys.exit()