# dodger_streamer_edition_v4.py
# V4: Fully Configurable via Config Dict

import pygame
import random
import math
import struct
import subprocess
import sys
import os
import time
import tempfile
from collections import deque

# ===========================
# GLOBAL DEFAULTS 
# (These will be overwritten by config in run_game)
# ===========================
WIDTH, HEIGHT = 854, 480 
FPS = 30
NEON_CYAN = (0, 255, 255)
NEON_MAGENTA = (255, 0, 255)
NEON_YELLOW = (255, 220, 0)
NEON_RED = (255, 50, 50)
NEON_GREEN = (50, 255, 50)
NEON_ORANGE = (255, 100, 0)

# Check for headless environment
if os.environ.get("SDL_VIDEODRIVER") == "dummy":
    FFMPEG_PATH = "ffmpeg"
else:
    # Local Windows path (Keep this if you run locally)
    FFMPEG_PATH = r"D:\GitHub\Game\Dodge\dodger-game-automation\ffmpeg-master-latest-win64-gpl-shared\bin\ffmpeg.exe"

# ===========================
# ASSET GENERATION (Audio)
# ===========================
def generate_tone(filename, freq, dur, vol=0.5, type='sine'):
    sr = 22050
    frames = int(sr * dur)
    data = bytearray()
    for n in range(frames):
        t = n / sr
        if type == 'sine':
            val = math.sin(2 * math.pi * freq * t)
        elif type == 'saw':
            val = 2 * (t * freq - math.floor(t * freq + 0.5))
        elif type == 'noise':
            val = random.uniform(-1, 1)
        env = 1.0
        if n < 100: env = n/100
        if n > frames - 500: env = (frames-n)/500
        val *= vol * env
        data.extend(struct.pack('<h', int(max(-1, min(1, val)) * 32767)))
    with open(filename, 'wb') as f:
        f.write(b'RIFF'); f.write(struct.pack('<I', 36 + len(data)))
        f.write(b'WAVEfmt '); f.write(struct.pack('<IHHIIHH', 16, 1, 1, sr, sr * 2, 2, 16))
        f.write(b'data'); f.write(struct.pack('<I', len(data))); f.write(data)

