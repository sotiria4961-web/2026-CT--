import pygame
import sys
import random
import os


# 1. 게임 초기화
pygame.init()
pygame.mixer.init()

# --- 2. 기본 상수 설정 ---
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600
FPS = 60

# 색상 정의
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
DARK_BLUE = (0, 0, 139)
LIGHT_BLUE = (173, 216, 230)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
GREY = (100, 100, 100)

# 캐릭터 데이터 정의
CHARACTERS_COLOR = {
    "A": RED, "B": GREEN, "C": BLUE, "D": YELLOW, "E": CYAN, "F": MAGENTA
}
CHARACTER_IDS = list(CHARACTERS_COLOR.keys())

GROUND_Y = SCREEN_HEIGHT - 100

# 플레이어 크기 및 속성
PLAYER_START_X = 90
PLAYER_START_Y = GROUND_Y
PLAYER_WIDTH = 70
PLAYER_HEIGHT = 90

GRAVITY = 1.0
JUMP_STRENGTH = -16
HIGH_JUMP_STRENGTH = -22

# --- 3. 게임 창 설정 ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("A+를 향해 달려라! (Final Fixed Ver.)")
clock = pygame.time.Clock()

# --- 4. 폰트 설정 ---
try:
    font_small = pygame.font.SysFont("malgungothic", 35)
    font_medium = pygame.font.SysFont("malgungothic", 45)
    font_large = pygame.font.SysFont("malgungothic", 60)
    font_xl = pygame.font.SysFont("malgungothic", 80)
    font_icon = pygame.font.SysFont("arialblack", 20)
    font_obstacle = pygame.font.SysFont("arialblack", 30)
except Exception as e:
    font_small = pygame.font.SysFont(None, 40)
    font_medium = pygame.font.SysFont(None, 50)
    font_large = pygame.font.SysFont(None, 60)
    font_xl = pygame.font.SysFont(None, 80)
    font_icon = pygame.font.SysFont(None, 30)
    font_obstacle = pygame.font.SysFont(None, 40)


# --- 5. 이미지 에셋 로드 함수 (경로 문제 완벽 해결 버전) ---
def load_image(filename, width, height, color_fallback):
    """
    이미지를 로드합니다.
    실행 위치와 상관없이, 무조건 game.py 파일이 있는 폴더를 기준으로 파일을 찾습니다.
    """
    # 1. 현재 실행 중인 파이썬 파일(game.py)의 폴더 경로를 확실하게 알아냅니다.
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 2. 우선 game.py 옆에서 찾아봅니다.
    path = os.path.join(current_dir, filename)

    # 3. 없으면 assets 폴더 안도 찾아봅니다.
    if not os.path.exists(path):
        path = os.path.join(current_dir, "assets", filename)

    try:
        if os.path.exists(path):
            image = pygame.image.load(path).convert_alpha()

            # 크기 조절 (0보다 클 때만)
            if width > 0 and height > 0:
                image = pygame.transform.scale(image, (width, height))
            else:
                # 로그가 너무 많으면 정신없으므로 원본 사용 알림은 주석 처리해도 됩니다.
                # print(f"[알림] {filename} 원본 크기 사용")
                pass

            print(f"[성공] 로드됨: {filename}")
            return image
        else:
            # 파일을 못 찾았을 때, 컴퓨터가 어디를 뒤졌는지 경로를 출력해줍니다. (디버깅용)
            print(f"[실패] 파일 없음: {filename}")
            print(f"      (탐색한 위치: {path})")
            raise FileNotFoundError

    except Exception as e:
        # 이미지가 없을 때 색상 박스로 대체
        target_w = width if width > 0 else 50
        target_h = height if height > 0 else 50
        surf = pygame.Surface((target_w, target_h))
        surf.fill(color_fallback)
        return surf


