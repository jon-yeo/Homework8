import pygame, sys, random, os
import map_data  #custom map file

# --- Initialize ---
pygame.init()

# --- Constants ---
TILE_SIZE = map_data.TILE_SIZE
MAP_WIDTH = len(map_data.grid[0])
MAP_HEIGHT = len(map_data.grid)
SCREEN_WIDTH, SCREEN_HEIGHT = MAP_WIDTH * TILE_SIZE, MAP_HEIGHT * TILE_SIZE
FPS = 60

# --- Colors ---
START_BG = (15, 25, 35)
GAME_BG = (30, 90, 143)
WIN_BG = (20, 40, 25)
MESSAGE_BOX_COLOR = (60, 20, 20)
MESSAGE_BORDER_COLOR = (255, 100, 100)

# --- Create window ---
WIN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Doctor’s Little Assistant")
clock = pygame.time.Clock()

# --- Sprite loader ---
def load_sprite(path, size, fallback_color):
    if os.path.exists(path):
        try:
            sprite = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(sprite, (size, size))
        except:
            pass
    surf = pygame.Surface((size, size))
    surf.fill(fallback_color)
    return surf

# --- Load sprites ---
player_sprite = load_sprite("assets/Robot.png", TILE_SIZE, (255, 255, 0))
wall_sprite = load_sprite("assets/wall_tile.png", TILE_SIZE, (100, 100, 100))
item_sprites = [
    load_sprite("assets/first_aid_kit.png", TILE_SIZE // 2, (255, 50, 50)),
    load_sprite("assets/Pills.png", TILE_SIZE // 2, (50, 255, 50)),
    load_sprite("assets/stringe.png", TILE_SIZE // 2, (50, 50, 255)),
]
goal_sprite = load_sprite("assets/doctor.png", TILE_SIZE * 1.5, (255, 215, 0))

# --- Map data ---
grid = map_data.grid
goal_pos = map_data.goal_pos

# --- Walls ---
wall_rects = [
    pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    for y in range(MAP_HEIGHT)
    for x in range(MAP_WIDTH)
    if grid[y][x] == 1
]

# --- Random goal counts ---
goal_counts = [random.randint(2, 4) for _ in range(3)]

# --- Player setup ---
player_pos = pygame.Vector2(2 * TILE_SIZE, 2 * TILE_SIZE)
player_speed = 2
score = [0, 0, 0]
camera_x, camera_y = 0, 0
font = pygame.font.SysFont(None, 30)

# --- Create collectables ---
items = []
for item_type in range(3):
    for _ in range(goal_counts[item_type]):
        while True:
            ix, iy = random.randint(1, MAP_WIDTH - 2), random.randint(1, MAP_HEIGHT - 2)
            if grid[iy][ix] == 0 and (ix, iy) not in [(x, y) for x, y, _ in items]:
                items.append((ix, iy, item_type))
                break

# --- Drawing ---
def draw(message=None):
    WIN.fill(GAME_BG)  #background color for gameplay

    # Draw walls
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            if grid[y][x] == 1:
                WIN.blit(wall_sprite, (x * TILE_SIZE - camera_x, y * TILE_SIZE - camera_y))

    # Draw items
    for ix, iy, itype in items:
        WIN.blit(item_sprites[itype],
                 (ix * TILE_SIZE + TILE_SIZE * 0.25 - camera_x,
                  iy * TILE_SIZE + TILE_SIZE * 0.25 - camera_y))

    # Draw player
    WIN.blit(player_sprite, (player_pos.x - camera_x, player_pos.y - camera_y))

    # Draw goal
    gx, gy = goal_pos
    WIN.blit(goal_sprite, (gx * TILE_SIZE - camera_x, gy * TILE_SIZE - camera_y))

    # --- Draw collected items horizontally ---
    hud_x, hud_y = 10, 10
    spacing = 120
    for i in range(3):
        WIN.blit(item_sprites[i], (hud_x + i * spacing, hud_y))
        text_surf = font.render(f"{score[i]}/{goal_counts[i]}", True, (255, 255, 255))
        WIN.blit(text_surf, (hud_x + i * spacing + TILE_SIZE // 2 + 5, hud_y + TILE_SIZE // 4))

    # --- Reminder message with background box ---
    if message:
        msg_text = font.render(message, True, (255, 255, 255))
        msg_rect = msg_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        box_rect = msg_rect.inflate(40, 20)
        pygame.draw.rect(WIN, MESSAGE_BOX_COLOR, box_rect, border_radius=8)
        pygame.draw.rect(WIN, MESSAGE_BORDER_COLOR, box_rect, 3, border_radius=8)
        WIN.blit(msg_text, msg_rect)

    pygame.display.flip()

# --- Start screen ---
def start_screen():
    font_big = pygame.font.SysFont(None, 50)
    font_small = pygame.font.SysFont(None, 24)
    title = font_big.render("Doctor’s Little Assistant", True, (255, 255, 255))
    story_lines = [
        "You are a medical robot.",
        "The doctor has assigned you to collect",
        "all necessary items for surgery.",
        "Use W A S D to move"
    ]
    subtitle = font_small.render("Press SPACE to Start", True, (200, 200, 200))

    lines = [
        ("First-aid Kits", goal_counts[0], item_sprites[0]),
        ("Pills", goal_counts[1], item_sprites[1]),
        ("Syringes", goal_counts[2], item_sprites[2])
    ]

    while True:
        WIN.fill(START_BG)  # NEW background color for start screen
        WIN.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))

        for i, line in enumerate(story_lines):
            story_text = font_small.render(line, True, (220, 220, 220))
            WIN.blit(story_text, (SCREEN_WIDTH // 2 - story_text.get_width() // 2, 120 + i * 30))

        start_y = 250
        for i, (name, count, sprite) in enumerate(lines):
            sprite_pos = (SCREEN_WIDTH // 2 - 80, start_y + i * 40)
            WIN.blit(sprite, sprite_pos)
            text_surf = font_small.render(f"{name}: {count}", True, (220, 220, 220))
            WIN.blit(text_surf, (sprite_pos[0] + 40, sprite_pos[1] + 5))

        WIN.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, SCREEN_HEIGHT - 80))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return

# --- Win screen ---
def win_screen():
    font_big = pygame.font.SysFont(None, 60)
    font_small = pygame.font.SysFont(None, 30)
    msg = font_big.render("OPERATION SUCCESS!", True, (0, 255, 0))

    play_again_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 50, 200, 50)
    quit_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 120, 200, 50)

    while True:
        WIN.fill(WIN_BG)  # NEW background color for win screen
        WIN.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2,
                       SCREEN_HEIGHT // 2 - 100))

        pygame.draw.rect(WIN, (50, 50, 200), play_again_rect)
        pygame.draw.rect(WIN, (200, 50, 50), quit_rect)

        play_text = font_small.render("Play Again", True, (255, 255, 255))
        quit_text = font_small.render("Quit", True, (255, 255, 255))
        WIN.blit(play_text, (play_again_rect.centerx - play_text.get_width()//2,
                             play_again_rect.centery - play_text.get_height()//2))
        WIN.blit(quit_text, (quit_rect.centerx - quit_text.get_width()//2,
                             quit_rect.centery - quit_text.get_height()//2))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if play_again_rect.collidepoint(mx, my):
                    # Reset
                    global player_pos, score, items, goal_counts
                    player_pos = pygame.Vector2(2 * TILE_SIZE, 2 * TILE_SIZE)
                    score = [0, 0, 0]
                    goal_counts = [random.randint(2, 4) for _ in range(3)]
                    items = []
                    for item_type in range(3):
                        for _ in range(goal_counts[item_type]):
                            while True:
                                ix, iy = random.randint(1, MAP_WIDTH - 2), random.randint(1, MAP_HEIGHT - 2)
                                if grid[iy][ix] == 0 and (ix, iy) not in [(x, y) for x, y, _ in items]:
                                    items.append((ix, iy, item_type))
                                    break
                    return
                if quit_rect.collidepoint(mx, my):
                    pygame.quit(); sys.exit()

# --- Main loop ---
def main():
    global player_pos, camera_x, camera_y, score
    start_screen()

    while True:
        dt = clock.tick(FPS) / 1000.0
        message = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

        # Movement input
        keys = pygame.key.get_pressed()
        move = pygame.Vector2(0, 0)
        if keys[pygame.K_w]: move.y = -1
        if keys[pygame.K_s]: move.y = 1
        if keys[pygame.K_a]: move.x = -1
        if keys[pygame.K_d]: move.x = 1
        if move.length_squared() > 0: move = move.normalize()

        # Move player
        player_rect = pygame.Rect(player_pos.x, player_pos.y, TILE_SIZE, TILE_SIZE)
        velocity = move * player_speed * 100 * dt
        player_rect.x += velocity.x
        player_rect.y += velocity.y

        # Wall collisions
        for wall in wall_rects:
            if player_rect.colliderect(wall):
                overlap_x = min(player_rect.right - wall.left, wall.right - player_rect.left)
                overlap_y = min(player_rect.bottom - wall.top, wall.bottom - player_rect.top)
                if overlap_x < overlap_y:
                    if player_rect.centerx < wall.centerx:
                        player_rect.right = wall.left
                    else:
                        player_rect.left = wall.right
                else:
                    if player_rect.centery < wall.centery:
                        player_rect.bottom = wall.top
                    else:
                        player_rect.top = wall.bottom

        player_pos.update(player_rect.x, player_rect.y)

        # Item pickups
        for item in items[:]:
            item_rect = pygame.Rect(
                item[0] * TILE_SIZE + TILE_SIZE * 0.25,
                item[1] * TILE_SIZE + TILE_SIZE * 0.25,
                TILE_SIZE * 0.5, TILE_SIZE * 0.5)
            if player_rect.colliderect(item_rect):
                items.remove(item)
                score[item[2]] += 1

        # Goal check
        gx, gy = goal_pos
        goal_rect = pygame.Rect(gx * TILE_SIZE, gy * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        if player_rect.colliderect(goal_rect):
            if all(score[i] >= goal_counts[i] for i in range(3)):
                win_screen()
            else:
                message = "Collect all items first!"

        # Camera follow
        camera_x = player_pos.x - SCREEN_WIDTH / 2 + TILE_SIZE / 2
        camera_y = player_pos.y - SCREEN_HEIGHT / 2 + TILE_SIZE / 2
        camera_x = max(0, min(camera_x, MAP_WIDTH * TILE_SIZE - SCREEN_WIDTH))
        camera_y = max(0, min(camera_y, MAP_HEIGHT * TILE_SIZE - SCREEN_HEIGHT))

        draw(message)

# --- Run ---
if __name__ == "__main__":
    main()
