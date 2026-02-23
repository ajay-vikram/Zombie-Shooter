from game import ZombieShooter

WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 800
WORLD_WIDTH, WORLD_HEIGHT = 1800, 1200
FPS = 60

game = ZombieShooter(
    window_width=WINDOW_WIDTH,
    window_height=WINDOW_HEIGHT,
    world_width=WORLD_WIDTH,
    world_height=WORLD_HEIGHT,
    fps=FPS,
    sound=True
)

# Game loop
while True:
    game.step()