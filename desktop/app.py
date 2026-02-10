import sys
import requests
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


API_BASE = 'http://127.0.0.1:8000/api'


class ChartCanvas(FigureCanvas):
    def __init__(self):
        self.figure = Figure(figsize=(8, 6))
        super().__init__(self.figure)

    def render_charts(self, df: pd.DataFrame):
        self.figure.clear()

        ax1 = self.figure.add_subplot(311)
        ax1.plot(df['Session ID'], df['Wind Speed (km/h)'], marker='o')
        ax1.set_title('Wind Speed vs Session')

        ax2 = self.figure.add_subplot(312)
        ax2.bar(df['Session ID'], df['Distance Covered (km)'])
        ax2.set_title('Distance Covered per Session')

        ax3 = self.figure.add_subplot(313)
        counts = df['Board Type'].value_counts()
        ax3.pie(counts.values, labels=counts.index, autopct='%1.1f%%')
        ax3.set_title('Board Type Distribution')

        self.figure.tight_layout()
        self.draw()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.token = None
        self.df = None

        self.setWindowTitle('Windsurf Desktop Analytics')
        self.resize(1000, 800)

        root = QWidget()
        layout = QVBoxLayout(root)

        auth_layout = QHBoxLayout()
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Username')
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText('Password')
        self.login_btn = QPushButton('Login')
        self.login_btn.clicked.connect(self.handle_login)
        auth_layout.addWidget(QLabel('Auth:'))
        auth_layout.addWidget(self.username_input)
        auth_layout.addWidget(self.password_input)
        auth_layout.addWidget(self.login_btn)

        actions_layout = QGridLayout()
        self.upload_btn = QPushButton('Upload CSV')
        self.upload_btn.clicked.connect(self.upload_csv)
        self.history_btn = QPushButton('Fetch History')
        self.history_btn.clicked.connect(self.fetch_history)
        self.pdf_btn = QPushButton('Download PDF')
        self.pdf_btn.clicked.connect(self.download_pdf)
        actions_layout.addWidget(self.upload_btn, 0, 0)
        actions_layout.addWidget(self.history_btn, 0, 1)
        actions_layout.addWidget(self.pdf_btn, 0, 2)

        self.summary_box = QTextEdit()
        self.summary_box.setReadOnly(True)
        self.chart = ChartCanvas()

        layout.addLayout(auth_layout)
        layout.addLayout(actions_layout)
        layout.addWidget(QLabel('Summary / History'))
        layout.addWidget(self.summary_box)
        layout.addWidget(self.chart)

        self.setCentralWidget(root)

    def auth_headers(self):
        if not self.token:
            return {}
        return {'Authorization': f'Token {self.token}'}

    def handle_login(self):
        payload = {
            'username': self.username_input.text().strip(),
            'password': self.password_input.text().strip(),
        }
        resp = requests.post(f'{API_BASE}/auth/token/', json=payload, timeout=10)
        if resp.status_code == 200:
            self.token = resp.json()['token']
            QMessageBox.information(self, 'Success', 'Login successful.')
        else:
            QMessageBox.warning(self, 'Error', f'Login failed: {resp.text}')

    def upload_csv(self):
        if not self.token:
            QMessageBox.warning(self, 'Error', 'Login first.')
            return
        path, _ = QFileDialog.getOpenFileName(self, 'Select CSV', '', 'CSV Files (*.csv)')
        if not path:
            return

        with open(path, 'rb') as file_obj:
            files = {'file': (path.split('/')[-1], file_obj, 'text/csv')}
            resp = requests.post(f'{API_BASE}/upload/', files=files, headers=self.auth_headers(), timeout=20)

        if resp.status_code != 201:
            QMessageBox.warning(self, 'Upload Failed', resp.text)
            return

        data = resp.json()
        self.summary_box.setPlainText(str(data['summary']))
        self.df = pd.read_csv(path)
        self.chart.render_charts(self.df)

    def fetch_history(self):
        if not self.token:
            QMessageBox.warning(self, 'Error', 'Login first.')
            return
        resp = requests.get(f'{API_BASE}/history/', headers=self.auth_headers(), timeout=10)
        self.summary_box.setPlainText(resp.text)

    def download_pdf(self):
        if not self.token:
            QMessageBox.warning(self, 'Error', 'Login first.')
            return
        resp = requests.get(f'{API_BASE}/report/pdf/', headers=self.auth_headers(), timeout=20)
        if resp.status_code != 200:
            QMessageBox.warning(self, 'Error', resp.text)
            return
        path, _ = QFileDialog.getSaveFileName(self, 'Save PDF', 'windsurf_report.pdf', 'PDF Files (*.pdf)')
        if path:
            with open(path, 'wb') as f:
                f.write(resp.content)
            QMessageBox.information(self, 'Saved', f'PDF saved to {path}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
