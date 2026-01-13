import os
import sys
import pygame

# --- Make src/ importable when running this file directly ---
THIS_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.dirname(THIS_DIR)
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from settings import GRID_WIDTH, GRID_HEIGHT, CELL_SIZE, WINDOW_HEIGHT, WINDOW_WIDTH
import random

# ----------------------------------------------------------
# Helpers
# ----------------------------------------------------------
def rand_pos():
    x = random.randrange(0,GRID_WIDTH)
    y = random.randrange(0,GRID_HEIGHT)
    return (x,y)

def rand_empty_pos(occupied):
    x = random.randrange(0,GRID_WIDTH)
    y = random.randrange(0,GRID_HEIGHT)
    while (x,y) in occupied:
        x = random.randrange(0,GRID_WIDTH)
        y = random.randrange(0,GRID_HEIGHT)
    return (x,y)


# ----------------------------------------------------------
# Main entry point
# ----------------------------------------------------------

def main() -> None:
    # --- 1. Startup / Bootstrapping ---
    pygame.init()

    font = pygame.font.SysFont(None, 36)
    screen = create_window()
    clock = pygame.time.Clock()

    state = create_initial_game_state()

    running = True

    # --- 2. Main Game Loop ---
    while state["running"]:
        # A) Handle input
        running = handle_events(state)

        # B) Update game logic (movement, collisions, etc)
        update_game(state)

        # C) Draw everything
        render_game(screen, state, font)

        # D) Control frame rate
        clock.tick(60)

    pygame.quit()


# ----------------------------------------------------------
# Window / setup
# ----------------------------------------------------------

def create_window() -> pygame.Surface:
    """
    Creates and returns the pygame window.
    """
    # TODO: Choose window size
    width = WINDOW_WIDTH
    height = WINDOW_HEIGHT

    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Snake")

    return screen


def create_initial_game_state() -> dict:
    """
    Returns a dictionary containing all game state.
    This is the single source of truth for the game.
    """
    return {
        "snake": [(8,9), (8,8), (8,7)],
        "direction": (1,0),
        "last_move_time": 0,
        "move_delay": 240,
        # TODO: add food position
        # TODO: add score
        "score": 0,
        "food": [rand_pos()],
        "score": 0,
        # TODO: add timers (last move time)
        "running": True,
        "food_spawn_delay" : 5000,
        "last_food_spawn": 0

    }


# ----------------------------------------------------------
# Input
# ----------------------------------------------------------

def handle_events(state: dict) -> bool:
    """
    Reads keyboard + window events.
    Returns False if the game should exit.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            state["running"] = False
            return False

        if event.type == pygame.KEYDOWN:
            handle_key(event.key, state)

    return True


def handle_key(key: int, state: dict) -> None:
    """
    Reacts to key presses.
    """
    current_dx, current_dy = state["direction"]

    # change snake direction logic
    if key == pygame.K_UP:
        new_dir = (0,-1)
    elif key == pygame.K_DOWN:
        new_dir = (0,1)
    elif key == pygame.K_LEFT:
        new_dir = (-1,0)
    elif key == pygame.K_RIGHT:
        new_dir = (1,0)
    else:
        return

    # enforce no-reverse rule
    if new_dir == (-current_dx, -current_dy):
        return

    state["direction"] = new_dir


# ----------------------------------------------------------
# Update
# ----------------------------------------------------------

def update_game(state: dict) -> None:
    """
    Advances the game by one step.
    This should:
    - Move the snake on a timer
    - Detect collisions
    - Handle food eating
    - Update score
    """
    current_time = pygame.time.get_ticks()

    #update head if time is good, calculate new head
    if current_time - state["last_move_time"] >= state["move_delay"]:
        head_x, head_y = state["snake"][0]
        dx, dy = state["direction"]
        new_x = head_x + dx
        new_y = head_y + dy
        new_head = (new_x, new_y)
        state["last_move_time"] = current_time
    else:
        return
    
    # check wall/self collisions
    if new_x < 0 or new_x >= GRID_WIDTH:
        state["running"] = False
        return
    elif new_y < 0 or new_y >= GRID_HEIGHT:
        state["running"] = False
        return
    elif new_head in state["snake"]:
        state["running"] = False
        return
    else:
        pass

    #move   
    state["snake"].insert(0, new_head)
    if new_head in state["food"]:
        state["food"].remove(new_head)
        state["score"] = state["score"] + 1
    else:
        state["snake"].pop()

    #food spawn
    if current_time - state["last_food_spawn"] >= state["food_spawn_delay"]:
        state["food"].append(rand_empty_pos(state["snake"] + state["food"]))
        state["last_food_spawn"]=current_time


# ----------------------------------------------------------
# Rendering
# ----------------------------------------------------------

def render_game(screen: pygame.Surface, state: dict, font) -> None:
    """
    Draws the current game state.
    """
    screen.fill((20, 20, 20))

    for (x, y) in state["snake"]:
        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, (80, 200, 120), rect)  # green snake

    # draw grid
    for x in range(GRID_WIDTH+1):
        px = x * CELL_SIZE
        pygame.draw.line(screen, (40,40,40), (px,0), (px,GRID_HEIGHT * CELL_SIZE))

    for y in range(GRID_HEIGHT+1):
        py = y * CELL_SIZE
        pygame.draw.line(screen, (40, 40, 40), (0, py), (GRID_WIDTH * CELL_SIZE, py))

    # draw food
    for item in state["food"]:
        food_x, food_y = item
        pygame.draw.rect(screen, (220,80,80), (food_x*CELL_SIZE, food_y*CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # TODO: draw score
    text_surface = font.render(f'Score: {state["score"]}', True, (255,255,255))
    screen.blit(text_surface, (10,10))

    pygame.display.flip()


# ----------------------------------------------------------

if __name__ == "__main__":
    main()
