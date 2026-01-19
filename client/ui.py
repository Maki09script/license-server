from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QPoint, QThread, pyqtSignal, QTimer
from api import LicenseClient
import os

class ValidationWorker(QThread):
    result_signal = pyqtSignal(bool, str, object)

    def __init__(self, api, key):
        super().__init__()
        self.api = api
        self.key = key

    def run(self):
        # The actual network request happens here, in the background
        success, msg, data = self.api.validate_key(self.key)
        self.result_signal.emit(success, msg, data)

class LoginWindow(QtWidgets.QDialog):
    login_success = pyqtSignal(dict) 

    def __init__(self):
        super().__init__()
        self.api = LicenseClient()
        self.setupUi()
        self.oldPos = self.pos()
        self.analyzing = False
        
        # Load saved key
        self.load_key()

    def setupUi(self):
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.resize(400, 500)

        self.frame = QtWidgets.QFrame(self)
        self.frame.setGeometry(QtCore.QRect(10, 10, 380, 480))
        self.frame.setStyleSheet("""
            QFrame { 
                background-color: #121216;
                border-radius: 15px; 
                border: 1px solid #2f2f3d; 
            }
            QLabel { color: #e0e0e0; font-family: 'Segoe UI'; }
            QLineEdit { 
                background-color: #1e1e24; 
                border: 1px solid #2f2f3d; 
                border-radius: 8px; 
                padding: 10px; 
                color: #ffffff; 
                font-size: 14px;
            }
            QLineEdit:focus { border: 1px solid #5865f2; }
            QPushButton {
                background-color: #5865f2;
                color: white; 
                border-radius: 8px; 
                font-weight: bold; 
                font-size: 14px;
                border: none;
                padding: 10px;
            }
            QPushButton:hover { background-color: #4752c4; }
            QPushButton:pressed { background-color: #3c45a5; }
            
            QPushButton#closeBtn { 
                background-color: transparent; 
                color: #aaa; 
                font-size: 20px; 
            }
            QPushButton#closeBtn:hover { color: #fff; }
        """)

        self.closeBtn = QtWidgets.QPushButton("×", self.frame)
        self.closeBtn.setObjectName("closeBtn")
        self.closeBtn.setGeometry(QtCore.QRect(340, 10, 30, 30))
        self.closeBtn.clicked.connect(self.close)

        self.titleLabel = QtWidgets.QLabel("AUTHENTICATION", self.frame)
        self.titleLabel.setGeometry(QtCore.QRect(0, 40, 380, 30))
        self.titleLabel.setAlignment(Qt.AlignCenter)
        self.titleLabel.setStyleSheet("font-size: 20px; font-weight: bold; border: none;")

        self.descLabel = QtWidgets.QLabel("Please enter your license key to continue.", self.frame)
        self.descLabel.setGeometry(QtCore.QRect(20, 80, 340, 40))
        self.descLabel.setAlignment(Qt.AlignCenter)
        self.descLabel.setWordWrap(True)
        self.descLabel.setStyleSheet("color: #aaa; font-size: 12px; border: none;")

        self.keyInput = QtWidgets.QLineEdit(self.frame)
        self.keyInput.setPlaceholderText("XXXXX-XXXXX-XXXXX-XXXXX")
        self.keyInput.setGeometry(QtCore.QRect(40, 140, 300, 45))
        self.keyInput.setAlignment(Qt.AlignCenter)

        self.loginBtn = QtWidgets.QPushButton("LOGIN", self.frame)
        self.loginBtn.setGeometry(QtCore.QRect(40, 210, 300, 45))
        self.loginBtn.clicked.connect(self.start_login)

        self.statusLabel = QtWidgets.QLabel("", self.frame)
        self.statusLabel.setGeometry(QtCore.QRect(20, 270, 340, 60)) # Increased height for multi-line
        self.statusLabel.setAlignment(Qt.AlignCenter)
        self.statusLabel.setStyleSheet("font-size: 12px; font-weight: bold; border: none; color: #aaa;")

        self.hwidLabel = QtWidgets.QLabel(f"HWID: {self.api.hwid}", self.frame)
        self.hwidLabel.setGeometry(QtCore.QRect(20, 440, 340, 20))
        self.hwidLabel.setAlignment(Qt.AlignCenter)
        self.hwidLabel.setStyleSheet("color: #444; font-size: 10px; border: none;")

    def load_key(self):
        if os.path.exists("license.dat"):
            try:
                with open("license.dat", "r") as f:
                    key = f.read().strip()
                self.keyInput.setText(key)
            except: pass

    def save_key(self, key):
        try:
            with open("license.dat", "w") as f:
                f.write(key)
        except: pass

    def start_login(self):
        if self.analyzing: return
        
        key = self.keyInput.text().strip()
        if not key:
            self.statusLabel.setText("Please enter a key.")
            self.statusLabel.setStyleSheet("color: #ed4245; border: none;")
            return

        self.analyzing = True
        self.loginBtn.setEnabled(False)
        self.keyInput.setEnabled(False)
        self.statusLabel.setStyleSheet("color: #fee75c; border: none;") # Yellow
        self.statusLabel.setText("Just analyzing... if it is connecting...")
        
        # Start background worker
        self.worker = ValidationWorker(self.api, key)
        self.worker.result_signal.connect(self.on_validation_finished)
        self.worker.start()

    def on_validation_finished(self, success, msg, data):
        self.analyzing = False
        self.loginBtn.setEnabled(True)
        self.keyInput.setEnabled(True)
        
        if success:
            self.statusLabel.setText("ACCESS GRANTED")
            self.statusLabel.setStyleSheet("color: #3ba55d; border: none;") # Green
            self.save_key(self.keyInput.text().strip())
            
            # Short delay for user to see "ACCESS GRANTED" before closing
            QTimer.singleShot(800, lambda: self.emit_success(data))
        else:
            self.statusLabel.setText(msg.upper())
            self.statusLabel.setStyleSheet("color: #ed4245; border: none;") # Red

    def emit_success(self, data):
        self.login_success.emit(data)
        self.close()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            delta = QPoint(event.globalPos() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()
