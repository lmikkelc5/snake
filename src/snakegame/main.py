import os
import sys
import pygame

# --- Make src/ importable when running this file directly ---
THIS_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.dirname(THIS_DIR)
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)


# ----------------------------------------------------------
# Main entry point
# ----------------------------------------------------------

def main() -> None:
    # --- 1. Startup / Bootstrapping ---
    pygame.init()

    screen = create_window()
    clock = pygame.time.Clock()

    game_state = create_initial_game_state()

    running = True

    # --- 2. Main Game Loop ---
    while running:
        # A) Handle input
        running = handle_events(game_state)

        # B) Update game logic (movement, collisions, etc)
        update_game(game_state)

        # C) Draw everything
        render_game(screen, game_state)

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
    width = 800
    height = 600

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
        # TODO: add food position
        # TODO: add score
        # TODO: add timers (last move time)
        "running": True
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
        new_dir = (0,1)
    elif key == pygame.K_DOWN:
        new_dir = (0,-1)
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
    # TODO: implement movement timer
    # TODO: compute next head
    # TODO: check wall/self collisions
    # TODO: check food
    pass


# ----------------------------------------------------------
# Rendering
# ----------------------------------------------------------

def render_game(screen: pygame.Surface, state: dict) -> None:
    """
    Draws the current game state.
    """
    screen.fill((20, 20, 20))

    # TODO: draw grid
    # TODO: draw food
    # TODO: draw snake
    # TODO: draw score

    pygame.display.flip()


# ----------------------------------------------------------

if __name__ == "__main__":
    main()
