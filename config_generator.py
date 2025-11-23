import random

def generate_config():
    """
    Generates a dictionary of unique parameters for the game.
    This fulfills the requirement of generating variables outside the game logic.
    """
    seed = random.randint(0, 999999)
    
    # Randomize duration (e.g., between 45s and 90s)
    duration = random.choice([45, 60, 75, 90])
    
    # Randomize AI Skill (0.95 to 1.1)
    ai_skill = round(random.uniform(0.95, 1.1), 2)
    
    # Randomize Theme Colors
    themes = [
        {'bg': (10, 10, 18), 'grid': (40, 0, 60), 'accent': (0, 255, 255)},   # Cyberpunk
        {'bg': (5, 20, 5),   'grid': (0, 60, 0),  'accent': (50, 255, 50)},   # Matrix
        {'bg': (20, 5, 5),   'grid': (60, 0, 0),  'accent': (255, 50, 50)},   # Red Alert
        {'bg': (15, 15, 15), 'grid': (50, 50, 50),'accent': (255, 220, 0)},   # Industrial
    ]
    theme = random.choice(themes)
    
    return {
        "seed": seed,
        "duration": duration,
        "ai_skill": ai_skill,
        "theme": theme
    }

if __name__ == "__main__":
    print(generate_config())
