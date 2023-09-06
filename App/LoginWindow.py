from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QTextEdit, QComboBox, QWidget, \
    QMessageBox
from PyQt5.QtGui import QFont
import psycopg2
from TaskManangerWindow import TaskManagerWindow



class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Авторизация")
        self.setGeometry(750, 350, 400, 300)


        # ввод логина и пароля
        self.label_username = QLabel(self)
        self.label_username.setText("Почта:")
        self.label_username.move(50, 50)
        self.label_username.setFont(QFont("Arial", 12))

        self.lineedit_username = QLineEdit(self)
        self.lineedit_username.setGeometry(150, 50, 200, 30)
        self.lineedit_username.setFont(QFont("Arial", 12))

        self.label_password = QLabel(self)
        self.label_password.setText("Пароль:")
        self.label_password.move(50, 100)
        self.label_password.setFont(QFont("Arial", 12))

        self.lineedit_password = QLineEdit(self)
        self.lineedit_password.setGeometry(150, 100, 200, 30)
        self.lineedit_password.setEchoMode(QLineEdit.Password)
        self.lineedit_password.setFont(QFont("Arial", 12))

        self.button_login = QPushButton(self)
        self.button_login.setText("Login")
        self.button_login.setGeometry(150, 150, 100, 30)
        self.button_login.setFont(QFont("Arial", 12))
        self.button_login.clicked.connect(self.login)

    def login(self):
        username = self.lineedit_username.text()
        password = self.lineedit_password.text()
        conn = psycopg2.connect(database="Boss", user="postgres", password="postgres", host="localhost",
                                port="5432")
        cur = conn.cursor()
        cur.execute("SELECT * FROM workers WHERE email=%s AND password=%s", (username, password))
        row = cur.fetchone()
        print(row)
        if row is not None:
            self.close()
            self.taskWindow = TaskManagerWindow()
            self.taskWindow.show()

        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Неправильный логин или пароль")
            msg.setWindowTitle("Ошибка авторизации")
            msg.exec_()

