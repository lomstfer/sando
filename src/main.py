import taichi as ti
import pygame
import intents
import utils
import consts


def simulate(pixels_current, 
             pixels_next, 
             pixel_intents,
             pixel_directions):
    
    pixel_intents.fill(0)

    for color in consts.COLORS:
        intents.update_intents(pixels_current,
                               color,
                               pixel_intents, 
                               pixel_directions,
                            )
    

    intents.update_pixels_from_intents(pixels_current, 
                                       pixels_next, 
                                       pixel_intents, 
                                       pixel_directions)


def main():
    ti.init(arch=ti.gpu)
    pixels_current = ti.Vector.field(3, ti.u8, shape=(consts.WIDTH, consts.HEIGHT))
    pixels_next = ti.Vector.field(3, ti.u8, shape=(consts.WIDTH, consts.HEIGHT))
    pixels_current.fill(consts.EMPTY_COLOR[0])
    pixel_intents = ti.Vector.field(2, ti.i8, shape=(consts.WIDTH, consts.HEIGHT))
    pixel_directions = ti.Vector.field(2, ti.i8, shape=(consts.WIDTH, consts.HEIGHT))
    
    material_keybinds = {
        consts.SAND_COLOR:      pygame.K_q,
        consts.WATER_COLOR:     pygame.K_w,
        consts.ROCK_COLOR:      pygame.K_r,
    }
    
    pygame.init()
    screen = pygame.display.set_mode((consts.WIN_WIDTH, consts.WIN_HEIGHT), pygame.RESIZABLE)
    
    render_surface = pygame.Surface((consts.WIDTH, consts.HEIGHT))
    clock = pygame.time.Clock()
    
    draw_size = 10
    time_elapsed = 0.0
    running = True
    update_fps = 60
    sim_accumulator = 0.0
    sim_fps = 60
    ticks_per_tick = 10
    current_color = consts.SAND_COLOR

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False                
            if event.type == pygame.MOUSEWHEEL:
                draw_size = int(max(0, draw_size + event.y*(draw_size*0.2+1)))
        
        keys = pygame.key.get_pressed()
        keys_jp = pygame.key.get_just_pressed()

        if keys[pygame.K_UP]:
            sim_fps += 1 + int(0.03 * sim_fps)

        if keys[pygame.K_DOWN]:
            sim_fps = max(1, sim_fps - 1)

        for col, k in material_keybinds.items():
            if keys_jp[k]:
                current_color = col
        
        if keys_jp[pygame.K_ESCAPE]:
            running = False
        if keys_jp[pygame.K_k]:
            pixels_current.fill(consts.EMPTY_COLOR[0])

        mx, my = pygame.mouse.get_pos()
        sim_x = int(min(consts.WIDTH - 1, mx * consts.WIDTH // screen.width))
        sim_y = int(min(consts.HEIGHT - 1, my * consts.HEIGHT // screen.height))
        if pygame.mouse.get_pressed()[0]:
            utils.set_pix_around(sim_x, sim_y, draw_size, current_color, pixels_current)
        if pygame.mouse.get_pressed()[2]:
            utils.set_pix_around(sim_x, sim_y, draw_size, consts.EMPTY_COLOR, pixels_current)

        dt = clock.tick(update_fps) / 1000.0
        time_elapsed += dt

        sim_accumulator += dt
        while sim_accumulator > 1 / sim_fps:
            sim_accumulator -= 1 / sim_fps
            for _ in range(ticks_per_tick):
                simulate(pixels_current, pixels_next, pixel_intents, pixel_directions)
                pixels_current, pixels_next = pixels_next, pixels_current

        # draw ----------------------
        frame = pixels_current.to_numpy()
        pygame.surfarray.blit_array(render_surface, frame)

        pygame.draw.circle(render_surface, current_color, (sim_x, sim_y), draw_size)
        
        scaled = pygame.transform.scale(render_surface, (screen.width, screen.height))
        screen.blit(scaled, (0, 0))

        pygame.display.set_caption(f"FPS: {clock.get_fps():.1f}")

        pygame.display.flip()
        

    pygame.quit()

if __name__ == "__main__":
    main()