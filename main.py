import pygame
import random
import os
import asyncio
import math

pygame.init()

try:
    pygame.mixer.init()
    AUDIO_OK = True
except:
    AUDIO_OK = False

WIDTH = 900
HEIGHT = 600
FPS = 60

ARENA_RIGHT = 680
PANEL_X = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("WORLD OF SNAKES — FUTURE")

clock = pygame.time.Clock()

bg = pygame.image.load("backgroundimg.png").convert()
bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))

font_tiny = pygame.font.SysFont("arial", 15)
font_small = pygame.font.SysFont("arial", 20)
font_medium = pygame.font.SysFont("arial", 28, bold=True)
font_large = pygame.font.SysFont("arial", 48, bold=True)
font_huge = pygame.font.SysFont("arial", 72, bold=True)

WHITE = (240, 245, 255)
CYAN = (0, 255, 255)
BLUE = (40, 120, 255)
GREEN = (0, 255, 120)
RED = (255, 60, 80)
YELLOW = (255, 220, 0)
PURPLE = (190, 70, 255)
DARK = (5, 8, 20)

snake_size = 20
initial_length = 3

hiscore = 0

if os.path.exists("hiscore.txt"):
    try:
        with open("hiscore.txt", "r") as f:
            hiscore = int(f.read())
    except:
        hiscore = 0


def save_highscore():
    global hiscore

    try:
        with open("hiscore.txt", "w") as f:
            f.write(str(hiscore))
    except:
        pass


def draw_grid():
    for x in range(0, ARENA_RIGHT, 40):
        pygame.draw.line(
            screen,
            (10, 30, 55),
            (x, 65),
            (x, HEIGHT),
            1
        )

    for y in range(80, HEIGHT, 40):
        pygame.draw.line(
            screen,
            (10, 30, 55),
            (0, y),
            (ARENA_RIGHT, y),
            1
        )


def draw_arena_border():
    pygame.draw.rect(
        screen,
        (0, 100, 130),
        (0, 65, ARENA_RIGHT, HEIGHT - 65),
        2
    )


def draw_glow_rect(rect, color, glow=8):
    for i in range(glow, 0, -2):
        alpha = max(10, 70 - i * 6)

        surface = pygame.Surface(
            (rect.width + i * 2, rect.height + i * 2),
            pygame.SRCALPHA
        )

        pygame.draw.rect(
            surface,
            (*color, alpha),
            surface.get_rect(),
            2,
            border_radius=5
        )

        screen.blit(
            surface,
            (rect.x - i, rect.y - i)
        )

    pygame.draw.rect(
        screen,
        color,
        rect,
        border_radius=5
    )


def draw_snake(snk_list):
    for i, (x, y) in enumerate(snk_list):

        if i == len(snk_list) - 1:
            color = CYAN
        else:
            brightness = max(
                60,
                220 - int((len(snk_list) - i) * 5)
            )

            color = (
                0,
                brightness,
                255
            )

        rect = pygame.Rect(
            x,
            y,
            snake_size,
            snake_size
        )

        draw_glow_rect(
            rect,
            color,
            6
        )

        if i == len(snk_list) - 1:

            pygame.draw.circle(
                screen,
                WHITE,
                (x + 6, y + 6),
                2
            )

            pygame.draw.circle(
                screen,
                WHITE,
                (x + 14, y + 6),
                2
            )


def create_particles(x, y, color, amount=15):
    particles = []

    for _ in range(amount):

        angle = random.uniform(
            0,
            math.pi * 2
        )

        speed = random.uniform(
            1,
            4
        )

        particles.append({
            "x": x,
            "y": y,
            "vx": math.cos(angle) * speed,
            "vy": math.sin(angle) * speed,
            "life": random.randint(15, 35),
            "color": color
        })

    return particles


def update_particles(particles):
    for particle in particles:
        particle["x"] += particle["vx"]
        particle["y"] += particle["vy"]
        particle["life"] -= 1


