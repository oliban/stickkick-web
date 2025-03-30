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
GRASS_GREEN = (34, 139, 34)
RED = (200, 0, 0)
YELLOW = (255, 255, 0)
TEXT_COLOR = (10, 10, 50)
ARROW_RED = (255, 50, 50)
STAR_YELLOW = (255, 255, 100)
STAR_ORANGE = (255, 180, 0)
DEBUG_BLUE = (0, 0, 255) # For highlighting the kicking leg

# Physics
GRAVITY = 0.5
PLAYER_SPEED = 5
JUMP_POWER = -12
BASE_KICK_FORCE_X = 14 # Increased horizontal force
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

# Animation
WALK_CYCLE_SPEED = 0.3
BODY_WOBBLE_AMOUNT = 0 #Disable body wobble - important for the blocky look

# Arms
RUN_UPPER_ARM_SWING = math.pi / 3.5; RUN_UPPER_ARM_WOBBLE_AMP = math.pi / 5; RUN_UPPER_ARM_WOBBLE_SPEED = 2.1
RUN_FOREARM_SWING = math.pi / 3.0; RUN_FOREARM_WOBBLE_AMP = math.pi / 4; RUN_FOREARM_WOBBLE_SPEED = 3.5
RUN_FOREARM_OFFSET_FACTOR = 0.3; JUMP_UPPER_ARM_BASE = -math.pi * 0.4; JUMP_UPPER_ARM_WOBBLE_AMP = math.pi / 3.5
JUMP_UPPER_ARM_WOBBLE_SPEED = 0.012; JUMP_UPPER_ARM_VY_FACTOR = 0.04; JUMP_FOREARM_BASE = math.pi * 0.2
JUMP_FOREARM_WOBBLE_AMP = math.pi / 2.5; JUMP_FOREARM_WOBBLE_SPEED = 0.025
# Legs
LEG_THIGH_SWING = math.pi / 4.0; LEG_SHIN_BEND_WALK = math.pi / 3.5; LEG_SHIN_BEND_SHIFT = math.pi / 2.5
KICK_THIGH_WINDUP_ANGLE = -math.pi / 3.0; KICK_THIGH_FOLLOW_ANGLE = math.pi * 0.8; KICK_SHIN_WINDUP_ANGLE = math.pi * 0.6
KICK_SHIN_IMPACT_ANGLE = -math.pi * 0.1; KICK_SHIN_FOLLOW_ANGLE = math.pi * 0.3; JUMP_THIGH_TUCK = math.pi * 0.3; JUMP_SHIN_TUCK = math.pi * 0.4

# Star Explosion
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

# --- Particle Class ---
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

