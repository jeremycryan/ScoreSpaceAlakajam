WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

WINDOW_HEIGHT = 600
WINDOW_WIDTH = 800
WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT

PORT_URL = "https://raw.githubusercontent.com/jeremycryan/ScoreSpaceAlakajam/master/port.txt"
da
LORE_TEXT = ("New York plunged into chaos when the alien ship landed. Millions were killed, and the remainder forced into hiding.",
    "Like many, we were separated.",
    "It's been three days. If you're still out there, I'll find you --- regardless of how many connections it takes me.")

def distance_between_points(x1, y1, x2, y2):
    return ((x1-x2)**2 + (y1-y2)**2)**0.5
