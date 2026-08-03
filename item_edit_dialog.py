# item_edit_dialog.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QPushButton, \
    QMessageBox
from db_helper import DB, DB_CONFIG

class ItemEditDialog(QDialog):
    def __init__(self, iid, name, price, stock, user_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("상품 수정")
        self.db = DB(**DB_CONFIG)

        self.user_id = user_id

        self.original_values = (name, price, stock)
        self.updated = False

        self.input_id = QLineEdit(str(iid))
        self.input_id.setReadOnly(True)

        self.input_name = QLineEdit(name)
        self.input_price = QLineEdit(str(price))
        self.input_stock = QLineEdit(str(stock))

        form = QFormLayout()
        form.addRow("ID", self.input_id)
        form.addRow("이름", self.input_name)
        form.addRow("가격", self.input_price)
        form.addRow("재고", self.input_stock)

        self.btn_update = QPushButton("수정")
        self.btn_update.clicked.connect(self.update_item)

        self.btn_cancel = QPushButton("취소")
        self.btn_cancel.clicked.connect(self.reject)

        buttons = QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(self.btn_update)
        buttons.addWidget(self.btn_cancel)

        vbox = QVBoxLayout(self)
        vbox.addLayout(form)
        vbox.addLayout(buttons)

    def update_item(self):
        name = self.input_name.text().strip()
        price = self.input_price.text().strip()
        stock = self.input_stock.text().strip()
        if not name or not price or not stock:
            QMessageBox.warning(self, "오류", "항목들을 모두 입력하세요.")
            return

        # 정수가 아닌 값에 대한 예외 처리
        try:
            price = int(price)
            stock = int(stock)
        except ValueError:
            QMessageBox.warning(self, "오류", "가격과 재고를 소수점 없는 숫자로 입력하세요.")
            return

        if price < 10 or price % 10 != 0:
            QMessageBox.warning(self, "오류", "가격을 10원 단위로 입력하세요.")
            return
        if stock < 0:
            QMessageBox.warning(self, "오류", "재고를 0개 이상 입력하세요.")
            return

        if (name, price, stock) == self.original_values:
            QMessageBox.information(self, "완료", "변경된 내용이 없습니다.")
            self.accept()
            return

        ok = self.db.update_item(self.user_id, int(self.input_id.text()), name, price, stock)
        if ok:
            self.updated = True
            QMessageBox.information(self, "완료", "수정되었습니다.")
            self.accept()
        else:
            QMessageBox.critical(self, "실패", "수정 중 오류가 발생했습니다.")