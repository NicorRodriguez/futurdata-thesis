import math
from typing import Tuple, List


def distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)


def angle_between_points(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    return math.atan2(p2[1] - p1[1], p2[0] - p1[0])


def snap_to_grid(x: float, y: float, grid_size: int = 50) -> Tuple[float, float]:
    snapped_x = round(x / grid_size) * grid_size
    snapped_y = round(y / grid_size) * grid_size
    return (snapped_x, snapped_y)


def point_in_rect(px: float, py: float, x1: float, y1: float, x2: float, y2: float) -> bool:
    return x1 <= px <= x2 and y1 <= py <= y2


def rect_intersects(r1: Tuple[float, float, float, float], r2: Tuple[float, float, float, float]) -> bool:
    x1, y1, x2, y2 = r1
    x3, y3, x4, y4 = r2
    return not (x2 < x3 or x4 < x1 or y2 < y3 or y4 < y1)


def get_arrow_points(x1: float, y1: float, x2: float, y2: float, arrow_size: int = 10) -> List[Tuple[float, float]]:
    angle = math.atan2(y2 - y1, x2 - x1)
    angle1 = angle + math.pi * 0.85
    angle2 = angle - math.pi * 0.85
    x3 = x2 - arrow_size * math.cos(angle1)
    y3 = y2 - arrow_size * math.sin(angle1)
    x4 = x2 - arrow_size * math.cos(angle2)
    y4 = y2 - arrow_size * math.sin(angle2)
    return [(x2, y2), (x3, y3), (x4, y4)]


def calculate_bezier_point(t: float, p0: Tuple[float, float], p1: Tuple[float, float],
                           p2: Tuple[float, float], p3: Tuple[float, float]) -> Tuple[float, float]:
    mt = 1 - t
    x = mt**3 * p0[0] + 3 * mt**2 * t * p1[0] + 3 * mt * t**2 * p2[0] + t**3 * p3[0]
    y = mt**3 * p0[1] + 3 * mt**2 * t * p1[1] + 3 * mt * t**2 * p2[1] + t**3 * p3[1]
    return (x, y)


def find_alignment_guides(moving_shape, other_shapes, tolerance: int = 5) -> dict:
    guides = {'vertical': [], 'horizontal': []}
    for shape in other_shapes:
        if shape == moving_shape:
            continue
        if abs(moving_shape.x - shape.x) < tolerance:
            guides['vertical'].append(shape.x)
        if abs(moving_shape.y - shape.y) < tolerance:
            guides['horizontal'].append(shape.y)
    return guides


def normalize_rect(x1: float, y1: float, x2: float, y2: float) -> Tuple[float, float, float, float]:
    return (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))


def calculate_bounding_rect(points: List[Tuple[float, float]]) -> Tuple[float, float, float, float]:
    if not points:
        return (0, 0, 0, 0)
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return (min(xs), min(ys), max(xs), max(ys))
