import os
import sys
import pygame

# --- Make src/ importable when running this file directly ---
THIS_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.dirname(THIS_DIR)
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

HIGHSCORE_FILE = os.path.normpath(os.path.join(THIS_DIR, "..", "..", "data", "highscores.json"))
HIGHSCORE_FILE = os.path.normpath(os.path.join(THIS_DIR, "..", "..", "data", "highscores.json"))
os.makedirs(os.path.dirname(HIGHSCORE_FILE), exist_ok=True)
print("HIGHSCORE_FILE =", HIGHSCORE_FILE)  # TEMP: confirm path


from settings import GRID_WIDTH, GRID_HEIGHT, CELL_SIZE, WINDOW_HEIGHT, WINDOW_WIDTH, MODE_MENU, MODE_GAME_OVER,MODE_PLAY
import random
import json
import time

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

def handle_menu_keydown(event: pygame.event.Event, state: dict) -> None:
    if event.key == pygame.K_RETURN:
        if state["player_name"].strip():
            start_new_game(state)
            state["mode"] = MODE_PLAY
        return

    if event.key == pygame.K_BACKSPACE:
        state["player_name"] = state["player_name"][:-1]
        return

    # add character (printable)
    if event.unicode and event.unicode.isprintable():
        if len(state["player_name"]) < 16:
            state["player_name"] += event.unicode


def handle_game_over_keydown(event: pygame.event.Event, state: dict) -> None:
    if event.key == pygame.K_RETURN:
        # keep same name; restart
        start_new_game(state)
        state["mode"] = MODE_PLAY
    elif event.key == pygame.K_ESCAPE:
        # go back to menu, let them retype name
        state["player_name"] = ""
        state["mode"] = MODE_MENU

def start_new_game(state: dict) -> None:
    now = pygame.time.get_ticks()

    state["snake"] = [(8, 9), (8, 8), (8, 7)]
    state["direction"] = (1, 0)

    state["score"] = 0
    state["food"] = [rand_pos()]

    state["last_move_time"] = now
    state["move_delay"] = 240

    state["last_food_spawn"] = now
    state["last_acceleration"] = now

    state["just_saved"] = False
    state["round_start_time"] = pygame.time.get_ticks()

