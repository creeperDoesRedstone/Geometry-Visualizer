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
        if isinstance(sprite, BGText):          return -1
        if isinstance(sprite, Line):            return 0
        if isinstance(sprite, Triangle):        return 0
        if isinstance(sprite, QuadBezierCurve): return 0
        if isinstance(sprite, Point):           return 1
        if isinstance(sprite, Text):            return 2
    def draw(self, surface:pygame.Surface):
        sorted_sprites = self.sprites
        sorted_sprites.sort(key=self.get_sprite_type)
        for sprite in self.sprites:
            sprite.draw(surface)
    def update(self):
        for sprite in self.sprites:
            sprite.update()

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
            if pos[0] < self.x + self.radius and pos[0] > self.x - self.radius and pos[1] < self.y + self.radius and pos[1] > self.y - self.radius and not dragging:
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
    def bezier_interpolation(self, t:float):
        inter_a = self.linear_interpolation(self.start_point, self.control_point, t)
        inter_b = self.linear_interpolation(self.control_point, self.end_point, t)
        return self.linear_interpolation(inter_a, inter_b, t)
    def draw(self, surface:pygame.Surface):
        res = 50
        previous_point = self.start_point
        for i in range(res):
            t = (i + 1) / res
            next_point = self.bezier_interpolation(t)
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
        text_rect.center = (self.point.x, self.point.y - self.point.radius - 15) if isinstance(self.point, Point) else self.point
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

group1 = Group()
group2 = Group()
group3 = Group()

##########################
# GROUP 1
##########################

# Background
group1.add(BGText("Two points on a line", (120, 120, 120), (screen_width/2, 50), 32))
group1.add(BGText("The red point is not draggable", (50, 50, 50), (screen_width/2, 500), 32))
# Points
group1.add(Point(200, 320, 10, "red", False))
group1.add(Point(760, 320, 10, "white"))
# Lines
group1.add(Line(group1.sprites[2], group1.sprites[3], 3, "green"))
# Text
group1.add(Text("A", "white", group1.sprites[2], 20))
group1.add(Text("B", "white", group1.sprites[3], 20))
group1.add(LineText(group1.sprites[2], group1.sprites[3], "cyan", 20))
group1.add(LineText(group1.sprites[2], group1.sprites[3], (0, 150, 150), 16, 40, "Length of line (px):"))

##########################
# GROUP 2
##########################

# Background
group2.add(BGText("Triangle", (120, 120, 120), (screen_width/2, 50), 32))
# Points
group2.add(Point(330, 440, 8, (80, 80, 80)))
group2.add(Point(630, 440, 8, (80, 80, 80)))
group2.add(Point(480, 200, 8, (80, 80, 80)))
# Lines
group2.add(Triangle(group2.sprites[1], group2.sprites[2], group2.sprites[3], 3, "magenta", "white"))
# Text
group2.add(Text("A", "white", group2.sprites[1], 20))
group2.add(Text("B", "white", group2.sprites[2], 20))
group2.add(Text("C", "white", group2.sprites[3], 20))

##########################
# GROUP 3
##########################

# Background
group3.add(BGText("Quadratic Bézier Curve", (120, 120, 120), (screen_width/2, 50), 32))

group3.add(Point(280, 340, 8, "white"))
group3.add(Point(700, 250, 8, "white"))
group3.add(Point(480, 100, 8, "orange"))
group3.add(Point(500, 420, 8, "white"))
group3.add(Point(800, 330, 8, "orange"))

group3.add(Line(group3.sprites[1], group3.sprites[3], 1, "cyan"))
group3.add(Line(group3.sprites[2], group3.sprites[3], 1, "cyan"))
group3.add(Line(group3.sprites[2], group3.sprites[5], 1, "green"))
group3.add(Line(group3.sprites[4], group3.sprites[5], 1, "green"))

# Curve
group3.add(QuadBezierCurve(group3.sprites[1], group3.sprites[2], group3.sprites[3], "yellow", 3))
group3.add(QuadBezierCurve(group3.sprites[2], group3.sprites[4], group3.sprites[5], "red", 3))

group3.add(Text("A", "white" , group3.sprites[1], 20))
group3.add(Text("B", "white" , group3.sprites[2], 20))
group3.add(Text("C", "orange", group3.sprites[3], 20))
group3.add(Text("D", "white" , group3.sprites[4], 20))
group3.add(Text("E", "orange", group3.sprites[5], 20))

##########################
# GROUPS
##########################
groups = iter([group1, group2, group3])
main = next(groups)

while running:
    screen.fill(bg_col)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            try:
                main = next(groups)
            except StopIteration:
                pass
    
    main.update()
    main.draw(screen)

    pygame.display.flip()
    clock.tick(60)
pygame.quit()