def load_game_assets():
    print("--- 에셋 로딩 시작 ---")
    assets = {
        "backgrounds": {},
        "characters": {},
        "road": None,
        "items": {},
        "die": None,
        "title_screen": None,
        "obstacles": {
            1: {"force_jump": [], "tall_jump": [], "force_slide": []},
            2: {"force_jump": [], "tall_jump": [], "force_slide": []},
            3: {"force_jump": [], "tall_jump": [], "force_slide": []}
        }
    }

    # 1. 배경 이미지 로드
    bg_width = SCREEN_WIDTH * 2
    for i in range(1, 4):
        bg = load_image(f"background{i}.png", bg_width, SCREEN_HEIGHT, BLACK)
        assets["backgrounds"][i] = bg

    # 2. 캐릭터 이미지 로드
    for char_id in CHARACTER_IDS:
        char_assets = {"run": [], "jump": None, "slide": None}
        base_color = CHARACTERS_COLOR[char_id]
        for frame in range(1, 4):
            fname = f"{char_id}{frame}.png"
            img = load_image(fname, PLAYER_WIDTH, PLAYER_HEIGHT, base_color)
            char_assets["run"].append(img)
        fname_jump = f"{char_id}J.png"
        char_assets["jump"] = load_image(fname_jump, PLAYER_WIDTH, PLAYER_HEIGHT, base_color)
        fname_slide = f"{char_id}S.png"
        char_assets["slide"] = load_image(fname_slide, PLAYER_WIDTH, PLAYER_HEIGHT//2, base_color)
        char_assets["portrait"] = load_image(f"{char_id}.png", 1000, 1000, base_color)
        assets["characters"][char_id] = char_assets

    # 3. 아이템 이미지 로드
    assets["items"]["invincibility"] = load_image("Item1.png", 60, 60, CYAN)
    assets["items"]["dash"] = load_image("Item2.png", 60, 60, YELLOW)

    # 4. 도로 이미지 로드
    assets["road"] = load_image("road.png", 0, 0, DARK_BLUE)

    # 5. 비석 이미지 로드
    assets["die"] = load_image("Die.png", 80, 80, GREY)

    # 6. 장애물 이미지 로드 (챕터/타입별)
    type_map = {
        "Small": "force_jump",
        "Tall": "tall_jump",
        "Slide": "force_slide"
    }
    for chapter in range(1, 4):
        for file_type, game_type in type_map.items():
            for i in range(1, 6):
                fname = f"Obs_C{chapter}_{file_type}_{i}.png"
                path = fname
                if not os.path.exists(path): path = os.path.join("assets", fname)
                if os.path.exists(path):
                    img = pygame.image.load(path).convert_alpha()
                    assets["obstacles"][chapter][game_type].append(img)
                    print(f"[성공] 장애물 로드: {fname} -> {game_type}")
    # 타이틀
    assets["title_screen"] = load_image("1screen.png", SCREEN_WIDTH, SCREEN_HEIGHT, BLUE)


    print("--- 에셋 로딩 완료 ---\n")
    return assets


GAME_ASSETS = load_game_assets()

# --- 6. 게임 진행도 변수 ---
max_unlocked_chapter = 1
character_roster = []


# --- 7. 플레이어 클래스 ---
class Player(pygame.sprite.Sprite):
    def __init__(self, char_id):
        super().__init__()
        self.character_id = char_id
        self.assets = GAME_ASSETS["characters"][char_id]
        self.image = self.assets["run"][0]
        self.rect = pygame.Rect(PLAYER_START_X, PLAYER_START_Y - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.run_index = 0
        self.anim_timer = 0
        self.anim_speed = 0.15
        self.vel_y = 0
        self.is_jumping = True
        self.is_sliding = False
        self.is_dead = False
        self.is_reviving = False
        self.double_jumps = 0
        self.max_jumps = 2
        self.effect_active = False
        self.effect_start_time = 0
        self.effect_duration = 3000
        self.current_effect_color = None
        self.high_jump_active = False
        self.high_jump_end_time = 0
        self.is_big = False
        self.skill_used_this_chapter = False
        self.is_visible = True

    def update(self, pit_group, platform_group, speed):
        if self.is_dead:
            self.rect.x -= speed
            return

        keys = pygame.key.get_pressed()

        # [슬라이드 키 입력] 공중에 살짝 떠도 슬라이드 상태 유지
        if keys[pygame.K_DOWN] and (not self.is_jumping or self.is_sliding):
            self.slide(True)
        else:
            self.slide(False)

        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

        on_platform = False

        # [수정] 떨어지는 중이거나(vel_y > 0) 바닥에 붙어있을 때 발판 체크
        # '+ 15'로 인식 범위를 늘려서 슬라이드 시 발이 살짝 들려도 놓치지 않게 함
        if self.vel_y >= 0:
            platform_hits = pygame.sprite.spritecollide(self, platform_group, False)
            for platform in platform_hits:
                # 발바닥이 발판 상단보다 살짝 아래(15px)까지 허용 -> 확실하게 밟힘
                if self.rect.bottom <= platform.rect.top + (self.vel_y + 15) and self.rect.bottom >= platform.rect.top:
                    if self.rect.right > platform.rect.left + 10 and self.rect.left < platform.rect.right - 10:
                        self.rect.bottom = platform.rect.top
                        self.vel_y = 0
                        self.is_jumping = False
                        self.double_jumps = 0
                        on_platform = True
                        break

        # 바닥(GROUND) 체크
        if self.rect.top > GROUND_Y:
            self.is_dead = True
            self.vel_y = 0
            return

        on_ground = (self.rect.bottom >= GROUND_Y)

        if on_platform:
            pass
        elif on_ground:
            pit_hit_list = pygame.sprite.spritecollide(self, pit_group, False)
            if pit_hit_list:
                self.is_jumping = True
            else:
                self.rect.bottom = GROUND_Y
                self.vel_y = 0
                self.is_jumping = False
                self.double_jumps = 0
        else:
            self.is_jumping = True

        self.update_animation()

        # (이펙트 처리 코드는 기존과 동일하므로 생략하지 않고 그대로 두셔도 됩니다)
        # ... 아래 이펙트 코드는 그대로 두세요 ...
        if self.effect_active:
            current_time = pygame.time.get_ticks()
            time_elapsed = current_time - self.effect_start_time
            time_remaining = self.effect_duration - time_elapsed
            if time_remaining <= 0:
                self.deactivate_effect()
            elif time_remaining < 1000:
                self.is_visible = (current_time // 100) % 2 == 0
            else:
                self.is_visible = True
        else:
            self.is_visible = True

        if self.high_jump_active:
            if pygame.time.get_ticks() > self.high_jump_end_time:
                self.high_jump_active = False

        if self.is_reviving:
            self.rect.x += speed * 0.5
            if self.rect.centerx >= (PLAYER_START_X + PLAYER_WIDTH / 2):
                self.is_reviving = False
                self.rect.centerx = PLAYER_START_X + PLAYER_WIDTH / 2
        else:
            self.rect.centerx = PLAYER_START_X + (PLAYER_WIDTH / 2)

    def update_animation(self):
        if self.is_sliding:
            self.image = self.assets["slide"]
        elif self.is_jumping:
            self.image = self.assets["jump"]
        else:
            self.anim_timer += 1 / FPS
            if self.anim_timer >= self.anim_speed:
                self.anim_timer = 0
                self.run_index = (self.run_index + 1) % 3
                self.image = self.assets["run"][self.run_index]

    def jump(self):
        jump_power = HIGH_JUMP_STRENGTH if self.high_jump_active else JUMP_STRENGTH
        if self.double_jumps < self.max_jumps:
            self.vel_y = jump_power
            self.is_jumping = True
            self.double_jumps += 1

    def slide(self, is_sliding_key_pressed):
        # 1. 슬라이드 시작
        if is_sliding_key_pressed and not self.is_sliding:
            self.is_sliding = True
            # 현재 발 위치(midbottom)를 기억해둡니다.
            current_pos = self.rect.midbottom
            # 슬라이드 크기(높이 절반)로 Rect를 새로 잡되, 발 위치는 그대로 유지합니다.
            self.rect = pygame.Rect(self.rect.x, 0, PLAYER_WIDTH, PLAYER_HEIGHT // 2)
            self.rect.midbottom = current_pos

        # 2. 슬라이드 끝 (일어서기)
        elif not is_sliding_key_pressed and self.is_sliding:
            self.is_sliding = False
            # 다시 원래 발 위치를 기준으로 일어섭니다.
            current_pos = self.rect.midbottom
            self.rect = pygame.Rect(self.rect.x, 0, PLAYER_WIDTH, PLAYER_HEIGHT)
            self.rect.midbottom = current_pos

    def draw(self, surface):
        if not self.is_visible: return
        if self.is_dead:
            self.draw_dead(surface, force_y=GROUND_Y)
            return
        surface.blit(self.image, self.rect)

    def draw_dead(self, surface, force_y=None):
        die_image = GAME_ASSETS["die"]
        bottom_y = force_y if force_y is not None else self.rect.bottom
        center_x = self.rect.centerx
        die_rect = die_image.get_rect(midbottom=(center_x, bottom_y))
        surface.blit(die_image, die_rect)

    def activate_skill(self):
        current_time = pygame.time.get_ticks()
        if not self.skill_used_this_chapter:
            self.skill_used_this_chapter = True

            # [수정] A 또는 D일 때: 높은 점프 (RED 효과)
            if self.character_id in ['A', 'D']:
                self.high_jump_active = True
                self.high_jump_end_time = current_time + self.effect_duration
                # D도 A와 똑같이 빨간색 이펙트를 냅니다.
                # (만약 D는 노란색을 내고 싶다면 apply_effect(YELLOW, ...)로 색만 분기하면 됩니다)
                self.apply_effect(RED, is_big=False)

            # [수정] B 또는 E일 때: 거대화 (CYAN 효과)
            elif self.character_id in ['B', 'E']:
                self.apply_effect(CYAN, is_big=True)

            # [수정] C 또는 F일 때: 대시 (YELLOW 효과)
            elif self.character_id in ['C', 'F']:
                self.apply_effect(YELLOW, is_big=False)

            else:
                # 스킬이 없는 캐릭터 (현재는 없음)
                self.skill_used_this_chapter = False
        else:
            print("스킬을 이미 사용했습니다.")

    def activate_item_effect(self, item_type):
        if item_type == 'invincibility':
            self.apply_effect(CYAN, is_big=True)
        elif item_type == 'dash':
            self.apply_effect(YELLOW, is_big=False)

    def apply_effect(self, color, is_big=False):
        self.effect_active = True
        self.effect_start_time = pygame.time.get_ticks()
        self.current_effect_color = color
        self.is_big = is_big
        self.is_visible = True

    def deactivate_effect(self):
        self.effect_active = False
        self.current_effect_color = None
        self.is_big = False
        self.is_visible = True

    def revive(self, start_x):
        self.is_dead = False
        self.is_reviving = True
        self.rect.bottomleft = (start_x, GROUND_Y)
        self.vel_y = 0
        self.is_jumping = True
        self.double_jumps = 0
        self.is_visible = True
        self.deactivate_effect()


# --- 8. 장애물 클래스 ---
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, obs_type, chapter, x_pos=SCREEN_WIDTH, y_pos=GROUND_Y):
        super().__init__()
        self.obs_type = obs_type

        # 크기 설정 (너비 40)
        if self.obs_type == 'force_jump':
            width, height = 30, 60
            self.rect = pygame.Rect(0, 0, width, height)
            self.rect.bottomleft = (x_pos, y_pos)
        elif self.obs_type == 'tall_jump':
            width, height = 30, 110
            self.rect = pygame.Rect(0, 0, width, height)
            self.rect.bottomleft = (x_pos, y_pos)
        elif self.obs_type == 'force_slide':
            width, height = 30, 230
            self.rect = pygame.Rect(0, 0, width, height)
            self.rect.bottomleft = (x_pos, y_pos - 70)

        # 이미지 랜덤 적용
        if GAME_ASSETS["obstacles"][chapter][self.obs_type]:
            chosen_image = random.choice(GAME_ASSETS["obstacles"][chapter][self.obs_type])
            self.image = pygame.transform.scale(chosen_image, (width, height))
        else:
            self.image = pygame.Surface([width, height])
            self.image.fill(RED)
            pygame.draw.rect(self.image, WHITE, (5, 5, width - 10, height - 10), 3)
            try:
                text = font_obstacle.render("F", True, WHITE)
                text_rect = text.get_rect(center=(width // 2, height // 2))
                self.image.blit(text, text_rect)
            except:
                pass

    def update(self, speed):
        self.rect.x -= speed
        if self.rect.right < 0:
            self.kill()

    def draw(self, surface):
        surface.blit(self.image, self.rect)


# --- 9. 구멍 클래스 ---
class Pit(pygame.sprite.Sprite):
    def __init__(self, x_pos=SCREEN_WIDTH, width=None):
        super().__init__()
        if width is None:
            pit_width = random.randint(100, 250)
        else:
            pit_width = width
        self.image = pygame.Surface([pit_width, 100])
        self.image.fill(BLACK)
        self.rect = self.image.get_rect(topleft=(x_pos, GROUND_Y))

    def update(self, speed):
        self.rect.x -= speed
        if self.rect.right < 0: self.kill()

    def draw(self, surface):
        surface.blit(self.image, self.rect)


# --- 10. 플랫폼 클래스 ---
class Platform(pygame.sprite.Sprite):
    def __init__(self, plat_type, width, x_pos=SCREEN_WIDTH, y_pos=None):
        super().__init__()
        self.plat_type = plat_type
        plat_width = width
        plat_height = 40

        if self.plat_type == 'floating':
            plat_y = y_pos if y_pos is not None else random.randint(GROUND_Y - 180, GROUND_Y - 100)
        elif self.plat_type == 'low_ground':
            plat_y = y_pos if y_pos is not None else GROUND_Y - 80
        elif self.plat_type == 'ground':
            plat_y = y_pos if y_pos is not None else GROUND_Y

        self.image = pygame.Surface([plat_width, plat_height])
        road_img = GAME_ASSETS.get("road")
        if road_img and road_img.get_width() > 1:
            img_w = road_img.get_width()
            img_h = road_img.get_height()
            scale_factor = plat_height / img_h
            new_w = int(img_w * scale_factor)
            new_h = plat_height
            scaled_road = pygame.transform.scale(road_img, (new_w, new_h))
            for x in range(0, plat_width, new_w):
                self.image.blit(scaled_road, (x, 0))
        else:
            self.image.fill(DARK_BLUE)
            pygame.draw.rect(self.image, LIGHT_BLUE, (0, 0, plat_width, plat_height // 3))
        self.rect = self.image.get_rect(topleft=(x_pos, plat_y))

    def update(self, speed):
        self.rect.x -= speed
        if self.rect.right < 0: self.kill()

    def draw(self, surface):
        surface.blit(self.image, self.rect)


# --- 11. 아이템/젤리 등 ---
class Item(pygame.sprite.Sprite):
    def __init__(self, item_type):
        super().__init__()
        self.item_type = item_type
        if self.item_type == 'invincibility':
            self.image = GAME_ASSETS["items"]["invincibility"]
        elif self.item_type == 'dash':
            self.image = GAME_ASSETS["items"]["dash"]
        else:
            self.image = pygame.Surface([60, 60])
            self.image.fill(YELLOW)
        float_y = random.randint(GROUND_Y - 120, GROUND_Y - 50)
        self.rect = self.image.get_rect(midleft=(SCREEN_WIDTH, float_y))

    def update(self, speed):
        self.rect.x -= speed
        if self.rect.right < 0: self.kill()

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Collectible(pygame.sprite.Sprite):
    def __init__(self, coll_type, x_pos=SCREEN_WIDTH, y_pos=None):
        super().__init__()
        self.coll_type = coll_type
        self.image = pygame.Surface([20, 25])
        self.image.fill(BLACK)
        self.image.set_colorkey(BLACK)
        if self.coll_type == 'grade_point':
            pygame.draw.rect(self.image, MAGENTA, (0, 0, 20, 25), border_radius=7)
        if y_pos is None: y_pos = random.randint(GROUND_Y - 180, GROUND_Y - 50)
        self.rect = self.image.get_rect(midleft=(x_pos, y_pos))

    def update(self, speed):
        self.rect.x -= speed
        if self.rect.right <20: self.kill()

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class SpeedLine(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([random.randint(20, 40), 2])
        self.image.fill(WHITE)
        y_pos = random.randint(0, SCREEN_HEIGHT)
        self.rect = self.image.get_rect(topleft=(SCREEN_WIDTH, y_pos))

    def update(self, speed):
        self.rect.x -= speed * 5
        if self.rect.right < 0: self.kill()


# --- 12. 버튼 정의 ---
chapter_buttons = {
    1: pygame.Rect(SCREEN_WIDTH // 4 - 100, SCREEN_HEIGHT // 2 - 75, 200, 150),
    2: pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 75, 200, 150),
    3: pygame.Rect(SCREEN_WIDTH * 3 // 4 - 100, SCREEN_HEIGHT // 2 - 75, 200, 150),
}
confirm_yes_button = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50, 120, 50)
confirm_no_button = pygame.Rect(SCREEN_WIDTH // 2 + 30, SCREEN_HEIGHT // 2 + 50, 120, 50)

character_buttons = {}
btn_width, btn_height = 100, 100
btn_spacing = 40
total_width = (btn_width * 6) + (btn_spacing * 5)
start_x = (SCREEN_WIDTH - total_width) / 2
for i, (char_id, char_color) in enumerate(CHARACTERS_COLOR.items()):
    x = start_x + i * (btn_width + btn_spacing)
    y = SCREEN_HEIGHT // 2 - 50
    character_buttons[char_id] = pygame.Rect(x, y, btn_width, btn_height)

restart_button_rect = pygame.Rect((SCREEN_WIDTH - 160) / 2, (SCREEN_HEIGHT // 2) + 80, 160, 60)
relay_yes_button_rect = pygame.Rect((SCREEN_WIDTH // 2 - 150), (SCREEN_HEIGHT // 2 + 50), 120, 50)
relay_no_button_rect = pygame.Rect((SCREEN_WIDTH // 2 + 30), (SCREEN_HEIGHT // 2 + 50), 120, 50)


# --- 13. 메인 게임 루프 ---
def main_game():
    global max_unlocked_chapter, character_roster

    player1 = None
    player2 = None
    current_player = None

    obstacle_group = pygame.sprite.Group()
    item_group = pygame.sprite.Group()
    pit_group = pygame.sprite.Group()
    platform_group = pygame.sprite.Group()
    speed_line_group = pygame.sprite.Group()
    collectible_group = pygame.sprite.Group()
    ground_group = pygame.sprite.Group()

    game_state = "TITLE_SCREEN"

    try:
        if os.path.exists("open.wav") or os.path.exists("assets/open.wav"):
            pygame.mixer.music.load('open.wav' if os.path.exists("open.wav") else "assets/open.wav")
            pygame.mixer.music.play(-1)
    except:
        pass

    game_start_time = 0
    elapsed_seconds = 0
    score = 0
    relay_prompt_start_time = 0
    selected_chapter = 0
    current_chapter = 1
    current_obstacle_speed = 7
    final_grade = ""
    last_obstacle_spawn_time = 0
    next_obstacle_spawn_delay = 4500
    item_spawn_count = 0
    item_spawn_limit = 0
    selected_char_index = 0
    selected_button_index = 0
    transition_start_time = 0

    current_background = None
    background_x = 0

    ITEM_SPAWN_TIMER = pygame.USEREVENT + 2
    pygame.time.set_timer(ITEM_SPAWN_TIMER, 6000)
    COLLECTIBLE_SPAWN_TIMER = pygame.USEREVENT + 3
    pygame.time.set_timer(COLLECTIBLE_SPAWN_TIMER, 1000)

    running = True
    while running:
        current_time_ticks = pygame.time.get_ticks()
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if game_state == "TITLE_SCREEN":
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    if not character_roster:
                        game_state = "CHARACTER_SELECT"
                    else:
                        game_state = "CHAPTER_SELECT"

            elif game_state == "CHAPTER_SELECT":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for chapter, rect in chapter_buttons.items():
                        if chapter == 2 and max_unlocked_chapter < 2: continue
                        if rect.collidepoint(event.pos):
                            if chapter <= max_unlocked_chapter:
                                selected_chapter = chapter
                                selected_button_index = 0
                                game_state = "CONFIRM_START"

            elif game_state == "CONFIRM_START":
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_LEFT, pygame.K_UP):
                        selected_button_index = 0
                    elif event.key in (pygame.K_RIGHT, pygame.K_DOWN):
                        selected_button_index = 1
                    elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        if selected_button_index == 0:
                            game_state = "LOADING_TRANSITION"
                            transition_start_time = current_time_ticks
                        else:
                            game_state = "CHAPTER_SELECT"
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if confirm_yes_button.collidepoint(event.pos):
                        game_state = "LOADING_TRANSITION"
                        transition_start_time = current_time_ticks
                    elif confirm_no_button.collidepoint(event.pos):
                        game_state = "CHAPTER_SELECT"

            elif game_state == "CHARACTER_SELECT":
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_LEFT, pygame.K_UP):
                        selected_char_index = (selected_char_index - 1) % 6
                    elif event.key in (pygame.K_RIGHT, pygame.K_DOWN):
                        selected_char_index = (selected_char_index + 1) % 6
                    elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        char_id = CHARACTER_IDS[selected_char_index]
                        if len(character_roster) < 2 and char_id not in character_roster:
                            character_roster.append(char_id)
                            if len(character_roster) == 2:
                                game_state = "CHAPTER_SELECT"
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for i, rect in enumerate(character_buttons.values()):
                        if rect.collidepoint(event.pos):
                            char_id = CHARACTER_IDS[i]
                            if len(character_roster) < 2 and char_id not in character_roster:
                                character_roster.append(char_id)
                                if len(character_roster) == 2:
                                    game_state = "CHAPTER_SELECT"

            elif game_state == "PLAYING":
                if event.type == pygame.KEYDOWN:
                    jump_sound = pygame.mixer.Sound("jump.mp3")
                    if event.key == pygame.K_UP: current_player.jump()
                    if event.key == pygame.K_UP: jump_sound.play()
                    if event.key == pygame.K_SPACE: current_player.activate_skill()
                    if event.key == pygame.K_p: game_state = "PAUSED"
                    if event.key == pygame.K_ESCAPE: running = False
                if event.type == ITEM_SPAWN_TIMER and item_spawn_count < item_spawn_limit:
                    item_type = random.choice(['invincibility', 'dash'])
                    new_item = Item(item_type)
                    all_obstacles = pygame.sprite.Group(obstacle_group, platform_group, ground_group)
                    if not pygame.sprite.spritecollide(new_item, all_obstacles, False):
                        item_spawn_count += 1
                        item_group.add(new_item)
                if event.type == COLLECTIBLE_SPAWN_TIMER:
                    if random.random() < 0.7: collectible_group.add(Collectible('grade_point'))

            elif game_state == "PAUSED":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p: game_state = "PLAYING"
                    if event.key == pygame.K_ESCAPE: running = False

            elif game_state == "RELAY_PROMPT":
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_LEFT, pygame.K_UP):
                        selected_button_index = 0
                    elif event.key in (pygame.K_RIGHT, pygame.K_DOWN):
                        selected_button_index = 1
                    elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        if selected_button_index == 0:
                            current_player = player2
                            current_player.revive(player1.rect.x - 150)
                            obstacle_group.empty();
                            item_group.empty();
                            pit_group.empty()
                            platform_group.empty();
                            speed_line_group.empty();
                            collectible_group.empty()
                            game_state = "PLAYING"
                        else:
                            game_state = "GAME_OVER"
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if relay_yes_button_rect.collidepoint(event.pos):
                        current_player = player2
                        current_player.revive(player1.rect.x - 150)
                        obstacle_group.empty();
                        item_group.empty();
                        pit_group.empty()
                        platform_group.empty();
                        speed_line_group.empty();
                        collectible_group.empty()
                        game_state = "PLAYING"
                    elif relay_no_button_rect.collidepoint(event.pos):
                        game_state = "GAME_OVER"

            elif game_state == "GAME_OVER":
                if (event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_RETURN)) or \
                        (event.type == pygame.MOUSEBUTTONDOWN and restart_button_rect.collidepoint(event.pos)):
                    game_state = "TITLE_SCREEN"
                    max_unlocked_chapter = 1
                    character_roster = []
                    player1 = None;
                    player2 = None;
                    current_player = None
                    obstacle_group.empty();
                    item_group.empty();
                    pit_group.empty()
                    platform_group.empty();
                    speed_line_group.empty();
                    collectible_group.empty()
                    ground_group.empty()

            elif game_state == "GAME_CLEAR":
                if final_grade != "A+":
                    if (event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_RETURN)) or \
                            (event.type == pygame.MOUSEBUTTONDOWN and restart_button_rect.collidepoint(event.pos)):
                        game_state = "CHAPTER_SELECT"
                        obstacle_group.empty();
                        item_group.empty();
                        pit_group.empty()
                        platform_group.empty();
                        speed_line_group.empty();
                        collectible_group.empty()
                        ground_group.empty()
                else:
                    if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                        game_state = "HIDDEN_CREDIT"

            elif game_state == "HIDDEN_CREDIT":
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    game_state = "TITLE_SCREEN"
                    character_roster = []

        if game_state == "PLAYING":
            if not player1.is_dead:
                current_player = player1
            else:
                current_player = player2

            elapsed_time = current_time_ticks - game_start_time
            elapsed_seconds = elapsed_time // 1000
            time_boost = 1 if elapsed_seconds > 30 else 0
            current_accelerated_speed = current_obstacle_speed + time_boost
            speed_multiplier = 1.0
            if (current_player.effect_active and current_player.current_effect_color == YELLOW):
                speed_multiplier = 3.0
            final_speed = current_accelerated_speed * speed_multiplier

            if speed_multiplier > 1.0 or current_player.is_reviving:
                if random.randint(1, 4) == 1: speed_line_group.add(SpeedLine())

            if current_background:
                bg_width = current_background.get_width()
                max_scroll = bg_width - SCREEN_WIDTH
                progress = min(elapsed_seconds / 45.0, 1.0)
                background_x = - (max_scroll * progress)

            player1.update(pit_group, platform_group, final_speed)
            player2.update(pit_group, platform_group, final_speed)
            obstacle_group.update(final_speed)
            item_group.update(final_speed)
            pit_group.update(final_speed)
            platform_group.update(final_speed)
            speed_line_group.update(final_speed)
            collectible_group.update(final_speed)
            ground_group.update(final_speed)

            if ground_group:
                last_ground = max(ground_group, key=lambda g: g.rect.right)
                if last_ground.rect.right < SCREEN_WIDTH + 200:
                    new_plat_width = random.randint(300, 550)
                    ground_group.add(Platform('ground', new_plat_width, x_pos=last_ground.rect.right))

            if elapsed_seconds > 45:
                if current_chapter == 3 and current_player is player1:
                    final_grade = "A+"
                    game_state = "GAME_CLEAR"
                else:
                    final_grade = "A"
                    if current_chapter == max_unlocked_chapter:
                        max_unlocked_chapter = min(max_unlocked_chapter + 1, 3)
                    if current_chapter < 3:
                        game_state = "CHAPTER_SELECT"
                    else:
                        game_state = "GAME_CLEAR"

            if current_time_ticks - last_obstacle_spawn_time > next_obstacle_spawn_delay:
                spawn_choice = random.choices(['obstacle', 'pit', 'platform'], weights=[0.5, 0.2, 0.3], k=1)[0]
                if spawn_choice == 'obstacle':
                    obstacle_group.add(
                        Obstacle(random.choice(['force_jump', 'force_slide', 'tall_jump']), chapter=current_chapter))
                elif spawn_choice == 'pit':
                    if not platform_group: pit_group.add(Pit())
                else:
                    plat_type = random.choice(['floating', 'low_ground'])
                    new_width = random.randint(300, 550) if plat_type == 'floating' else random.randint(300, 600)
                    new_platform = Platform(plat_type, new_width)
                    platform_group.add(new_platform)
                    if random.random() < 0.5:
                        obs_type = random.choice(['force_jump', 'tall_jump'])
                        obstacle_x = SCREEN_WIDTH + random.randint(30, new_width - 60)
                        obstacle_y = new_platform.rect.top
                        obstacle_group.add(
                            Obstacle(obs_type, chapter=current_chapter, x_pos=obstacle_x, y_pos=obstacle_y))

                last_obstacle_spawn_time = current_time_ticks
                if current_accelerated_speed < 9:
                    next_obstacle_spawn_delay = random.randint(400, 1200)
                elif current_accelerated_speed < 12:
                    next_obstacle_spawn_delay = random.randint(300, 900)
                else:
                    next_obstacle_spawn_delay = random.randint(250, 700)

            # 젤리 충돌 (버그 수정됨)
            for item in pygame.sprite.spritecollide(current_player, collectible_group, True):
                game_start_time -= 1000
                item_sound = pygame.mixer.Sound("coin.mp3")
                item_sound.play()


            for item in pygame.sprite.spritecollide(current_player, item_group, True):
                current_player.activate_item_effect(item.item_type)

            if (current_player.is_dead or \
                (not current_player.effect_active and pygame.sprite.spritecollide(current_player, obstacle_group,
                                                                                  False))) \
                    and not current_player.is_reviving:
                if current_chapter == 1:
                    grade_to_set = "F"
                elif current_chapter == 2:
                    grade_to_set = "D" if elapsed_seconds < 30 else "C"
                elif current_chapter == 3:
                    grade_to_set = "B" if elapsed_seconds < 30 else "A (Fail)"

                if current_player is player1:
                    game_state = "RELAY_PROMPT"
                    final_grade = grade_to_set
                    player1.is_dead = True
                    relay_prompt_start_time = current_time_ticks
                    selected_button_index = 0
                elif current_player is player2:
                    game_state = "GAME_OVER"
                    final_grade = grade_to_set
                    player2.is_dead = True

        elif game_state == "RELAY_PROMPT":
            if current_time_ticks - relay_prompt_start_time > 10000:
                game_state = "GAME_OVER"

        elif game_state == "LOADING_TRANSITION":
            elapsed = current_time_ticks - transition_start_time
            radius = int((elapsed / 1500) * SCREEN_WIDTH * 0.7)
            if radius > SCREEN_WIDTH * 0.7:
                game_state = "PLAYING"
                player1 = Player(character_roster[0])
                player2 = Player(character_roster[1])
                player2.is_dead = True;
                player2.rect.x = -200
                current_player = player1
                game_start_time = current_time_ticks
                elapsed_seconds = 0
                score = 0
                current_chapter = selected_chapter

                if current_chapter in GAME_ASSETS["backgrounds"]:
                    current_background = GAME_ASSETS["backgrounds"][current_chapter]
                    background_x = 0
                else:
                    current_background = None
                    background_x = 0

                if current_chapter == 1:
                    current_obstacle_speed = 6
                elif current_chapter == 2:
                    current_obstacle_speed = 8
                elif current_chapter == 3:
                    current_obstacle_speed = 10
                final_grade = ""
                last_obstacle_spawn_time = current_time_ticks
                next_obstacle_spawn_delay = 2000
                item_spawn_count = 0
                item_spawn_limit = random.randint(1, 2)
                obstacle_group.empty();
                item_group.empty();
                pit_group.empty()
                platform_group.empty();
                speed_line_group.empty();
                collectible_group.empty()
                ground_group.empty()
                ground_group.add(Platform('ground', SCREEN_WIDTH * 2, x_pos=0, y_pos=GROUND_Y))

        # --- 화면 그리기 ---
        if game_state == "PLAYING" and current_background:
            screen.blit(current_background, (background_x, 0))
        else:
            screen.fill(BLACK)

        if game_state in ["PLAYING", "RELAY_PROMPT", "PAUSED", "HIDDEN_CREDIT"]:
            ground_group.draw(screen)
        if game_state in ["PLAYING", "RELAY_PROMPT", "PAUSED"]:
            pit_group.draw(screen)
            platform_group.draw(screen)

        if game_state == "TITLE_SCREEN":
            if GAME_ASSETS["title_screen"]:
                screen.blit(GAME_ASSETS["title_screen"], (0, 0))
            else:
                screen.fill(BLUE)

                # --- [추가] 번쩍이는 효과 구현 ---

                # 현재 시간을 기준으로 깜빡임 주기 설정 (1000ms = 1초)
                # 500ms 동안 켜지고, 500ms 동안 꺼짐
                flash_on = (current_time_ticks % 1000) < 500

                # [효과 1] 눈 번쩍임 (빨간색 원 그리기)
                if flash_on:
                    # ★중요★: 아래 좌표(X, Y)와 반지름 숫자들을 실행해보면서 눈 위치에 맞게 조절해야 합니다.
                    eye_center_x = 625  # 눈의 중심 X 좌표 (추정치)
                    eye_center_y = 265  # 눈의 중심 Y 좌표 (추정치)
                    eye_radius = 18  # 빨간 눈의 크기

                    # 바깥쪽 진한 빨강
                    pygame.draw.circle(screen, (200, 0, 0), (eye_center_x, eye_center_y), eye_radius)
                    # 안쪽 밝은 빨강 (더 빛나는 느낌)
                    pygame.draw.circle(screen, (255, 50, 50), (eye_center_x, eye_center_y), eye_radius - 5)

                # [효과 2] 글씨 번쩍임 (검은색으로 덮기)
                # flash_on이 False일 때(꺼진 타임일 때) 검은 박스로 글씨를 가립니다.
                if not flash_on:
                    # ★중요★: 아래 사각형 좌표(Left, Top, Width, Height)를 글씨를 딱 가릴 만큼 조절해야 합니다.
                    text_cover_rect = pygame.Rect(350, 480, 500, 70)
                    # 디버깅용: 위치 잡을 때는 BLACK 대신 RED로 바꿔서 영역을 확인해보세요.
                    pygame.draw.rect(screen, BLACK, text_cover_rect)

        elif game_state == "CHAPTER_SELECT":
            title_text = font_large.render("챕터를 선택하세요", True, WHITE)
            title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
            screen.blit(title_text, title_rect)
            for chapter, rect in chapter_buttons.items():
                if chapter == 3 and max_unlocked_chapter < 3: continue
                is_hovered = rect.collidepoint(mouse_pos)
                if chapter == 3:
                    chapter_num_text = font_large.render("BOSS", True, WHITE)
                else:
                    chapter_num_text = font_xl.render(str(chapter), True, WHITE)
                chapter_num_rect = chapter_num_text.get_rect(center=rect.center)
                if chapter <= max_unlocked_chapter:
                    if is_hovered:
                        hover_rect = rect.inflate(20, 20)
                        pygame.draw.rect(screen, LIGHT_BLUE, hover_rect, border_radius=15)
                    else:
                        pygame.draw.rect(screen, BLUE, rect, border_radius=15)
                    pygame.draw.rect(screen, WHITE, rect, 4, border_radius=15)
                    screen.blit(chapter_num_text, chapter_num_rect)
                else:
                    pygame.draw.rect(screen, GREY, rect, border_radius=15)
                    pygame.draw.rect(screen, BLACK, rect, 4, border_radius=15)
                    screen.blit(chapter_num_text, chapter_num_rect)
                    locked_text = font_large.render("LOCKED", True, RED)
                    locked_rect = locked_text.get_rect(center=rect.center)
                    screen.blit(locked_text, locked_rect)

        elif game_state == "CONFIRM_START":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA);
            overlay.fill((0, 0, 0, 180));
            screen.blit(overlay, (0, 0))
            confirm_text = font_large.render(f"Chapter {selected_chapter}을(를) 시작하시겠습니까?", True, WHITE)
            confirm_rect = confirm_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            screen.blit(confirm_text, confirm_rect)
            if confirm_yes_button.collidepoint(mouse_pos):
                pygame.draw.rect(screen, GREEN, confirm_yes_button.inflate(10, 10), border_radius=10)
            else:
                pygame.draw.rect(screen, GREEN, confirm_yes_button, border_radius=10)
            if selected_button_index == 0: pygame.draw.rect(screen, WHITE, confirm_yes_button.inflate(10, 10), 5,
                                                            border_radius=10)
            yes_text = font_small.render("예", True, BLACK)
            yes_rect = yes_text.get_rect(center=confirm_yes_button.center)
            screen.blit(yes_text, yes_rect)
            if confirm_no_button.collidepoint(mouse_pos):
                pygame.draw.rect(screen, RED, confirm_no_button.inflate(10, 10), border_radius=10)
            else:
                pygame.draw.rect(screen, RED, confirm_no_button, border_radius=10)
            if selected_button_index == 1: pygame.draw.rect(screen, WHITE, confirm_no_button.inflate(10, 10), 5,
                                                            border_radius=10)
            no_text = font_small.render("아니오", True, WHITE)
            no_rect = no_text.get_rect(center=confirm_no_button.center)
            screen.blit(no_text, no_rect)

        elif game_state == "CHARACTER_SELECT":
            title_text = font_large.render("이어달리기 2명 선택", True, WHITE)
            title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 150))
            screen.blit(title_text, title_rect)
            for i, (char_id, rect) in enumerate(character_buttons.items()):
                if i == selected_char_index:
                    pygame.draw.rect(screen, WHITE, rect.inflate(10, 10), 3)
                if char_id in character_roster:
                    pygame.draw.rect(screen, GREEN, rect.inflate(10, 10), 3)
                char_img = GAME_ASSETS["characters"][char_id]["portrait"]
                scaled_img = pygame.transform.scale(char_img, (80, 80))
                img_rect = scaled_img.get_rect(center=rect.center)
                screen.blit(scaled_img, img_rect)
            selected_text = font_small.render(f"선택: {', '.join(character_roster)} (방향키, 스페이스)", True, WHITE)
            selected_rect = selected_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT / 2 + 150))
            screen.blit(selected_text, selected_rect)

        elif game_state == "PLAYING":
            if player1: player1.draw(screen)
            if player2: player2.draw(screen)
            obstacle_group.draw(screen)
            item_group.draw(screen)
            collectible_group.draw(screen)
            speed_line_group.draw(screen)
            progress_percent = (elapsed_seconds % 45) / 45.0
            progress_rect_fg = pygame.Rect(0, 10, SCREEN_WIDTH * progress_percent, 20)
            progress_rect_bg = pygame.Rect(0, 10, SCREEN_WIDTH, 20)
            pygame.draw.rect(screen, GREEN, progress_rect_fg)
            pygame.draw.rect(screen, WHITE, progress_rect_bg, 2)
            score_text = font_small.render(f"점수: {score}", True, WHITE)
            score_rect = score_text.get_rect(topright=(SCREEN_WIDTH - 20, 40))
            screen.blit(score_text, score_rect)
            runner_text = font_small.render(f"주자: {1 if current_player is player1 else 2} / 2", True, WHITE)
            screen.blit(runner_text, (20, 40))
            chapter_text = font_small.render(f"챕터: {current_chapter}", True, WHITE)
            screen.blit(chapter_text, (20, 70))
            time_text = font_small.render(f"시간: {elapsed_seconds} 초", True, WHITE)
            screen.blit(time_text, (20, 100))
            if not current_player.skill_used_this_chapter:
                skill_text = font_small.render("SKILL READY (SPACE)", True, GREEN)
            else:
                skill_text = font_small.render("SKILL USED", True, RED)
            screen.blit(skill_text, (20, 130))

        elif game_state == "PAUSED":
            if player1: player1.draw(screen)
            if player2: player2.draw(screen)
            obstacle_group.draw(screen);
            item_group.draw(screen);
            collectible_group.draw(screen);
            speed_line_group.draw(screen)
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA);
            overlay.fill((0, 0, 0, 180));
            screen.blit(overlay, (0, 0))
            pause_text = font_large.render("일시 정지", True, WHITE)
            pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            screen.blit(pause_text, pause_rect)
            resume_text = font_small.render("계속하려면 P를 누르세요", True, WHITE)
            resume_rect = resume_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            screen.blit(resume_text, resume_rect)

        elif game_state == "RELAY_PROMPT":
            if player1: player1.draw(screen)
            obstacle_group.draw(screen);
            item_group.draw(screen);
            collectible_group.draw(screen);
            speed_line_group.draw(screen)
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA);
            overlay.fill((0, 0, 0, 180));
            screen.blit(overlay, (0, 0))
            elapsed_prompt_time = current_time_ticks - relay_prompt_start_time
            time_left = max(0, 10 - (elapsed_prompt_time // 1000))
            confirm_text = font_large.render(f"이어달리기 하시겠습니까? ({time_left})", True, WHITE)
            confirm_rect = confirm_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            screen.blit(confirm_text, confirm_rect)
            pygame.draw.rect(screen, GREEN, relay_yes_button_rect.inflate(10, 10) if relay_yes_button_rect.collidepoint(
                mouse_pos) else relay_yes_button_rect, border_radius=10)
            if selected_button_index == 0: pygame.draw.rect(screen, WHITE, relay_yes_button_rect.inflate(10, 10), 5,
                                                            border_radius=10)
            yes_text = font_small.render("예", True, BLACK)
            yes_rect = yes_text.get_rect(center=relay_yes_button_rect.center)
            screen.blit(yes_text, yes_rect)
            pygame.draw.rect(screen, RED, relay_no_button_rect.inflate(10, 10) if relay_no_button_rect.collidepoint(
                mouse_pos) else relay_no_button_rect, border_radius=10)
            if selected_button_index == 1: pygame.draw.rect(screen, WHITE, relay_no_button_rect.inflate(10, 10), 5,
                                                            border_radius=10)
            no_text = font_small.render("아니오", True, WHITE)
            no_rect = no_text.get_rect(center=relay_no_button_rect.center)
            screen.blit(no_text, no_rect)

        elif game_state == "GAME_OVER":
            if player1: player1.draw(screen)
            if player2: player2.draw(screen)
            if final_grade == "F":
                grade_message = "학점: F. 다음 학기에 뵙겠습니다."
            elif final_grade == "D":
                grade_message = "학점: D. 재수강 위기입니다."
            elif final_grade == "C":
                grade_message = "학점: C. 분발하세요."
            elif final_grade == "B":
                grade_message = "학점: B. 를 놓쳤습니다!"
            elif final_grade == "A (Fail)":
                grade_message = "학점: A (Fail). 아깝게 클리어 실패!"
            text = font_large.render("GAME OVER", True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
            screen.blit(text, text_rect)
            grade_text = font_medium.render(grade_message, True, RED)
            grade_rect = grade_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
            screen.blit(grade_text, grade_rect)
            score_text = font_small.render(f"최종 점수: {score}", True, WHITE)
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
            screen.blit(score_text, score_rect)
            pygame.draw.rect(screen, RED, restart_button_rect.inflate(10, 10) if restart_button_rect.collidepoint(
                mouse_pos) else restart_button_rect, border_radius=10)
            btn_text = font_small.render("재수강", True, WHITE)
            btn_text_rect = btn_text.get_rect(center=restart_button_rect.center)
            screen.blit(btn_text, btn_text_rect)

        elif game_state == "GAME_CLEAR":
            if final_grade == "A+":
                text = font_large.render("!! CHAPTER 3 CLEAR !!", True, YELLOW)
                text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
                screen.blit(text, text_rect)
                grade_text = font_xl.render("A+학점 달성!", True, GREEN)
                grade_rect = grade_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                screen.blit(grade_text, grade_rect)
                score_text = font_small.render(f"최종 점수: {score}", True, WHITE)
                score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
                screen.blit(score_text, score_rect)
                credit_hint_text = font_medium.render("아무 키나 눌러 히든 크레딧 보기", True, WHITE)
                credit_hint_rect = credit_hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 120))
                screen.blit(credit_hint_text, credit_hint_rect)
            else:
                text = font_large.render(f"!! CHAPTER {current_chapter} CLEAR !!", True, YELLOW)
                text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
                screen.blit(text, text_rect)
                grade_text = font_large.render(f"축하합니다! {final_grade}학점으로 클리어!", True, GREEN)
                grade_rect = grade_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                screen.blit(grade_text, grade_rect)
                score_text = font_small.render(f"최종 점수: {score}", True, WHITE)
                score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
                screen.blit(score_text, score_rect)
                if restart_button_rect.collidepoint(mouse_pos):
                    pygame.draw.rect(screen, BLUE, restart_button_rect.inflate(10, 10), border_radius=10)
                else:
                    pygame.draw.rect(screen, BLUE, restart_button_rect, border_radius=10)
                btn_text = font_small.render("챕터 선택", True, WHITE)
                btn_text_rect = btn_text.get_rect(center=restart_button_rect.center)
                screen.blit(btn_text, btn_text_rect)

        elif game_state == "HIDDEN_CREDIT":
            credit_text = font_large.render("대학원 입학을 축하합니다!", True, WHITE)
            credit_rect = credit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 200))
            screen.blit(credit_text, credit_rect)
            press_key_text = font_small.render("아무 키나 눌러 시작 화면으로", True, WHITE)
            press_key_rect = press_key_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
            screen.blit(press_key_text, press_key_rect)

        elif game_state == "LOADING_TRANSITION":
            elapsed = current_time_ticks - transition_start_time
            radius = int((elapsed / 1500) * SCREEN_WIDTH * 0.7)
            if radius < SCREEN_WIDTH * 0.7:
                pygame.draw.circle(screen, BLACK, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), radius)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main_game()