def generate_dynamic_music(path_low, path_high, duration_seconds):
    sr = 44100
    bpm = 140
    # Generate enough music for the video plus a buffer
    seconds = duration_seconds + 10
    total_samples = int(seconds * sr)
    beat_samples = int(sr * 60 / bpm)
    roots = [43.65, 51.91, 38.89, 43.65]
    print("Generating dynamic music...")
    data_low = bytearray()
    data_high = bytearray()
    for n in range(total_samples):
        t = n / sr
        beat_pos = (n % beat_samples) / beat_samples
        measure = (n // (beat_samples * 4)) % 4
        root = roots[measure]
        kick = 0.0
        if beat_pos < 0.1: kick = (1.0 - beat_pos/0.1) * math.exp(-beat_pos * 10)
        bass = 0.0
        for h in range(1, 3): bass += (0.4/h) * (1 if (int(t * root * h * 2) % 2) else -1)
        bass *= 0.5 * (1.0 - beat_pos*0.5)
        lead = 0.0
        hat = 0.0
        if (n % (beat_samples//2)) < 1000: hat = random.uniform(-0.1, 0.1)
        arp_note = root * (2 if (int(t * 8) % 2) else 1)
        lead = 0.15 * math.sin(2 * math.pi * arp_note * t)
        sample_low = (kick * 0.9 + bass * 0.8) * 0.4
        sample_high = (kick * 0.8 + bass * 0.6 + lead + hat) * 0.4
        data_low.extend(struct.pack('<h', int(max(-1, min(1, sample_low)) * 32767)))
        data_high.extend(struct.pack('<h', int(max(-1, min(1, sample_high)) * 32767)))
    def save_wav(fname, d):
        with open(fname, 'wb') as f:
            f.write(b'RIFF'); f.write(struct.pack('<I', 36 + len(d)))
            f.write(b'WAVEfmt '); f.write(struct.pack('<IHHIIHH', 16, 1, 1, sr, sr * 2, 2, 16))
            f.write(b'data'); f.write(struct.pack('<I', len(d))); f.write(d)
    save_wav(path_low, data_low)
    save_wav(path_high, data_high)

# ===========================
# CLASSES
# ===========================

class CartoonPlayer:
    def __init__(self):
        # Use Global HEIGHT
        self.rect = pygame.Rect(100, HEIGHT//2, 50, 50)
        self.y_float = float(self.rect.y)
        self.velocity = 0.0
        self.trail = []
        self.face_seed = random.randint(0, 1000)
        self.blink_timer = 0
        self.wobble = 0
        
    def update(self, target_y, smooth_factor):
        diff = target_y - self.rect.centery
        self.velocity += diff * 0.08
        self.velocity *= 0.82
        self.y_float += self.velocity
        if self.y_float < 0: self.y_float = 0; self.velocity = -self.velocity * 0.5
        if self.y_float > HEIGHT - self.rect.height: self.y_float = HEIGHT - self.rect.height; self.velocity = -self.velocity * 0.5
        self.rect.y = int(self.y_float)
        if abs(self.velocity) > 1:
            self.trail.append((self.rect.centerx, self.rect.centery, random.randint(5, 10)))
        if len(self.trail) > 10: self.trail.pop(0)
        self.wobble = math.sin(time.time() * 10) * 3

    def draw(self, surface):
        cx, cy = self.rect.centerx, self.rect.centery + self.wobble
        for i, (tx, ty, tr) in enumerate(self.trail):
            alpha = int(150 * (i/10))
            s = pygame.Surface((tr*2, tr*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*NEON_CYAN, alpha), (tr, tr), tr)
            surface.blit(s, (tx - tr, ty - tr))
        pygame.draw.circle(surface, (0, 100, 100), (cx, cy), 28)
        pygame.draw.circle(surface, NEON_CYAN, (cx, cy), 24)
        pygame.draw.circle(surface, (200, 255, 255), (cx - 8, cy - 8), 8)
        self.blink_timer += 1
        if self.blink_timer > 150:
            pygame.draw.line(surface, (0,0,0), (cx + 6, cy - 2), (cx + 14, cy - 2), 3)
            if self.blink_timer > 160: self.blink_timer = 0
        else:
            pygame.draw.circle(surface, (0,0,0), (cx + 10, cy - 2), 4)
        pygame.draw.circle(surface, (0,0,0), (cx + 18, cy - 2), 3)
        pygame.draw.arc(surface, (0,0,0), (cx + 8, cy + 2, 10, 10), 3.14, 6.28, 2)
        pygame.draw.line(surface, (100, 100, 100), (cx, cy - 24), (cx, cy - 35), 2)
        pygame.draw.circle(surface, NEON_RED, (cx, cy - 35), 4)

class Obstacle:
    def __init__(self, x, y, w, h, color):
        self.rect = pygame.Rect(x, y, w, h)
        self.x_float = float(x)
        self.color = color
        self.passed = False

    def update(self, speed):
        self.x_float -= speed
        self.rect.x = int(self.x_float)

    def draw(self, surface):
        pygame.draw.rect(surface, (20, 10, 20), self.rect)
        pygame.draw.rect(surface, self.color, self.rect, 3)
        pygame.draw.line(surface, (255, 255, 255), (self.rect.centerx, self.rect.top), (self.rect.centerx, self.rect.bottom), 1)

class Particle:
    def __init__(self, x, y, color):
        self.x = x; self.y = y
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-5, 5)
        self.life = 40
        self.color = color
    
    def update(self):
        self.x += self.vx; self.y += self.vy; self.life -= 1
        
    def draw(self, surface):
        if self.life > 0:
            alpha = int(255 * (self.life/40))
            s = pygame.Surface((6,6), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (3,3), 3)
            surface.blit(s, (self.x, self.y))

class LevelManager:
    def __init__(self):
        self.level = 1
        self.xp = 0
        self.next_level_xp = 500
        self.level_text_timer = 0
        self.colors = [NEON_MAGENTA, NEON_GREEN, NEON_ORANGE, NEON_RED]
        
    def add_xp(self, amount):
        self.xp += amount
        if self.xp >= self.next_level_xp:
            self.level += 1
            self.xp = 0
            self.next_level_xp = int(self.next_level_xp * 1.5)
            self.level_text_timer = 120
            return True
        return False
        
    def get_color(self):
        return self.colors[(self.level - 1) % len(self.colors)]

class EnhancedChat:
    def __init__(self):
        self.messages = [] 
        self.users = [
            "NeonNinja", "CyberWolf", "PixelPusher", "GlitchGamer", "RetroRex", 
            "VaporWave", "SynthLord", "BitMaster", "CodeCrusher", "StreamQueen"
        ]
        self.comments_normal = ["Pog", "Nice", "Clean", "Smooth", "Music is vibe", "Hi youtube", "First"]
        self.comments_hype = ["OMG", "INSANE", "GOD GAMER", "HOW???", "CLIP IT", "POGCHAMP", "⚡⚡⚡"]
        self.comments_scared = ["monkaS", "Close one", "Sweating", "Careful!", "Heart rate 📈"]
        self.timer = 0
        self.next_msg_time = 0
        self.font = pygame.font.SysFont("Arial", 16, bold=True)

    def add_message(self, type='normal'):
        user = random.choice(self.users)
        color = random.choice([NEON_CYAN, NEON_MAGENTA, NEON_GREEN, NEON_YELLOW])
        
        if type == 'hype': text = random.choice(self.comments_hype)
        elif type == 'scared': text = random.choice(self.comments_scared)
        else: text = random.choice(self.comments_normal)
        
        self.messages.append({
            'user': user, 'color': color, 'text': text, 
            'slide': -50, 'alpha': 0, 'life': 300
        })
        if len(self.messages) > 7: self.messages.pop(0)

    def update(self, state='normal'):
        self.timer += 1
        if self.timer >= self.next_msg_time:
            self.timer = 0
            self.next_msg_time = random.randint(30, 100)
            self.add_message(state)
            
        for m in self.messages:
            if m['slide'] < 0: m['slide'] += 5 
            if m['alpha'] < 255: m['alpha'] += 15 
            m['life'] -= 1

    def draw(self, surface, x, y):
        s = pygame.Surface((250, 200), pygame.SRCALPHA)
        for i in range(200):
            pygame.draw.line(s, (0,0,0, int(150 * (i/200))), (0, i), (250, i))
        surface.blit(s, (x, y))
        
        curr_y = y + 180
        for m in reversed(self.messages):
            if m['life'] <= 0: continue
            
            pygame.draw.circle(surface, m['color'], (x + 15 + int(m['slide']), curr_y + 8), 8)
            
            u_surf = self.font.render(m['user'], True, (200, 200, 200))
            t_surf = self.font.render(m['text'], True, (255, 255, 255))
            
            u_surf.set_alpha(m['alpha'])
            t_surf.set_alpha(m['alpha'])
            
            surface.blit(u_surf, (x + 30 + int(m['slide']), curr_y))
            surface.blit(t_surf, (x + 30 + u_surf.get_width() + 10 + int(m['slide']), curr_y))
            
            curr_y -= 25
            if curr_y < y: break

class ExpressiveFacecam:
    def __init__(self):
        self.state = 'normal'
        self.color = NEON_CYAN
        self.blink_timer = 0
        self.bob_timer = 0
        self.shake = 0
        
    def update(self, player, obstacles, level_just_up):
        self.state = 'normal'
        self.shake = 0
        
        if level_just_up:
            self.state = 'hype'
        else:
            p_rect = player.rect.inflate(50, 50)
            for o in obstacles:
                if p_rect.colliderect(o.rect):
                    self.state = 'scared'
                    self.shake = random.randint(-2, 2)
                    break
        
        self.bob_timer += 0.2 if self.state == 'normal' else 0.5

    def draw(self, surface, x, y):
        w, h = 160, 120
        pygame.draw.rect(surface, (10, 10, 15), (x, y, w, h))
        
        border_col = self.color
        if self.state == 'scared': border_col = NEON_RED
        if self.state == 'hype': border_col = NEON_YELLOW
        
        pygame.draw.rect(surface, border_col, (x, y, w, h), 3)
        
        cx = x + w//2 + self.shake
        cy = y + h + math.sin(self.bob_timer) * 5
        
        pygame.draw.circle(surface, (50, 50, 60), (cx, cy + 20), 40)
        head_y = cy - 30
        pygame.draw.circle(surface, (200, 180, 150), (cx, int(head_y)), 25)
        
        self.blink_timer += 1
        blink = False
        if self.state == 'normal' and self.blink_timer > 200:
            blink = True
            if self.blink_timer > 210: self.blink_timer = 0
            
        eye_y = int(head_y)
        if self.state == 'scared':
            pygame.draw.circle(surface, (255, 255, 255), (cx - 8, eye_y), 6)
            pygame.draw.circle(surface, (255, 255, 255), (cx + 8, eye_y), 6)
            pygame.draw.circle(surface, (0,0,0), (cx - 8, eye_y), 2)
            pygame.draw.circle(surface, (0,0,0), (cx + 8, eye_y), 2)
        elif self.state == 'hype':
            pygame.draw.line(surface, (0,0,0), (cx - 10, eye_y - 3), (cx - 4, eye_y + 3), 2)
            pygame.draw.line(surface, (0,0,0), (cx - 10, eye_y + 3), (cx - 4, eye_y - 3), 2)
            pygame.draw.line(surface, (0,0,0), (cx + 4, eye_y - 3), (cx + 10, eye_y + 3), 2)
            pygame.draw.line(surface, (0,0,0), (cx + 4, eye_y + 3), (cx + 10, eye_y - 3), 2)
        elif blink:
            pygame.draw.line(surface, (0,0,0), (cx - 10, eye_y), (cx - 4, eye_y), 2)
            pygame.draw.line(surface, (0,0,0), (cx + 4, eye_y), (cx + 10, eye_y), 2)
        else:
            pygame.draw.circle(surface, (0,0,0), (cx - 7, eye_y), 3)
            pygame.draw.circle(surface, (0,0,0), (cx + 7, eye_y), 3)

        pygame.draw.arc(surface, border_col, (cx - 28, int(head_y) - 25, 56, 50), 0, 3.14, 4)
        pygame.draw.rect(surface, (30,30,30), (cx - 30, int(head_y) - 5, 10, 20))
        pygame.draw.rect(surface, (30,30,30), (cx + 20, int(head_y) - 5, 10, 20))

def run_game(config, output_file="output.mp4"):
    """
    Runs the game with the provided configuration and saves the video.
    """
    # 1. LOAD CONFIG INTO GLOBALS
    global WIDTH, HEIGHT, FPS
    WIDTH = config.get('width', 854)
    HEIGHT = config.get('height', 480)
    FPS = config.get('fps', 30)
    DURATION = config.get('duration', 15)
    
    SEED = config.get('seed', 12345)
    AI_SKILL = config.get('ai_skill', 1.0)
    THEME = config.get('theme', {'bg': (10, 10, 18), 'grid': (40, 0, 60), 'accent': (0, 255, 255)})
    
    random.seed(SEED)
    print(f"Starting Game | Res: {WIDTH}x{HEIGHT} | FPS: {FPS} | Duration: {DURATION}s")
    
    # Initialize Pygame (Headless check)
    if os.environ.get("SDL_VIDEODRIVER") == "dummy":
        print("Running in Headless Mode")
    
    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    pygame.font.init()
    
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    
    # Assets
    temp_dir = tempfile.mkdtemp()
    music_low = os.path.join(temp_dir, "bgm_low.wav")
    music_high = os.path.join(temp_dir, "bgm_high.wav")
    
    generate_dynamic_music(music_low, music_high, DURATION) 
    
    sfx_death = os.path.join(temp_dir, "death.wav")
    generate_tone(sfx_death, 150, 0.5, type='saw')
    sfx_level = os.path.join(temp_dir, "level.wav")
    generate_tone(sfx_level, 600, 0.3, type='sine')
    
    chan_music_low = pygame.mixer.Channel(0)
    chan_music_high = pygame.mixer.Channel(1)
    snd_low = pygame.mixer.Sound(music_low)
    snd_high = pygame.mixer.Sound(music_high)
    snd_death = pygame.mixer.Sound(sfx_death)
    snd_level = pygame.mixer.Sound(sfx_level)
    
    chan_music_low.play(snd_low, loops=-1)
    chan_music_high.play(snd_high, loops=-1)
    chan_music_high.set_volume(0)
    
    # Objects
    player = CartoonPlayer()
    obstacles = []
    particles = []
    level_mgr = LevelManager()
    chat = EnhancedChat()
    facecam = ExpressiveFacecam()
    
    # Apply Theme
    facecam.color = THEME['accent']
    
    font_huge = pygame.font.SysFont("Impact", 80)
    font_big = pygame.font.SysFont("Impact", 50)
    font_med = pygame.font.SysFont("Arial", 24)
    
    frame_count = 0
    score = 0
    speed = 6.0 * AI_SKILL
    spawn_timer = 0
    game_over = False
    game_over_timer = 0
    level_just_up = False
    
    MAX_FRAMES = FPS * DURATION
    GAMEOVER_DURATION = 3
    
    cmd = [
        FFMPEG_PATH, "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{WIDTH}x{HEIGHT}", "-r", str(FPS),
        "-i", "-", "-i", music_high,
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "ultrafast",
        "-c:a", "aac", "-b:a", "192k", "-shortest",
        output_file
    ]
    
    try:
        ffmpeg = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    except FileNotFoundError:
        print(f"Error: FFmpeg not found at {FFMPEG_PATH}")
        return None

    running = True
    while running:
        # Event Pump (Required even in headless)
        pygame.event.pump()
                
        if not game_over:
            # Logic
            speed = (6.0 * AI_SKILL) + (level_mgr.level * 1.5) + (frame_count / 1000.0)
            mix = min(1.0, max(0.0, (speed - 8.0) / 5.0))
            chan_music_low.set_volume(1.0 - mix)
            chan_music_high.set_volume(mix)
            
            spawn_timer += 1
            if spawn_timer > max(20, 60 - int(speed*2)):
                spawn_timer = 0
                gap = 250 - (level_mgr.level * 10)
                gap_y = random.randint(50, HEIGHT - 50 - gap)
                col = level_mgr.get_color()
                obstacles.append(Obstacle(WIDTH, 0, 60, gap_y, col))
                obstacles.append(Obstacle(WIDTH, gap_y + gap, 60, HEIGHT - (gap_y + gap), col))
            
            for o in obstacles: o.update(speed)
            
            active_obstacles = []
            for o in obstacles:
                if o.rect.right >= 0:
                    active_obstacles.append(o)
                else:
                    if o.rect.y == 0:
                        score += 100
                        if level_mgr.add_xp(100):
                            snd_level.play()
                            level_just_up = True
                            chat.add_message('hype')
            obstacles = active_obstacles
            
            # AI Logic
            target_y = HEIGHT // 2
            visible = [o for o in obstacles if o.rect.right > player.rect.left]
            if visible:
                visible.sort(key=lambda x: x.rect.left)
                nearest = visible[0]
                pair = [o for o in visible if abs(o.rect.x - nearest.rect.x) < 50]
                if len(pair) >= 2:
                    pair.sort(key=lambda x: x.rect.top)
                    target_y = (pair[0].rect.bottom + pair[1].rect.top) / 2
            
            base_jitter = math.sin(frame_count/10) * 30
            jitter = base_jitter * (2.0 - AI_SKILL) * 0.5
            player.update(target_y + jitter, 0.15)
            
            p_hitbox = player.rect.inflate(-15, -15)
            for o in obstacles:
                if p_hitbox.colliderect(o.rect):
                    game_over = True
                    snd_death.play()
                    chat.add_message('scared')
                    for _ in range(100):
                        particles.append(Particle(player.rect.centerx, player.rect.centery, NEON_RED))
                    break
            
            if frame_count > MAX_FRAMES: game_over = True
            
        else:
            game_over_timer += 1
            if game_over_timer > (GAMEOVER_DURATION * FPS): running = False
        
        for p in particles: p.update()
        facecam.update(player, obstacles, level_just_up)
        chat.update(facecam.state)
        level_just_up = False
        
        # Draw
        screen.fill(THEME['bg']) 
        off = (frame_count * speed) % 50
        for x in range(int(-off), WIDTH, 50): pygame.draw.line(screen, THEME['grid'], (x, 0), (x, HEIGHT))
        for o in obstacles: o.draw(screen)
        if not game_over: player.draw(screen)
        for p in particles: p.draw(screen)
        
        # UI
        s_surf = font_big.render(f"{score}", True, NEON_YELLOW)
        screen.blit(s_surf, (WIDTH//2 - s_surf.get_width()//2, 20))
        
        if level_mgr.level_text_timer > 0:
            level_mgr.level_text_timer -= 1
            scale = 1.0 + math.sin(level_mgr.level_text_timer * 0.2) * 0.2
            txt = f"LEVEL {level_mgr.level}"
            col = level_mgr.get_color()
            l_surf = font_huge.render(txt, True, col)
            w = int(l_surf.get_width() * scale)
            h = int(l_surf.get_height() * scale)
            l_surf = pygame.transform.scale(l_surf, (w, h))
            screen.blit(l_surf, (WIDTH//2 - w//2, HEIGHT//3))
            
        chat.draw(screen, 20, HEIGHT - 220)
        facecam.draw(screen, WIDTH - 180, HEIGHT - 140)
        
        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0, 180))
            screen.blit(overlay, (0,0))
            t1 = font_huge.render("WASTED", True, NEON_RED)
            t2 = font_big.render(f"FINAL SCORE: {score}", True, NEON_CYAN)
            screen.blit(t1, (WIDTH//2 - t1.get_width()//2, HEIGHT//2 - 60))
            screen.blit(t2, (WIDTH//2 - t2.get_width()//2, HEIGHT//2 + 40))
            
        pygame.display.flip()
        if ffmpeg:
            try: ffmpeg.stdin.write(pygame.image.tostring(screen, 'RGB'))
            except: pass
        frame_count += 1
        clock.tick(FPS)
        
    if ffmpeg: ffmpeg.stdin.close(); ffmpeg.wait()
    pygame.quit()
    try: import shutil; shutil.rmtree(temp_dir)
    except: pass
    print(f"Done. Saved {output_file}")
    return output_file

if __name__ == "__main__":
    import config_generator
    cfg = config_generator.generate_config()
    run_game(cfg, "recording_test.mp4")