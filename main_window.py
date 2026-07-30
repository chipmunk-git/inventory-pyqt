# main_window.py
import sys
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QFormLayout, QTableWidget, QTableWidgetItem, \
    QLineEdit, QPushButton, QMessageBox, QApplication
from db_helper import DB, DB_CONFIG

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("소매하는다람쥐 둔산1호점 재고 관리")
        self.db = DB(**DB_CONFIG)

        # 중앙 위젯 및 레이아웃
        central = QWidget()
        self.setCentralWidget(central)
        vbox = QVBoxLayout(central)

        # 상단: 입력 폼 + 추가 버튼
        self.input_name = QLineEdit()
        self.input_price = QLineEdit()
        self.input_stock = QLineEdit()

        form = QFormLayout()
        form.addRow("이름", self.input_name)
        form.addRow("가격", self.input_price)
        form.addRow("재고", self.input_stock)

        self.btn_add = QPushButton("추가")
        self.btn_add.clicked.connect(self.add_item)

        form_box = QVBoxLayout()
        form_box.addLayout(form)
        form_box.addWidget(self.btn_add)

        # 중앙: 테이블 위젯
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "이름", "가격", "재고"])
        self.table.setEditTriggers(self.table.NoEditTriggers)  # 표준 예시: 목록은 읽기 전용
        self.table.verticalHeader().setVisible(False)

        # 배치
        vbox.addLayout(form_box)
        vbox.addWidget(self.table)

        # 초기 데이터 로드
        self.load_items()

    def load_items(self):
        rows = self.db.fetch_items()
        self.table.setRowCount(len(rows))
        for r, (iid, name, price, stock) in enumerate(rows):
            self.table.setItem(r, 0, QTableWidgetItem(str(iid)))
            self.table.setItem(r, 1, QTableWidgetItem(name))
            self.table.setItem(r, 2, QTableWidgetItem(str(price)))
            self.table.setItem(r, 3, QTableWidgetItem(str(stock)))
        self.table.resizeColumnsToContents()

    def add_item(self):
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
        ok = self.db.insert_item(name, price, stock)
        if ok:
            QMessageBox.information(self, "완료", "추가되었습니다.")
            self.input_name.clear()
            self.input_price.clear()
            self.input_stock.clear()
            self.load_items()
        else:
            QMessageBox.critical(self, "실패", "추가 중 오류가 발생했습니다.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MainWindow()
    myWindow.show()
    app.exec_()