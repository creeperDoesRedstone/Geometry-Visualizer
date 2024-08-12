import math, pygame

pygame.init()
screen_height = 540
screen_width = 960

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Visualization")
bg_col = "black"

clock = pygame.time.Clock()
running = True
dragging = False

class Sprite:
    def __init__(self):
        self.x = None
        self.y = None
    def draw(self, surface:pygame.Surface):
        pass
    def update(self):
        pass

class Group:
    def __init__(self):
        self.sprites : list[Sprite] = []
    def add(self, sprite:Sprite): 
        self.sprites = self.sprites + [sprite]
    def get_sprite_type(self, sprite:Sprite):
        if isinstance(sprite, BGText):           return -1
        if isinstance(sprite, Line):             return 0
        if isinstance(sprite, Triangle):         return 0
        if isinstance(sprite, QuadBezierCurve):  return 0
        if isinstance(sprite, CubicBezierCurve): return 0
        if isinstance(sprite, Point):            return 1
        if isinstance(sprite, Text):             return 2
    def draw(self, surface:pygame.Surface):
        sorted_sprites = self.sprites
        sorted_sprites.sort(key=self.get_sprite_type)
        for sprite in self.sprites:
            sprite.draw(surface)
    def update(self):
        for sprite in self.sprites:
            sprite.update()

def load(fn:str):
    try:
        file = open(fn, "r")
    except FileNotFoundError:
        raise Exception(f"File {fn} not found.")
    else:
        groups = []
        for line in file:
            if line != "\n":
                line = line.replace("\n", "")
                if line[0] == "@":
                    group = Group()
                    continue
                elif line == "END":
                    groups += [group]
                    continue
                spl_line = line.split()
                if spl_line[0] == "BGTXT":
                    spl_line[1] = spl_line[1].replace("`", " ").replace("Bezier", "Bézier")
                    col = spl_line[2]
                    if col[0] == "(" and col[-1] == ")":
                        col = list(map(int, col[1:-1].split(",")))
                    pos = spl_line[3]
                    if pos[0] == "(" and pos[-1] == ")":
                        pos = list(map(int, pos[1:-1].split(",")))
                    elif pos.startswith("ADDR"):
                        pos = group.sprites(int(pos[4:]))
                    group.add(BGText(spl_line[1], col, pos, int(spl_line[4])))
                elif spl_line[0] == "POINT":
                    col = spl_line[4]
                    if col[0] == "(" and col[-1] == ")":
                        col = list(map(int, col[1:-1].split(",")))
                    group.add(Point(int(spl_line[1]), int(spl_line[2]), int(spl_line[3]), col))
                    if len(spl_line) == 6:
                        if spl_line[5] == "False":
                            group.sprites[-1].draggable = False
                elif spl_line[0] == "LINE":
                    spl_line[1] = group.sprites[int(spl_line[1][4:])]
                    spl_line[2] = group.sprites[int(spl_line[2][4:])]
                    group.add(Line(spl_line[1], spl_line[2], int(spl_line[3]), spl_line[4]))
                elif spl_line[0] == "TRI":
                    spl_line[1] = group.sprites[int(spl_line[1][4:])]
                    spl_line[2] = group.sprites[int(spl_line[2][4:])]
                    spl_line[3] = group.sprites[int(spl_line[3][4:])]
                    if len(spl_line) == 5:
                        group.add(Triangle(spl_line[1], spl_line[2], spl_line[3], int(spl_line[4])))
                    if len(spl_line) == 6:
                        group.add(Triangle(spl_line[1], spl_line[2], spl_line[3], int(spl_line[4]), spl_line[5]))
                    if len(spl_line) == 7:
                        group.add(Triangle(spl_line[1], spl_line[2], spl_line[3], int(spl_line[4]), spl_line[5], spl_line[6]))
                elif spl_line[0] == "BCURVEQ":
                    spl_line[1] = group.sprites[int(spl_line[1][4:])]
                    spl_line[2] = group.sprites[int(spl_line[2][4:])]
                    spl_line[3] = group.sprites[int(spl_line[3][4:])]
                    col = spl_line[4]
                    if col[0] == "(" and col[-1] == ")":
                        col = list(map(int, col[1:-1].split(",")))
                    group.add(QuadBezierCurve(spl_line[1], spl_line[2], spl_line[3], col, int(spl_line[5])))
                elif spl_line[0] == "BCURVEC":
                    spl_line[1] = group.sprites[int(spl_line[1][4:])]
                    spl_line[2] = group.sprites[int(spl_line[2][4:])]
                    spl_line[3] = group.sprites[int(spl_line[3][4:])]
                    spl_line[4] = group.sprites[int(spl_line[4][4:])]
                    col = spl_line[5]
                    if col[0] == "(" and col[-1] == ")":
                        col = list(map(int, col[1:-1].split(",")))
                    group.add(CubicBezierCurve(spl_line[1], spl_line[2], spl_line[3], spl_line[4], col, int(spl_line[6])))
                elif spl_line[0] == "TEXT":
                    spl_line[1] = spl_line[1] = spl_line[1].replace("`", " ").replace("Bezier", "Bézier")
                    col = spl_line[2]
                    if col[0] == "(" and col[-1] == ")":
                        col = list(map(int, col[1:-1].split(",")))
                    pos = spl_line[3]
                    if pos[0] == "(" and pos[-1] == ")":
                        pos = list(map(int, pos[1:-1].split(",")))
                    elif pos.startswith("ADDR"):
                        pos = group.sprites[int(pos[4:])]
                    group.add(Text(spl_line[1], col, pos, int(spl_line[4])))
                elif spl_line[0] == "LNTXT":
                    spl_line[1] = group.sprites[int(spl_line[1][4:])]
                    spl_line[2] = group.sprites[int(spl_line[2][4:])]
                    col = spl_line[3]
                    if col[0] == "(" and col[-1] == ")":
                        col = list(map(int, col[1:-1].split(",")))
                    size = int(spl_line[4])
                    if len(spl_line) > 5:
                        offset = int(spl_line[5])
                        if len(spl_line) > 6:
                            spl_line[6] = spl_line[6].replace("`", " ").replace("Bezier", "Bézier")
                            group.add(LineText(spl_line[1], spl_line[2], col, size, offset, spl_line[6]))
                        else:
                            group.add(LineText(spl_line[1], spl_line[2], col, size, offset))
                    else:
                        group.add(LineText(spl_line[1], spl_line[2], col, size))
        else:
            return groups
    finally:
        file.close()

