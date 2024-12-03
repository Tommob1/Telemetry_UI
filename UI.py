import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QHBoxLayout
from PyQt5.QtCore import QTimer, Qt
import pyqtgraph as pg
import serial
from serial.tools import list_ports
from collections import deque


class TelemetryApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Telemetry Dashboard")
        self.setWindowState(Qt.WindowFullScreen)

        self.temperature_data = deque(maxlen=100)
        self.humidity_data = deque(maxlen=100)
        self.power_data = deque(maxlen=100)
        self.light_data = deque(maxlen=100)
        self.time_data = deque(maxlen=100)
        self.counter = 0

        self.main_title = QLabel("Live Telemetry")
        self.main_title.setStyleSheet("color: #00FF00; font-size: 35px; font-family: Consolas;")
        self.main_title.setAlignment(Qt.AlignCenter)

        self.temperature_label = QLabel("Temperature: N/A")
        self.humidity_label = QLabel("Humidity: N/A")
        self.power_label = QLabel("Power: N/A")
        self.light_label = QLabel("Light: N/A")

        label_style = "color: #00FF00; font-size: 24px; font-family: Consolas;"
        self.temperature_label.setStyleSheet(label_style)
        self.humidity_label.setStyleSheet(label_style)
        self.power_label.setStyleSheet(label_style)
        self.light_label.setStyleSheet(label_style)

        self.temperature_graph = pg.PlotWidget()
        self.humidity_graph = pg.PlotWidget()
        self.power_graph = pg.PlotWidget()
        self.light_graph = pg.PlotWidget()

        for graph in [self.temperature_graph, self.humidity_graph, self.power_graph, self.light_graph]:
            graph.setBackground('black')
            graph.getAxis('left').setPen('w')
            graph.getAxis('bottom').setPen('w')

        self.temperature_graph.setTitle("Temperature", color="w", size="16pt")
        self.humidity_graph.setTitle("Humidity", color="w", size="16pt")
        self.power_graph.setTitle("Power", color="w", size="16pt")
        self.light_graph.setTitle("Light", color="w", size="16pt")  # Title for light graph

        self.temperature_curve = self.temperature_graph.plot(pen=pg.mkPen('r', width=2))
        self.humidity_curve = self.humidity_graph.plot(pen=pg.mkPen('g', width=2))
        self.power_curve = self.power_graph.plot(pen=pg.mkPen('b', width=2))
        self.light_curve = self.light_graph.plot(pen=pg.mkPen('y', width=2))  # Yellow for light graph

        label_layout = QVBoxLayout()
        label_layout.addWidget(self.temperature_label)
        label_layout.addWidget(self.humidity_label)
        label_layout.addWidget(self.light_label)  # Add light label above power
        label_layout.addWidget(self.power_label)

        graph_layout = QVBoxLayout()
        graph_layout.addWidget(self.temperature_graph)
        graph_layout.addWidget(self.humidity_graph)
        graph_layout.addWidget(self.light_graph)  # Add light graph
        graph_layout.addWidget(self.power_graph)

        content_layout = QHBoxLayout()
        content_layout.addLayout(label_layout)
        content_layout.addLayout(graph_layout)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.main_title)
        main_layout.addLayout(content_layout)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        central_widget.setStyleSheet("background-color: black;")
        self.setCentralWidget(central_widget)

        self.ser = self.initialize_serial_connection()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.read_telemetry)
        self.timer.start(500)

    def initialize_serial_connection(self):
        port = self.find_arduino_port()
        if port:
            try:
                ser = serial.Serial(port, 9600, timeout=1)
                print(f"Connected to Arduino on port {port}")
                return ser
            except Exception as e:
                print(f"Failed to connect to Arduino: {e}")
        else:
            print("Arduino not found.")
        return None

    def find_arduino_port(self):
        ports = list(list_ports.comports())
        for port in ports:
            if 'Arduino' in port.description or 'usbmodem' in port.device:
                return port.device
        return None

    def read_telemetry(self):
        if self.ser and self.ser.in_waiting > 0:
            try:
                line = self.ser.readline().decode('utf-8').strip()
                print(f"Raw Data: {line}")

                if line.startswith("Temp:") and "Hum:" in line and "Rail V:" in line and "Light:" in line:
                    temperature_part = line.split(",")[0].split(":")[1].strip().replace("C", "")
                    humidity_part = line.split(",")[1].split(":")[1].strip().replace("%", "")
                    power_part = line.split(",")[2].split(":")[1].strip().replace("V", "")
                    light_part = line.split(",")[3].split(":")[1].strip()

                    self.update_labels(temperature_part, humidity_part, power_part, light_part)
                    self.update_graphs(float(temperature_part), float(humidity_part), float(power_part), float(light_part))
                else:
                    print("Unexpected Data Format")
            except Exception as e:
                print(f"Error reading telemetry: {e}")

    def update_labels(self, temperature, humidity, power, light):
        self.temperature_label.setText(f"Temperature: {temperature} °C")
        self.humidity_label.setText(f"Humidity: {humidity} %")
        self.power_label.setText(f"Power: {power} V")
        self.light_label.setText(f"Light: {light}")

    def update_graphs(self, temperature, humidity, power, light):
        self.counter += 1
        self.time_data.append(self.counter)
        self.temperature_data.append(temperature)
        self.humidity_data.append(humidity)
        self.power_data.append(power)
        self.light_data.append(light)

        self.temperature_curve.setData(self.time_data, self.temperature_data)
        self.humidity_curve.setData(self.time_data, self.humidity_data)
        self.power_curve.setData(self.time_data, self.power_data)
        self.light_curve.setData(self.time_data, self.light_data)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    telemetry_app = TelemetryApp()
    telemetry_app.show()
    sys.exit(app.exec_())