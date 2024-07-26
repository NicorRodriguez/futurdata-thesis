from PyQt6.QtWidgets import QMainWindow, QFileDialog, QApplication, QLabel, QPushButton, QDialog, QLineEdit
from PyQt6.QtGui import QPixmap, QPainter, QPen
from PyQt6.QtCore import Qt, QPoint
from PyQt6 import uic
import math

from structure import structure
import generalUtils

class ProcessWizardWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/main.ui', self)
        self.current_level_id = 0
        self.current_image_path = None
        self.drawing_enabled = False
        

        self.current_polygon_points = []
        
        self.actionOpen_image.triggered.connect(self.open_image)
        self.draw_polygon_pushButton.clicked.connect(self.enable_drawing)
        self.add_basic_object_pushButton.clicked.connect(self.open_add_basic_object_form)
        self.add_basic_action_pushButton.clicked.connect(self.open_add_basic_action_form)


    def open_add_basic_object_form(self):
        dialog = BasicObjectForm(self)
        dialog.exec()  # Open the form as a modal dialog

        # Get the returned data if the dialog was accepted
        if dialog.result() == QDialog.DialogCode.Accepted:
            data = dialog.get_form_data()
            print("Form Data:", data)  # You can now use the data in the main window

    def open_add_basic_action_form(self):
        dialog = BasicActionForm(self)
        dialog.exec()  # Open the form as a modal dialog

        # Get the returned data if the dialog was accepted
        if dialog.result() == QDialog.DialogCode.Accepted:
            data = dialog.get_form_data()
            print("Form Data:", data)  # You can now use the data in the main window


    def open_image(self):
        print('Opening image')
        self.start_browse_image()

    

    def start_browse_image(self):
        file_filter = "Image Files (*.png *.jpg *.bmp *.gif);;All Files (*)"
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select Image File', filter=file_filter)
        if file_path:
            self.current_image_path = file_path
            print(self.current_image_path)
            self.display_image(file_path)

    def display_image(self, image_path):
        pixmap = QPixmap(image_path)
        self.image_label.setPixmap(pixmap)
        self.image_label.setScaledContents(True)  # Optionally scale the image to fit the label

    def enable_drawing(self):
        self.drawing_enabled = True
        self.image_label.mousePressEvent = self.mousePressEvent
        print('drawing enabled')
        # self.image_label.mouseReleaseEvent = self.mouseReleaseEvent
        

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.drawing_enabled:
            point = event.position().toPoint()
            print(f'pointedd position {point}')
            self.current_polygon_points.append(point)
            self.draw_line()
            if self.is_close_to_start_point(point):
                self.enable_drawing = False

    

    def draw_line(self):
        if self.drawing_enabled and len(self.current_polygon_points) > 1:
            # Draw the line on a copy of the pixmap
            pixmap = self.image_label.pixmap().copy()
            painter = QPainter(pixmap)
            pen = QPen(Qt.GlobalColor.black, 2)
            painter.setPen(pen)
            
            # Get the QLabel's position
            label_position = self.get_absolute_label_position()
            label_x, label_y = label_position.x(), label_position.y()
            print(label_y)
            # Calculate the adjusted start and end positions for the line
            previous_point = self.current_polygon_points[-2]
            current_point = self.current_polygon_points[-1]
            draw_position_start = QPoint(previous_point.x() + label_x + 10, previous_point.y() + label_y +30)
            draw_position_end = QPoint(current_point.x() + label_x + 10, current_point.y() + label_y + 30)
            print(f'end point {draw_position_end}')
            # Draw the line
            painter.drawLine(draw_position_start, draw_position_end)
            painter.end()

            # Set the updated pixmap back to the label
            self.image_label.setPixmap(pixmap)
    
    def get_absolute_label_position(self):
        # Get the top-left corner of the main window (which is the starting point (0,0))
        main_window_top_left = self.mapToGlobal(QPoint(0, 0))

        # Get the top-left corner of the QLabel relative to the screen
        label_top_left = self.image_label.mapToGlobal(QPoint(0, 0))

        # Calculate the QLabel's position relative to the main window
        absolute_position = label_top_left - main_window_top_left

        # Print the absolute position
        print(f"Absolute position of label - x: {absolute_position.x()}, y: {absolute_position.y()}")
        return absolute_position

    def is_close_to_start_point(self, point):
        if len(self.current_polygon_points) > 0:
            ref_point = self.current_polygon_points[0]

            # Calculate the Euclidean distance between the points
            distance = math.sqrt((point.x() - ref_point.x())**2 + (point.y() - ref_point.y())**2)

            # Check if the distance is within the radius of 10 pixels
            if distance <= 10:
                return True

        return False


class BasicObjectForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('./ui/basic_object.ui', self)  # Load the form UI

        self.baisc_object_confirm_pushButton.clicked.connect(self.accept)  # Closes the dialog and sets result to Accepted

    def get_form_data(self):
        # Gather data from the form fields
        return {
            'name': self.basic_object_name_lineEdit.text(),
            'weight': self.basic_object_weight_lineEdit.text(),
            'color': self.basic_object_color_lineEdit.text(),
            'serial_number': self.basic_object_serial_lineEdit.text(),
            'bucket': self.basic_object_bucket_lineEdit.text(),
            'quality': self.basic_object_quality_lineEdit.text()
        }


class BasicActionForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tools = generalUtils.read_tools_from_json('./data/tools.json')
        uic.loadUi('./ui/basic_action.ui', self)  # Load the form UI
        self.fill_tools_list()
        # UI elements
        
        self.basic_action_confirm_pushButton.clicked.connect(self.accept)  # Closes the dialog and sets result to Accepted


    def fill_tools_list(self):
        tools_list = [None] + [t.name for t in self.tools]
        self.basic_action_tool_comboBox.addItems(tools_list)

    def get_form_data(self):
        # Gather data from the form fields
        return {
            'tool': self.basic_action_tool_comboBox.currentText(),
            'time': self.basic_action_time_lineEdit.text(),
            'anomaly_action': self.basic_action_anomaly_lineEdit.text()
        }

if __name__ == '__main__':
    app = QApplication([])
    window = ProcessWizardWindow()
    window.show()
    app.exec()