class Point(Sprite):
    def __init__(self, x, y, radius, col, draggable=True):
        self.x = x
        self.y = y
        self.radius = radius
        self.col = col
        self.dragged = False
        self.draggable = draggable
    def draw(self, surface:pygame.Surface):
        pygame.draw.circle(surface, self.col, (self.x, self.y), self.radius)
    def update(self):
        pos = pygame.mouse.get_pos()
        mouse_down = pygame.mouse.get_pressed(3)[0]
        global dragging
        if mouse_down:
            if pos[0] < self.x + self.radius and pos[0] > self.x - self.radius and pos[1] < self.y + self.radius and pos[1] > self.y - self.radius and not dragging and self.draggable:
                dragging = True
                self.dragged = True
        else:
            dragging = False
            self.dragged = False
        if dragging and self.dragged and self.draggable:
            self.x = pos[0]
            self.y = pos[1]
            self.x = min(self.x, screen_width - self.radius)
            self.x = max(self.radius, self.x)
            self.y = min(self.y, screen_height - self.radius)
            self.y = max(self.radius, self.y)

def get_adv_distance(p1:Point, p2:Point, dp:int=3):
    dx = abs(p2.x - p1.x)
    dy = abs(p2.y - p1.y)
    dist = round(math.sqrt(dx * dx + dy * dy), dp)
    if p2.y > p1.y:
        dist = -dist
    return dx, dy, dist

class Line(Sprite):
    def __init__(self, p1, p2, width, col):
        self.p1 = p1
        self.p2 = p2
        self.width = width
        self.col = col
    def draw(self, surface:pygame.Surface):
        pygame.draw.line(
            surface, self.col, (self.p1.x, self.p1.y), (self.p2.x, self.p2.y), self.width
        )

class Triangle(Sprite):
    def __init__(self, p1, p2, p3, width, fill_col=None, outline_col=None):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.width = width
        self.fill_col = fill_col
        self.outline_col = outline_col
    def draw(self, surface:pygame.Surface):
        if self.fill_col:
            pygame.draw.polygon(
                surface, self.fill_col,
                ((self.p1.x, self.p1.y), (self.p2.x, self.p2.y), (self.p3.x, self.p3.y)),
            )
        if self.outline_col:
            pygame.draw.line(
                surface, self.outline_col, (self.p1.x, self.p1.y), (self.p2.x, self.p2.y), self.width
            )
            pygame.draw.line(
                surface, self.outline_col, (self.p2.x, self.p2.y), (self.p3.x, self.p3.y), self.width
            )
            pygame.draw.line(
                surface, self.outline_col, (self.p3.x, self.p3.y), (self.p1.x, self.p1.y), self.width
            )

