import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer
import serial
from serial.tools import list_ports


class TelemetryApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Telemetry Dashboard")
        self.setGeometry(100, 100, 400, 300)

        # Initialize UI components
        self.temperature_label = QLabel("Temperature: N/A")
        self.humidity_label = QLabel("Humidity: N/A")
        self.power_label = QLabel("Power: N/A")

        # Set up layout
        layout = QVBoxLayout()
        layout.addWidget(self.temperature_label)
        layout.addWidget(self.humidity_label)
        layout.addWidget(self.power_label)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Initialize serial connection
        self.ser = self.initialize_serial_connection()

        # Set up a timer to read data periodically
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.read_telemetry)
        self.timer.start(1000)  # Read every second

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
    
    def read_telemetry(self):
        if self.ser and self.ser.in_waiting > 0:
            try:
                line = self.ser.readline().decode('utf-8').strip()
                print(f"Raw Data: {line}")  # Debugging: Print raw data
                data = line.split(",")  # Assuming "temp,hum,power" format from Arduino
                if len(data) == 3:
                    temperature, humidity, power = data
                    self.update_labels(temperature, humidity, power)
                else:
                    print(f"Unexpected Data Format: {data}")  # Debugging: Print unexpected format
            except Exception as e:
                print(f"Error reading telemetry: {e}")

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
                data = line.split(",")  # Assuming "temp,hum,power" format from Arduino
                if len(data) == 3:
                    temperature, humidity, power = data
                    self.update_labels(temperature, humidity, power)
            except Exception as e:
                print(f"Error reading telemetry: {e}")

    def update_labels(self, temperature, humidity, power):
        self.temperature_label.setText(f"Temperature: {temperature} °C")
        self.humidity_label.setText(f"Humidity: {humidity} %")
        self.power_label.setText(f"Power: {power} W")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    telemetry_app = TelemetryApp()
    telemetry_app.show()
    sys.exit(app.exec_())