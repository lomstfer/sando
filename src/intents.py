import taichi as ti
import consts
import utils


@ti.func
def falling_intent(x, y, intents, pixels) -> bool:
    intent = False
    if utils.in_view(x, y+1, pixels):
        if utils.is_empty(x, y+1, pixels):
            utils.set_2Dvec(x, y, ti.cast(0, ti.i8), ti.cast(1, ti.i8), intents)
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
        utils.set_2Dvec(x, y, ti.cast(slide_x, ti.i8), ti.cast(-1, ti.i8), intents)
    elif can_slide_right:
        utils.set_2Dvec(x, y, ti.cast(1, ti.i8), ti.cast(-1, ti.i8), intents)
    elif can_slide_left: 
        utils.set_2Dvec(x, y, ti.cast(-1, ti.i8), ti.cast(-1, ti.i8), intents)
    
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
def float_sink_intent(x, y, intents, pixels):
    set_intent = False
    this = utils.get_color(x, y, pixels)
    this_density = consts.density_of_color(this)

    if utils.in_view(x, y-1, pixels):
        above = utils.get_color(x, y-1, pixels)
        above_density = consts.density_of_color(above)
        if this_density < above_density:
            utils.set_2Dvec(x, y, 0, -1, intents)
            set_intent = True

    if not set_intent:
        if utils.in_view(x, y+1, pixels):
            below = utils.get_color(x, y+1, pixels)
            below_density = consts.density_of_color(below)
            if this_density > below_density:
                utils.set_2Dvec(x, y, 0, 1, intents)
                set_intent = True

    return set_intent


@ti.func
def do_sand_intents(x, y, intents, pixels) -> bool:
    handled = False

    if not handled:
        handled = falling_intent(x, y, intents, pixels)
    
    if not handled:
        handled = sand_slide_intent(x, y, intents, pixels)

    return handled


@ti.func
def do_water_intents(x, y, intents, directions, pixels) -> bool:
    handled = False

    if not handled:
        handled = falling_intent(x, y, intents, pixels)
    
    if not handled:
        handled = water_slide_intent(x, y, intents, directions, pixels)

    return handled


@ti.kernel
def update_intents(pixels: ti.template(),
                   intents: ti.template(), 
                   directions: ti.template()):
    for x, y in ti.ndrange(consts.WIDTH, consts.HEIGHT):
        empty = utils.is_empty(x, y, pixels)

        if empty:
            continue
        
        has_intent = False
        if utils.has_color(x, y, consts.SAND_COLOR, pixels):
            has_intent = do_sand_intents(x, y, intents, pixels)
        elif utils.has_color(x, y, consts.WATER_COLOR, pixels):
            has_intent = do_water_intents(x, y, intents, directions, pixels)
        
        if not has_intent:
            has_intent = float_sink_intent(x, y, intents, pixels)


@ti.kernel
def update_pixels_from_intents(current: ti.template(), 
                               next: ti.template(), 
                               intents: ti.template(), 
                               directions: ti.template()):
    for x, y in ti.ndrange(consts.WIDTH, consts.HEIGHT):
        utils.set_pixel(x, y, utils.get_color(x, y, current), next)
    
    for x, y in ti.ndrange(consts.WIDTH, consts.HEIGHT):
        empty = utils.is_empty(x, y, current)
        
        if not empty:
            # check for float/sink switch
            if utils.has_2Dvec(x, y, 0, 1, intents):            # wants to "sink"
                if utils.in_view(x, y+1, current):
                    if utils.has_2Dvec(x, y+1, 0, -1, intents): # the pixel below wants to float
                        col = utils.get_color(x, y, current)
                        utils.set_pixel(x, y+1, col, next)
                        utils.set_2Dvec(x, y+1, 0, 1, directions)
            elif utils.has_2Dvec(x, y, 0, -1, intents):         # wants to "float"
                if utils.in_view(x, y-1, current):
                    if utils.has_2Dvec(x, y-1, 0, 1, intents):  # the pixel above wants to sink
                        col = utils.get_color(x, y, current)
                        utils.set_pixel(x, y-1, col, next)
                        utils.set_2Dvec(x, y-1, 0, -1, directions)


            continue

        n_counts, n = utils.nonempty_neighbours_shuffled(x, y, current)
        for i in range(n_counts):
            nx = n[i, 0]
            ny = n[i, 1]
            ix, iy = x - nx, y - ny
            if utils.has_2Dvec(nx, ny, ix, iy, intents):
                col = utils.get_color(nx, ny, current)
                utils.set_pixel(x, y, col, next)
                utils.set_pixel(nx, ny, consts.EMPTY_COLOR, next)
                utils.set_2Dvec(x, y, ix, iy, directions)
                break