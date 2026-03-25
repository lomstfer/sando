import taichi as ti
import consts

@ti.func
def neighbours_count(x, y, pixels):
    nbrs_count = 0
    
    for dx, dy in ti.ndrange((-1, 2), (-1, 2)):
        if dx == 0 and dy == 0:
            continue
            
        nx = x + dx
        ny = y + dy
        
        if not (0 <= nx < pixels.shape[0] and 0 <= ny < pixels.shape[1]):
            continue
        if not is_empty(nx, ny, pixels):
            nbrs_count += 1
    
    return nbrs_count


@ti.func
def nonempty_neighbours(x, y, pixels):
    nbrs = ti.Matrix.zero(ti.i32, 8, 2)
    count = 0
    
    for dx, dy in ti.ndrange((-1, 2), (-1, 2)):
        if dx == 0 and dy == 0:
            continue
            
        nx = x + dx
        ny = y + dy
        
        if not in_view(nx, ny, pixels):
            continue
        if is_empty(nx, ny, pixels):
            continue
        nbrs[count, 0] = nx
        nbrs[count, 1] = ny
        count += 1
                
    return count, nbrs



@ti.func
def ti_rand_int(min_incl: ti.i32, max_excl: ti.i32) -> ti.i32: # type: ignore
    return min_incl + ti.random(ti.i32) % (max_excl - min_incl)


@ti.func
def nonempty_neighbours_shuffled(x, y, pixels):
    count, nbrs = nonempty_neighbours(x, y, pixels)
    for i in range(count-1):
        rand_idx_pick = ti_rand_int(i, count)
        # swap
        nbrs[i, 0], nbrs[rand_idx_pick, 0] = nbrs[rand_idx_pick, 0], nbrs[i, 0]
        nbrs[i, 1], nbrs[rand_idx_pick, 1] = nbrs[rand_idx_pick, 1], nbrs[i, 1]
    
    return count, nbrs


@ti.func
def has_color(x, y, color, pixels):
    is_of_color = 1
    for channel in ti.static(range(3)):
        is_match = ti.cast(pixels[x, y][channel] == color[channel], ti.i32)
        is_of_color = is_of_color & is_match
        
    return is_of_color


@ti.func
def is_color(col1, col2):
    is_of_color = 1
    for channel in ti.static(range(3)):
        is_match = ti.cast(col1[channel] == col2[channel], ti.i32)
        is_of_color = is_of_color & is_match
        
    return is_of_color


@ti.func
def get_color(x, y, pixels):
    color = ti.Vector([0, 0, 0])
    for channel in ti.static(range(3)):
        color[channel] = pixels[x, y][channel]
    return color


@ti.func
def set_pixel(x, y, color, pixels):
    for channel in ti.static(range(3)):
        pixels[x, y][channel] = ti.cast(color[channel], ti.u8)


@ti.func
def is_empty(x, y, pixels):
    empty = 1
    for channel in ti.static(range(3)):
        empty = empty & ti.cast(pixels[x, y][channel] == consts.EMPTY_COLOR[channel], ti.i32)
    return empty


@ti.func
def in_view(x, y, pixels):
    return 0 <= x < pixels.shape[0] and 0 <= y < pixels.shape[1]


@ti.kernel
def set_pix_around(x: ti.i32, y: ti.i32, radius: ti.i32, color: ti.types.vector(3, ti.u8), pixels: ti.template()):   # type: ignore
    for w, h in ti.ndrange(radius * 2 + 1, radius * 2 + 1):
        xs = x + w - radius
        ys = y + h - radius
        if not in_view(xs, ys, pixels):# or xs % 2 == 0 or ys % 2 == 0:
            continue
        if (xs - x) ** 2 + (ys - y) ** 2 <= radius ** 2:
            set_pixel(xs, ys, color, pixels)


@ti.kernel
def count_nonempty(pixels: ti.template()) -> ti.i32: # type: ignore
    count = 0
    for x, y in ti.ndrange(pixels.shape[0], pixels.shape[1]):
        if not is_empty(x, y, pixels):
            count += 1
    return count


@ti.func
def set_2Dvec(x, y, nx, ny, field):
    field[x, y][0] = ti.cast(nx, ti.i8)
    field[x, y][1] = ti.cast(ny, ti.i8)


@ti.func
def get_2Dvec(x, y, field):
    return field[x, y][0], field[x, y][1]


@ti.func
def has_2Dvec(x, y, x2, y2, field) -> bool:
    x, y = get_2Dvec(x, y, field)
    return x == x2 and y == y2


@ti.func 
def is_heavier(x, y, x2, y2, pixels):
    col1 = get_color(x, y, pixels)
    col2 = get_color(x2, y2, pixels)
    return consts.density_of_color(col1) > consts.density_of_color(col2)