def draw_particles(particles):
    for particle in particles:

        if particle["life"] > 0:

            pygame.draw.circle(
                screen,
                particle["color"],
                (
                    int(particle["x"]),
                    int(particle["y"])
                ),
                max(
                    1,
                    particle["life"] // 8
                )
            )


def draw_food(x, y, bonus=False):

    if bonus:
        color = PURPLE
        size = 14
    else:
        color = RED
        size = 10

    pulse = math.sin(
        pygame.time.get_ticks() * 0.008
    ) * 3

    pygame.draw.circle(
        screen,
        color,
        (
            int(x + snake_size / 2),
            int(y + snake_size / 2)
        ),
        int(size + pulse)
    )

    pygame.draw.circle(
        screen,
        WHITE,
        (
            int(x + snake_size / 2 - 3),
            int(y + snake_size / 2 - 3)
        ),
        2
    )


def draw_powerup(x, y, power_type):

    colors = {
        "speed": YELLOW,
        "shield": CYAN,
        "bonus": PURPLE
    }

    symbols = {
        "speed": "S",
        "shield": "D",
        "bonus": "2X"
    }

    color = colors[power_type]

    pulse = math.sin(
        pygame.time.get_ticks() * 0.006
    ) * 4

    radius = int(
        14 + pulse
    )

    pygame.draw.circle(
        screen,
        color,
        (
            x + snake_size // 2,
            y + snake_size // 2
        ),
        radius
    )

    text = font_small.render(
        symbols[power_type],
        True,
        DARK
    )

    screen.blit(
        text,
        (
            x + snake_size // 2 -
            text.get_width() // 2,
            y + snake_size // 2 -
            text.get_height() // 2
        )
    )


def draw_game_guide():

    panel_x = PANEL_X
    panel_y = 78
    panel_w = 190
    panel_h = 360

    pygame.draw.rect(
        screen,
        (3, 8, 20),
        (
            panel_x,
            panel_y,
            panel_w,
            panel_h
        ),
        border_radius=12
    )

    pygame.draw.rect(
        screen,
        CYAN,
        (
            panel_x,
            panel_y,
            panel_w,
            panel_h
        ),
        2,
        border_radius=12
    )

    title = font_medium.render(
        "POWER GUIDE",
        True,
        CYAN
    )

    screen.blit(
        title,
        (
            panel_x + 12,
            panel_y + 12
        )
    )

    pygame.draw.line(
        screen,
        (30, 100, 120),
        (
            panel_x + 10,
            panel_y + 52
        ),
        (
            panel_x + panel_w - 10,
            panel_y + 52
        ),
        1
    )

    items = [
        ("FOOD", "+10 POINTS", "Grow snake", RED),
        ("SPEED", "SPEED BOOST", "Move faster", YELLOW),
        ("SHIELD", "1 HIT SAFE", "Blocks collision", CYAN),
        ("2X BONUS", "DOUBLE POINTS", "Temporary bonus", PURPLE)
    ]

    y = panel_y + 68

    for name, effect, description, color in items:

        pygame.draw.circle(
            screen,
            color,
            (
                panel_x + 20,
                y + 9
            ),
            7
        )

        name_text = font_small.render(
            name,
            True,
            color
        )

        effect_text = font_tiny.render(
            effect,
            True,
            WHITE
        )

        desc_text = font_tiny.render(
            description,
            True,
            (150, 170, 190)
        )

        screen.blit(
            name_text,
            (
                panel_x + 35,
                y - 2
            )
        )

        screen.blit(
            effect_text,
            (
                panel_x + 35,
                y + 18
            )
        )

        screen.blit(
            desc_text,
            (
                panel_x + 35,
                y + 35
            )
        )

        y += 68

    pygame.draw.line(
        screen,
        (30, 100, 120),
        (
            panel_x + 10,
            y - 10
        ),
        (
            panel_x + panel_w - 10,
            y - 10
        ),
        1
    )

    controls_title = font_small.render(
        "CONTROLS",
        True,
        GREEN
    )

    screen.blit(
        controls_title,
        (
            panel_x + 15,
            y + 2
        )
    )

    controls = [
        "ARROWS / WASD  Move",
        "P  Pause",
        "ENTER  Restart"
    ]

    y += 32

    for text in controls:

        control_text = font_tiny.render(
            text,
            True,
            WHITE
        )

        screen.blit(
            control_text,
            (
                panel_x + 15,
                y
            )
        )

        y += 20


