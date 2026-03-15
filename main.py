import pygame
import random
import enum
import math

SCREEN_WIDTH = 160
SCREEN_HEIGHT = 120
SCALE = 5
FPS = 60
SIM_FPS = 20


class Pix(enum.IntEnum):
    EMPTY = 0
    STEAM = 1
    WATER = 2
    SAND = 3
    LAVA = 4
    ROCK = 5
    WOOD = 6

COLORS = {
    Pix.EMPTY: (30, 30, 30),  
    Pix.SAND: (194, 178, 128),
    Pix.WATER: (50, 100, 220),
    Pix.ROCK: (90, 90, 90),   
    Pix.WOOD: (90, 70, 40),   
    Pix.LAVA: (220, 50, 50),  
    Pix.STEAM: (240, 240, 240),  
}

INPUT = {
    Pix.EMPTY: pygame.K_q,  
    Pix.SAND: pygame.K_w,
    Pix.WATER: pygame.K_e,
    Pix.ROCK: pygame.K_r,   
    Pix.WOOD: pygame.K_a,   
    Pix.LAVA: pygame.K_s,  
    Pix.STEAM: pygame.K_d,
}

FLOAT_SINK_DENSITY = {
    Pix.STEAM: -1,
    Pix.EMPTY: 0,  
    Pix.WATER: 1,
    Pix.LAVA: 2,  
    Pix.SAND: 3,
}



def in_screen(x, y):
    return 0 <= x < SCREEN_WIDTH and 0 <= y < SCREEN_HEIGHT


def get_neighbours_in_screen(x, y):
    neighbours = []
    for nx, ny in [(x + 1, y), (x - 1, y), (x, y - 1), (x, y + 1)]:
        if in_screen(nx, ny):
            neighbours.append((nx, ny))
    return neighbours


def can_move_to(x, y, pix, npix):
    return pix[y][x] == Pix.EMPTY and npix[y][x] == Pix.EMPTY


def try_sink_float(fx, fy, tx, ty, pix, npix):
    if not in_screen(fx, fy) or not in_screen(tx, ty):
        return False
    
    if npix[fy][fx] or npix[ty][tx]:
        # pixels has already been updated
        return False
    
    from_type = pix[fy][fx]
    to_type = pix[ty][tx]

    if not (from_type in FLOAT_SINK_DENSITY and to_type in FLOAT_SINK_DENSITY):
        return False

    sinking = fy < ty and FLOAT_SINK_DENSITY[from_type] > FLOAT_SINK_DENSITY[to_type]
    floating = fy > ty and FLOAT_SINK_DENSITY[from_type] < FLOAT_SINK_DENSITY[to_type]
    
    if sinking or floating:
        npix[fy][fx] = to_type
        npix[ty][tx] = from_type
        return True

def sand(x, y, pix, npix):
    if npix[y][x]:
        # this pixel has already been updated
        return

    if y >= SCREEN_HEIGHT-1:
        npix[y][x] = Pix.SAND
        return

    if try_sink_float(x, y, x, y+1, pix, npix):
        return
    
    left = random.randint(0, 1) == 0
    if left and x > 0 and can_move_to(x - 1, y + 1, pix, npix):
        npix[y+1][x-1] = Pix.SAND
        return
    
    if not left and x < SCREEN_WIDTH-1 and can_move_to(x + 1, y + 1, pix, npix):
        npix[y+1][x+1] = Pix.SAND
        return
    
    npix[y][x] = Pix.SAND    


def water(x, y, pix, npix):
    if npix[y][x]:
        # this pixel has already been updated
        return
    
    for nx, ny in get_neighbours_in_screen(x, y):
        if pix[ny][nx] == Pix.LAVA:
            npix[y][x] = Pix.STEAM
            return

    if y >= SCREEN_HEIGHT-1:
        npix[y][x] = Pix.WATER
        return

    if try_sink_float(x, y, x, y+1, pix, npix):
        return
    
    left = random.randint(0, 1) == 0
    if left and x > 0 and can_move_to(x - 1, y, pix, npix):
        npix[y][x-1] = Pix.WATER
        return
    
    if not left and x < SCREEN_WIDTH-1 and can_move_to(x + 1, y, pix, npix):
        npix[y][x+1] = Pix.WATER
        return
    
    npix[y][x] = Pix.WATER


def rock(x, y, pix, npix):
    npix[y][x] = Pix.ROCK
    return


def wood(x, y, pix, npix):
    for nx, ny in get_neighbours_in_screen(x, y):
        if pix[ny][nx] == Pix.LAVA:
            npix[y][x] = Pix.EMPTY
            return
    npix[y][x] = Pix.WOOD
    return


