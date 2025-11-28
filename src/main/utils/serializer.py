import json
import os
from typing import Optional


class DiagramSerializer:
    @staticmethod
    def save_to_file(diagram, file_path: str) -> bool:
        try:
            data = diagram.to_dict()
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            diagram.file_path = file_path
            diagram.modified = False
            return True
        except Exception as e:
            print(f"Error saving file: {e}")
            return False

    @staticmethod
    def load_from_file(file_path: str):
        try:
            from ..models.diagram import Diagram
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if not DiagramSerializer.validate_structure(data):
                raise ValueError("Invalid diagram file structure")
            diagram = Diagram.from_dict(data)
            diagram.file_path = file_path
            diagram.modified = False
            return diagram
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return None
        except json.JSONDecodeError as e:
            print(f"Invalid JSON: {e}")
            return None
        except Exception as e:
            print(f"Error loading file: {e}")
            return None

    @staticmethod
    def validate_structure(data: dict) -> bool:
        required_keys = ["metadata", "shapes", "connections"]
        for key in required_keys:
            if key not in data:
                print(f"Missing required key: {key}")
                return False
        if not isinstance(data["metadata"], dict):
            print("Invalid metadata")
            return False
        if not isinstance(data["shapes"], list):
            print("Invalid shapes")
            return False
        if not isinstance(data["connections"], list):
            print("Invalid connections")
            return False
        return True

    @staticmethod
    def export_to_json(diagram, file_path: str, pretty: bool = True) -> bool:
        return DiagramSerializer.save_to_file(diagram, file_path)
