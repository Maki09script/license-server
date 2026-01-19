from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QPoint, QThread, pyqtSignal, QTimer
import pymem
import pymem.process
import sys
import re
import os
import shutil
import datetime

# --- WORKER THREAD ---
class SolaraCleanerThread(QThread):
    log_signal = pyqtSignal(str, str)
    finished_signal = pyqtSignal()

    def run(self):
        targets_folders = ["Solara", "SolaraTab", "scripts", "autoexec", "workspace"]
        targets_files = ["BootstrapperNew.exe"]
        
        drives = [f"{d}:\\" for d in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{d}:\\")]
        
        self.log_signal.emit(f"Starting Deep Scan on drives: {', '.join(drives)}", "#5865f2")
        self.log_signal.emit("This may take a while...", "#aaaaaa")

        count = 0
        
        for drive in drives:
            for root, dirs, files in os.walk(drive, topdown=True):
                if "Windows" in root or "Program Files" in root or "ProgramData" in root:
                    continue
                
                # Check Dirs
                for d in dirs[:]:
                    if d.lower() in [t.lower() for t in targets_folders]:
                        full_path = os.path.join(root, d)
                        try:
                            self.log_signal.emit(f"Deleting folder: {full_path}", "#ff5f57")
                            shutil.rmtree(full_path, ignore_errors=True)
                            count += 1
                            dirs.remove(d) 
                        except Exception as e:
                            self.log_signal.emit(f"Failed to delete {d}: {e}", "#ff5f57")

                # Check Files
                for f in files:
                    if f.lower() in [t.lower() for t in targets_files]:
                        full_path = os.path.join(root, f)
                        try:
                            self.log_signal.emit(f"Deleting file: {full_path}", "#ff5f57")
                            os.remove(full_path)
                            count += 1
                        except Exception as e:
                             self.log_signal.emit(f"Failed to delete {f}: {e}", "#ff5f57")
                             
        self.log_signal.emit(f"Scan Complete. Removed {count} items.", "#3ba55d")
        self.finished_signal.emit()

# --- MAIN WINDOW ---
class Ui_Dialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setupUi()
        self.oldPos = self.pos()
        self.setup_timer()

    def setupUi(self):
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setObjectName("Dialog")
        self.resize(550, 650) 

        self.frame = QtWidgets.QFrame(self)
        self.frame.setGeometry(QtCore.QRect(10, 10, 530, 630))
        self.frame.setStyleSheet("""
            QFrame { 
                background-color: #121216;
                border-radius: 20px; 
                border: 1px solid #2f2f3d; 
            }
            QLabel { color: #e0e0e0; font-family: 'Segoe UI'; }
            QLineEdit { 
                background-color: #1e1e24; 
                border: 1px solid #2f2f3d; 
                border-radius: 10px; 
                padding: 12px; 
                color: #ffffff; 
                font-size: 13px;
                selection-background-color: #5865f2;
            }
            QLineEdit:focus { border: 1px solid #5865f2; background-color: #24242e; }
            QTextEdit { 
                background-color: #1e1e24; 
                border: 1px solid #2f2f3d; 
                border-radius: 10px; 
                color: #a0a0a0; 
                font-family: 'Consolas'; 
                font-size: 11px; 
                padding: 10px;
            }
            QPushButton {
                color: white; 
                border-radius: 10px; 
                font-weight: bold; 
                font-size: 13px;
                border: none;
                padding: 12px;
            }
            QPushButton:pressed { padding-top: 14px; padding-bottom: 10px; }
            
            QPushButton#removeBtn { 
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #5865f2, stop:1 #4752c4); 
            }
            QPushButton#removeBtn:hover { background-color: #4752c4; }
            
            QPushButton#cleanBtn { 
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3ba55d, stop:1 #2d7d46); 
            }
            QPushButton#cleanBtn:hover { background-color: #2d7d46; }

            QPushButton#solaraBtn { 
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ed4245, stop:1 #c03537); 
            }
            QPushButton#solaraBtn:hover { background-color: #c03537; }
            
            QPushButton#closeBtn { 
                background-color: transparent; 
                color: #555; 
                font-size: 24px; 
            }
            QPushButton#closeBtn:hover { color: #f04747; }
        """)

        self.closeBtn = QtWidgets.QPushButton("×", self.frame)
        self.closeBtn.setObjectName("closeBtn")
        self.closeBtn.setGeometry(QtCore.QRect(490, 10, 30, 30))
        self.closeBtn.clicked.connect(self.close_app)

        self.header_bg = QtWidgets.QLabel(self.frame)
        self.header_bg.setGeometry(QtCore.QRect(0, 0, 530, 80))
        self.header_bg.setStyleSheet("background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1a1a20, stop:1 #121216); border-bottom: 1px solid #2f2f3d; border-top-left-radius: 20px; border-top-right-radius: 20px;")
        self.header_bg.lower()

        self.titleLabel = QtWidgets.QLabel("MAKI", self.frame)
        self.titleLabel.setGeometry(QtCore.QRect(30, 20, 100, 40))
        self.titleLabel.setStyleSheet("background: transparent; color: #fff; font-weight: 800; font-size: 24px; border: none;")

        self.subtitleLabel = QtWidgets.QLabel("ADVANCED CLEANER", self.frame)
        self.subtitleLabel.setGeometry(QtCore.QRect(100, 30, 200, 25))
        self.subtitleLabel.setStyleSheet("background: transparent; color: #5865f2; font-weight: bold; font-size: 14px; border: none; letter-spacing: 2px;")

        self.timeLabel = QtWidgets.QLabel("Calculating time...", self.frame)
        self.timeLabel.setGeometry(QtCore.QRect(300, 30, 180, 25))
        self.timeLabel.setAlignment(QtCore.Qt.AlignRight)
        self.timeLabel.setStyleSheet("background: transparent; color: #00fa9a; font-size: 12px; font-weight: bold;")

        self.input_pid = QtWidgets.QLineEdit(self.frame)
        self.input_pid.setPlaceholderText("Enter Process ID (PID) to Inject/Clean...")
        self.input_pid.setGeometry(QtCore.QRect(30, 100, 470, 45))

        self.logArea = QtWidgets.QTextEdit(self.frame)
        self.logArea.setGeometry(QtCore.QRect(30, 160, 470, 220))
        self.logArea.setReadOnly(True)

        self.removeBtn = QtWidgets.QPushButton("EXECUTE MEMORY WIPE", self.frame)
        self.removeBtn.setObjectName("removeBtn")
        self.removeBtn.setGeometry(QtCore.QRect(30, 400, 470, 50))
        self.removeBtn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.removeBtn.clicked.connect(self.process_removal)

        self.cleanBtn = QtWidgets.QPushButton("MASS CLEAN PC (BATCH)", self.frame)
        self.cleanBtn.setObjectName("cleanBtn")
        self.cleanBtn.setGeometry(QtCore.QRect(30, 460, 470, 50))
        self.cleanBtn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.cleanBtn.clicked.connect(self.run_clean_bat)

        self.solaraBtn = QtWidgets.QPushButton("DELETE SOLARA (DEEP SCAN)", self.frame)
        self.solaraBtn.setObjectName("solaraBtn")
        self.solaraBtn.setGeometry(QtCore.QRect(30, 520, 470, 50))
        self.solaraBtn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.solaraBtn.clicked.connect(self.run_solara_clean)

        self.versionLabel = QtWidgets.QLabel("v2.5.0-Stable | Protected by MakiAuth", self.frame)
        self.versionLabel.setGeometry(QtCore.QRect(0, 590, 530, 20))
        self.versionLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.versionLabel.setStyleSheet("color: #444; font-size: 10px;")

    def setup_timer(self):
        self.expiration_str = os.getenv("MAKI_EXPIRATION", "")
        self.expires_at = None
        if self.expiration_str:
            try:
                # Format from FastAPI: 2026-01-19 13:02:08.076358 or w/o microsec
                # We need to handle potential timezones or naive dts. 
                # Ideally, expires_at from server is ISO.
                dt = datetime.datetime.fromisoformat(self.expiration_str)
                self.expires_at = dt
            except:
                pass
        
        # Anti-Tamper Offset
        self.time_offset = 0.0
        try:
            self.time_offset = float(os.getenv("MAKI_TIME_OFFSET", "0.0"))
        except:
            pass
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)
        self.update_timer()

    def update_timer(self):
        if self.expires_at:
            # CORRECTED TIME = Local Time + Offset
            now = datetime.datetime.now() + datetime.timedelta(seconds=self.time_offset)
            
            # Ensure we compare apples to apples (naive vs naive)
            # Assuming server returns naive, or we strip tz if needed.
            # Fast/simple: Subtracting two datetimes.
            remaining = self.expires_at - now
            
            if remaining.total_seconds() > 0:
                days = remaining.days
                hours, remainder = divmod(remaining.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                self.timeLabel.setText(f"{days}d {hours:02}h {minutes:02}m {seconds:02}s remaining")
                self.timeLabel.setStyleSheet("background: transparent; color: #00fa9a; font-size: 12px; font-weight: bold;")
            else:
                self.timeLabel.setText("LICENSE EXPIRED")
                self.timeLabel.setStyleSheet("color: #ff5f57; background: transparent; font-weight: bold;")
                # Force close on expiration logic could go here if GUI wants to enforce it visually
        else:
            self.timeLabel.setText("LIFETIME / UNLIMITED")
            self.timeLabel.setStyleSheet("background: transparent; color: #5865f2; font-size: 12px; font-weight: bold;")

    def log(self, text, color="#8e9297"):
        self.logArea.append(f'<span style="color: {color};">[{QtCore.QTime.currentTime().toString()}] {text}</span>')
        self.logArea.verticalScrollBar().setValue(self.logArea.verticalScrollBar().maximum())

    def close_app(self):
        QtCore.QCoreApplication.quit() # Better than sys.exit(0) for embedded use

    def run_clean_bat(self):
        # Look in current dir (if dev) or temp dir (if meipass)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        if getattr(sys, 'frozen', False):
             base_dir = sys._MEIPASS
        
        bat_path = os.path.join(base_dir, "maki.bat")

        if os.path.exists(bat_path):
            try:
                os.startfile(bat_path)
                self.log(f"SUCCESS: Running optimization script...", "#3ba55d")
            except Exception as e:
                self.log(f"ERROR: Failed to run script ({str(e)})", "#ff5f57")
        else:
            self.log(f"ERROR: maki.bat missing at {bat_path}!", "#ff5f57")

    def run_solara_clean(self):
        self.solaraBtn.setEnabled(False)
        self.solaraBtn.setText("SCANNING SYSTEM (DO NOT CLOSE)...")
        
        self.cleaner_thread = SolaraCleanerThread()
        self.cleaner_thread.log_signal.connect(self.log)
        self.cleaner_thread.finished_signal.connect(self.on_solara_finished)
        self.cleaner_thread.start()

    def on_solara_finished(self):
        self.solaraBtn.setEnabled(True)
        self.solaraBtn.setText("DELETE SOLARA (DEEP SCAN)")
        QtWidgets.QMessageBox.information(self, "Scan Complete", "Deep scan finished. Check logs for details.")

    def wipe_full_string(self, pm, start_addr, content, match_start, match_end, keyword, is_unicode=False):
        step = 2 if is_unicode else 1
        str_start = match_start
        while str_start >= step:
            if content[str_start-step:str_start] == (b'\x00\x00' if is_unicode else b'\x00'):
                break
            str_start -= step
        str_end = match_end
        while str_end <= len(content) - step:
            if content[str_end:str_end+step] == (b'\x00\x00' if is_unicode else b'\x00'):
                break
            str_end += step
        full_len = str_end - str_start
        if full_len > 0:
            target = start_addr + str_start
            try:
                pm.write_bytes(target, b'\x00' * full_len, full_len)
                return True
            except: pass
        return False

    def process_removal(self):
        try:
            pid_val = self.input_pid.text().strip()
            if not pid_val:
                self.log("ERROR: Enter a valid PID first!", "#f04747")
                return
            pid = int(pid_val)
            pm = pymem.Pymem()
            pm.open_process_from_id(pid)
            self.logArea.clear()
            self.log(f"Injecting into PID: {pid}...", "#7289da")
            
            keywords = ["solara", "bootstrapper"]
            total_cleaned = 0
            address = 0
            
            while address < 0x7FFFFFFFFFFF:
                try:
                    mbi = pymem.memory.virtual_query(pm.process_handle, address)
                    if mbi.State == 0x1000 and mbi.Protect & (0x02 | 0x04 | 0x40):
                        try:
                            content = pm.read_bytes(address, mbi.RegionSize)
                            for key in keywords:
                                pat_a = re.compile(key.encode(), re.IGNORECASE)
                                for m in pat_a.finditer(content):
                                    if self.wipe_full_string(pm, address, content, m.start(), m.end(), key, False):
                                        total_cleaned += 1
                                pat_u = re.compile(key.encode('utf-16le'), re.IGNORECASE)
                                for m in pat_u.finditer(content):
                                    if self.wipe_full_string(pm, address, content, m.start(), m.end(), key, True):
                                        total_cleaned += 1
                        except: pass
                    address += mbi.RegionSize
                except: address += 4096
                QtWidgets.QApplication.processEvents()

            self.log("-----------------------------------------")
            self.log(f"MEMORY WIPE COMPLETE! Removed {total_cleaned} strings.", "#5865f2")
        except Exception as e:
            self.log(f"Process Error: {str(e)}", "#ff5f57")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            delta = QPoint(event.globalPos() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()

# --- ADAPTER FOR MAIN.PY ---
class IluvMaryApp:
    def __init__(self):
        self.app = None
        self.window = None

    def start(self):
        if not QtWidgets.QApplication.instance():
            self.app = QtWidgets.QApplication(sys.argv)
        else:
            self.app = QtWidgets.QApplication.instance()
            
        self.window = Ui_Dialog()
        self.window.show()
        self.app.exec_()

    def stop(self):
        if self.app:
            self.app.quit() # Quit the event loop

if __name__ == "__main__":
    app = IluvMaryApp()
    app.start()
