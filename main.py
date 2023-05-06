import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, \
    QSizePolicy, QSplitter, QComboBox
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
        self.combobox_items = self.create_combobox_parameters_dict()

        self.sound_selector = None

        self.sound_axis, self.sound_canvas, sound_hbox = self.create_sound_box()
        self.parameter_axis, self.parameter_canvas = self.create_parameter_plot()

        self.sound_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.parameter_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        vbox_left = QVBoxLayout()
        vbox_right = QVBoxLayout()
        hbox_buttons = QHBoxLayout()
        hbox_parameters, self.parameter_selector = self.create_parameter_controls()

        hbox_buttons.addWidget(self.create_reset_button())
        hbox_buttons.addWidget(self.create_play_button())
        hbox_buttons.addWidget(self.create_open_file_button())

        vbox_left.addLayout(sound_hbox)

        # Wrap hbox_buttons in a QWidget and set a fixed height
        buttons_widget = QWidget()
        buttons_widget.setLayout(hbox_buttons)
        buttons_widget.setFixedHeight(100)
        vbox_left.addWidget(buttons_widget)

        vbox_right.addWidget(self.parameter_canvas)

        # Wrap hbox_parameters in a QWidget and set a fixed height
        parameters_widget = QWidget()
        parameters_widget.setLayout(hbox_parameters)
        parameters_widget.setFixedHeight(100)
        vbox_right.addWidget(parameters_widget)

        # Wrap the left and right sections in QWidget
        left_section = QWidget()
        left_section.setLayout(vbox_left)
        right_section = QWidget()
        right_section.setLayout(vbox_right)

        # Set the size policy for the sections
        left_section.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        right_section.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        # Use a QSplitter to separate the two sections
        splitter = QSplitter()
        splitter.addWidget(left_section)
        splitter.addWidget(right_section)

        self.setCentralWidget(splitter)
        self.on_select(0, self.sound.duration)

    def create_combobox_parameters_dict(self):
        parameters = {
            "Volume": lambda: self.draw_parameter_plot(self.parameters.volume(self.sound), "Relative volume"),
            "Negative volume": lambda: self.draw_parameter_plot(-self.parameters.volume(self.sound), "Negative volume"),
            "Frequency Centroid": lambda: self.draw_parameter_plot(self.parameters.frequency_centroid(self.sound), "Frequency centroid"),
            "Effective Bandwidth": lambda: self.draw_parameter_plot(self.parameters.effective_bandwidth(self.sound), "Effective bandwidth"),
            "Band Energy": lambda: self.draw_parameter_plot(self.parameters.band_energy(self.sound, 0), "Band energy"),
            "Band Energy Ratio": lambda: self.draw_parameter_plot(self.parameters.band_energy_ratio(self.sound, 0), "Band energy ratio"),
            "Spectral Flatness Measure": lambda: self.draw_parameter_plot(self.parameters.spectral_flatness_measure(self.sound, 0), "Spectral flatness measure"),
            "Spectral Crest Factor": lambda: self.draw_parameter_plot(self.parameters.spectral_crest_factor(self.sound, 0), "Spectral crest factor"),
        }

        return parameters

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

        # We need to keep the selector somewhere
        self.sound_selector = selector
        return axis, canvas, hbox

    @staticmethod
    def create_parameter_plot():
        figure = Figure(figsize=(5, 4), dpi=100)
        canvas = FigureCanvas(figure)
        axis = figure.add_subplot(111)
        return axis, canvas

    def select_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getOpenFileName(self, "Select file to analyze", "",
                                                  "Sound Files (*.wav);;All Files (*)", options=options)
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

    def create_parameter_controls(self):
        hbox = QHBoxLayout()

        prev_parameter_button = self.create_prev_parameter_button()
        hbox.addWidget(prev_parameter_button)

        parameter_selector = self.create_parameter_selector()
        hbox.addWidget(parameter_selector)

        next_parameter_button = self.create_next_parameter_button()
        hbox.addWidget(next_parameter_button)

        # Set the maximum height of the combo box to match the buttons
        button_height = prev_parameter_button.sizeHint().height()
        parameter_selector.setMaximumHeight(button_height)

        # Set size policies for the buttons and the combo box
        button_width = 25
        prev_parameter_button.setFixedSize(button_width, button_height)
        prev_parameter_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        parameter_selector.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        next_parameter_button.setFixedSize(button_width, button_height)
        next_parameter_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        return hbox, parameter_selector

    def create_parameter_selector(self):
        selector = QComboBox()

        for name, func in zip(self.combobox_items.keys(), self.combobox_items.values()):
            selector.addItem(name, func)

        # Add more items here for other parameters
        selector.currentIndexChanged.connect(self.draw_selected_parameter_plot)
        return selector

    def create_prev_parameter_button(self):
        prev_button = QPushButton('<')
        prev_button.clicked.connect(self.select_prev_parameter)
        return prev_button

    def create_next_parameter_button(self):
        next_button = QPushButton('>')
        next_button.clicked.connect(self.select_next_parameter)
        return next_button

    def select_prev_parameter(self):
        current_index = self.parameter_selector.currentIndex()
        new_index = (current_index - 1) % self.parameter_selector.count()
        self.parameter_selector.setCurrentIndex(new_index)

    def select_next_parameter(self):
        current_index = self.parameter_selector.currentIndex()
        new_index = (current_index + 1) % self.parameter_selector.count()
        self.parameter_selector.setCurrentIndex(new_index)

    @staticmethod
    def load_file(filename):
        return Sound(filename)

    def play_audio(self):
        _, sound = self.sound.get_selection_data()
        sd.play(sound, self.sound.framerate)

    def on_select(self, start, end):
        self.sound.select(start, end)
        self.parameters.restart_cache()
        self.draw_plots()

    def draw_plots(self):
        self.draw_plot_sound()
        self.draw_selected_parameter_plot()

    def draw_plot_sound(self):
        self.sound_axis.clear()
        selected_times, selected_sounds = self.sound.get_selection_data()
        if len(selected_times) == 0:
            return

        self.sound_axis.plot(selected_times, selected_sounds)
        self.sound_axis.set_title('Sound Wave')
        self.sound_axis.set_ylim((selected_sounds.min() * 0.9, selected_sounds.max() * 1.1))
        self.sound_canvas.draw()

    def draw_selected_parameter_plot(self):
        selected_index = self.parameter_selector.currentIndex()
        drawing_func = self.parameter_selector.itemData(selected_index)
        drawing_func()

    def draw_parameter_plot(self, values, title):
        times = self.parameters.times_window(self.sound)

        self.parameter_axis.clear()
        self.parameter_axis.plot(times, values)
        self.parameter_axis.set_title(title)

        #replace nans with zeros in values
        values = np.nan_to_num(values)

        min_value = values.min()
        max_value = values.max()
        padding = (max_value - min_value) * 0.05 if not max_value == min_value else 1
        self.parameter_axis.set_ylim((min_value - padding, max_value + padding))
        self.parameter_canvas.draw()

    def reset_plots(self):
        self.sound.reset()
        self.parameters.restart_cache()
        sd.stop()
        self.draw_plots()


app = QApplication([])
window = MainWindow()
window.setGeometry(100, 100, 1200, 500)
window.show()
app.exec_()
