# --- Main Game Loop ---
running = True
while running:
    dt = clock.tick(FPS) / 1000.0; dt = min(dt, 0.1)

    # --- Global Input & Event Processing ---
    # ... (Event loop remains the same: QUIT, SOUND_FINISHED, KEYDOWN, KEYUP) ...
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT: running = False
        if event.type == SOUND_FINISHED_EVENT: play_next_announcement()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: running = False
            if event.key == pygame.K_7: debug_mode = not debug_mode; print(f"Debug Mode {'ACT' if debug_mode else 'DEACT'}IVATED")
            # if event.key == pygame.K_6: flight_mode_active = not flight_mode_active; print(f"Flight Mode {'ACT' if flight_mode_active else 'DEACT'}IVATED") # Removed global toggle
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
        # ... (Game over logic and drawing remain the same) ...
        if not game_over_sound_played: announcement_queue = [];
        if overall_winner == 1: queue_sound(loaded_sounds['nils_wins'])
        elif overall_winner == 2: queue_sound(loaded_sounds['harry_wins'])
        play_next_announcement(); game_over_sound_played = True
        bg_color = DEBUG_BG_COLOR if debug_mode else SKY_BLUE # Simpler background check
        screen.fill(bg_color); pygame.draw.rect(screen, GRASS_GREEN, (0, GROUND_Y, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y))
        winner_name = "Nils" if overall_winner == 1 else "Harry"; draw_trophy(screen, winner_name, font_goal, font_large)
        draw_game_scores(screen, game_scores, font_small); pygame.display.flip(); continue

    # --- Handle Match Over State ---
    if match_over_timer > 0:
        match_over_timer -= dt
        if match_over_timer <= 0 and not game_over: start_new_match()

    # --- Process Announcement Sound Queue ---
    play_next_announcement()

    # --- Power-up Spawning --- <<< NEW BLOCK
    if not powerup.active and match_active: # Only spawn if none active and match is playing
        powerup_spawn_timer -= dt
        if powerup_spawn_timer <= 0:
            if random.random() < POWERUP_SPAWN_CHANCE:
                powerup.spawn()
            # Reset timer regardless of spawn success, add randomness
            powerup_spawn_timer = random.uniform(POWERUP_SPAWN_INTERVAL_MIN, POWERUP_SPAWN_INTERVAL_MAX)

    # --- Updates (Only if match active) ---
    if match_active:
        # ... (player/ball updates) ...
        player1.update(dt, player2); player2.update(dt, player1)
        ball_hit_ground_this_frame = ball.update(dt)
        particles = [p for p in particles if p.update(dt)]
        powerup.update(dt) # <<< Update powerup position

        # --- Power-up Collection --- <<< NEW BLOCK
        if powerup.active:
            if powerup.check_collision(player1):
                player1.is_flying = True
                player1.flight_timer = POWERUP_FLIGHT_DURATION
                # play_sound(loaded_sounds['powerup_collect']) # Add this sound if you have one
            elif powerup.check_collision(player2):
                 player2.is_flying = True
                 player2.flight_timer = POWERUP_FLIGHT_DURATION
                 # play_sound(loaded_sounds['powerup_collect'])

        # ... (player collisions, goal detection, etc.) ...
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
    # ... (Goal logic remains the same, including sound queuing) ...
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
            if not (p1_games_won >= GAME_WIN_LIMIT or p2_games_won >= GAME_WIN_LIMIT): # Queue sounds only if game not over
                announcement_queue = [] ; p1_games = p1_games_won; p2_games = p2_games_won
                if p1_games > p2_games: queue_sound(loaded_sounds['nils_ahead']); queue_specific_sound(loaded_sounds['numbers'].get(p1_games)); queue_specific_sound(loaded_sounds['numbers'].get(p2_games))
                elif p2_games > p1_games: queue_sound(loaded_sounds['harry_ahead']); queue_specific_sound(loaded_sounds['numbers'].get(p2_games)); queue_specific_sound(loaded_sounds['numbers'].get(p1_games))
                else: queue_specific_sound(loaded_sounds['numbers'].get(p1_games)); queue_specific_sound(loaded_sounds['numbers'].get(p2_games))
                play_next_announcement()
            if p1_games_won >= GAME_WIN_LIMIT: overall_winner = 1; game_over = True; print("PLAYER 1 WINS THE GAME!")
            elif p2_games_won >= GAME_WIN_LIMIT: overall_winner = 2; game_over = True; print("PLAYER 2 WINS THE GAME!")
        else: reset_positions(); continue

    # --- Drawing ---
    bg_color = SKY_BLUE
    if player1.is_flying or player2.is_flying: bg_color = FLIGHT_MODE_BG_COLOR # <<< Check individual player flight
    elif debug_mode: bg_color = DEBUG_BG_COLOR
    screen.fill(bg_color)
    pygame.draw.rect(screen, GRASS_GREEN, (0, GROUND_Y, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y))
    draw_goal_isometric(screen, GOAL_LINE_X_LEFT, GOAL_Y_POS, GOAL_HEIGHT, -GOAL_DEPTH_X, GOAL_DEPTH_Y, GOAL_POST_THICKNESS, GOAL_COLOR, GOAL_NET_COLOR)
    draw_goal_isometric(screen, GOAL_LINE_X_RIGHT, GOAL_Y_POS, GOAL_HEIGHT, GOAL_DEPTH_X, GOAL_DEPTH_Y, GOAL_POST_THICKNESS, GOAL_COLOR, GOAL_NET_COLOR)
    if screen_flash_timer > 0: flash_surf = pygame.Surface(screen.get_size(), pygame.SRCALPHA); flash_alpha = int(255 * (screen_flash_timer / SCREEN_FLASH_DURATION)); flash_surf.fill((SCREEN_FLASH_COLOR[0], SCREEN_FLASH_COLOR[1], SCREEN_FLASH_COLOR[2], flash_alpha)); screen.blit(flash_surf, (0,0))
    for p in particles: p.draw(screen)
    player1.draw(screen); player2.draw(screen); ball.draw(screen); powerup.draw(screen); draw_offscreen_arrow(screen, ball, None) # <<< Draw powerup

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