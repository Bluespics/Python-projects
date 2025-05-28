
import requests
from datetime import datetime
from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea, QLineEdit, QPushButton, QGroupBox
)

import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and PyInstaller """
    try:
        base_path = sys._MEIPASS  # PyInstaller sets this
    except AttributeError:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)



# Frame to display individual forecast information
class ForecastFrame(QFrame):
    def __init__(self, forecast, parent=None):
        super().__init__(parent)
        self.init_ui(forecast)

    def init_ui(self, forecast):
        layout = QVBoxLayout(self)
        hour = datetime.strptime(forecast['dt_txt'], "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
        hour_label = QLabel(f"{hour}")
        time_label = QLabel(f"Time: {forecast['dt_txt']}")
        temp_label = QLabel(f"Temperature: {int(forecast['main']['temp'])} °C")
        min_label = QLabel(f"Min Temp: {int(forecast['main']['temp_min'])} °C")
        max_label = QLabel(f"Max Temp: {int(forecast['main']['temp_max'])} °C")
        feels_label = QLabel(f"Feels Like: {int(forecast['main']['feels_like'])} °C") 
        humidity_label = QLabel(f"Humidity: {forecast['main']['humidity']}%")
        weather_label = QLabel(f"Weather: {forecast['weather'][0]['description'].capitalize()}")
        icon = forecast['weather'][0]['icon']
        fname = resource_path(f'weather_icons/{icon}.png')
        pixmap = QPixmap(fname)
        icon_label = QLabel()
        icon_label.setPixmap(pixmap)
        wind_label = QLabel(f"Wind Speed: {int(forecast['wind']['speed']*2.23694)} mph")
        layout.addWidget(hour_label)
        font = QtGui.QFont()
        font.setPointSize(14)
        hour_label.setFont(font)
        layout.addWidget(temp_label)
        layout.addWidget(weather_label)
        layout.addWidget(icon_label)
        layout.addWidget(min_label)
        layout.addWidget(max_label)
        layout.addWidget(feels_label)
        layout.addWidget(humidity_label)
        layout.addWidget(wind_label)
        layout.addWidget(time_label)
        self.setLayout(layout)
        self.setStyleSheet("background-color: rgb(47, 109, 255); color: white;")
        self.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.setLineWidth(2)

# Tab to hold all forecasts for a single day
class DayTab(QWidget):
    def __init__(self, day_forecasts, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        row_layout = None
        for i, forecast in enumerate(day_forecasts):
            if i % 8 == 0:
                row_layout = QHBoxLayout()
                layout.addLayout(row_layout)
            frame = ForecastFrame(forecast)
            row_layout.addWidget(frame)
        layout.addStretch()
        self.setLayout(layout)

class WeatherApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("5-Day Weather Forecast")
        self.setGeometry(100, 100, 900, 700)

        self.main_layout = QVBoxLayout()

        self.city_input_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter city name")
        self.search_button = QPushButton("Get Weather")
        self.search_button.clicked.connect(self.load_weather_data)
        self.city_input_layout.addWidget(self.search_input)
        self.city_input_layout.addWidget(self.search_button)
        self.main_layout.addLayout(self.city_input_layout)

        self.city_country_label = QLabel("")
        self.city_country_label.setAlignment(QtCore.Qt.AlignCenter)
        city_font = QtGui.QFont()
        city_font.setPointSize(18)
        city_font.setBold(True)
        self.city_country_label.setFont(city_font)
        self.city_country_label.setStyleSheet("color: black;")
        self.main_layout.addWidget(self.city_country_label)

        self.current_weather_group = QGroupBox("Current Weather")
        self.current_weather_layout = QVBoxLayout()
        self.current_weather_group.setLayout(self.current_weather_layout)
        self.main_layout.addWidget(self.current_weather_group)

        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)

        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)

    def load_weather_data(self):
        city = self.search_input.text().strip()
        if city:
            api_key = "1ddd434490e6555185c572abf8eb4389"
            try:
                weather_data = self.fetch_weather_data(api_key, city)
                self.populate_current_weather(weather_data['city'], weather_data['list'][0])
                self.populate_tabs(weather_data)
            except Exception as e:
                self.tab_widget.clear()
                error_label = QLabel(f"Error: {e}")
                error_tab = QWidget()
                error_layout = QVBoxLayout()
                error_layout.addWidget(error_label)
                error_tab.setLayout(error_layout)
                self.tab_widget.addTab(error_tab, "Error")

    def fetch_weather_data(self, api_key, city):
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&units=metric&appid={api_key}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def populate_current_weather(self, city_data, forecast):
        self.clear_layout(self.current_weather_layout)
        self.city_country_label.setText(f"{city_data['name']}, {city_data['country']}")
        self.current_weather_group.setStyleSheet(
            "QGroupBox {"
            "    background-color: rgb(47, 109, 255);"
            "    color: white;"
            "    border: 1px solid white;"
            "    border-radius: 10px;"
            "    padding: 10px;"
            "}"
            "QLabel { color: white; }"
        )

        layout = QHBoxLayout()
        icon = forecast['weather'][0]['icon']
        fname = resource_path(f'weather_icons/{icon}.png')
        pixmap = QPixmap(fname)
        icon_label = QLabel()
        icon_label.setPixmap(pixmap)
        layout.addWidget(icon_label)

        temp_label = QLabel(f"{int(forecast['main']['temp'])} °C")
        temp_font = QtGui.QFont()
        temp_font.setPointSize(36)
        temp_label.setFont(temp_font)
        layout.addWidget(temp_label)

        details_layout = QVBoxLayout()
        details_layout.addWidget(QLabel(f"Weather: {forecast['weather'][0]['description'].capitalize()}"))
        details_layout.addWidget(QLabel(f"Min Temp: {int(forecast['main']['temp_min'])} °C"))
        details_layout.addWidget(QLabel(f"Max Temp: {int(forecast['main']['temp_max'])} °C"))
        details_layout.addWidget(QLabel(f"Feels Like: {int(forecast['main']['feels_like'])} °C"))     
        details_layout.addWidget(QLabel(f"Humidity: {forecast['main']['humidity']}%"))
        details_layout.addWidget(QLabel(f"Wind Speed: {int(forecast['wind']['speed']*2.23694)} mph"))
        layout.addLayout(details_layout)

        self.current_weather_layout.addLayout(layout)

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            elif item.layout() is not None:
                self.clear_layout(item.layout())

    def populate_tabs(self, weather_data):
        self.tab_widget.clear()
        day_groups = self.group_forecasts_by_day(weather_data['list'])
        for day, forecasts in day_groups.items():
            day_tab = DayTab(forecasts)
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setWidget(day_tab)
            self.tab_widget.addTab(scroll_area, day)

    def group_forecasts_by_day(self, forecasts):
        day_groups = {}
        for forecast in forecasts:
            date = datetime.strptime(forecast['dt_txt'], "%Y-%m-%d %H:%M:%S").strftime("%A, %d %B")
            day_groups.setdefault(date, []).append(forecast)
        return day_groups

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = WeatherApp()
    main_window.show()
    sys.exit(app.exec_())
