WIN_WIDTH, WIN_HEIGHT = 1280, 720
WIDTH, HEIGHT = 320, 180

SIM_SCALE_X = WIN_WIDTH // WIDTH
SIM_SCALE_Y = WIN_HEIGHT // HEIGHT

EMPTY_COLOR = (30, 30, 30)
SAND_COLOR = (200, 170, 170)
WATER_COLOR = (20, 20, 200)
ROCK_COLOR = (70, 70, 70)
LAVA_COLOR = (200, 70, 70)
STEAM_COLOR = (255, 255, 255)

# ordered by density
COLORS = (
    ROCK_COLOR,
    SAND_COLOR,
    LAVA_COLOR,
    WATER_COLOR,
    STEAM_COLOR,
)

import taichi as ti
import utils
@ti.func
def density_of_color(color):
    density = ti.cast(0, ti.i32)
    if (utils.is_color(color, EMPTY_COLOR)):
        density = ti.cast(0, ti.i32)
    elif (utils.is_color(color, STEAM_COLOR)):
        density = ti.cast(10, ti.i32)
    elif (utils.is_color(color, WATER_COLOR)):
        density = ti.cast(20, ti.i32)
    elif (utils.is_color(color, LAVA_COLOR)):
        density = ti.cast(30, ti.i32)
    elif (utils.is_color(color, SAND_COLOR)):
        density = ti.cast(40, ti.i32)
    elif (utils.is_color(color, ROCK_COLOR)):
        density = ti.cast(50, ti.i32)

    return density