from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, \
    QFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.widgets import SpanSelector
import sounddevice as sd

from parameters import Parameters
from sound import Sound


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.sound = self.load_file("PinkPanther.wav")
        self.parameters = Parameters()
        self.sound_axis, self.sound_canvas, sound_hbox, self.sound_selector = self.create_sound_box()
        self.parameter_axis, self.parameter_canvas = self.create_parameter_plot()

        vbox_left = QVBoxLayout()
        vbox_right = QVBoxLayout()
        hbox_buttons = QHBoxLayout()
        hbox_parameters = QHBoxLayout()

        hbox_buttons.addWidget(self.create_reset_button())
        hbox_buttons.addWidget(self.create_play_button())
        hbox_buttons.addWidget(self.create_open_file_button())

        vbox_left.addLayout(sound_hbox)
        vbox_left.addLayout(hbox_buttons)

        vbox_right.addWidget(self.parameter_canvas)
        vbox_left.addLayout(hbox_parameters)

        hbox_root = QHBoxLayout()
        hbox_root.addLayout(vbox_left)
        hbox_root.addLayout(vbox_right)
        hbox_root.addStretch(1)

        central_widget = QWidget()
        central_widget.setLayout(hbox_root)
        self.setCentralWidget(central_widget)
        self.on_select(0, self.sound.n_frames)

    def create_sound_box(self):
        figure = Figure(figsize=(5, 4), dpi=100)
        canvas = FigureCanvas(figure)
        axis = figure.add_subplot(111)
        selector = SpanSelector(axis, self.on_select, 'horizontal', useblit=True)

        hbox = QHBoxLayout()

        button_left = QPushButton('<')
        button_left.clicked.connect(lambda: self.sound.shift_left(0.1) or self.draw_plots())
        hbox.addWidget(button_left)

        hbox.addWidget(canvas)

        button_right = QPushButton('>')
        button_right.clicked.connect(lambda: self.sound.shift_right(0.1) or self.draw_plots())
        hbox.addWidget(button_right)

        button_left.setFixedWidth(25)
        button_right.setFixedWidth(25)

        for i in range(hbox.count()):
            hbox.itemAt(i).widget().setFixedHeight(400)
        return axis, canvas, hbox, selector

    @staticmethod
    def create_parameter_plot():
        figure = Figure(figsize=(5, 4), dpi=100)
        canvas = FigureCanvas(figure)
        axis = figure.add_subplot(111)
        return axis, canvas

    def select_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                  "All Files (*);;Python Files (*.py)", options=options)
        if filename:
            self.load_file(filename)
            self.reset_plots()

    def create_open_file_button(self):
        open_file_button = QPushButton('Click to open File Dialog', self)
        open_file_button.clicked.connect(self.select_file)
        return open_file_button

    def create_play_button(self):
        play_button = QPushButton('Play')
        play_button.clicked.connect(self.play_audio)
        return play_button

    def create_reset_button(self):
        reset_button = QPushButton('Reset')
        reset_button.clicked.connect(self.reset_plots)
        return reset_button

    @staticmethod
    def load_file(filename):
        return Sound(filename)

    def play_audio(self):
        _, sound = self.sound.get_selection_data()
        sd.play(sound, self.sound.framerate)

    def on_select(self, start, end):
        self.sound.select(start, end)
        self.draw_plots()

    def draw_plots(self):
        self.draw_plot_sound()
        self.draw_parameter_plot(self.parameters.volume(self.sound), "Relative volume")

    def draw_plot_sound(self):
        self.sound_axis.clear()
        selected_times, selected_sounds = self.sound.get_selection_data()
        if len(selected_times) == 0:
            return

        self.sound_axis.plot(selected_times, selected_sounds)
        self.sound_axis.set_title('Sound Wave')
        self.sound_axis.set_ylim((selected_sounds.min() * 0.9, selected_sounds.max() * 1.1))
        self.sound_canvas.draw()

    def draw_parameter_plot(self, values, title):
        times, _ = self.sound.get_selection_data()

        self.parameter_axis.clear()
        self.parameter_axis.plot(times, values)
        self.parameter_axis.set_title(title)

        min_value = values.min()
        max_value = values.max()
        padding = (max_value - min_value) * 0.05 if not max_value == min_value else 1
        self.parameter_axis.set_ylim((min_value - padding, max_value + padding))
        self.parameter_canvas.draw()

    def reset_plots(self):
        self.sound.reset()
        sd.stop()
        self.draw_plots()


app = QApplication([])
window = MainWindow()
window.setGeometry(100, 100, 1200, 800)
window.show()
app.exec_()