def draw_hud(
    score,
    high_score,
    level,
    shield,
    speed_boost,
    bonus_mode
):

    pygame.draw.rect(
        screen,
        (3, 8, 20),
        (0, 0, ARENA_RIGHT, 65)
    )

    pygame.draw.line(
        screen,
        CYAN,
        (0, 64),
        (ARENA_RIGHT, 64),
        2
    )

    score_text = font_medium.render(
        f"SCORE  {score}",
        True,
        WHITE
    )

    high_text = font_tiny.render(
        f"HIGH  {high_score}",
        True,
        CYAN
    )

    level_text = font_medium.render(
        f"LEVEL {level}",
        True,
        GREEN
    )

    screen.blit(
        score_text,
        (15, 10)
    )

    screen.blit(
        high_text,
        (17, 42)
    )

    screen.blit(
        level_text,
        (
            ARENA_RIGHT // 2 -
            level_text.get_width() // 2,
            20
        )
    )

    x = ARENA_RIGHT - 145

    if shield:

        shield_text = font_tiny.render(
            "SHIELD",
            True,
            CYAN
        )

        screen.blit(
            shield_text,
            (x, 8)
        )

        x += 70

    if speed_boost:

        speed_text = font_tiny.render(
            "BOOST",
            True,
            YELLOW
        )

        screen.blit(
            speed_text,
            (x, 8)
        )

    if bonus_mode:

        bonus_text = font_tiny.render(
            "2X SCORE",
            True,
            PURPLE
        )

        screen.blit(
            bonus_text,
            (
                ARENA_RIGHT - 80,
                40
            )
        )


def draw_start_screen():

    screen.blit(
        bg,
        (0, 0)
    )

    draw_grid()

    overlay = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA
    )

    overlay.fill(
        (0, 0, 0, 150)
    )

    screen.blit(
        overlay,
        (0, 0)
    )

    title = font_huge.render(
        "WORLD OF SNAKES",
        True,
        CYAN
    )

    subtitle = font_medium.render(
        "FUTURE EDITION",
        True,
        PURPLE
    )

    start = font_medium.render(
        "PRESS ENTER TO START",
        True,
        WHITE
    )

    controls = font_small.render(
        "ARROWS / WASD  •  P = PAUSE",
        True,
        (180, 200, 220)
    )

    power = font_small.render(
        "FOOD +10  •  SPEED  •  SHIELD  •  2X BONUS",
        True,
        (180, 200, 220)
    )

    screen.blit(
        title,
        (
            WIDTH // 2 -
            title.get_width() // 2,
            170
        )
    )

    screen.blit(
        subtitle,
        (
            WIDTH // 2 -
            subtitle.get_width() // 2,
            245
        )
    )

    screen.blit(
        start,
        (
            WIDTH // 2 -
            start.get_width() // 2,
            340
        )
    )

    screen.blit(
        controls,
        (
            WIDTH // 2 -
            controls.get_width() // 2,
            405
        )
    )

    screen.blit(
        power,
        (
            WIDTH // 2 -
            power.get_width() // 2,
            435
        )
    )


async def welcome():

    if AUDIO_OK:

        try:
            pygame.mixer.music.load(
                "back.ogg"
            )

            pygame.mixer.music.set_volume(
                0.25
            )

            pygame.mixer.music.play(
                -1
            )

        except:
            pass

    while True:

        draw_start_screen()

        pygame.display.flip()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_RETURN:
                    return True

        await asyncio.sleep(0)


