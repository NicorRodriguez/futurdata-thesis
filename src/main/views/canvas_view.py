import tkinter as tk
from tkinter import ttk
from typing import Optional, List, Tuple
import math

from ..models import Shape, ProductBox, ActionCircle, DiamondStep, ComponentBox, ArrowShape, Connection
from ..utils.geometry import get_arrow_points


class DiagramCanvas(tk.Canvas):
    GRID_SIZE = 50
    GRID_COLOR = "#e0e0e0"
    SELECT_COLOR = "#667eea"
    GUIDE_COLOR = "#ff6b6b"
    PRODUCT_FILL = "#90EE90"
    PRODUCT_TEXT_COLOR = "#00cc00"
    ACTION_FILL = "white"
    DIAMOND_FILL = "white"
    COMPONENT_FILL = "white"
    BORDER_COLOR = "black"

    def __init__(self, parent, **kwargs):
        kwargs.setdefault('bg', 'white')
        kwargs.setdefault('highlightthickness', 0)
        super().__init__(parent, **kwargs)
        self.config(scrollregion=(0, 0, 2000, 2000))
        self.show_grid = True
        self.snap_to_grid = True
        self.alignment_guides = {'vertical': [], 'horizontal': []}
        self.draw_grid()

    def draw_grid(self):
        if not self.show_grid:
            return
        x1, y1 = 0, 0
        x2, y2 = 2000, 2000
        self.delete("grid")
        for x in range(0, x2 + 1, self.GRID_SIZE):
            self.create_line(x, y1, x, y2, fill=self.GRID_COLOR, tags="grid")
        for y in range(0, y2 + 1, self.GRID_SIZE):
            self.create_line(x1, y, x2, y, fill=self.GRID_COLOR, tags="grid")
        self.tag_lower("grid")

    def draw_shape(self, shape: Shape) -> None:
        if shape.shape_id is not None:
            self.delete(shape.shape_id)
        if shape.text_id is not None:
            self.delete(shape.text_id)

        if isinstance(shape, ProductBox):
            self._draw_product_box(shape)
        elif isinstance(shape, ActionCircle):
            self._draw_action_circle(shape)
        elif isinstance(shape, DiamondStep):
            self._draw_diamond_step(shape)
        elif isinstance(shape, ComponentBox):
            self._draw_component_box(shape)
        elif isinstance(shape, ArrowShape):
            self._draw_arrow_shape(shape)

        if shape.selected:
            self._draw_selection(shape)

    def _draw_product_box(self, shape: ProductBox):
        x1, y1, x2, y2 = shape.get_bounds()
        border_width = 3 if shape.selected else 2
        border_color = self.SELECT_COLOR if shape.selected else self.BORDER_COLOR
        shape.shape_id = self.create_rectangle(
            x1, y1, x2, y2, fill=self.PRODUCT_FILL, outline=border_color, width=border_width, tags="shape"
        )
        shape.text_id = self.create_text(
            shape.x, shape.y, text=shape.text, font=("Arial", 10, "bold"), fill=self.PRODUCT_TEXT_COLOR, tags="shape_text"
        )

    def _draw_action_circle(self, shape: ActionCircle):
        x1, y1, x2, y2 = shape.get_bounds()
        border_width = 3 if shape.selected else 2
        border_color = self.SELECT_COLOR if shape.selected else self.BORDER_COLOR
        shape.shape_id = self.create_oval(
            x1, y1, x2, y2, fill=self.ACTION_FILL, outline=border_color, width=border_width, tags="shape"
        )
        shape.text_id = self.create_text(
            shape.x, shape.y, text=shape.text, font=("Arial", 9), fill="black", tags="shape_text"
        )

    def _draw_diamond_step(self, shape: DiamondStep):
        half = shape.SIZE / 2
        points = [
            shape.x, shape.y - half,
            shape.x + half, shape.y,
            shape.x, shape.y + half,
            shape.x - half, shape.y
        ]
        border_width = 3 if shape.selected else 2
        border_color = self.SELECT_COLOR if shape.selected else self.BORDER_COLOR
        shape.shape_id = self.create_polygon(
            points, fill=self.DIAMOND_FILL, outline=border_color, width=border_width, tags="shape"
        )
        shape.text_id = self.create_text(
            shape.x, shape.y, text=shape.text, font=("Arial", 8), fill="black", tags="shape_text"
        )

    def _draw_component_box(self, shape: ComponentBox):
        x1, y1, x2, y2 = shape.get_bounds()
        border_width = 3 if shape.selected else 2
        border_color = self.SELECT_COLOR if shape.selected else self.BORDER_COLOR
        shape.shape_id = self.create_rectangle(
            x1, y1, x2, y2, fill=self.COMPONENT_FILL, outline=border_color, width=border_width, tags="shape"
        )
        shape.text_id = self.create_text(
            shape.x, shape.y, text=shape.text, font=("Arial", 9), fill="black", tags="shape_text"
        )

    def _draw_arrow_shape(self, shape: ArrowShape):
        if shape.from_shape and shape.to_shape:
            shape.update_from_shapes()
        end_x = shape.end_x
        end_y = shape.end_y
        border_width = 3 if shape.selected else 2
        border_color = self.SELECT_COLOR if shape.selected else self.BORDER_COLOR
        shape.shape_id = self.create_line(
            shape.x, shape.y, end_x, end_y, fill=border_color, width=border_width,
            arrow=tk.LAST, arrowshape=(12, 15, 6), tags="shape"
        )
        shape.text_id = None

    def _draw_selection(self, shape: Shape):
        pass

    def draw_connection(self, connection: Connection) -> None:
        if connection.arrow_id is not None:
            self.delete(connection.arrow_id)
        (x1, y1), (x2, y2) = connection.get_endpoints()
        dash = (5, 5) if connection.connection_type == "dashed" else None
        connection.arrow_id = self.create_line(
            x1, y1, x2, y2, fill=self.BORDER_COLOR, width=2,
            arrow=tk.LAST, arrowshape=(10, 12, 5), dash=dash, tags="connection"
        )
        self.tag_lower("connection", "shape")

    def draw_alignment_guides(self, guides: dict):
        self.delete("guide")
        for x in guides.get('vertical', []):
            self.create_line(x, 0, x, 2000, fill=self.GUIDE_COLOR, width=1, dash=(4, 4), tags="guide")
        for y in guides.get('horizontal', []):
            self.create_line(0, y, 2000, y, fill=self.GUIDE_COLOR, width=1, dash=(4, 4), tags="guide")

    def clear_alignment_guides(self):
        self.delete("guide")

    def clear_canvas(self):
        self.delete("shape")
        self.delete("shape_text")
        self.delete("connection")
        self.delete("guide")

    def redraw_all(self, diagram):
        self.clear_canvas()
        for connection in diagram.connections:
            self.draw_connection(connection)
        for shape in diagram.shapes:
            self.draw_shape(shape)

    def update_shape(self, shape: Shape):
        self.draw_shape(shape)

    def update_connection(self, connection: Connection):
        self.draw_connection(connection)

    def toggle_grid(self):
        self.show_grid = not self.show_grid
        if self.show_grid:
            self.draw_grid()
        else:
            self.delete("grid")

    def zoom_in(self):
        pass

    def zoom_out(self):
        pass

    def reset_zoom(self):
        pass
