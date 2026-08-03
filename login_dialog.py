# login_dialog.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QMessageBox
from db_helper import DB, DB_CONFIG

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("로그인")
        self.db = DB(**DB_CONFIG)

        self.user_id = None

        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)

        form = QFormLayout()
        form.addRow("아이디", self.username)
        form.addRow("비밀번호", self.password)

        self.btn_login = QPushButton("로그인")
        self.btn_login.clicked.connect(self.try_login)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(self.btn_login)
        self.setLayout(layout)

    def try_login(self):
        uid = self.username.text().strip()
        pw = self.password.text().strip()
        if not uid or not pw:
            QMessageBox.warning(self, "오류", "아이디와 비밀번호를 모두 입력하세요.")
            return

        user_id = self.db.verify_user(uid, pw)
        if user_id is not None:
            self.user_id = user_id
            self.accept()
        else:
            QMessageBox.critical(self, "실패", "아이디 또는 비밀번호가 올바르지 않습니다.")