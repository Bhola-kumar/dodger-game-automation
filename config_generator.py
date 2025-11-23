import random

# ==========================================
# CENTRAL CONFIGURATION
# Control your game settings here.
# ==========================================
STATIC_SETTINGS = {
    # Render Free Tier Safety Settings (Vertical / 9:16 Aspect Ratio)
    "width": 480,       # Narrow width for phone screens
    "height": 854,      # Tall height for phone screens
    "fps": 30,          # 30 FPS (Low CPU usage)
    "max_duration": 15, # Hard cap for video length (seconds)
}

def generate_config():
    """
    Generates a dictionary of unique parameters for the game.
    Merges random variation with static safety settings.
    """
    seed = random.randint(0, 999999)
    
    # Randomize duration (e.g., between 12s and 15s)
    # Kept short to prevent Render timeouts.
    requested_duration = random.choice([12, 13, 14, 15])
    
    # Enforce the hard cap defined above
    final_duration = min(requested_duration, STATIC_SETTINGS['max_duration'])
    
    # AI Skill Adjustment for Vertical
    # Vertical screen = obstacles spawn closer to player = less reaction time.
    # We slightly increase min skill so the AI doesn't die immediately.
    ai_skill = round(random.uniform(0.98, 1.1), 2)
    
    # Randomize Theme Colors
    themes = [
        {'bg': (10, 10, 18), 'grid': (40, 0, 60), 'accent': (0, 255, 255)},   # Cyberpunk
        {'bg': (5, 20, 5),   'grid': (0, 60, 0),  'accent': (50, 255, 50)},   # Matrix
        {'bg': (20, 5, 5),   'grid': (60, 0, 0),  'accent': (255, 50, 50)},   # Red Alert
        {'bg': (15, 15, 15), 'grid': (50, 50, 50),'accent': (255, 220, 0)},   # Industrial
        {'bg': (25, 10, 30), 'grid': (80, 0, 80), 'accent': (255, 100, 200)}, # Vaporwave
    ]
    theme = random.choice(themes)
    
    # Combine everything into one config dictionary
    config = {
        "seed": seed,
        "duration": final_duration,
        "ai_skill": ai_skill,
        "theme": theme
    }
    
    # Merge with static settings (resolution, fps, etc.)
    config.update(STATIC_SETTINGS)
    
    return config

if __name__ == "__main__":
    print(generate_config())