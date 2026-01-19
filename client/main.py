import sys
import os
from PyQt5 import QtWidgets
from ui import LoginWindow
from iluvmary_app import IluvMaryApp

def main():
    app = QtWidgets.QApplication(sys.argv)
    
    # 1. Show Login
    login = LoginWindow()
    
    # Container for passing data
    login_data = {}
    
    def on_success(data):
        login_data.update(data)
    
    login.login_success.connect(on_success)
    login.exec_()
    
    # 2. Check if login was successful
    if not login_data:
        sys.exit(0)
        
    # 3. Set Environment Variables for the App
    # The app reads MAKI_EXPIRATION and MAKI_TIME_OFFSET
    if login_data.get('expires_at'):
        os.environ["MAKI_EXPIRATION"] = login_data['expires_at']
    else:
        # Lifetime
        os.environ["MAKI_EXPIRATION"] = ""
        
    # Offset calculation if needed (Client Time vs Server Time)
    # Simplified here.
    
    # 4. Launch Main App
    # We create a new instance of the app logic.
    # Note: iluvmary_app.py uses its own QApplication if instance() is None.
    # Since we created one above, it should reuse it.
    
    try:
        protected_app = IluvMaryApp()
        
        # If the app class starts its own loop, we call start().
        # However, IluvMaryApp.start() does app.exec_(). 
        # Since we are already in an app context, we might need to adjust.
        # Looking at iluvmary_app.py:
        # if not QtWidgets.QApplication.instance(): ... else: instance()
        # window.show() -> app.exec_()
        
        protected_app.start()
        
    except Exception as e:
        QtWidgets.QMessageBox.critical(None, "Error", f"Failed to launch app: {e}")

if __name__ == "__main__":
    main()