class QuadBezierCurve(Sprite):
    def __init__(self, start_point:Point, end_point:Point, control_point:Point, col:pygame.Color, width:int):
        self.start_point = start_point
        self.end_point = end_point
        self.control_point = control_point
        self.col = col
        self.width = width
    def linear_interpolation(self, start_point:Point, end_point:Point, t:float) -> Point:
        offset = Point((end_point.x - start_point.x) * t,
                       (end_point.y - start_point.y) * t,
                       0, bg_col, False)
        return Point(start_point.x + offset.x,
                     start_point.y + offset.y,
                     0, bg_col, False)
    def draw(self, surface:pygame.Surface):
        res = 50
        previous_point = self.start_point
        for i in range(res):
            t = (i + 1) / res
            inter_a = self.linear_interpolation(self.start_point, self.control_point, t)
            inter_b = self.linear_interpolation(self.control_point, self.end_point, t)
            next_point = self.linear_interpolation(inter_a, inter_b, t)
            pygame.draw.line(surface, self.col,
                             (previous_point.x, previous_point.y),
                             (next_point.x, next_point.y),
                             self.width
                            )
            previous_point = next_point

class CubicBezierCurve(Sprite):
    def __init__(self, p0:Point, p1:Point, p2:Point, p3:Point, col:pygame.Color, width:int):
        self.p0 = p0
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.col = col
        self.width = width
    def linear_interpolation(self, p0:Point, p1:Point, t:float) -> Point:
        offset = Point((p1.x - p0.x) * t,
                       (p1.y - p0.y) * t,
                       0, bg_col, False)
        return Point(p0.x + offset.x,
                     p0.y + offset.y,
                     0, bg_col, False)
    def quadratic_interpolation(self, p0:Point, p1:Point, p2:Point, t:float) -> Point:
        inter_a = self.linear_interpolation(p0, p1, t)
        inter_b = self.linear_interpolation(p1, p2, t)
        return self.linear_interpolation(inter_a, inter_b, t)
    def draw(self, surface:pygame.Surface):
        res = 50
        previous_point = self.p0
        for i in range(res):
            t = (i + 1) / res
            inter_a = self.quadratic_interpolation(self.p0, self.p1, self.p2, t)
            inter_b = self.quadratic_interpolation(self.p1, self.p2, self.p3, t)
            next_point = self.linear_interpolation(inter_a, inter_b, t)
            pygame.draw.line(surface, self.col,
                             (previous_point.x, previous_point.y),
                             (next_point.x, next_point.y),
                             self.width
                            )
            previous_point = next_point

class Text(Sprite):
    def __init__(self, content:str, col:pygame.Color, point:Point|tuple, size:int):
        self.font = pygame.font.SysFont("JetBrains Mono", size, True)
        self.content = content
        self.col = col
        self.point = point
    def draw(self, surface:pygame.Surface):
        text = self.font.render(self.content, True, self.col)
        text_rect = text.get_rect()
        # text_rect.center = (self.point.x, self.point.y - self.point.radius - 15) if isinstance(self.point, Point) else self.point
        if isinstance(self.point, Point):
            text_rect.center = (self.point.x, self.point.y - self.point.radius - 15)
        else:
            text_rect.center = (self.point[0], self.point[1])
        surface.blit(text, text_rect)

class BGText(Text):
    def __init__(self, content:str, col:pygame.Color, point:Point|tuple, size:int):
        super().__init__(content, col, point, size)

class LineText(Text):
    def __init__(self, p1:Point, p2:Point, col:pygame.Color, size:int, offset:int=20, content:str=""):
        self.p1 = p1
        self.p2 = p2
        self.is_num = content == ""
        self.offset = offset
        self.x = (p1.x + p2.x) / 2
        self.y = (p1.y + p2.y) / 2 - offset
        super().__init__(content, col, (self.x, self.y), size)
    def update(self):
        if self.is_num:
            self.content = str(abs(get_adv_distance(self.p1, self.p2)[2]))
        self.x = (self.p1.x + self.p2.x) / 2
        self.y = (self.p1.y + self.p2.y) / 2 - self.offset
        self.point = (self.x, self.y)
    def draw(self, surface:pygame.Surface):
        text = self.font.render(self.content, True, self.col, bg_col)
        text_rect = text.get_rect()
        text_rect.center = (self.point.x, self.point.y - self.point.radius - 15) if isinstance(self.point, Point) else self.point
        surface.blit(text, text_rect)


##########################
# GROUPS
##########################
groups = load("config.txt")
idx = 0
main = groups[idx]

while running:
    screen.fill(bg_col)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            idx += 1
            if idx == len(groups): idx = 0
            main = groups[idx]
    
    main.update()
    main.draw(screen)

    pygame.display.flip()
    clock.tick(60)
pygame.quit()
