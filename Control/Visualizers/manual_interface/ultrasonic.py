import math as _math, pygame as _pygame

SHOW_AVG = True

US_RAY_COL = [50, 160, 200]
US_AVG_COL = [120, 180, 20]

class UltrasonicSensor:
    def __init__(self, params: dict, pixel_scale: int, x0: int, y0: int, text_font: _pygame.font.SysFont):
        global TEXT_FONT
        TEXT_FONT = text_font
        self._params: dict     = params
        self._location: tuple  = params['location']
        self._rotation: float  = _math.radians(params['rotation'])
        self._steps: int       = (params.get('steps', 6) // 2)
        self._angle: float     = (_math.radians(params.get('angle', 5)) / (2 * self._steps ))
        self._buffer_len: int  = params.get('buffer-len', 20)
        self._buffer: list     = [1] * self._buffer_len
        self._draw_mean: bool  = params.get('draw_mean', False)
        self._xoffset = params.get('xoffset', 10)
        self._yoffset = params.get('yoffset', 10)

        self.pixel_scale = pixel_scale
        self.x0 = x0
        self.y0 = y0

    def draw(self, screen: _pygame.Surface):
        dist = self.latest() * self.pixel_scale
        cx   = self.x0 + self.pixel_scale * self._location[0]
        cy   = self.y0 + self.pixel_scale * self._location[1]
        rot  = self._rotation
        if SHOW_AVG:
            avg = self.avg() * self.pixel_scale
        for step in range(-self._steps, self._steps + 1):
            angle = self._angle * step
            ex = cx + dist * _math.sin(rot - angle)
            ey = cy + dist * _math.cos(rot - angle)
            _pygame.draw.line(screen, US_RAY_COL, (cx, cy,), (ex, ey,))
            if SHOW_AVG:
                ex = cx + avg * _math.sin(rot - angle)
                ey = cy + avg * _math.cos(rot - angle)
                _pygame.draw.circle(screen, US_AVG_COL, (ex, ey,), 1)
        txt_val = f"{dist / self.pixel_scale * 0.3937:.1f}".encode('utf-8') # * 39.37
        txt = TEXT_FONT.render(txt_val, True, (0, 0, 0), (255, 255, 255))
        txt_rect = txt.get_rect()
        txt_rect.center = (cx + self._xoffset, cy + self._yoffset)
        screen.blit(txt, txt_rect)



    def append(self, value: float):
        _ = self._buffer.pop(0)
        self._buffer.append(value)

    def latest(self) -> float:
        return self._buffer[-1]

    def avg(self) -> float:
        return sum(self._buffer) / len(self._buffer)