# --- Stick Man Class ---
class StickMan:
    def __init__(self, x, y):
        self.x = x; self.y = y; self.base_y = y
        self.width = 20; self.height = 80
        self.vx = 0; self.vy = 0
        self.is_jumping = False; self.is_kicking = False; self.is_charging = False
        self.kick_timer = 0; self.kick_duration = 23
        self.charge_power = MIN_CHARGE_POWER; self.kick_charge_level = MIN_CHARGE_POWER
        self.walk_cycle_timer = 0.0
        self.kick_side = 'right'  # Which leg is kicking

        # Body part lengths
        self.head_radius = 10
        self.torso_length = 30
        self.upper_arm_length = 15
        self.forearm_length = 15
        self.thigh_length = 18
        self.shin_length = 18
        self.leg_length = self.thigh_length + self.shin_length

        # Limb angles (in radians)
        self.l_upper_arm_angle = 0
        self.r_upper_arm_angle = 0
        self.l_forearm_angle = 0
        self.r_forearm_angle = 0
        self.l_thigh_angle = 0
        self.r_thigh_angle = 0
        self.l_shin_angle = 0
        self.r_shin_angle = 0

        # Joint positions (calculated in update())
        self.head_pos = (0, 0)
        self.neck_pos = (0, 0)
        self.hip_pos = (0, 0)
        self.shoulder_pos = (0, 0)
        self.l_elbow_pos = (0, 0)
        self.r_elbow_pos = (0, 0)
        self.l_hand_pos = (0, 0)
        self.r_hand_pos = (0, 0)
        self.l_knee_pos = (0, 0)
        self.r_knee_pos = (0, 0)
        self.l_foot_pos = (0, 0)
        self.r_foot_pos = (0, 0)

    def move(self, direction):
        """
        Moves the stickman horizontally.

        Args:
            direction (int): -1 for left, 1 for right.
        """
        if not self.is_kicking:
            self.vx = direction * PLAYER_SPEED

    def stop_move(self):
        """Stops the stickman's horizontal movement."""
        self.vx = 0

    def jump(self):
        """Makes the stickman jump."""
        if not self.is_jumping:
            self.is_jumping = True
            self.vy = JUMP_POWER
            self.walk_cycle_timer = 0
        if self.is_charging:
            self.is_charging = False
            self.charge_power = MIN_CHARGE_POWER

    def start_charge(self):
        """Starts charging for a kick."""
        if not self.is_kicking and not self.is_charging:
            self.is_charging = True
            self.charge_power = MIN_CHARGE_POWER

    def release_charge_and_kick(self, ball_x):
        """Releases the charge and initiates a kick."""
        if self.is_charging:
            self.is_charging = False
            self.kick_charge_level = self.charge_power
            self.charge_power = MIN_CHARGE_POWER
            self.vx = 0
            self.kick_side = 'left' if ball_x < self.x else 'right'
            self.start_kick()

    def start_kick(self):
        """Starts the kick animation and prepares for the kick."""
        if not self.is_kicking:
            self.is_kicking = True
            self.kick_timer = 0
            self.vx = 0

    def update(self, dt):
        """
        Updates the stickman's state (position, animation, etc.).

        Args:
            dt (float): The time delta since the last update (seconds).
        """
        time_ms = pygame.time.get_ticks()

        # Charging logic
        if self.is_charging:
            self.charge_power = min(self.charge_power + CHARGE_RATE * dt, MAX_CHARGE_POWER)

        # Horizontal movement
        if not self.is_kicking:
            self.x += self.vx
            self.x = max(self.width / 2, min(self.x, SCREEN_WIDTH - self.width / 2))

        # Vertical movement (jumping/falling)
        if self.y < self.base_y or self.vy < 0:
            self.vy += GRAVITY
            self.y += self.vy

        # Walking animation cycle
        is_walking_on_ground = abs(self.vx) > 0 and not self.is_jumping and not self.is_kicking
        if is_walking_on_ground:
            self.walk_cycle_timer += WALK_CYCLE_SPEED
        elif not self.is_jumping and not self.is_kicking:
            self.walk_cycle_timer *= 0.9  # Slow down walk cycle if not walking

        if abs(self.walk_cycle_timer) < 0.1:
            self.walk_cycle_timer = 0

        # Limb Angle Calculations
        if self.is_kicking:
            # Kick animation logic
            self.walk_cycle_timer = 0
            self.kick_timer += 1
            progress = min(self.kick_timer / self.kick_duration, 1.0)

            # Calculate thigh and shin angles based on kick progress
            if progress < 0.3:
                thigh_prog_angle = KICK_THIGH_WINDUP_ANGLE * (progress / 0.3)
            elif progress < 0.6:
                thigh_prog_angle = KICK_THIGH_WINDUP_ANGLE + (KICK_THIGH_FOLLOW_ANGLE - KICK_THIGH_WINDUP_ANGLE) * ((progress - 0.3) / 0.3)
            else:
                thigh_prog_angle = KICK_THIGH_FOLLOW_ANGLE * (1.0 - (progress - 0.6) / 0.4)

            if progress < 0.4:
                shin_prog_angle = KICK_SHIN_WINDUP_ANGLE * (progress / 0.4)
            elif progress < 0.65:
                shin_prog_angle = KICK_SHIN_WINDUP_ANGLE + (KICK_SHIN_IMPACT_ANGLE - KICK_SHIN_WINDUP_ANGLE) * ((progress - 0.4) / 0.25)
            else:
                shin_prog_angle = KICK_SHIN_IMPACT_ANGLE + (KICK_SHIN_FOLLOW_ANGLE - KICK_SHIN_IMPACT_ANGLE) * ((progress - 0.65) / 0.35)

            # Apply angles based on which leg is kicking
            if self.kick_side == 'right':
                self.r_thigh_angle = thigh_prog_angle
                self.r_shin_angle = shin_prog_angle
                self.l_thigh_angle = -thigh_prog_angle * 0.1
                self.l_shin_angle = 0.1
            else:
                self.l_thigh_angle = thigh_prog_angle
                self.l_shin_angle = shin_prog_angle
                self.r_thigh_angle = -thigh_prog_angle * 0.1
                self.r_shin_angle = 0.1

            # Arm angles during the kick
            self.l_upper_arm_angle = -thigh_prog_angle * 0.05 if self.kick_side == 'right' else thigh_prog_angle * 0.03
            self.r_upper_arm_angle = thigh_prog_angle * 0.03 if self.kick_side == 'right' else -thigh_prog_angle * 0.05
            self.l_forearm_angle = 0.1
            self.r_forearm_angle = 0.1

            if self.kick_timer >= self.kick_duration:
                # Kick animation finished
                self.is_kicking = False
                self.kick_timer = 0
                self.r_thigh_angle = 0
                self.l_thigh_angle = 0
                self.r_shin_angle = 0
                self.l_shin_angle = 0
                self.l_upper_arm_angle = 0
                self.r_upper_arm_angle = 0
                self.l_forearm_angle = 0
                self.r_forearm_angle = 0
                self.kick_charge_level = MIN_CHARGE_POWER
        else:
            # Not kicking - Walking or Jumping animation logic
            if is_walking_on_ground:
                # Walking animation
                walk_sin = math.sin(self.walk_cycle_timer)
                up_wobble_l = math.sin(self.walk_cycle_timer * RUN_UPPER_ARM_WOBBLE_SPEED)
                up_wobble_r = math.sin(self.walk_cycle_timer * RUN_UPPER_ARM_WOBBLE_SPEED + math.pi / 1.5)
                self.l_upper_arm_angle = RUN_UPPER_ARM_SWING * walk_sin + RUN_UPPER_ARM_WOBBLE_AMP * up_wobble_l
                self.r_upper_arm_angle = -RUN_UPPER_ARM_SWING * walk_sin + RUN_UPPER_ARM_WOBBLE_AMP * up_wobble_r

                fore_wobble_l = math.sin(self.walk_cycle_timer * RUN_FOREARM_WOBBLE_SPEED + math.pi / 3)
                fore_wobble_r = math.sin(self.walk_cycle_timer * RUN_FOREARM_WOBBLE_SPEED + math.pi)
                self.l_forearm_angle = RUN_FOREARM_SWING * math.sin(self.walk_cycle_timer - RUN_FOREARM_OFFSET_FACTOR) + RUN_FOREARM_WOBBLE_AMP * fore_wobble_l
                self.r_forearm_angle = -RUN_FOREARM_SWING * math.sin(self.walk_cycle_timer - RUN_FOREARM_OFFSET_FACTOR) + RUN_FOREARM_WOBBLE_AMP * fore_wobble_r

                self.l_thigh_angle = -LEG_THIGH_SWING * walk_sin
                self.r_thigh_angle = LEG_THIGH_SWING * walk_sin
                shin_bend = LEG_SHIN_BEND_WALK * max(0, math.sin(self.walk_cycle_timer + LEG_SHIN_BEND_SHIFT))
                self.l_shin_angle = shin_bend if self.l_thigh_angle < 0 else 0.1
                self.r_shin_angle = shin_bend if self.r_thigh_angle < 0 else 0.1
            elif self.is_jumping:
                # Jumping animation
                up_jump_wobble = math.sin(time_ms * JUMP_UPPER_ARM_WOBBLE_SPEED)
                base_up_angle = JUMP_UPPER_ARM_BASE + JUMP_UPPER_ARM_WOBBLE_AMP * up_jump_wobble - self.vy * JUMP_UPPER_ARM_VY_FACTOR
                self.l_upper_arm_angle = base_up_angle + random.uniform(-0.2, 0.2)
                self.r_upper_arm_angle = base_up_angle + random.uniform(-0.2, 0.2)

                fore_jump_wobble = math.sin(time_ms * JUMP_FOREARM_WOBBLE_SPEED)
                base_fore_angle = JUMP_FOREARM_BASE + JUMP_FOREARM_WOBBLE_AMP * fore_jump_wobble
                self.l_forearm_angle = base_fore_angle + random.uniform(-0.3, 0.3)
                self.r_forearm_angle = base_fore_angle + random.uniform(-0.3, 0.3)

                jump_progress = max(0, min(1, 1 - (self.y / self.base_y)))
                thigh_tuck = JUMP_THIGH_TUCK * jump_progress
                shin_tuck = JUMP_SHIN_TUCK * jump_progress
                self.l_thigh_angle = thigh_tuck
                self.r_thigh_angle = thigh_tuck
                self.l_shin_angle = shin_tuck
                self.r_shin_angle = shin_tuck
            elif self.is_charging:
                # Charging crouch animation
                charge_crouch = (self.charge_power - MIN_CHARGE_POWER) / (MAX_CHARGE_POWER - MIN_CHARGE_POWER)
                squat_angle = math.pi * 0.05 * charge_crouch
                self.l_thigh_angle = squat_angle
                self.r_thigh_angle = squat_angle
                self.l_shin_angle = squat_angle * 1.5
                self.r_shin_angle = squat_angle * 1.5
                self.l_upper_arm_angle = squat_angle
                self.r_upper_arm_angle = squat_angle
                self.l_forearm_angle = math.pi * 0.1
                self.r_forearm_angle = math.pi * 0.1
            else:
                # Idle animation (or no specific animation)
                self.l_upper_arm_angle = 0
                self.r_upper_arm_angle = 0
                self.l_forearm_angle = 0
                self.r_forearm_angle = 0
                self.l_thigh_angle = 0
                self.r_thigh_angle = 0
                self.l_shin_angle = 0
                self.r_shin_angle = 0

        # Calculate All Joint Positions Based on Angles
        current_y = self.y
        current_x = self.x
        wobble_offset = 0
        if is_walking_on_ground:
            wobble_offset = BODY_WOBBLE_AMOUNT * math.sin(self.walk_cycle_timer)

        self.hip_pos = (current_x, current_y - (self.thigh_length + self.shin_length) * 0.9)
        upper_body_x = current_x + wobble_offset
        self.neck_pos = (upper_body_x, self.hip_pos[1] - self.torso_length)
        self.head_pos = (upper_body_x, self.neck_pos[1] - self.head_radius)
        self.shoulder_pos = self.neck_pos

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

        # Grounding & Landing Logic
        ground = self.base_y
        if self.is_jumping or self.is_kicking:
            self.l_foot_pos = (l_foot_x, l_foot_y)
            self.r_foot_pos = (r_foot_x, r_foot_y)
            if self.y >= ground and self.vy >= 0 and not self.is_kicking:
                # Check if landing conditions met after kick finished
                self.is_jumping = False
                self.vy = 0
                # Re-ground feet explicitly after landing decision
                self.l_foot_pos = (self.l_foot_pos[0], ground)
                self.r_foot_pos = (self.r_foot_pos[0], ground)
                self.y = ground
        else:
            # Not jumping or kicking - Force ground
            self.l_foot_pos = (l_foot_x, min(l_foot_y, ground))
            self.r_foot_pos = (r_foot_x, min(r_foot_y, ground))
            self.y = ground
            if self.vy > 0:
                self.vy = 0  # Ensure vy is 0 when grounded

    def get_kick_impact_point(self):
        """
        Returns the kick impact point if the stickman is kicking, otherwise returns None.

        Returns:
            tuple or None: The (x, y) coordinates of the kick impact point, or None if not kicking.
        """
        if self.is_kicking:
            progress = self.kick_timer / self.kick_duration
            if 0.4 < progress < 0.65:
                return self.l_foot_pos if self.kick_side == 'left' else self.r_foot_pos
        return None

    def get_head_position_radius(self):
        """
        Returns the head position and radius for headbutt collision detection.

        Returns:
            tuple: The (x, y) coordinates of the head center and the head radius.
        """
        return self.head_pos, self.head_radius

    def draw(self, screen):
        """
        Draws the stickman on the screen.

        Args:
            screen (pygame.Surface): The surface to draw on.
        """
        # Charge Bar
        if self.is_charging:
            bar_width = 50
            bar_height = 8
            bar_x = self.head_pos[0] - bar_width / 2
            bar_y = self.head_pos[1] - self.head_radius - bar_height - 5
            fill_ratio = (self.charge_power - MIN_CHARGE_POWER) / (MAX_CHARGE_POWER - MIN_CHARGE_POWER)
            fill_width = bar_width * max(0, min(1, fill_ratio))
            pygame.draw.rect(screen, BLACK, (bar_x - 1, bar_y - 1, bar_width + 2, bar_height + 2), 1)
            pygame.draw.rect(screen, YELLOW, (bar_x, bar_y, fill_width, bar_height))

        # Body & Head
        pygame.draw.line(screen, BLACK, self.neck_pos, self.hip_pos, 3)
        pygame.draw.circle(screen, BLACK, (int(self.head_pos[0]), int(self.head_pos[1])), self.head_radius, 0)
        pygame.draw.circle(screen, WHITE, (int(self.head_pos[0]), int(self.head_pos[1])), self.head_radius, 1)

        # Arms
        pygame.draw.line(screen, BLACK, self.shoulder_pos, self.l_elbow_pos, 3)
        pygame.draw.line(screen, BLACK, self.l_elbow_pos, self.l_hand_pos, 3)
        pygame.draw.line(screen, BLACK, self.shoulder_pos, self.r_elbow_pos, 3)
        pygame.draw.line(screen, BLACK, self.r_elbow_pos, self.r_hand_pos, 3)

        # --- DEBUG LEG DRAWING ---
        left_leg_color = BLACK
        right_leg_color = BLACK
        if self.is_kicking:
            if self.kick_side == 'left':
                left_leg_color = DEBUG_BLUE
            else:
                right_leg_color = DEBUG_BLUE
        # -------------------------

        # Legs (2 Segments) with Debug Color
        pygame.draw.line(screen, left_leg_color, self.hip_pos, self.l_knee_pos, 3)
        pygame.draw.line(screen, left_leg_color, self.l_knee_pos, self.l_foot_pos, 3)
        pygame.draw.line(screen, right_leg_color, self.hip_pos, self.r_knee_pos, 3)
        pygame.draw.line(screen, right_leg_color, self.r_knee_pos, self.r_foot_pos, 3)