def load_highscores() -> list[dict]:
    if not os.path.exists(HIGHSCORE_FILE):
        return []
    try:
        with open(HIGHSCORE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        return []


def save_highscores(scores: list[dict]) -> None:
    try:
        with open(HIGHSCORE_FILE, "w", encoding="utf-8") as f:
            json.dump(scores, f, indent=2)
        print("Saved highscores ✅", HIGHSCORE_FILE)  # TEMP
    except Exception as e:
        print("FAILED to save highscores ❌", e)      # TEMP



def add_highscore(scores: list[dict], name: str, score: int) -> list[dict]:
    scores.append({
        "name": name.strip() if name else "Player",
        "score": int(score),
        "timestamp": int(time.time())
    })
    scores.sort(key=lambda x: x["score"], reverse=True)
    return scores[:50]  # keep top 50 in the file (menu shows top 5)


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
        "score": 0,
        "food": [rand_pos()],
        "running": True,
        "food_spawn_delay" : 5000,
        "last_food_spawn": 0,
        "acceleration_delay": 10000,
        "acceleration_amount": 5,
        "last_acceleration": 0,
        "mode": MODE_MENU,
        "player_name": "",
        "just_saved": False,  # so game over save happens once
        "highscores": load_highscores(),
        "round_start_time": 0,
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
            if state["mode"] == MODE_MENU:
                handle_menu_keydown(event, state)
            elif state["mode"] == MODE_PLAY:
                handle_key(event.key, state)
            elif state["mode"] == MODE_GAME_OVER:
                handle_game_over_keydown(event, state)

    return True


def handle_key(key: int, state: dict) -> None:
    """
    Reacts to key presses.
    """
    if state["mode"] != MODE_PLAY:
        return
    
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
    if state["mode"] != MODE_PLAY:
        return
    
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
        state["mode"] = MODE_GAME_OVER
        if not state.get("just_saved", False):
            state["highscores"] = add_highscore(state["highscores"], state["player_name"], state["score"])
            save_highscores(state["highscores"])
            state["just_saved"] = True
        return
    elif new_y < 0 or new_y >= GRID_HEIGHT:
        state["mode"] = MODE_GAME_OVER
        if not state.get("just_saved", False):
            state["highscores"] = add_highscore(state["highscores"], state["player_name"], state["score"])
            save_highscores(state["highscores"])
            state["just_saved"] = True
        return
    elif new_head in state["snake"]:
        state["mode"] = MODE_GAME_OVER
        if not state.get("just_saved", False):
            state["highscores"] = add_highscore(state["highscores"], state["player_name"], state["score"])
            save_highscores(state["highscores"])
            state["just_saved"] = True
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

    #accelerate
    if current_time - state["last_acceleration"] >= state["acceleration_delay"]:
        if state["move_delay"] >= 100:
            state['move_delay'] -= state['acceleration_amount']
            state["last_acceleration"] = current_time
        else:
            pass


# ----------------------------------------------------------
# Rendering
# ----------------------------------------------------------
def render_game(screen: pygame.Surface, state: dict, font) -> None:
    if state["mode"] == MODE_MENU:
        render_menu(screen, state, font)
    elif state["mode"] == MODE_PLAY:
        render_play(screen, state, font)
    elif state["mode"] == MODE_GAME_OVER:
        render_game_over(screen, state, font)

    pygame.display.flip()

def render_menu(screen, state, font):
    screen.fill((20, 20, 20))
    title = font.render("Snake", True, (255, 255, 255))
    prompt = font.render("Enter name and press ENTER:", True, (255, 255, 255))

    cursor_on = (pygame.time.get_ticks() // 500) % 2 == 0
    name = state["player_name"] + ("|" if cursor_on else "")
    name_text = font.render(name, True, (255, 255, 255))

    screen.blit(title, (20, 20))
    screen.blit(prompt, (20, 80))
    screen.blit(name_text, (20, 130))

    # --- Highscore list (top 5) ---
    hs_title = font.render("Top 5 High Scores", True, (255, 255, 255))
    screen.blit(hs_title, (20, 200))

    top5 = state.get("highscores", [])[:5]
    y = 240
    if not top5:
        none = font.render("No scores yet", True, (200, 200, 200))
        screen.blit(none, (20, y))
    else:
        for i, entry in enumerate(top5, start=1):
            line = font.render(f'{i}. {entry["name"]} - {entry["score"]}', True, (200, 200, 200))
            screen.blit(line, (20, y))
            y += 30

def render_game_over(screen, state, font):
    screen.fill((20, 20, 20))
    over = font.render("GAME OVER", True, (255, 255, 255))
    score = font.render(f'{state["player_name"]} score: {state["score"]}', True, (255, 255, 255))
    hint = font.render("ENTER: play again   ESC: menu", True, (255, 255, 255))

    screen.blit(over, (20, 20))
    screen.blit(score, (20, 80))
    screen.blit(hint, (20, 140))


def render_play(screen: pygame.Surface, state: dict, font) -> None:
    """
    Draws the current game state.
    """
    screen.fill((20, 20, 20))

    #draw snake
    for (x, y) in state["snake"]:
        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, (80, 200, 120), rect)  # green snake

    # draw x lines
    for x in range(GRID_WIDTH+1):
        px = x * CELL_SIZE
        pygame.draw.line(screen, (40,40,40), (px,0), (px,GRID_HEIGHT * CELL_SIZE))

    #draw y lines
    for y in range(GRID_HEIGHT+1):
        py = y * CELL_SIZE
        pygame.draw.line(screen, (40, 40, 40), (0, py), (GRID_WIDTH * CELL_SIZE, py))

    # draw food
    for item in state["food"]:
        food_x, food_y = item
        pygame.draw.rect(screen, (220,80,80), (food_x*CELL_SIZE, food_y*CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # Write score
    text_surface = font.render(f'Score: {state["score"]}', True, (255,255,255))
    screen.blit(text_surface, (10,10))
    
    #write time
    elapsed = (pygame.time.get_ticks() - state["round_start_time"]) // 1000
    current_time = f"Time: {elapsed}"
    time_text = font.render(current_time, True, (255,255,255))
    screen.blit(time_text, (10,40))


# ----------------------------------------------------------

if __name__ == "__main__":
    main()
