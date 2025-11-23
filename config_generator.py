import random

# ==========================================
# CENTRAL CONFIGURATION
# Control your game settings here.
# ==========================================
STATIC_SETTINGS = {
    # Render Free Tier Safety Settings (Vertical / 9:16 Aspect Ratio)
    "width": 480,       
    "height": 854,      
    "fps": 30,          
    
    # CHANGED: Increased limit to 40s to allow your 34s choice
    "max_duration": 40, 
    
    # NEW: Control how long the "Game Over/Wasted" screen records (in seconds).
    # Set to 0 if you want the video to cut immediately when the game ends.
    # Set to 2 or 3 if you want a short fade-out/score screen.
    "tail_duration":3, 
    
    # --- SPEED SETTINGS ---
    "base_speed": 12.0,   
    "speed_ramp": 100.0,  
}

def generate_config():
    """
    Generates a dictionary of unique parameters for the game.
    """
    seed = random.randint(0, 999999)
    
    # CHANGED: Your requested list of durations
    requested_duration = random.choice([30, 31, 32, 34])
    
    # Enforce the hard cap
    final_duration = min(requested_duration, STATIC_SETTINGS['max_duration'])
    
    ai_skill = round(random.uniform(1.05, 1.2), 2)
    
    themes = [
        {'bg': (10, 10, 18), 'grid': (40, 0, 60), 'accent': (0, 255, 255)},   
        {'bg': (5, 20, 5),   'grid': (0, 60, 0),  'accent': (50, 255, 50)},   
        {'bg': (20, 5, 5),   'grid': (60, 0, 0),  'accent': (255, 50, 50)},   
        {'bg': (15, 15, 15), 'grid': (50, 50, 50),'accent': (255, 220, 0)},   
        {'bg': (25, 10, 30), 'grid': (80, 0, 80), 'accent': (255, 100, 200)}, 
    ]
    theme = random.choice(themes)
    
    config = {
        "seed": seed,
        "duration": final_duration,
        "ai_skill": ai_skill,
        "theme": theme
    }
    
    config.update(STATIC_SETTINGS)
    
    return config

if __name__ == "__main__":
    print(generate_config())