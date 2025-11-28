from typing import Dict, Tuple, List
import math


class Shape:
    _id_counter = 0

    def __init__(self, x: float, y: float, shape_type: str):
        Shape._id_counter += 1
        self.id = Shape._id_counter
        self.x = x
        self.y = y
        self.shape_type = shape_type
        self.text = ""
        self.shape_id = None
        self.text_id = None
        self.selected = False

    @classmethod
    def reset_counter(cls):
        cls._id_counter = 0

    def get_bounds(self) -> Tuple[float, float, float, float]:
        raise NotImplementedError()

    def get_connection_points(self) -> Dict[str, Tuple[float, float]]:
        raise NotImplementedError()

    def contains_point(self, px: float, py: float) -> bool:
        raise NotImplementedError()

    def move(self, dx: float, dy: float):
        self.x += dx
        self.y += dy

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.shape_type,
            "x": self.x,
            "y": self.y,
            "text": self.text
        }

    @staticmethod
    def from_dict(data: dict) -> 'Shape':
        shape_type = data["type"]

        if shape_type == "product":
            shape = ProductBox(data["x"], data["y"])
        elif shape_type == "action":
            shape = ActionCircle(data["x"], data["y"])
        elif shape_type == "diamond":
            shape = DiamondStep(data["x"], data["y"])
        elif shape_type == "component":
            shape = ComponentBox(data["x"], data["y"])
        elif shape_type == "arrow":
            shape = ArrowShape(data["x"], data["y"])
        else:
            raise ValueError(f"Unknown shape type: {shape_type}")

        shape.id = data["id"]
        shape.text = data.get("text", "")

        if hasattr(shape, 'load_properties'):
            shape.load_properties(data)

        return shape


class ProductBox(Shape):
    WIDTH = 200
    HEIGHT = 80

    def __init__(self, x: float, y: float):
        super().__init__(x, y, "product")
        self.text = "Product\nBrand:\nModel:"
        self.brand = ""
        self.model = ""

    def get_bounds(self) -> Tuple[float, float, float, float]:
        half_w = self.WIDTH / 2
        half_h = self.HEIGHT / 2
        return (self.x - half_w, self.y - half_h, self.x + half_w, self.y + half_h)

    def get_connection_points(self) -> Dict[str, Tuple[float, float]]:
        half_h = self.HEIGHT / 2
        half_w = self.WIDTH / 2
        return {
            'top': (self.x, self.y - half_h),
            'bottom': (self.x, self.y + half_h),
            'left': (self.x - half_w, self.y),
            'right': (self.x + half_w, self.y)
        }

    def contains_point(self, px: float, py: float) -> bool:
        x1, y1, x2, y2 = self.get_bounds()
        return x1 <= px <= x2 and y1 <= py <= y2

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({"brand": self.brand, "model": self.model})
        return data

    def load_properties(self, data: dict):
        self.brand = data.get("brand", "")
        self.model = data.get("model", "")


class ActionCircle(Shape):
    RADIUS = 60

    def __init__(self, x: float, y: float):
        super().__init__(x, y, "action")
        self.text = "Action\naction_id:\ntools:"
        self.action_id = ""
        self.name = ""
        self.tools = ""

    def get_bounds(self) -> Tuple[float, float, float, float]:
        r = self.RADIUS
        return (self.x - r, self.y - r, self.x + r, self.y + r)

    def get_connection_points(self) -> Dict[str, Tuple[float, float]]:
        r = self.RADIUS
        return {
            'top': (self.x, self.y - r),
            'bottom': (self.x, self.y + r),
            'left': (self.x - r, self.y),
            'right': (self.x + r, self.y)
        }

    def contains_point(self, px: float, py: float) -> bool:
        distance = math.sqrt((px - self.x)**2 + (py - self.y)**2)
        return distance <= self.RADIUS

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({"action_id": self.action_id, "name": self.name, "tools": self.tools})
        return data

    def load_properties(self, data: dict):
        self.action_id = data.get("action_id", "")
        self.name = data.get("name", "")
        self.tools = data.get("tools", "")


class DiamondStep(Shape):
    SIZE = 100

    def __init__(self, x: float, y: float):
        super().__init__(x, y, "diamond")
        self.text = "Activity"
        self.step_description = ""
        self.image_path = ""

    def get_bounds(self) -> Tuple[float, float, float, float]:
        half = self.SIZE / 2
        return (self.x - half, self.y - half, self.x + half, self.y + half)

    def get_connection_points(self) -> Dict[str, Tuple[float, float]]:
        half = self.SIZE / 2
        return {
            'top': (self.x, self.y - half),
            'bottom': (self.x, self.y + half),
            'left': (self.x - half, self.y),
            'right': (self.x + half, self.y)
        }

    def contains_point(self, px: float, py: float) -> bool:
        dx = abs(px - self.x)
        dy = abs(py - self.y)
        half = self.SIZE / 2
        return (dx + dy) <= half

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({"step_description": self.step_description, "image_path": self.image_path})
        return data

    def load_properties(self, data: dict):
        self.step_description = data.get("step_description", "")
        self.image_path = data.get("image_path", "")


