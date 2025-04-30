import pgzrun
from pgzero.builtins import Actor, Rect, sounds, keys
from random import randint

WIDTH = 800
HEIGHT = 600
TITLE = "MoonHopper"

background = Actor("background")

game_state = "menu"
sound_on = True
game_over_timer = 0

button_start = Actor("button_start", center=(WIDTH // 2, 200))
button_sound = Actor("button_sound", center=(WIDTH // 2, 300))
button_exit = Actor("button_exit", center=(WIDTH // 2, 400))

keys_held = set()

class Hero(Actor):
    def __init__(self, images, pos):
        super().__init__(images[0], pos)
        self.images = images
        self.frame_index = 0
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.anim_speed = 0.2

    def update(self):
        self.frame_index += self.anim_speed
        self.frame_index %= len(self.images)
        self.image = self.images[int(self.frame_index)]

        # Horizontal movement
        if keys.LEFT in keys_held:
            self.vx = -3
        elif keys.RIGHT in keys_held:
            self.vx = 3
        else:
            self.vx = 0

        self.x += self.vx

        # Gravity
        self.vy += 0.5
        self.y += self.vy

        if self.y > HEIGHT:
            reset_game()

    def jump(self):
        if self.on_ground:
            self.vy = -12.5
            if sound_on:
                try:
                    sounds.jump.play()
                except:
                    print("Warning: jump.wav not found")

class Enemy(Actor):
    def __init__(self, images, pos, patrol_range):
        super().__init__(images[0], pos)
        self.images = images
        self.frame_index = 0
        self.direction = 1
        self.patrol_range = patrol_range
        self.start_x = pos[0]
        self.anim_speed = 0.2

    def update(self):
        self.frame_index += self.anim_speed
        self.frame_index %= len(self.images)
        self.image = self.images[int(self.frame_index)]
        self.x += self.direction * 1
        if abs(self.x - self.start_x) > self.patrol_range:
            self.direction *= -1

hero = Hero(["hero1", "hero2", "hero3"], (100, 500))
enemies = [
    Enemy(["enemy1", "enemy2", "enemy3"], (400, 500), 100),
    Enemy(["enemy1", "enemy2", "enemy3"], (600, 400), 150),
]
platforms = [
    Rect((0, 550), (800, 50)),
    Rect((300, 450), (200, 20)),
    Rect((600, 350), (150, 20)),
]
star_seed = Actor("star_seed", center=(700, 330))

def start_game():
    global game_state
    game_state = "playing"
    if sound_on:
        try:
            music.play("background_music")
        except:
            print("Warning: background_music.mp3 not found")

def reset_game():
    global game_state, game_over_timer
    hero.x, hero.y = 100, 500
    hero.vx, hero.vy = 0, 0
    game_state = "game_over"
    game_over_timer = 60
    if sound_on:
        try:
            music.stop()
        except:
            pass

def win_game():
    global game_state
    game_state = "win"
    if sound_on:
        try:
            music.stop()
        except:
            pass

def draw():
    screen.clear()
    background.draw()
    if game_state == "menu":
        button_start.draw()
        button_sound.draw()
        button_exit.draw()
    elif game_state == "playing":
        for plat in platforms:
            screen.draw.filled_rect(plat, (100, 100, 100))
        hero.draw()
        star_seed.draw()
        for enemy in enemies:
            enemy.draw()
    elif game_state == "game_over":
        screen.draw.text("Game Over", center=(WIDTH // 2, HEIGHT // 2), fontsize=64, color="red")
    elif game_state == "win":
        screen.draw.text("You Win!", center=(WIDTH // 2, HEIGHT // 2), fontsize=64, color="yellow")

def update():
    global game_state, game_over_timer
    if game_state == "playing":
        hero.update()
        for enemy in enemies:
            enemy.update()

        # --- Correct platform collision logic ---
        hero.on_ground = False
        for plat in platforms:
            hero_bottom = hero.y + hero.height // 2
            plat_top = plat.top

            if (hero.vy >= 0 and
                hero_bottom >= plat_top - 5 and
                hero_bottom <= plat_top + 10 and
                hero.colliderect(plat)):

                hero.y = plat_top - hero.height // 2
                hero.vy = 0
                hero.on_ground = True
                break

        for enemy in enemies:
            if hero.colliderect(enemy):
                if sound_on:
                    try:
                        sounds.enemy_hit.play()
                    except:
                        print("Warning: enemy_hit.wav not found")
                reset_game()

        if hero.colliderect(star_seed):
            win_game()

    elif game_state == "game_over":
        game_over_timer -= 1
        if game_over_timer <= 0:
            game_state = "menu"

def on_mouse_down(pos):
    global sound_on
    if game_state == "menu":
        if button_start.collidepoint(pos):
            start_game()
        elif button_sound.collidepoint(pos):
            sound_on = not sound_on
            if not sound_on:
                try:
                    music.stop()
                except:
                    pass
            elif game_state == "playing":
                try:
                    music.play("background_music")
                except:
                    print("Warning: background_music.mp3 not found")
        elif button_exit.collidepoint(pos):
            pgzrun.quit()

def on_key_down(key):
    keys_held.add(key)
    if game_state == "playing":
        if key == keys.SPACE:
            hero.jump()
        elif key == keys.ESCAPE:
            pgzrun.quit()

def on_key_up(key):
    if key in keys_held:
        keys_held.remove(key)

pgzrun.go()