def lava(x, y, pix, npix):
    if npix[y][x]:
        # this pixel has already been updated
        return

    if y >= SCREEN_HEIGHT-1:
        npix[y][x] = Pix.LAVA
        return

    if try_sink_float(x, y, x, y+1, pix, npix):
        return
    
    left = random.randint(0, 1) == 0
    if left and x > 0 and can_move_to(x - 1, y, pix, npix):
        npix[y][x-1] = Pix.LAVA
        return
    
    if not left and x < SCREEN_WIDTH-1 and can_move_to(x + 1, y, pix, npix):
        npix[y][x+1] = Pix.LAVA
        return
    
    npix[y][x] = Pix.LAVA


def steam(x, y, pix, npix):
    if npix[y][x]:
        # this pixel has already been updated
        return

    if y <= 0:
        npix[y][x] = Pix.STEAM
        return

    if try_sink_float(x, y, x, y-1, pix, npix):
        return
    
    left = random.randint(0, 1) == 0
    if left and x > 0 and can_move_to(x - 1, y, pix, npix):
        npix[y][x-1] = Pix.STEAM
        return
    
    if not left and x < SCREEN_WIDTH-1 and can_move_to(x + 1, y, pix, npix):
        npix[y][x+1] = Pix.STEAM
        return
    
    npix[y][x] = Pix.STEAM


def pix_copy(pix):
    return [row[:] for row in pix]


def empty_pix():
    return [[Pix.EMPTY] * SCREEN_WIDTH for _ in range(SCREEN_HEIGHT)]


def update(pix):
    npix = empty_pix()
    for y in range(SCREEN_HEIGHT):
        for x in range(SCREEN_WIDTH):
            if not pix[y][x]:
                continue
            if pix[y][x] == Pix.SAND:
                sand(x, y, pix, npix)
            if pix[y][x] == Pix.WATER:
                water(x, y, pix, npix)
            if pix[y][x] == Pix.ROCK:
                rock(x, y, pix, npix)
            if pix[y][x] == Pix.WOOD:
                wood(x, y, pix, npix)
            if pix[y][x] == Pix.LAVA:
                lava(x, y, pix, npix)
            if pix[y][x] == Pix.STEAM:
                steam(x, y, pix, npix)
    return npix


def draw(screen, canvas, pix):
    canvas.fill((30, 30, 30))
    nonempty = 0
    for y in range(SCREEN_HEIGHT):
        for x in range(SCREEN_WIDTH):
            if not pix[y][x]:
                continue
            else:
                nonempty += 1
            canvas.set_at((x, y), COLORS[pix[y][x]])
    pygame.transform.scale(canvas, (SCREEN_WIDTH * SCALE, SCREEN_HEIGHT * SCALE), screen)
    pygame.display.flip()


def set_pix_around(x, y, type, radius, pix):
    for xs in range(x-radius, x+radius+1):
        for ys in range(y-radius, y+radius+1):
            if not in_screen(xs, ys):
                continue
            if (xs - x)**2 + (ys - y)**2 <= radius**2:
                pix[ys][xs] = type


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH * SCALE, SCREEN_HEIGHT * SCALE))
    canvas = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("sando")
    clock = pygame.Clock()

    pix = empty_pix()
    selected_pix = Pix.SAND
    draw_size = 0

    snapshots = []
    snapshot_index = 0

    sim_accumulator = 0
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        sim_accumulator += dt
        if (sim_accumulator > 1 / SIM_FPS):
            pix = update(pix)
            sim_accumulator = 0
        
        if pygame.mouse.get_just_pressed()[0]:
            snapshots = snapshots[:snapshot_index]
            snapshots.append(pix_copy(pix))
            snapshot_index += 1

        if pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_pos()
            mx //= SCALE
            my //= SCALE
            if in_screen(mx, my):
                set_pix_around(mx, my, selected_pix, draw_size, pix)  
        
        draw(screen, canvas, pix)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                for k in INPUT:
                    if event.key == INPUT[k]:
                        selected_pix = k
            if event.type == pygame.MOUSEWHEEL:
                draw_size = max(0, draw_size + event.y)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z and (event.mod & pygame.KMOD_CTRL):
                    if snapshot_index > 0:
                        pix = snapshots[snapshot_index - 1]
                        snapshot_index -= 1
                if event.key == pygame.K_y and (event.mod & pygame.KMOD_CTRL):
                    if snapshot_index < len(snapshots):
                        snapshot_index += 1
                        pix = snapshots[snapshot_index]

    pygame.quit()


if __name__ == "__main__":
    main()