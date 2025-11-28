from typing import List, Any


class Command:
    def execute(self):
        raise NotImplementedError()

    def undo(self):
        raise NotImplementedError()

    def get_description(self) -> str:
        return "Command"


class CommandHistory:
    def __init__(self, max_history: int = 100):
        self.history: List[Command] = []
        self.current_index = -1
        self.max_history = max_history

    def execute(self, command: Command):
        command.execute()
        self.history = self.history[:self.current_index + 1]
        self.history.append(command)
        self.current_index += 1
        if len(self.history) > self.max_history:
            self.history.pop(0)
            self.current_index -= 1

    def undo(self) -> bool:
        if not self.can_undo():
            return False
        command = self.history[self.current_index]
        command.undo()
        self.current_index -= 1
        return True

    def redo(self) -> bool:
        if not self.can_redo():
            return False
        self.current_index += 1
        command = self.history[self.current_index]
        command.execute()
        return True

    def can_undo(self) -> bool:
        return self.current_index >= 0

    def can_redo(self) -> bool:
        return self.current_index < len(self.history) - 1

    def clear(self):
        self.history.clear()
        self.current_index = -1

    def get_undo_description(self) -> str:
        if self.can_undo():
            return self.history[self.current_index].get_description()
        return ""

    def get_redo_description(self) -> str:
        if self.can_redo():
            return self.history[self.current_index + 1].get_description()
        return ""


class AddShapeCommand(Command):
    def __init__(self, diagram, shape):
        self.diagram = diagram
        self.shape = shape

    def execute(self):
        self.diagram.add_shape(self.shape)

    def undo(self):
        self.diagram.remove_shape(self.shape)

    def get_description(self) -> str:
        return f"Add {self.shape.shape_type}"


class RemoveShapeCommand(Command):
    def __init__(self, diagram, shape):
        self.diagram = diagram
        self.shape = shape
        self.removed_connections = []

    def execute(self):
        self.removed_connections = self.diagram.get_connections_for_shape(self.shape)
        self.diagram.remove_shape(self.shape)

    def undo(self):
        self.diagram.add_shape(self.shape)
        for conn in self.removed_connections:
            self.diagram.add_connection(conn)

    def get_description(self) -> str:
        return f"Remove {self.shape.shape_type}"


class MoveShapeCommand(Command):
    def __init__(self, shapes, dx, dy):
        self.shapes = shapes if isinstance(shapes, list) else [shapes]
        self.dx = dx
        self.dy = dy

    def execute(self):
        for shape in self.shapes:
            shape.move(self.dx, self.dy)

    def undo(self):
        for shape in self.shapes:
            shape.move(-self.dx, -self.dy)

    def get_description(self) -> str:
        if len(self.shapes) == 1:
            return f"Move {self.shapes[0].shape_type}"
        return f"Move {len(self.shapes)} shapes"


class AddConnectionCommand(Command):
    def __init__(self, diagram, connection):
        self.diagram = diagram
        self.connection = connection

    def execute(self):
        self.diagram.add_connection(self.connection)

    def undo(self):
        self.diagram.remove_connection(self.connection)

    def get_description(self) -> str:
        return "Add connection"


class RemoveConnectionCommand(Command):
    def __init__(self, diagram, connection):
        self.diagram = diagram
        self.connection = connection

    def execute(self):
        self.diagram.remove_connection(self.connection)

    def undo(self):
        self.diagram.add_connection(self.connection)

    def get_description(self) -> str:
        return "Remove connection"


class EditShapePropertiesCommand(Command):
    def __init__(self, shape, old_properties, new_properties):
        self.shape = shape
        self.old_properties = old_properties
        self.new_properties = new_properties

    def execute(self):
        self._apply_properties(self.new_properties)

    def undo(self):
        self._apply_properties(self.old_properties)

    def _apply_properties(self, properties):
        for key, value in properties.items():
            if hasattr(self.shape, key):
                setattr(self.shape, key, value)

    def get_description(self) -> str:
        return f"Edit {self.shape.shape_type} properties"


class MultiCommand(Command):
    def __init__(self, commands: List[Command], description: str = "Multiple actions"):
        self.commands = commands
        self.description = description

    def execute(self):
        for command in self.commands:
            command.execute()

    def undo(self):
        for command in reversed(self.commands):
            command.undo()

    def get_description(self) -> str:
        return self.description