class ComponentBox(Shape):
    WIDTH = 160
    HEIGHT = 80

    def __init__(self, x: float, y: float):
        super().__init__(x, y, "component")
        self.text = "Component\ncolor:\nmaterial:"
        self.component_name = ""
        self.color = ""
        self.material = ""
        self.weight = ""

    def get_bounds(self) -> Tuple[float, float, float, float]:
        half_w = self.WIDTH / 2
        half_h = self.HEIGHT / 2
        return (self.x - half_w, self.y - half_h, self.x + half_w, self.y + half_h)

    def get_connection_points(self) -> Dict[str, Tuple[float, float]]:
        half_h = self.HEIGHT / 2
        half_w = self.WIDTH / 2
        return {
            'top': (self.x, self.y - half_h),
            'bottom': (self.x, self.y + half_h),
            'left': (self.x - half_w, self.y),
            'right': (self.x + half_w, self.y)
        }

    def contains_point(self, px: float, py: float) -> bool:
        x1, y1, x2, y2 = self.get_bounds()
        return x1 <= px <= x2 and y1 <= py <= y2

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            "component_name": self.component_name,
            "color": self.color,
            "material": self.material,
            "weight": self.weight
        })
        return data

    def load_properties(self, data: dict):
        self.component_name = data.get("component_name", "")
        self.color = data.get("color", "")
        self.material = data.get("material", "")
        self.weight = data.get("weight", "")


class ArrowShape(Shape):
    LENGTH = 150
    WIDTH = 10

    def __init__(self, x: float, y: float, from_shape=None, to_shape=None):
        super().__init__(x, y, "arrow")
        self.text = ""
        self.from_shape = from_shape
        self.to_shape = to_shape
        self.from_anchor = "bottom"
        self.to_anchor = "top"

        if from_shape and to_shape:
            self.update_from_shapes()
        else:
            self.angle = 0
            self.end_x = x + self.LENGTH
            self.end_y = y

    def update_from_shapes(self):
        if self.from_shape and self.to_shape:
            self.auto_calculate_anchors()
            from_points = self.from_shape.get_connection_points()
            to_points = self.to_shape.get_connection_points()
            start = from_points.get(self.from_anchor, (self.from_shape.x, self.from_shape.y))
            end = to_points.get(self.to_anchor, (self.to_shape.x, self.to_shape.y))
            self.x, self.y = start
            self.end_x, self.end_y = end
            dx = self.end_x - self.x
            dy = self.end_y - self.y
            self.angle = math.degrees(math.atan2(dy, dx))

    def auto_calculate_anchors(self):
        if not (self.from_shape and self.to_shape):
            return
        dx = self.to_shape.x - self.from_shape.x
        dy = self.to_shape.y - self.from_shape.y
        if abs(dx) > abs(dy):
            self.from_anchor = 'right' if dx > 0 else 'left'
        else:
            self.from_anchor = 'bottom' if dy > 0 else 'top'
        if abs(dx) > abs(dy):
            self.to_anchor = 'left' if dx > 0 else 'right'
        else:
            self.to_anchor = 'top' if dy > 0 else 'bottom'

    def get_bounds(self) -> Tuple[float, float, float, float]:
        if self.from_shape and self.to_shape:
            self.update_from_shapes()
        padding = 15
        x1 = min(self.x, self.end_x) - padding
        y1 = min(self.y, self.end_y) - padding
        x2 = max(self.x, self.end_x) + padding
        y2 = max(self.y, self.end_y) + padding
        return (x1, y1, x2, y2)

    def get_connection_points(self) -> Dict[str, Tuple[float, float]]:
        if self.from_shape and self.to_shape:
            self.update_from_shapes()
        mid_x = (self.x + self.end_x) / 2
        mid_y = (self.y + self.end_y) / 2
        return {
            'top': (mid_x, mid_y - 20),
            'bottom': (mid_x, mid_y + 20),
            'left': (self.x, self.y),
            'right': (self.end_x, self.end_y)
        }

    def contains_point(self, px: float, py: float) -> bool:
        if self.from_shape and self.to_shape:
            self.update_from_shapes()
        line_length_sq = (self.end_x - self.x) ** 2 + (self.end_y - self.y) ** 2
        if line_length_sq == 0:
            distance = math.sqrt((px - self.x) ** 2 + (py - self.y) ** 2)
        else:
            t = max(0, min(1, ((px - self.x) * (self.end_x - self.x) +
                               (py - self.y) * (self.end_y - self.y)) / line_length_sq))
            proj_x = self.x + t * (self.end_x - self.x)
            proj_y = self.y + t * (self.end_y - self.y)
            distance = math.sqrt((px - proj_x) ** 2 + (py - proj_y) ** 2)
        return distance <= 10

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            "angle": self.angle,
            "end_x": self.end_x,
            "end_y": self.end_y,
            "from_shape_id": self.from_shape.id if self.from_shape else None,
            "to_shape_id": self.to_shape.id if self.to_shape else None,
            "from_anchor": self.from_anchor,
            "to_anchor": self.to_anchor
        })
        return data

    def load_properties(self, data: dict):
        self.angle = data.get("angle", 0)
        self.end_x = data.get("end_x", self.x + self.LENGTH)
        self.end_y = data.get("end_y", self.y)
        self.from_anchor = data.get("from_anchor", "bottom")
        self.to_anchor = data.get("to_anchor", "top")
