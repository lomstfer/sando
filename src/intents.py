import taichi as ti
import consts
import utils


@ti.func
def set_2Dvec(x, y, ixd, iyd, directions):
    directions[x, y][0] = ti.cast(ixd, ti.i8)
    directions[x, y][1] = ti.cast(iyd, ti.i8)


@ti.func
def get_2Dvec(x, y, directions):
    return directions[x, y][0], directions[x, y][1]


@ti.func
def has_2Dvec(x, y, dx, dy, directions) -> bool:
    direction_x, direction_y = get_2Dvec(x, y, directions)
    return direction_x == dx and direction_y == dy




@ti.func
def falling_intent(x, y, intents, pixels) -> bool:
    intent = False
    if utils.in_view(x, y+1, pixels):
        if utils.is_empty(x, y+1, pixels):
            set_2Dvec(x, y, ti.cast(0, ti.i8), ti.cast(1, ti.i8), intents)
            intent = True
    return intent


@ti.func
def sand_slide_intent(x, y, intents, pixels) -> bool:
    can_slide_left = False
    can_slide_right = False

    if utils.in_view(x+1, y+1, pixels):
        if utils.is_empty(x+1, y+1, pixels):
            can_slide_right = True

    if utils.in_view(x-1, y+1, pixels):
        if utils.is_empty(x-1, y+1, pixels):
            can_slide_left = True
    
    if can_slide_left and can_slide_right:
        slide_x = 1 if ti.random() > 0.5 else -1
        set_2Dvec(x, y, ti.cast(slide_x, ti.i8), ti.cast(-1, ti.i8), intents)
    elif can_slide_right:
        set_2Dvec(x, y, ti.cast(1, ti.i8), ti.cast(-1, ti.i8), intents)
    elif can_slide_left: 
        set_2Dvec(x, y, ti.cast(-1, ti.i8), ti.cast(-1, ti.i8), intents)
    
    return can_slide_left or can_slide_right


@ti.func
def water_slide_intent(x, y, intents, directions, pixels) -> bool:
    can_slide_left = False
    can_slide_right = False

    if utils.in_view(x+1, y, pixels):
        if utils.is_empty(x+1, y, pixels):
            can_slide_right = True

    if utils.in_view(x-1, y, pixels):
        if utils.is_empty(x-1, y, pixels):
            can_slide_left = True
    
    if can_slide_left and can_slide_right:
        if has_2Dvec(x, y, 1, 0, directions):
            set_2Dvec(x, y, ti.cast(1, ti.i8), ti.cast(0, ti.i8), intents)
        elif has_2Dvec(x, y, -1, 0, directions):
            set_2Dvec(x, y, ti.cast(-1, ti.i8), ti.cast(0, ti.i8), intents)
        else:
            slide_x = 1 if ti.random() > 0.5 else -1
            set_2Dvec(x, y, ti.cast(slide_x, ti.i8), ti.cast(0, ti.i8), intents)
    elif can_slide_right:
        set_2Dvec(x, y, ti.cast(1, ti.i8), ti.cast(0, ti.i8), intents)
    elif can_slide_left:
        set_2Dvec(x, y, ti.cast(-1, ti.i8), ti.cast(0, ti.i8), intents)
    
    return can_slide_left or can_slide_right


@ti.func
def do_sand_intents(x, y, intents, pixels):
    handled = False

    if not handled:
        handled = falling_intent(x, y, intents, pixels)
    
    if not handled:
        handled = sand_slide_intent(x, y, intents, pixels)

    return

@ti.func
def do_water_intents(x, y, intents, directions, pixels):
    handled = False

    if not handled:
        handled = falling_intent(x, y, intents, pixels)
    
    if not handled:
        handled = water_slide_intent(x, y, intents, directions, pixels)

    return


@ti.kernel
def update_intents(pixels: ti.template(), intents: ti.template(), directions: ti.template()):
    for x, y in ti.ndrange(consts.WIDTH, consts.HEIGHT):
        empty = utils.is_empty(x, y, pixels)

        if empty:
            continue
        
        if utils.has_color(x, y, consts.SAND_COLOR, pixels):
            do_sand_intents(x, y, intents, pixels)
        elif utils.has_color(x, y, consts.WATER_COLOR, pixels):
            do_water_intents(x, y, intents, directions, pixels)


@ti.kernel
def update_pixels_from_intents(current: ti.template(), next: ti.template(), intents: ti.template(), directions: ti.template()):
    for x, y in ti.ndrange(consts.WIDTH, consts.HEIGHT):
        utils.set_pixel(x, y, utils.get_color(x, y, current), next)
    
    for x, y in ti.ndrange(consts.WIDTH, consts.HEIGHT):
        empty = utils.is_empty(x, y, current)
        
        if not empty:
            continue

        n_counts, n = utils.nonempty_neighbours_shuffled(x, y, current)
        for i in range(n_counts):
            nx = n[i, 0]
            ny = n[i, 1]
            ix, iy = x - nx, y - ny
            if has_2Dvec(nx, ny, ix, iy, intents):
                col = utils.get_color(nx, ny, current)
                utils.set_pixel(x, y, col, next)
                utils.set_pixel(nx, ny, consts.EMPTY_COLOR, next)
                set_2Dvec(x, y, ix, iy, directions)
                break