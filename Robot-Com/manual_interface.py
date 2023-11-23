"""Manual interface (what we had for milestone 1)."""

####################
### BASE IMPORTS ###
####################
import yaml as _yaml, os as _os, pygame



####################
### BASE IMPORTS ###
####################
import sys; sys.path.append(_os.path.dirname(__file__))

from _manual_interface.ultrasonic    import UltrasonicSensor
from _manual_interface.communication import get_ultrasonics, enter_manual_mode, fwd, bwd, clockwise, counter_clockwise, in_manual_mode
from _manual_interface._cfg import _cfg

_ = sys.path.pop()



######################
### DISPLAY CONFIG ###
######################
PIXEL_SCALE = 8
WIDTH       = 1200
HEIGHT      = 800

X0 = WIDTH  // 2
Y0 = HEIGHT // 2

BG_COL_MAN  = [0,   0,   0]
BG_COL_DEF  = [50, 50, 50]
ROB_COL =     [200, 140, 80]

BLACK   = [0,   0,   0  ]
WHITE   = [255, 255, 255]

pygame.init()
TEXT_FONT  = pygame.font.SysFont("Times New Roman", 18)

####################
### ROBOT CONFIG ###
####################
robot_outline = [(x * PIXEL_SCALE + X0, y * PIXEL_SCALE + Y0) for x, y  in _cfg['outline']]

ultrasonics_  = {name: UltrasonicSensor(params, PIXEL_SCALE, X0, Y0, TEXT_FONT) for (name, params) in _cfg['ultrasonic'].items()}
ultrasonics   = [ultrasonics_[name] for name in sorted(ultrasonics_.keys())]



############
### MAIN ###
############
if __name__ == '__main__':
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    while True:
        clock.tick(10)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_o:
                    enter_manual_mode()

                elif event.key == pygame.K_w:
                    fwd()

                elif event.key == pygame.K_s:
                    bwd()

                elif event.key == pygame.K_q:
                    counter_clockwise()

                elif event.key == pygame.K_e:
                    clockwise()

                ## K_s, K_q, K_e

        screen.fill(BG_COL_MAN if in_manual_mode() else BG_COL_DEF)
        pygame.draw.polygon(screen, ROB_COL, robot_outline, 0)

        try:
            for model, reading in zip(ultrasonics, get_ultrasonics()):
                model.append(reading)
                model.draw(screen)

            diff            = f"{ultrasonics_['u1'].latest() - ultrasonics_['u2'].latest():.1f}"
            txt             = TEXT_FONT.render(diff, True, BLACK, WHITE)
            txt_rect        = txt.get_rect()
            txt_rect.center = (X0, Y0)
            screen.blit(txt, txt_rect)

        except:
            pass

        pygame.display.flip()