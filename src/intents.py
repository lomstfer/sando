import taichi as ti
import consts
import utils


@ti.func
def falling_intent(x, y, intents, pixels) -> bool:
    intent = False
    if utils.in_view(x, y+1, pixels):
        if utils.is_empty(x, y+1, pixels) or utils.is_heavier(x, y, x, y+1, pixels):
            utils.set_2Dvec(x, y, ti.cast(0, ti.i8), ti.cast(1, ti.i8), intents)
            intent = True
    return intent


@ti.func
def sand_slide_intent(x, y, intents, pixels) -> bool:
    can_slide_left = False
    can_slide_right = False

    if utils.in_view(x+1, y+1, pixels):
        if utils.is_empty(x+1, y+1, pixels) or utils.is_heavier(x, y, x+1, y+1, pixels):
            can_slide_right = True

    if utils.in_view(x-1, y+1, pixels):
        if utils.is_empty(x-1, y+1, pixels) or utils.is_heavier(x, y, x-1, y+1, pixels):
            can_slide_left = True
    
    if can_slide_left and can_slide_right:
        slide_x = 1 if ti.random() > 0.5 else -1
        utils.set_2Dvec(x, y, ti.cast(slide_x, ti.i8), ti.cast(1, ti.i8), intents)
    elif can_slide_right:
        utils.set_2Dvec(x, y, ti.cast(1, ti.i8), ti.cast(1, ti.i8), intents)
    elif can_slide_left: 
        utils.set_2Dvec(x, y, ti.cast(-1, ti.i8), ti.cast(1, ti.i8), intents)
    
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
        if utils.has_2Dvec(x, y, 1, 0, directions):
            utils.set_2Dvec(x, y, ti.cast(1, ti.i8), ti.cast(0, ti.i8), intents)
        elif utils.has_2Dvec(x, y, -1, 0, directions):
            utils.set_2Dvec(x, y, ti.cast(-1, ti.i8), ti.cast(0, ti.i8), intents)
        else:
            slide_x = 1 if ti.random() > 0.5 else -1
            utils.set_2Dvec(x, y, ti.cast(slide_x, ti.i8), ti.cast(0, ti.i8), intents)
    elif can_slide_right:
        utils.set_2Dvec(x, y, ti.cast(1, ti.i8), ti.cast(0, ti.i8), intents)
    elif can_slide_left:
        utils.set_2Dvec(x, y, ti.cast(-1, ti.i8), ti.cast(0, ti.i8), intents)
    
    return can_slide_left or can_slide_right


@ti.func
def has_neighbour_with_intent_to_it(x, y, pixels, intents) -> bool:
    has = False
    ncount, neighs = utils.nonempty_neighbours_shuffled(x, y, pixels)
    for i in range(ncount):
        nx, ny = neighs[i, 0], neighs[i, 1]
        if utils.has_2Dvec(nx, ny, x-nx, y-ny, intents):
            has = True
            break
    return has


@ti.func
def do_sand_intents(x, y, intents, pixels):
    if has_neighbour_with_intent_to_it(x, y, pixels, intents):
        pass

    elif falling_intent(x, y, intents, pixels):
        pass
    elif sand_slide_intent(x, y, intents, pixels):
        pass


@ti.func
def do_water_intents(x, y, intents, directions, pixels):
    if has_neighbour_with_intent_to_it(x, y, pixels, intents):
        pass

    elif falling_intent(x, y, intents, pixels):
        pass
    elif water_slide_intent(x, y, intents, directions, pixels):
        pass


@ti.func
def do_rock_intents(x, y, intents, pixels):
    pass


@ti.kernel
def update_intents(pixels: ti.template(), 
                   color_to_update: ti.types.vector(3, ti.u8),
                   intents: ti.template(), 
                   directions: ti.template()):
    for x, y in ti.ndrange(consts.WIDTH, consts.HEIGHT):
        col = utils.get_color(x, y, pixels)

        if not utils.is_color(col, color_to_update):
            continue
        
        if utils.is_color(col, consts.SAND_COLOR):
            do_sand_intents(x, y, intents, pixels)
        elif utils.is_color(col, consts.WATER_COLOR):
            do_water_intents(x, y, intents, directions, pixels)
        elif utils.is_color(col, consts.ROCK_COLOR):
            do_rock_intents(x, y, intents, pixels)


@ti.kernel
def update_pixels_from_intents(current: ti.template(), 
                               next: ti.template(), 
                               intents: ti.template(), 
                               directions: ti.template()):
    for x, y in ti.ndrange(consts.WIDTH, consts.HEIGHT):
        utils.set_pixel(x, y, utils.get_color(x, y, current), next)
    
    for x, y in ti.ndrange(consts.WIDTH, consts.HEIGHT):
        n_counts, n = utils.nonempty_neighbours_shuffled(x, y, current)
        this_col = utils.get_color(x, y, current)
        for i in range(n_counts):
            nx = n[i, 0]
            ny = n[i, 1]
            ix, iy = x - nx, y - ny
            if utils.has_2Dvec(nx, ny, ix, iy, intents):
                col = utils.get_color(nx, ny, current)
                utils.set_pixel(x, y, col, next)
                utils.set_pixel(nx, ny, this_col, next)
                utils.set_2Dvec(x, y, ix, iy, directions)
                if not utils.is_color(col, consts.EMPTY_COLOR):
                    utils.set_2Dvec(nx, ny, -ix, -iy, directions)
                break