async def gameloop():

    global hiscore

    snake_x = 300
    snake_y = 300

    velocity_x = 4
    velocity_y = 0

    snk_list = []

    snake_length = initial_length

    food_x = random.randrange(
        40,
        ARENA_RIGHT - 40,
        snake_size
    )

    food_y = random.randrange(
        100,
        HEIGHT - 40,
        snake_size
    )

    score = 0
    level = 1

    base_speed = 4

    shield = False
    speed_boost = False
    bonus_mode = False

    powerup_type = None
    powerup_x = 0
    powerup_y = 0

    powerup_timer = 0
    speed_timer = 0
    bonus_timer = 0

    particles = []

    paused = False
    game_over = False

    while True:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_p and not game_over:
                    paused = not paused

                if event.key == pygame.K_RETURN and game_over:
                    return True

                if not paused and not game_over:

                    if event.key in (
                        pygame.K_LEFT,
                        pygame.K_a
                    ) and velocity_x == 0:

                        velocity_x = -base_speed
                        velocity_y = 0

                    elif event.key in (
                        pygame.K_RIGHT,
                        pygame.K_d
                    ) and velocity_x == 0:

                        velocity_x = base_speed
                        velocity_y = 0

                    elif event.key in (
                        pygame.K_UP,
                        pygame.K_w
                    ) and velocity_y == 0:

                        velocity_y = -base_speed
                        velocity_x = 0

                    elif event.key in (
                        pygame.K_DOWN,
                        pygame.K_s
                    ) and velocity_y == 0:

                        velocity_y = base_speed
                        velocity_x = 0

        if not paused and not game_over:

            current_speed = (
                base_speed * 1.7
                if speed_boost
                else base_speed
            )

            if velocity_x > 0:
                velocity_x = current_speed

            elif velocity_x < 0:
                velocity_x = -current_speed

            if velocity_y > 0:
                velocity_y = current_speed

            elif velocity_y < 0:
                velocity_y = -current_speed

            snake_x += velocity_x
            snake_y += velocity_y

            head = [
                int(snake_x),
                int(snake_y)
            ]

            snk_list.append(head)

            if len(snk_list) > snake_length:
                del snk_list[0]

            wall_collision = (
                snake_x < 0
                or snake_x >= ARENA_RIGHT
                or snake_y < 65
                or snake_y >= HEIGHT
            )

            self_collision = (
                len(snk_list) > 5
                and head in snk_list[:-1]
            )

            if wall_collision or self_collision:

                if shield:

                    shield = False

                    snake_x = 300
                    snake_y = 300

                    velocity_x = base_speed
                    velocity_y = 0

                    snk_list = []

                else:

                    game_over = True

                    if score > hiscore:
                        hiscore = score
                        save_highscore()

                    if AUDIO_OK:

                        try:
                            pygame.mixer.music.stop()

                            end_sound = pygame.mixer.Sound(
                                "end.ogg"
                            )

                            end_sound.play()

                        except:
                            pass

            head_rect = pygame.Rect(
                snake_x,
                snake_y,
                snake_size,
                snake_size
            )

            food_rect = pygame.Rect(
                food_x,
                food_y,
                snake_size,
                snake_size
            )

            if head_rect.colliderect(food_rect):

                points = (
                    20
                    if bonus_mode
                    else 10
                )

                score += points
                snake_length += 1

                particles += create_particles(
                    food_x + snake_size // 2,
                    food_y + snake_size // 2,
                    PURPLE if bonus_mode else RED,
                    20
                )

                food_x = random.randrange(
                    40,
                    ARENA_RIGHT - 40,
                    snake_size
                )

                food_y = random.randrange(
                    100,
                    HEIGHT - 40,
                    snake_size
                )

                if score // 100 + 1 > level:

                    level += 1

                    base_speed = min(
                        10,
                        4 + level - 1
                    )

                if random.random() < 0.25:

                    powerup_type = random.choice(
                        [
                            "speed",
                            "shield",
                            "bonus"
                        ]
                    )

                    powerup_x = random.randrange(
                        40,
                        ARENA_RIGHT - 40,
                        snake_size
                    )

                    powerup_y = random.randrange(
                        100,
                        HEIGHT - 40,
                        snake_size
                    )

                    powerup_timer = 600

                if not speed_boost:

                    if velocity_x > 0:
                        velocity_x = base_speed

                    elif velocity_x < 0:
                        velocity_x = -base_speed

                    if velocity_y > 0:
                        velocity_y = base_speed

                    elif velocity_y < 0:
                        velocity_y = -base_speed

            if powerup_type is not None:

                power_rect = pygame.Rect(
                    powerup_x,
                    powerup_y,
                    snake_size,
                    snake_size
                )

                if head_rect.colliderect(
                    power_rect
                ):

                    particles += create_particles(
                        powerup_x + snake_size // 2,
                        powerup_y + snake_size // 2,
                        CYAN,
                        25
                    )

                    if powerup_type == "speed":

                        speed_boost = True
                        speed_timer = 360

                    elif powerup_type == "shield":

                        shield = True

                    elif powerup_type == "bonus":

                        bonus_mode = True
                        bonus_timer = 360

                    powerup_type = None

                powerup_timer -= 1

                if powerup_timer <= 0:
                    powerup_type = None

            if speed_boost:

                speed_timer -= 1

                if speed_timer <= 0:
                    speed_boost = False

            if bonus_mode:

                bonus_timer -= 1

                if bonus_timer <= 0:
                    bonus_mode = False

        update_particles(
            particles
        )

        particles = [
            p for p in particles
            if p["life"] > 0
        ]

        screen.blit(
            bg,
            (0, 0)
        )

        draw_grid()
        draw_arena_border()

        if powerup_type is not None:

            draw_powerup(
                powerup_x,
                powerup_y,
                powerup_type
            )

        draw_food(
            food_x,
            food_y,
            bonus_mode
        )

        draw_snake(
            snk_list
        )

        draw_particles(
            particles
        )

        draw_hud(
            score,
            hiscore,
            level,
            shield,
            speed_boost,
            bonus_mode
        )

        draw_game_guide()

        if paused:

            pause_overlay = pygame.Surface(
                (WIDTH, HEIGHT),
                pygame.SRCALPHA
            )

            pause_overlay.fill(
                (0, 0, 0, 160)
            )

            screen.blit(
                pause_overlay,
                (0, 0)
            )

            pause_text = font_huge.render(
                "PAUSED",
                True,
                CYAN
            )

            pause_info = font_small.render(
                "PRESS P TO CONTINUE",
                True,
                WHITE
            )

            screen.blit(
                pause_text,
                (
                    WIDTH // 2 -
                    pause_text.get_width() // 2,
                    240
                )
            )

            screen.blit(
                pause_info,
                (
                    WIDTH // 2 -
                    pause_info.get_width() // 2,
                    330
                )
            )

        if game_over:

            overlay = pygame.Surface(
                (WIDTH, HEIGHT),
                pygame.SRCALPHA
            )

            overlay.fill(
                (0, 0, 0, 185)
            )

            screen.blit(
                overlay,
                (0, 0)
            )

            game_text = font_huge.render(
                "SYSTEM FAILURE",
                True,
                RED
            )

            score_text = font_medium.render(
                f"SCORE: {score}",
                True,
                WHITE
            )

            level_text = font_medium.render(
                f"LEVEL: {level}",
                True,
                CYAN
            )

            restart_text = font_small.render(
                "PRESS ENTER TO RESTART",
                True,
                GREEN
            )

            screen.blit(
                game_text,
                (
                    WIDTH // 2 -
                    game_text.get_width() // 2,
                    190
                )
            )

            screen.blit(
                score_text,
                (
                    WIDTH // 2 -
                    score_text.get_width() // 2,
                    290
                )
            )

            screen.blit(
                level_text,
                (
                    WIDTH // 2 -
                    level_text.get_width() // 2,
                    330
                )
            )

            screen.blit(
                restart_text,
                (
                    WIDTH // 2 -
                    restart_text.get_width() // 2,
                    400
                )
            )

        pygame.display.flip()

        await asyncio.sleep(0)


async def main():

    while True:

        start = await welcome()

        if not start:
            break

        restart = await gameloop()

        if not restart:
            break

    pygame.quit()


asyncio.run(main())