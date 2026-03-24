import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional

from .canvas_view import DiagramCanvas
from .properties_panel import PropertiesPanel
from ..models import ActionCircle, DiamondStep, ComponentBox, ArrowShape


class MainWindow:
    def __init__(self, root: tk.Tk, controller):
        self.root = root
        self.controller = controller
        self.root.title("Disassembly Flow Diagram Builder")
        self.root.geometry("1400x800")
        self.root.minsize(1000, 600)

        self._create_menu()
        self._create_toolbar()
        self._create_main_area()
        self._create_status_bar()
        self._bind_shortcuts()
        self.update_ui_state()

    def _create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", accelerator="Ctrl+N", command=self.controller.new_diagram)
        file_menu.add_command(label="Open...", accelerator="Ctrl+O", command=self.controller.open_diagram)
        file_menu.add_command(label="Save", accelerator="Ctrl+S", command=self.controller.save_diagram)
        file_menu.add_command(label="Save As...", accelerator="Ctrl+Shift+S", command=self.controller.save_diagram_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_exit)

        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", accelerator="Ctrl+Z", command=self.controller.undo)
        edit_menu.add_command(label="Redo", accelerator="Ctrl+Y", command=self.controller.redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="Delete", accelerator="Del", command=self.controller.delete_selected)
        edit_menu.add_command(label="Select All", accelerator="Ctrl+A", command=self.controller.select_all)
        edit_menu.add_separator()
        edit_menu.add_command(label="Add Color...", command=self.controller.show_add_color_dialog)
        edit_menu.add_command(label="Add Material...", command=self.controller.show_add_material_dialog)
        edit_menu.add_separator()
        edit_menu.add_command(label="Clear Canvas", command=self.controller.clear_canvas)

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def _create_toolbar(self):
        toolbar = ttk.Frame(self.root, relief="raised", padding=5)
        toolbar.pack(side="top", fill="x")

        ttk.Button(toolbar, text="New", width=8, command=self.controller.new_diagram).pack(side="left", padx=2)
        ttk.Button(toolbar, text="Open", width=8, command=self.controller.open_diagram).pack(side="left", padx=2)
        ttk.Button(toolbar, text="Save", width=8, command=self.controller.save_diagram).pack(side="left", padx=2)

        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=5)

        self.undo_button = ttk.Button(toolbar, text="Undo", width=8, command=self.controller.undo)
        self.undo_button.pack(side="left", padx=2)
        self.redo_button = ttk.Button(toolbar, text="Redo", width=8, command=self.controller.redo)
        self.redo_button.pack(side="left", padx=2)

        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=5)

        ttk.Button(toolbar, text="Delete", width=8, command=self.controller.delete_selected).pack(side="left", padx=2)

        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=5)

        ttk.Button(toolbar, text="Clear", width=8, command=self.controller.clear_canvas).pack(side="left", padx=2)

    def _create_main_area(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(side="top", fill="both", expand=True)

        palette_frame = ttk.LabelFrame(main_frame, text="Shape Palette", padding=10, width=150)
        palette_frame.pack(side="left", fill="y", padx=(5, 0), pady=5)
        palette_frame.pack_propagate(False)

        ttk.Label(palette_frame, text="Click to add:").pack(anchor="w", pady=(0, 10))
        ttk.Button(palette_frame, text="▭ Root Component", command=lambda: self.controller.add_shape("component_root")).pack(fill="x", pady=2)
        ttk.Button(palette_frame, text="▭ Leaf Component", command=lambda: self.controller.add_shape("component_leaf")).pack(fill="x", pady=2)
        ttk.Button(palette_frame, text="▭ Composite Comp.", command=lambda: self.controller.add_shape("component_composite")).pack(fill="x", pady=2)
        ttk.Button(palette_frame, text="○ Action Circle", command=lambda: self.controller.add_shape("action")).pack(fill="x", pady=2)
        ttk.Button(palette_frame, text="◇ Diamond Step", command=lambda: self.controller.add_shape("diamond")).pack(fill="x", pady=2)
        ttk.Button(palette_frame, text="→ Arrow", command=lambda: self.controller.add_shape("arrow")).pack(fill="x", pady=2)

        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.canvas = DiagramCanvas(canvas_frame, bg="white")
        self.canvas.pack(side="left", fill="both", expand=True)

        v_scroll = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        v_scroll.pack(side="right", fill="y")
        self.canvas.config(yscrollcommand=v_scroll.set)

        h_scroll = ttk.Scrollbar(self.root, orient="horizontal", command=self.canvas.xview)
        h_scroll.pack(side="bottom", fill="x", before=canvas_frame)
        self.canvas.config(xscrollcommand=h_scroll.set)

        self.properties_panel = PropertiesPanel(main_frame, on_apply_callback=self.controller.apply_properties)
        self.properties_panel.pack(side="right", fill="y", padx=(0, 5), pady=5)

    def _create_status_bar(self):
        self.status_bar = ttk.Frame(self.root, relief="sunken")
        self.status_bar.pack(side="bottom", fill="x")

        self.status_label = ttk.Label(self.status_bar, text="Ready", padding=(5, 2))
        self.status_label.pack(side="left")

        self.shape_count_label = ttk.Label(self.status_bar, text="Shapes: 0", padding=(5, 2))
        self.shape_count_label.pack(side="right")

    def _bind_shortcuts(self):
        self.root.bind('<Control-n>', lambda e: self.controller.new_diagram())
        self.root.bind('<Control-o>', lambda e: self.controller.open_diagram())
        self.root.bind('<Control-s>', lambda e: self.controller.save_diagram())
        self.root.bind('<Control-Shift-S>', lambda e: self.controller.save_diagram_as())
        self.root.bind('<Control-z>', lambda e: self.controller.undo())
        self.root.bind('<Control-y>', lambda e: self.controller.redo())
        self.root.bind('<Delete>', lambda e: self.controller.delete_selected())
        self.root.bind('<Control-a>', lambda e: self.controller.select_all())
        self.root.bind('<Control-plus>', lambda e: self.controller.zoom_in())
        self.root.bind('<Control-minus>', lambda e: self.controller.zoom_out())
        self.root.bind('<Control-0>', lambda e: self.controller.reset_zoom())
        self.root.bind('c', lambda e: self.controller.toggle_connect_mode())
        self.root.bind('<Escape>', lambda e: self.controller.on_escape(e))
        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)

    def update_ui_state(self):
        can_undo = self.controller.can_undo()
        can_redo = self.controller.can_redo()
        self.undo_button.config(state="normal" if can_undo else "disabled")
        self.redo_button.config(state="normal" if can_redo else "disabled")
        shape_count = len(self.controller.diagram.shapes)
        self.shape_count_label.config(text=f"Shapes: {shape_count}")

    def set_status(self, message: str):
        self.status_label.config(text=message)

    def update_properties_panel(self, shape=None):
        self.properties_panel.load_shape(shape)

    def refresh_properties_panel(self):
        self.properties_panel.refresh()

    def show_about(self):
        messagebox.showinfo(
            "About",
            "Disassembly Flow Diagram Builder\n\n"
            "Version 1.0\n\n"
            "A visual tool for creating disassembly flow diagrams\n"
            "for product documentation and analysis.\n\n"
            "Created as part of a thesis project."
        )

    def on_exit(self):
        if self.controller.check_unsaved_changes():
            self.root.quit()

    def ask_save_changes(self) -> Optional[str]:
        result = messagebox.askyesnocancel("Unsaved Changes", "You have unsaved changes. Do you want to save them?")
        if result is True:
            return 'save'
        elif result is False:
            return 'discard'
        else:
            return 'cancel'

    def ask_file_path(self, save=True, file_types=None) -> Optional[str]:
        if file_types is None:
            file_types = [("JSON files", "*.json"), ("All files", "*.*")]
        if save:
            return filedialog.asksaveasfilename(defaultextension=".json", filetypes=file_types)
        else:
            return filedialog.askopenfilename(filetypes=file_types)

    def show_error(self, title: str, message: str):
        messagebox.showerror(title, message)

    def show_info(self, title: str, message: str):
        messagebox.showinfo(title, message)
