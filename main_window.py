# main_window.py
import sys
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QTableWidget, \
    QTableWidgetItem, QLineEdit, QPushButton, QMessageBox, QApplication, QCheckBox, QFrame
from PyQt5.QtCore import Qt
from db_helper import DB, DB_CONFIG
from trash_dialog import TrashDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("소매하는다람쥐 둔산1호점 재고 관리")
        self.db = DB(**DB_CONFIG)

        # 중앙 위젯 및 레이아웃
        self.resize(620, 520)
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

        # 입력 폼과 목록 조작 영역 사이의 구분선
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)

        # 목록 조작 영역
        list_controls = QHBoxLayout()

        self.check_all = QCheckBox("전체 선택")
        self.check_all.stateChanged.connect(self.set_all_checked)

        self.btn_soft_delete = QPushButton("선택 삭제")
        self.btn_soft_delete.clicked.connect(self.soft_delete_selected_items)

        self.btn_trash = QPushButton("휴지통 열기")
        self.btn_trash.clicked.connect(self.open_trash)

        list_controls.addWidget(self.check_all)
        list_controls.addWidget(self.btn_soft_delete)
        list_controls.addStretch()
        list_controls.addWidget(self.btn_trash)

        # 상품 목록 테이블
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["선택", "ID", "이름", "가격", "재고"])
        self.table.setEditTriggers(self.table.NoEditTriggers)  # 표준 예시: 목록은 읽기 전용
        self.table.verticalHeader().setVisible(False)

        # 배치
        vbox.addLayout(form_box)
        vbox.addWidget(separator)
        vbox.addLayout(list_controls)
        vbox.addWidget(self.table)

        # 초기 데이터 로드
        self.load_items()

    def load_items(self):
        rows = self.db.fetch_items()

        self.check_all.blockSignals(True)
        self.check_all.setChecked(False)
        self.check_all.blockSignals(False)

        self.table.setRowCount(len(rows))
        for r, (iid, name, price, stock) in enumerate(rows):
            check_item = QTableWidgetItem()
            check_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable)
            check_item.setCheckState(Qt.Unchecked)

            self.table.setItem(r, 0, check_item)
            self.table.setItem(r, 1, QTableWidgetItem(str(iid)))
            self.table.setItem(r, 2, QTableWidgetItem(name))
            self.table.setItem(r, 3, QTableWidgetItem(str(price)))
            self.table.setItem(r, 4, QTableWidgetItem(str(stock)))
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

    def set_all_checked(self, state):
        check_state = Qt.Checked if state == Qt.Checked else Qt.Unchecked

        for row in range(self.table.rowCount()):
            self.table.item(row, 0).setCheckState(check_state)

    def soft_delete_selected_items(self):
        item_ids = self._get_checked_item_ids()

        if not item_ids:
            QMessageBox.warning(self, "오류", "삭제할 상품을 선택하세요.")
            return

        # 소프트 삭제는 확인 메시지 없이 즉시 처리
        if self.db.soft_delete_items(item_ids):
            self.load_items()
        else:
            QMessageBox.critical(self, "실패", "삭제 중 오류가 발생했습니다.")

    def open_trash(self):
        dialog = TrashDialog(self)
        dialog.exec_()

        # 휴지통에서 복원한 상품이 있을 수 있으므로 목록 갱신
        self.load_items()

    def _get_checked_item_ids(self):
        item_ids = []

        for row in range(self.table.rowCount()):
            check_item = self.table.item(row, 0)

            if check_item.checkState() == Qt.Checked:
                item_id = int(self.table.item(row, 1).text())
                item_ids.append(item_id)
        return item_ids

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MainWindow()
    myWindow.show()
    app.exec_()