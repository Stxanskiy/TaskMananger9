from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QMainWindow, QTableWidget, QTableWidgetItem, QPushButton, QDialog, QFormLayout, QLineEdit, QComboBox
from PyQt5.QtCore import Qt
import psycopg2

class TaskManagerWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # установка заголовка окна
        self.setWindowTitle("Мененджер задач ")

        # установка размеров окна
        self.setMinimumWidth(1920)
        self.setMinimumHeight(1080)

        # создание таблицы для отображения задач
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Номер задачи", "Название задачи", "Описание", "Статус", "Редактирование", "Удаление"])
        self.setCentralWidget(self.table)
        font = QFont("Arial", 12)
        self.table.setFont(font)




        # создание кнопки для добавления новых задач
        self.add_button = QPushButton("Добавить задачу")
        self.add_button.clicked.connect(self.add_task)
        self.add_button.setFixedSize(200,50)
        font = QFont("Arial", 12)
        self.table.setFont(font)

        #создание кнокпи для нового сотрцудника компании
        self.add_worker =QPushButton("Новый сотрудник ")
        self.add_worker.clicked.connect(self.add_task)
        self.add_worker.setFixedSize(200, 50)
        font = QFont("Times new roman", 12)
        self.table.setFont(font)



        # создание кнопки для показа задач, присвоенных только выбранному пользователю
        self.show_user_tasks_button = QPushButton("Посмотреть задачи сотрудников")
        self.show_user_tasks_button.clicked.connect(self.show_user_tasks)
        self.show_user_tasks_button.setFixedSize(250, 50)
        font = QFont("Arial", 12)
        self.table.setFont(font)

        # создание кнопки для очистки списка задач
        self.clear_tasks_button = QPushButton("Очистить задачи")
        self.clear_tasks_button.clicked.connect(self.clear_tasks)
        self.clear_tasks_button.setFixedSize(200, 50)
        font = QFont("Arial", 12)
        self.table.setFont(font)

        # добавление кнопок на панель инструментов
        toolbar = self.addToolBar("Настроки")
        toolbar.addWidget(self.add_button)
        toolbar.addWidget(self.show_user_tasks_button)
        toolbar.addWidget(self.clear_tasks_button)
        toolbar.addWidget(self.add_worker)

        # подключение к базе данных PostgreSQL
        self.conn = psycopg2.connect(
            host="localhost",
            database="Boss",
            user="postgres",
            password="postgres"
        )

        # получение списка задач из базы данных
        self.get_tasks()

    def get_tasks(self):
        # запрос на получение списка задач из базы данных
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM tasks")
        tasks = cur.fetchall()

        # очистка таблицы
        self.table.setRowCount(0)

        # заполнение таблицы данными
        for task in tasks:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            for i, item in enumerate(task):
                self.table.setItem(row_position, i, QTableWidgetItem(str(item)))

            # создание кнопок для удаления и редактирования задачи
            edit_button = QPushButton("Редактировать")
            edit_button.clicked.connect(lambda checked, row=row_position: self.edit_task(row))
            self.table.setCellWidget(row_position, 4, edit_button)

            delete_button = QPushButton("Удалить")
            delete_button.clicked.connect(lambda checked, row=row_position: self.delete_task(row))
            self.table.setCellWidget(row_position, 5, delete_button)

            # автоматическое изменение ширины колонки с задачами в зависимости от текста
            self.table.resizeColumnToContents(2)

    def add_task(self):
        # создание диалогового окна для добавления новой задачи
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить задачу")

        # создание формы для ввода данных о задаче
        form_layout = QFormLayout()

        title_input = QLineEdit()
        form_layout.addRow("Задачи", title_input)

        description_input = QLineEdit()
        form_layout.addRow("Описание:", description_input)

        status_input = QLineEdit()
        form_layout.addRow("Статус задачи:", status_input)

        # создание выпадающего списка для выбора сотрудника, которому нужно присвоить задачу
        worker_id_input = QComboBox()
        cur = self.conn.cursor()
        cur.execute("SELECT id, name FROM workers")
        workers = cur.fetchall()
        for worker in workers:
            worker_id_input.addItem(f"{worker[1]} ({worker[0]})", worker[0])
        form_layout.addRow("Сотрудники:", worker_id_input)

        dialog.setLayout(form_layout)

        # создание кнопок для сохранения и отмены
        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(
            lambda: self.save_task(dialog, title_input.text(), description_input.text(), status_input.text(),
                                   worker_id_input.currentData()))

        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(dialog.reject)

        # добавление кнопок на форму
        form_layout.addRow(save_button, cancel_button)

        # отображение диалогового окна
        dialog.exec_()

    def save_task(self, dialog, title, description, status, worker_id):
        # запрос на добавление новой задачи в базу данных
        cur = self.conn.cursor()
        cur.execute("INSERT INTO tasks (title, description, status, worker_id) VALUES (%s, %s, %s, %s)",
                    (title, description, status, worker_id))
        self.conn.commit()

        # обновление списка задач на главной форме
        self.get_tasks()

        # закрытие диалогового окна
        dialog.accept()

    def edit_task(self, row):
        # получение ID задачи из таблицы
        task_id = int(self.table.item(row, 0).text())

        # получение данных о задаче из базы данных
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
        task = cur.fetchone()

        # создание диалогового окна для редактирования задачи
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit")

        # создание формы для ввода данных о задаче
        form_layout = QFormLayout()

        title_input = QLineEdit(str(task[1]))
        form_layout.addRow("Наименование:", title_input)

        description_input = QLineEdit(str(task[2]))
        form_layout.addRow("Описание:", description_input)

        status_input = QLineEdit(str(task[3]))
        form_layout.addRow("Статус", status_input)

        # создание выпадающего списка для выбора сотрудника, которому нужно присвоить задачу
        worker_id_input = QComboBox()
        cur.execute("SELECT id, name FROM workers")
        workers = cur.fetchall()
        for worker in workers:
            worker_id_input.addItem(f"{worker[1]} ({worker[0]})", worker[0])
        worker_id_input.setCurrentIndex(worker_id_input.findData(task[4]))
        form_layout.addRow("Worker:", worker_id_input)

        dialog.setLayout(form_layout)

        # создание кнопок для сохранения и отмены
        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(
            lambda: self.update_task(dialog, task_id, title_input.text(), description_input.text(), status_input.text(),
                                     worker_id_input.currentData()))

        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(dialog.reject)

        # добавление кнопок на форму
        form_layout.addRow(save_button, cancel_button)

        # отображение диалогового окна
        dialog.exec_()

    def update_task(self, dialog, task_id, title, description, status, worker_id):
        # запрос на обновление данных о задаче в базе данных
        cur = self.conn.cursor()
        cur.execute("UPDATE tasks SET title = %s, description = %s, status = %s, worker_id = %s WHERE id = %s",
                    (title, description, status, worker_id, task_id))
        self.conn.commit()

        # обновление списка задач на главной форме
        self.get_tasks()

        # закрытие диалогового окна
        dialog.accept()

    def delete_task(self, row):
        # получение ID задачи из таблицы
        task_id = int(self.table.item(row, 0).text())

        # запрос на удаление задачи из базы данных
        cur = self.conn.cursor()
        cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        self.conn.commit()

        # удаление строки из таблицы на главной форме
        self.table.removeRow(row)

    def clear_tasks(self):
        # запрос на удаление всех задач из базы данных
        cur = self.conn.cursor()
        cur.execute("DELETE FROM tasks")
        self.conn.commit()

        # обновление списка задач на главной форме
        self.get_tasks()

    def show_user_tasks(self):
        # создание диалогового окна для выбора сотрудника
        dialog = QDialog(self)
        dialog.setWindowTitle("Показать Задачи сотрудника")

        # создание выпадающего списка для выбора сотрудника
        worker_id_input = QComboBox()
        cur = self.conn.cursor()
        cur.execute("SELECT id, name FROM workers")
        workers = cur.fetchall()
        for worker in workers:
            worker_id_input.addItem(f"{worker[1]} ({worker[0]})", worker[0])

        # создание кнопок для показа задач и отмены
        show_button = QPushButton("Показать Задачи")
        show_button.clicked.connect(lambda: self.get_user_tasks(worker_id_input.currentData(), dialog))

        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(dialog.reject)

        # добавление выпадающего списка и кнопок на форму
        form_layout = QFormLayout()
        form_layout.addRow("Worker:", worker_id_input)
        form_layout.addRow(show_button, cancel_button)
        dialog.setLayout(form_layout)

        # отображение диалогового окна
        dialog.exec_()

    def get_user_tasks(self, worker_id, dialog):
        # запрос на получение списка задач, присвоенных выбранному сотруднику
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM tasks WHERE worker_id = %s", (worker_id,))
        tasks = cur.fetchall()

        # очистка таблицы
        self.table.setRowCount(0)

        # заполнение таблицы данными
        for task in tasks:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            for i, item in enumerate(task):
                self.table.setItem(row_position, i, QTableWidgetItem(str(item)))

            # создание кнопок для удаления и редактирования задачи
            edit_button = QPushButton("Редактировать")
            edit_button.clicked.connect(lambda checked, row=row_position: self.edit_task(row))
            self.table.setCellWidget(row_position, 4, edit_button)

            delete_button = QPushButton("Удалить")
            delete_button.clicked.connect(lambda checked, row=row_position: self.delete_task(row))
            self.table.setCellWidget(row_position, 5, delete_button)

        # автоматическое изменение ширины колонки с задачами в зависимости от текста
        self.table.resizeColumnToContents(4)
        # закрытие диалогового окна
        dialog.accept()


    #Метод для добавления нового сотрудника в баззу данных