# --- Ball Class ---
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
        pygame.draw.circle(screen, WHITE, center, self.radius)
        pent_sz=self.radius*0.45; off_d=self.radius*0.6
        for i in range(3):
            a=self.rotation_angle+(i*2*math.pi/3); px=center[0]+off_d*math.cos(a); py=center[1]+off_d*math.sin(a)
            draw_pentagon(screen,BLACK,(px,py),pent_sz,self.rotation_angle*1.5)
        pygame.draw.circle(screen,BLACK,center,self.radius,1)

# --- Game Setup ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Max Height Score!")
clock = pygame.time.Clock()
player = StickMan(SCREEN_WIDTH // 4, GROUND_Y)
ball = Ball(SCREEN_WIDTH // 2, GROUND_Y - 20, 15)
font_large = pygame.font.Font(None, 50)
font_medium = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 28)

# --- Score Variables ---
current_max_height = 0.0
current_hit_count = 0
high_score = 0
high_score_max_height = 0.0
high_score_hit_count = 0
ball_was_on_ground = True

particles = []  # List for explosion particles
can_headbutt = True  # Cooldown state for headbutt

# --- Off-screen Arrow Function ---
def draw_offscreen_arrow(s, ball, p_pos):
    ar_sz = 15
    pad = 25
    is_off = False
    tx, ty = ball.x, ball.y
    ax = max(pad, min(ball.x, SCREEN_WIDTH - pad))
    ay = max(pad, min(ball.y, SCREEN_HEIGHT - pad))
    if ball.x < 0 or ball.x > SCREEN_WIDTH:
        ax = pad if ball.x < 0 else SCREEN_WIDTH - pad
        is_off = True
    if ball.y < 0 or ball.y > SCREEN_HEIGHT:
        ay = pad if ball.y < 0 else SCREEN_HEIGHT - pad
        is_off = True
    if not is_off:
        return
    ang = math.atan2(ty - ay, tx - ax)
    p1 = (ar_sz, 0)
    p2 = (-ar_sz / 2, -ar_sz / 2)
    p3 = (-ar_sz / 2, ar_sz / 2)
    cos_a, sin_a = math.cos(ang), math.sin(ang)
    p1r = (p1[0] * cos_a - p1[1] * sin_a, p1[0] * sin_a + p1[1] * cos_a)
    p2r = (p2[0] * cos_a - p2[1] * sin_a, p2[0] * sin_a + p2[1] * cos_a)
    p3r = (p3[0] * cos_a - p3[1] * sin_a, p3[0] * sin_a + p3[1] * cos_a)
    pts = [
        (ax + p1r[0], ay + p1r[1]),
        (ax + p2r[0], ay + p2r[1]),
        (ax + p3r[0], ay + p3r[1]),
    ]
    pygame.draw.polygon(s, ARROW_RED, [(int(p[0]), int(p[1])) for p in pts])


# --- Main Game Loop ---
running = True
while running:
    dt = clock.tick(FPS) / 1000.0
    dt = min(dt, 0.1)
    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player.move(-1)
            elif event.key == pygame.K_RIGHT:
                player.move(1)
            elif event.key == pygame.K_UP:
                player.jump()
            elif event.key == pygame.K_SPACE:
                player.start_charge()
            elif event.key == pygame.K_ESCAPE:
                running = False
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT and player.vx < 0:
                player.stop_move()
            elif event.key == pygame.K_RIGHT and player.vx > 0:
                player.stop_move()
            elif event.key == pygame.K_SPACE:
                player.release_charge_and_kick(ball.x)  # Pass ball x pos

    # Updates
    player.update(dt)
    ball_hit_ground_this_frame = ball.update(dt) # Capture the return value
    particles = [p for p in particles if p.update(dt)]  # Update & filter particles

    # Score / Height Tracking Logic
    is_ball_airborne = not ball.is_on_ground() # NOW THIS METHOD EXISTS
    if is_ball_airborne:
        current_height_pixels = max(0, GROUND_Y - (ball.y + ball.radius))
        current_max_height = max(current_max_height, current_height_pixels)
        ball_was_on_ground = False
    elif ball_hit_ground_this_frame: # Use the captured flag
        if not ball_was_on_ground:  # Just hit ground
            final_sequence_score = int(current_max_height * current_hit_count)
            if final_sequence_score > high_score:  # Update high score details
                high_score = final_sequence_score
                high_score_max_height = current_max_height
                high_score_hit_count = current_hit_count
            current_max_height = 0.0
            current_hit_count = 0  # Reset session
        ball_was_on_ground = True
    display_score = int(current_max_height * current_hit_count)  # Calculate score to show

    # Collision & Score
    score_increased_this_frame = False
    # Kick
    kick_point = player.get_kick_impact_point()
    if kick_point:
        dist_x = kick_point[0] - ball.x
        dist_y = kick_point[1] - ball.y
        dist_sq = dist_x**2 + dist_y**2
        kick_rad = 13
        if dist_sq < (ball.radius + kick_rad)**2:
            if player.kick_timer < (player.kick_duration * 0.65):
                kick_x_base = BASE_KICK_FORCE_X
                if player.kick_side == "left":
                    kick_x_base = -kick_x_base  # Apply direction based on kick_side
                kick_x = kick_x_base * player.kick_charge_level
                kick_y = BASE_KICK_FORCE_Y * player.kick_charge_level
                if player.vy < 0:
                    kick_y += player.vy * 0.3  # Volley boost
                ball.apply_force(kick_x, kick_y)
                if is_ball_airborne:
                    current_hit_count += 1
                    score_increased_this_frame = True  # Count hit
    # Headbutt
    head_pos, head_radius = player.get_head_position_radius()
    dist_x_head = ball.x - head_pos[0]
    dist_y_head = ball.y - head_pos[1]
    dist_head_sq = dist_x_head**2 + dist_y_head**2
    headbutt_cooldown_applied = False
    if dist_head_sq < (ball.radius + head_radius)**2:
        if can_headbutt:
            force_y = -HEADBUTT_UP_FORCE
            if player.vy < 0:
                force_y -= abs(player.vy) * HEADBUTT_VY_MULTIPLIER
            force_x = player.vx * HEADBUTT_PLAYER_VX_FACTOR - dist_x_head * HEADBUTT_POS_X_FACTOR
            ball.apply_force(force_x, force_y)
            can_headbutt = False
            headbutt_cooldown_applied = True
            if is_ball_airborne:
                current_hit_count += 1
                score_increased_this_frame = True  # Count hit
    # Headbutt cooldown reset
    if not headbutt_cooldown_applied:
        if dist_head_sq > (ball.radius + head_radius + 15) ** 2:
            can_headbutt = True

    # Trigger Star Explosion (every 5 hits)
    if score_increased_this_frame and kick_point and current_hit_count > 0 and current_hit_count % 5 == 0: # Check kick_point exists
        num_kick_particles = 5  # Reduced particles for less clutter
        for _ in range(num_kick_particles):
            # Slightly offset particle origin from the kick point for more visual interest
            particle_x = kick_point[0] + random.uniform(-5, 5)
            particle_y = kick_point[1] + random.uniform(-5, 5)
            particles.append(Particle(particle_x, particle_y))  # Reduced particles

    # --- Drawing ---
    screen.fill(SKY_BLUE)
    pygame.draw.rect(screen, GRASS_GREEN, (0, GROUND_Y, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y))
    for p in particles:
        p.draw(screen)  # Draw particles
    player.draw(screen)
    ball.draw(screen)
    draw_offscreen_arrow(screen, ball, (player.x, player.y))  # Draw arrow

    # Draw Scores
    score_text = f"{display_score}"
    score_surf = font_large.render(score_text, True, TEXT_COLOR)
    score_rect = score_surf.get_rect(centerx=SCREEN_WIDTH // 2, top=10)
    screen.blit(score_surf, score_rect)
    # High Score Display (Updated Format)
    if high_score > 0:
        high_score_text = (
            f"Best: {high_score} ({high_score_max_height:.0f}px * {high_score_hit_count} hits)"
        )
    else:
        high_score_text = f"Best: {high_score}"
    high_score_surf = font_medium.render(high_score_text, True, TEXT_COLOR)
    high_score_rect = high_score_surf.get_rect(topright=(SCREEN_WIDTH - 15, 10))
    screen.blit(high_score_surf, high_score_rect)
    # Current Session Stats
    height_text = f"Max H: {current_max_height:.0f}"
    height_surf = font_small.render(height_text, True, TEXT_COLOR)
    height_rect = height_surf.get_rect(topleft=(15, 10))
    screen.blit(height_surf, height_rect)
    hits_text = f"Hits: {current_hit_count}"
    hits_surf = font_small.render(hits_text, True, TEXT_COLOR)
    hits_rect = hits_surf.get_rect(topleft=(15, 10 + height_rect.height + 2))
    screen.blit(hits_surf, hits_rect)

    # Simple cooldown indicator above the head
    if not can_headbutt:
        cooldown_color = (255, 0, 0)  # Red color
        cooldown_radius = 5
        head_x, head_y = player.head_pos
        indicator_x = int(head_x)
        indicator_y = int(head_y - player.head_radius - cooldown_radius - 2)
        pygame.draw.circle(screen, cooldown_color, (indicator_x, indicator_y), cooldown_radius)

    pygame.display.flip()

# Cleanup
pygame.quit()
sys.exit()