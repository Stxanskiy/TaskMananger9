from LoginWindow import *
from TaskManangerWindow import TaskManagerWindow


app = QApplication([])
login_window = LoginWindow()
login_window.show()




def get_username():
    return login_window.lineedit_username.text()

def get_password():
    return login_window.lineedit_password.text()

app.exec_()