import tkinter as tk
from tkinter import ttk, colorchooser
from typing import Optional, Callable

from ..models import Shape, ProductBox, ActionCircle, DiamondStep, ComponentBox


class PropertiesPanel(ttk.Frame):
    def __init__(self, parent, on_apply_callback: Optional[Callable] = None):
        super().__init__(parent, padding=10)
        self.on_apply_callback = on_apply_callback
        self.current_shape: Optional[Shape] = None
        self._create_widgets()

    def _create_widgets(self):
        title = ttk.Label(self, text="Properties", font=("Arial", 12, "bold"))
        title.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        ttk.Label(self, text="Shape ID:").grid(row=1, column=0, sticky="w", pady=2)
        self.id_label = ttk.Label(self, text="-", foreground="gray")
        self.id_label.grid(row=1, column=1, sticky="w", pady=2)

        ttk.Label(self, text="Type:").grid(row=2, column=0, sticky="w", pady=2)
        self.type_label = ttk.Label(self, text="-", foreground="gray")
        self.type_label.grid(row=2, column=1, sticky="w", pady=2)

        ttk.Separator(self, orient="horizontal").grid(row=3, column=0, columnspan=2, sticky="ew", pady=10)

        ttk.Label(self, text="Text:").grid(row=4, column=0, sticky="nw", pady=2)
        text_frame = ttk.Frame(self)
        text_frame.grid(row=4, column=1, sticky="ew", pady=2)

        self.text_entry = tk.Text(text_frame, height=4, width=25, font=("Arial", 9))
        self.text_entry.pack(side="left", fill="both", expand=True)

        text_scroll = ttk.Scrollbar(text_frame, command=self.text_entry.yview)
        text_scroll.pack(side="right", fill="y")
        self.text_entry.config(yscrollcommand=text_scroll.set)

        self.product_frame = ttk.LabelFrame(self, text="Product Info", padding=5)
        ttk.Label(self.product_frame, text="Brand:").grid(row=0, column=0, sticky="w", pady=2)
        self.brand_entry = ttk.Entry(self.product_frame, width=25)
        self.brand_entry.grid(row=0, column=1, sticky="ew", pady=2)
        ttk.Label(self.product_frame, text="Model:").grid(row=1, column=0, sticky="w", pady=2)
        self.model_entry = ttk.Entry(self.product_frame, width=25)
        self.model_entry.grid(row=1, column=1, sticky="ew", pady=2)

        self.action_frame = ttk.LabelFrame(self, text="Action Info", padding=5)
        ttk.Label(self.action_frame, text="Action ID:").grid(row=0, column=0, sticky="w", pady=2)
        self.action_id_entry = ttk.Entry(self.action_frame, width=25)
        self.action_id_entry.grid(row=0, column=1, sticky="ew", pady=2)
        ttk.Label(self.action_frame, text="Name:").grid(row=1, column=0, sticky="w", pady=2)
        self.action_name_entry = ttk.Entry(self.action_frame, width=25)
        self.action_name_entry.grid(row=1, column=1, sticky="ew", pady=2)
        ttk.Label(self.action_frame, text="Tools:").grid(row=2, column=0, sticky="w", pady=2)
        self.tools_entry = ttk.Entry(self.action_frame, width=25)
        self.tools_entry.grid(row=2, column=1, sticky="ew", pady=2)

        self.diamond_frame = ttk.LabelFrame(self, text="Step Info", padding=5)
        ttk.Label(self.diamond_frame, text="Description:").grid(row=0, column=0, sticky="w", pady=2)
        self.step_desc_entry = ttk.Entry(self.diamond_frame, width=25)
        self.step_desc_entry.grid(row=0, column=1, sticky="ew", pady=2)
        ttk.Label(self.diamond_frame, text="Image Path:").grid(row=1, column=0, sticky="w", pady=2)
        image_frame = ttk.Frame(self.diamond_frame)
        image_frame.grid(row=1, column=1, sticky="ew", pady=2)
        self.image_path_entry = ttk.Entry(image_frame)
        self.image_path_entry.pack(side="left", fill="x", expand=True)
        ttk.Button(image_frame, text="Browse...", width=8).pack(side="right")

        self.component_frame = ttk.LabelFrame(self, text="Component Info", padding=5)
        ttk.Label(self.component_frame, text="Name:").grid(row=0, column=0, sticky="w", pady=2)
        self.component_name_entry = ttk.Entry(self.component_frame, width=25)
        self.component_name_entry.grid(row=0, column=1, sticky="ew", pady=2)
        ttk.Label(self.component_frame, text="Color:").grid(row=1, column=0, sticky="w", pady=2)
        color_frame = ttk.Frame(self.component_frame)
        color_frame.grid(row=1, column=1, sticky="ew", pady=2)
        self.color_entry = ttk.Entry(color_frame)
        self.color_entry.pack(side="left", fill="x", expand=True)
        self.color_button = ttk.Button(color_frame, text="🎨", width=3, command=self._choose_color)
        self.color_button.pack(side="right")
        ttk.Label(self.component_frame, text="Material:").grid(row=2, column=0, sticky="w", pady=2)
        self.material_combo = ttk.Combobox(
            self.component_frame,
            values=["Plastic", "Metal", "PCB", "Rubber", "Glass", "Composite", "Other"],
            width=22
        )
        self.material_combo.grid(row=2, column=1, sticky="ew", pady=2)
        ttk.Label(self.component_frame, text="Weight:").grid(row=3, column=0, sticky="w", pady=2)
        weight_frame = ttk.Frame(self.component_frame)
        weight_frame.grid(row=3, column=1, sticky="ew", pady=2)
        self.weight_entry = ttk.Entry(weight_frame, width=15)
        self.weight_entry.pack(side="left")
        ttk.Label(weight_frame, text="g").pack(side="left", padx=2)

        self.apply_button = ttk.Button(self, text="Apply Changes", command=self._on_apply)

        self.empty_label = ttk.Label(
            self, text="Select a shape to\nedit its properties", foreground="gray", justify="center"
        )

        self._show_empty_state()

    def _show_empty_state(self):
        self.product_frame.grid_remove()
        self.action_frame.grid_remove()
        self.diamond_frame.grid_remove()
        self.component_frame.grid_remove()
        self.apply_button.grid_remove()
        self.empty_label.grid(row=5, column=0, columnspan=2, pady=20)

    def load_shape(self, shape: Optional[Shape]):
        self.current_shape = shape

        if shape is None:
            self._show_empty_state()
            self.id_label.config(text="-")
            self.type_label.config(text="-")
            return

        self.empty_label.grid_remove()
        self.apply_button.grid(row=10, column=0, columnspan=2, pady=10, sticky="ew")

        self.id_label.config(text=f"#{shape.id}")
        self.type_label.config(text=shape.shape_type.capitalize())

        self.text_entry.delete("1.0", "end")
        self.text_entry.insert("1.0", shape.text)

        self.product_frame.grid_remove()
        self.action_frame.grid_remove()
        self.diamond_frame.grid_remove()
        self.component_frame.grid_remove()

        if isinstance(shape, ProductBox):
            self.product_frame.grid(row=5, column=0, columnspan=2, sticky="ew", pady=5)
            self.brand_entry.delete(0, "end")
            self.brand_entry.insert(0, shape.brand)
            self.model_entry.delete(0, "end")
            self.model_entry.insert(0, shape.model)
        elif isinstance(shape, ActionCircle):
            self.action_frame.grid(row=5, column=0, columnspan=2, sticky="ew", pady=5)
            self.action_id_entry.delete(0, "end")
            self.action_id_entry.insert(0, shape.action_id)
            self.action_name_entry.delete(0, "end")
            self.action_name_entry.insert(0, shape.name)
            self.tools_entry.delete(0, "end")
            self.tools_entry.insert(0, shape.tools)
        elif isinstance(shape, DiamondStep):
            self.diamond_frame.grid(row=5, column=0, columnspan=2, sticky="ew", pady=5)
            self.step_desc_entry.delete(0, "end")
            self.step_desc_entry.insert(0, shape.step_description)
            self.image_path_entry.delete(0, "end")
            self.image_path_entry.insert(0, shape.image_path)
        elif isinstance(shape, ComponentBox):
            self.component_frame.grid(row=5, column=0, columnspan=2, sticky="ew", pady=5)
            self.component_name_entry.delete(0, "end")
            self.component_name_entry.insert(0, shape.component_name)
            self.color_entry.delete(0, "end")
            self.color_entry.insert(0, shape.color)
            self.material_combo.set(shape.material)
            self.weight_entry.delete(0, "end")
            self.weight_entry.insert(0, shape.weight)

    def _on_apply(self):
        if self.current_shape is None:
            return
        old_properties = self._get_current_properties()
        self._update_shape_properties()
        new_properties = self._get_current_properties()
        if self.on_apply_callback:
            self.on_apply_callback(self.current_shape, old_properties, new_properties)

    def _get_current_properties(self) -> dict:
        if self.current_shape is None:
            return {}
        properties = {"text": self.current_shape.text}
        if isinstance(self.current_shape, ProductBox):
            properties.update({"brand": self.current_shape.brand, "model": self.current_shape.model})
        elif isinstance(self.current_shape, ActionCircle):
            properties.update({
                "action_id": self.current_shape.action_id,
                "name": self.current_shape.name,
                "tools": self.current_shape.tools
            })
        elif isinstance(self.current_shape, DiamondStep):
            properties.update({
                "step_description": self.current_shape.step_description,
                "image_path": self.current_shape.image_path
            })
        elif isinstance(self.current_shape, ComponentBox):
            properties.update({
                "component_name": self.current_shape.component_name,
                "color": self.current_shape.color,
                "material": self.current_shape.material,
                "weight": self.current_shape.weight
            })
        return properties

    def _update_shape_properties(self):
        if self.current_shape is None:
            return
        self.current_shape.text = self.text_entry.get("1.0", "end-1c")
        if isinstance(self.current_shape, ProductBox):
            self.current_shape.brand = self.brand_entry.get()
            self.current_shape.model = self.model_entry.get()
        elif isinstance(self.current_shape, ActionCircle):
            self.current_shape.action_id = self.action_id_entry.get()
            self.current_shape.name = self.action_name_entry.get()
            self.current_shape.tools = self.tools_entry.get()
        elif isinstance(self.current_shape, DiamondStep):
            self.current_shape.step_description = self.step_desc_entry.get()
            self.current_shape.image_path = self.image_path_entry.get()
        elif isinstance(self.current_shape, ComponentBox):
            self.current_shape.component_name = self.component_name_entry.get()
            self.current_shape.color = self.color_entry.get()
            self.current_shape.material = self.material_combo.get()
            self.current_shape.weight = self.weight_entry.get()

    def _choose_color(self):
        color = colorchooser.askcolor(title="Choose Color")
        if color[1]:
            self.color_entry.delete(0, "end")
            self.color_entry.insert(0, color[1])

    def clear(self):
        self.load_shape(None)
