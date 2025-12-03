import tkinter as tk
from typing import Optional, Tuple
import os

from ..models import Diagram, ProductBox, ActionCircle, DiamondStep, ComponentBox, ArrowShape, Connection
from ..utils import (
    CommandHistory, AddShapeCommand, RemoveShapeCommand, MoveShapeCommand,
    AddConnectionCommand, EditShapePropertiesCommand, snap_to_grid,
    find_alignment_guides, DiagramSerializer
)


class AppController:

    def __init__(self):
        self.diagram = Diagram()
        self.command_history = CommandHistory()
        self.view = None
        self.selected_shape = None
        self.dragging = False
        self.drag_start = None
        self.drag_initial_positions = {}
        self.drag_shapes = []
        self.connect_mode = False
        self.arrow_mode = False
        self.connecting_from = None
        self.preview_line_id = None

    def set_view(self, view):
        self.view = view
        self._bind_canvas_events()

    def _bind_canvas_events(self):
        canvas = self.view.canvas
        canvas.bind("<Button-1>", self.on_canvas_click)
        canvas.bind("<B1-Motion>", self.on_canvas_drag)
        canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        canvas.bind("<Button-3>", self.on_canvas_right_click)
        canvas.bind("<Motion>", self.on_canvas_motion)
        canvas.bind("<Escape>", self.on_escape)
        canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        canvas.bind("<Button-4>", self.on_mouse_wheel)
        canvas.bind("<Button-5>", self.on_mouse_wheel)
        canvas.bind("<Shift-MouseWheel>", self.on_shift_mouse_wheel)

    def on_mouse_wheel(self, event):
        if event.num == 4:
            self.view.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.view.canvas.yview_scroll(1, "units")
        else:
            self.view.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def on_shift_mouse_wheel(self, event):
        self.view.canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

    def on_canvas_motion(self, event):
        """Show preview line when in arrow/connect mode and have a starting shape."""
        if (self.arrow_mode or self.connect_mode) and self.connecting_from is not None:
            x = self.view.canvas.canvasx(event.x)
            y = self.view.canvas.canvasy(event.y)
            # Draw preview line from connecting_from shape to mouse cursor
            self._update_preview_line(self.connecting_from.x, self.connecting_from.y, x, y)

    def _update_preview_line(self, x1, y1, x2, y2):
        """Draw or update the preview line for arrow/connection."""
        canvas = self.view.canvas
        if self.preview_line_id is not None:
            canvas.delete(self.preview_line_id)
        self.preview_line_id = canvas.create_line(
            x1, y1, x2, y2,
            fill="black", width=2, dash=(5, 5),
            arrow=tk.LAST, arrowshape=(12, 15, 6),
            tags="preview"
        )

    def _clear_preview_line(self):
        """Remove the preview line."""
        if self.preview_line_id is not None:
            self.view.canvas.delete(self.preview_line_id)
            self.preview_line_id = None

    def on_escape(self, event):
        """Cancel arrow/connect mode."""
        if self.arrow_mode or self.connect_mode:
            self._clear_preview_line()
            self.arrow_mode = False
            self.connect_mode = False
            self.connecting_from = None
            self.view.set_status("Cancelled")

    def on_canvas_click(self, event):
        x = self.view.canvas.canvasx(event.x)
        y = self.view.canvas.canvasy(event.y)
        clicked_shape = self.diagram.find_shape_at_point(x, y)

        if self.arrow_mode:
            if clicked_shape:
                self._handle_arrow_connection_click(clicked_shape)
            return

        if self.connect_mode:
            if clicked_shape:
                self._handle_connection_click(clicked_shape)
            return

        multi_select = event.state & 0x0004

        if clicked_shape:
            self.diagram.select_shape(clicked_shape, multi_select=multi_select)
            self.dragging = True
            self.drag_start = (x, y)
            self.drag_shapes = list(self.diagram.selected_shapes)
            self.drag_initial_positions = {shape: (shape.x, shape.y) for shape in self.drag_shapes}
        else:
            if not multi_select:
                self.diagram.clear_selection()

        self._update_view()

    def on_canvas_drag(self, event):
        if not self.dragging or not self.drag_shapes:
            return

        self._auto_scroll_viewport(event.x, event.y)

        x = self.view.canvas.canvasx(event.x)
        y = self.view.canvas.canvasy(event.y)
        dx = x - self.drag_start[0]
        dy = y - self.drag_start[1]

        # Move each shape freely during drag (no snapping)
        for shape in self.drag_shapes:
            shape.x += dx
            shape.y += dy
            # Fast move - just moves existing canvas items
            self.view.canvas.move_items(shape, dx, dy)
            # Expand canvas if needed
            self.view.canvas.expand_canvas_if_needed(shape.x, shape.y)

        self.drag_start = (x, y)

        # Update connections attached to dragged shapes
        self.view.canvas.update_connections_for_shapes(self.drag_shapes, self.diagram)

        if len(self.drag_shapes) == 1:
            guides = find_alignment_guides(
                self.drag_shapes[0],
                [s for s in self.diagram.shapes if s not in self.drag_shapes]
            )
            self.view.canvas.draw_alignment_guides(guides)

    def _auto_scroll_viewport(self, mouse_x: int, mouse_y: int):
        """Scroll the canvas when mouse is near the edge of visible area."""
        canvas = self.view.canvas
        margin = 50  # Distance from edge to trigger scroll

        visible_width = canvas.winfo_width()
        visible_height = canvas.winfo_height()

        # Scroll right
        if mouse_x > visible_width - margin:
            canvas.xview_scroll(3, "units")
        # Scroll left
        elif mouse_x < margin:
            canvas.xview_scroll(-3, "units")

        # Scroll down
        if mouse_y > visible_height - margin:
            canvas.yview_scroll(3, "units")
        # Scroll up
        elif mouse_y < margin:
            canvas.yview_scroll(-3, "units")

    def on_canvas_release(self, event):
        if self.dragging and self.drag_shapes and self.drag_initial_positions:
            # Snap to grid on release if enabled
            if self.diagram.snap_to_grid:
                for shape in self.drag_shapes:
                    shape.x, shape.y = snap_to_grid(shape.x, shape.y)

            first_shape = self.drag_shapes[0]
            initial_pos = self.drag_initial_positions[first_shape]
            dx = first_shape.x - initial_pos[0]
            dy = first_shape.y - initial_pos[1]

            if abs(dx) > 1 or abs(dy) > 1:
                command = MoveShapeCommand(self.drag_shapes, dx, dy)
                self.command_history.history.append(command)
                self.command_history.current_index += 1

        self.dragging = False
        self.drag_start = None
        self.drag_shapes = []
        self.drag_initial_positions = {}
        self.view.canvas.clear_alignment_guides()
        # Redraw grid to cover expanded canvas area
        self.view.canvas.draw_grid()
        # Full redraw to sync canvas with snapped positions
        self.view.canvas.redraw_all(self.diagram)
        self._update_view()

    def on_canvas_right_click(self, event):
        x = self.view.canvas.canvasx(event.x)
        y = self.view.canvas.canvasy(event.y)
        clicked_shape = self.diagram.find_shape_at_point(x, y)

        if clicked_shape:
            if self.arrow_mode or self.connect_mode:
                self._clear_preview_line()
                self.arrow_mode = False
                self.connect_mode = False
                self.connecting_from = None
            self._show_context_menu(event, clicked_shape)

    def _show_context_menu(self, event, shape):
        menu = tk.Menu(self.view.root, tearoff=0)
        menu.add_command(label="Edit Properties", command=lambda: self._edit_shape_properties(shape))
        menu.add_separator()
        menu.add_command(label="Duplicate", command=lambda: self._duplicate_shape(shape))
        menu.add_command(label="Delete", command=lambda: self._delete_shape(shape))
        menu.add_separator()
        menu.add_command(label="Connect to...", command=lambda: self._start_connection_from(shape))
        menu.post(event.x_root, event.y_root)

    def _handle_arrow_connection_click(self, shape):
        # Also select the shape so Delete key works
        self.diagram.select_shape(shape, multi_select=False)
        self._update_view()

        if self.connecting_from is None:
            self.connecting_from = shape
            # Draw initial preview line from shape center (draw AFTER update_view)
            self._update_preview_line(shape.x, shape.y, shape.x + 100, shape.y)
            self.view.set_status(f"Arrow started from {shape.shape_type}. Click target shape or press Delete to remove.")
        else:
            self._clear_preview_line()
            if self.connecting_from != shape:
                self._create_arrow_connection(self.connecting_from, shape)
                self.view.set_status("Arrow created.")
            else:
                self.view.set_status("Cancelled - same shape.")
            self.connecting_from = None
            self.arrow_mode = False
            self._update_view()

    def _handle_connection_click(self, shape):
        if self.connecting_from is None:
            self.connecting_from = shape
            self.view.set_status(f"Connection started from {shape.shape_type}. Click target shape.")
        else:
            self._clear_preview_line()
            if self.connecting_from != shape:
                self._create_connection(self.connecting_from, shape)
                self.view.set_status("Connection created.")
            else:
                self.view.set_status("Cancelled - same shape.")
            self.connecting_from = None
            self.connect_mode = False

    def _create_arrow_connection(self, from_shape, to_shape):
        arrow = ArrowShape(0, 0, from_shape, to_shape)
        arrow.update_from_shapes()
        command = AddShapeCommand(self.diagram, arrow)
        self.command_history.execute(command)
        self._update_view()

    def _create_connection(self, from_shape, to_shape):
        connection = Connection(from_shape, to_shape)
        connection.auto_calculate_anchors()
        command = AddConnectionCommand(self.diagram, connection)
        self.command_history.execute(command)
        self._update_view()

    def _edit_shape_properties(self, shape):
        self.diagram.select_shape(shape, multi_select=False)
        self._update_view()

    def _duplicate_shape(self, shape):
        new_shape = self._create_shape_instance(shape.shape_type, shape.x + 50, shape.y + 50)
        new_shape.text = shape.text

        if isinstance(shape, ProductBox):
            new_shape.brand = shape.brand
            new_shape.model = shape.model
        elif isinstance(shape, ActionCircle):
            new_shape.action_id = shape.action_id
            new_shape.name = shape.name
            new_shape.tools = shape.tools
        elif isinstance(shape, DiamondStep):
            new_shape.step_description = shape.step_description
            new_shape.image_path = shape.image_path
        elif isinstance(shape, ComponentBox):
            new_shape.component_name = shape.component_name
            new_shape.color = shape.color
            new_shape.material = shape.material
            new_shape.weight = shape.weight

        command = AddShapeCommand(self.diagram, new_shape)
        self.command_history.execute(command)
        self._update_view()
        self.view.set_status(f"Duplicated {shape.shape_type}")

    def _delete_shape(self, shape):
        command = RemoveShapeCommand(self.diagram, shape)
        self.command_history.execute(command)
        self._update_view()
        self.view.set_status(f"Deleted {shape.shape_type}")

    def _start_connection_from(self, shape):
        self.connect_mode = True
        self.connecting_from = shape
        self.view.set_status(f"Connection started from {shape.shape_type}. Click target shape.")

    def add_shape(self, shape_type: str):
        if shape_type == "arrow":
            self.arrow_mode = True
            self.connecting_from = None
            self.view.set_status("Arrow mode: Click on a shape to start")
            return

        x, y = 700, 400
        shape = self._create_shape_instance(shape_type, x, y)
        command = AddShapeCommand(self.diagram, shape)
        self.command_history.execute(command)
        self.diagram.select_shape(shape, multi_select=False)
        self._update_view()
        self.view.set_status(f"Added {shape_type}")

    def _create_shape_instance(self, shape_type: str, x: float, y: float):
        if shape_type == "product":
            return ProductBox(x, y)
        elif shape_type == "action":
            return ActionCircle(x, y)
        elif shape_type == "diamond":
            return DiamondStep(x, y)
        elif shape_type == "component":
            return ComponentBox(x, y)
        elif shape_type == "arrow":
            return ArrowShape(x, y)
        else:
            raise ValueError(f"Unknown shape type: {shape_type}")

    def delete_selected(self):
        if not self.diagram.selected_shapes:
            self.view.set_status("No shapes selected")
            return

        if self.arrow_mode or self.connect_mode:
            self._clear_preview_line()
            self.arrow_mode = False
            self.connect_mode = False
            self.connecting_from = None

        for shape in list(self.diagram.selected_shapes):
            command = RemoveShapeCommand(self.diagram, shape)
            self.command_history.execute(command)

        self._update_view()
        self.view.set_status("Deleted selected shapes")

    def select_all(self):
        for shape in self.diagram.shapes:
            self.diagram.select_shape(shape, multi_select=True)
        self._update_view()
        self.view.set_status(f"Selected {len(self.diagram.shapes)} shapes")

    def toggle_connect_mode(self):
        self.connect_mode = not self.connect_mode
        self.connecting_from = None

        if self.connect_mode:
            self.view.set_status("Connection mode: Click source shape, then target shape")
        else:
            self.view.set_status("Connection mode disabled")

    def apply_properties(self, shape, old_properties, new_properties):
        command = EditShapePropertiesCommand(shape, old_properties, new_properties)
        self.command_history.execute(command)
        self._update_view()
        self.view.set_status("Properties updated")

    def undo(self):
        if self.command_history.undo():
            self._update_view()
            self.view.set_status(f"Undone: {self.command_history.get_redo_description()}")
        else:
            self.view.set_status("Nothing to undo")

    def redo(self):
        if self.command_history.redo():
            self._update_view()
            self.view.set_status(f"Redone: {self.command_history.get_undo_description()}")
        else:
            self.view.set_status("Nothing to redo")

    def can_undo(self) -> bool:
        return self.command_history.can_undo()

    def can_redo(self) -> bool:
        return self.command_history.can_redo()

    def toggle_grid(self):
        self.view.canvas.toggle_grid()
        self.view.set_status(f"Grid: {'on' if self.view.canvas.show_grid else 'off'}")

    def toggle_snap(self):
        self.diagram.snap_to_grid = not self.diagram.snap_to_grid
        self.view.set_status(f"Snap to grid: {'on' if self.diagram.snap_to_grid else 'off'}")

    def zoom_in(self):
        self.view.set_status("Zoom in (not yet implemented)")

    def zoom_out(self):
        self.view.set_status("Zoom out (not yet implemented)")

    def reset_zoom(self):
        self.view.set_status("Reset zoom (not yet implemented)")

    def new_diagram(self):
        if not self.check_unsaved_changes():
            return
        self.diagram.clear()
        self.command_history.clear()
        # Reset canvas to minimum size
        self.view.canvas.update_scroll_region_from_shapes([])
        self._update_view()
        self.view.set_status("New diagram created")

    def open_diagram(self):
        if not self.check_unsaved_changes():
            return

        file_path = self.view.ask_file_path(save=False)
        if not file_path:
            return

        diagram = DiagramSerializer.load_from_file(file_path)
        if diagram:
            self.diagram = diagram
            self.command_history.clear()
            # Update canvas scroll region to fit loaded shapes
            self.view.canvas.update_scroll_region_from_shapes(self.diagram.shapes)
            self._update_view()
            self.view.set_status(f"Opened: {os.path.basename(file_path)}")
        else:
            self.view.show_error("Error", "Failed to open file")

    def save_diagram(self):
        if self.diagram.file_path is None:
            return self.save_diagram_as()

        if DiagramSerializer.save_to_file(self.diagram, self.diagram.file_path):
            self.view.set_status(f"Saved: {os.path.basename(self.diagram.file_path)}")
            return True
        else:
            self.view.show_error("Error", "Failed to save file")
            return False

    def save_diagram_as(self):
        file_path = self.view.ask_file_path(save=True)
        if not file_path:
            return False

        self.diagram.file_path = file_path

        if DiagramSerializer.save_to_file(self.diagram, file_path):
            self.view.set_status(f"Saved as: {os.path.basename(file_path)}")
            return True
        else:
            self.view.show_error("Error", "Failed to save file")
            return False

    def clear_canvas(self):
        if not self.diagram.shapes:
            self.view.set_status("Canvas is already empty")
            return

        from tkinter import messagebox
        if not messagebox.askyesno("Clear Canvas", "Are you sure you want to clear the canvas?"):
            return

        self.diagram.clear()
        self.command_history.clear()
        # Reset canvas to minimum size
        self.view.canvas.update_scroll_region_from_shapes([])
        self._update_view()
        self.view.set_status("Canvas cleared")

    def check_unsaved_changes(self) -> bool:
        if not self.diagram.modified:
            return True

        result = self.view.ask_save_changes()

        if result == 'save':
            return self.save_diagram()
        elif result == 'discard':
            return True
        else:
            return False

    def _update_view(self):
        self.view.canvas.redraw_all(self.diagram)

        if len(self.diagram.selected_shapes) == 1:
            self.view.update_properties_panel(self.diagram.selected_shapes[0])
        else:
            self.view.update_properties_panel(None)

        self.view.update_ui_state()
