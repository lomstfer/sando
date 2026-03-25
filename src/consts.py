WIN_WIDTH, WIN_HEIGHT = 1280, 720
WIDTH, HEIGHT = 320, 180

SIM_SCALE_X = WIN_WIDTH // WIDTH
SIM_SCALE_Y = WIN_HEIGHT // HEIGHT

EMPTY_COLOR = (30, 30, 30)
SAND_COLOR = (210, 200, 200)
WATER_COLOR = (20, 20, 200)

COLORS = (
    SAND_COLOR,
    WATER_COLOR
)

import taichi as ti
import utils
@ti.func
def density_of_color(color):
    density = ti.cast(0, ti.i32)
    if (utils.is_color(color, SAND_COLOR)):
        density = ti.cast(2, ti.i32)
    elif (utils.is_color(color, WATER_COLOR)):
        density = ti.cast(1, ti.i32)
    return density