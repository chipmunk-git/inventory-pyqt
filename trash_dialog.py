# trash_dialog.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, \
    QMessageBox, QCheckBox
from PyQt5.QtCore import Qt
from db_helper import DB, DB_CONFIG

class TrashDialog(QDialog):
    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("휴지통")
        self.db = DB(**DB_CONFIG)

        self.user_id = user_id

        self.resize(650, 400)
        vbox = QVBoxLayout(self)

        # 휴지통 목록 조작 영역
        controls = QHBoxLayout()

        self.check_all = QCheckBox("전체 선택")
        self.check_all.stateChanged.connect(self.set_all_checked)

        self.btn_restore = QPushButton("선택 복원")
        self.btn_restore.clicked.connect(self.restore_selected_items)

        self.btn_permanent_delete = QPushButton("선택 영구 삭제")
        self.btn_permanent_delete.clicked.connect(self.permanently_delete_selected_items)

        self.btn_close = QPushButton("닫기")
        self.btn_close.clicked.connect(self.accept)

        controls.addWidget(self.check_all)
        controls.addWidget(self.btn_restore)
        controls.addWidget(self.btn_permanent_delete)
        controls.addStretch()
        controls.addWidget(self.btn_close)

        # 휴지통 테이블
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["선택", "ID", "이름", "가격", "재고", "삭제 일시"])
        self.table.setEditTriggers(self.table.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)

        vbox.addLayout(controls)
        vbox.addWidget(self.table)

        self.load_deleted_items()

    def load_deleted_items(self):
        rows = self.db.fetch_deleted_items(self.user_id)

        self.check_all.blockSignals(True)
        self.check_all.setChecked(False)
        self.check_all.blockSignals(False)

        self.table.setRowCount(len(rows))
        for r, (iid, name, price, stock, deleted_at) in enumerate(rows):
            check_item = QTableWidgetItem()
            check_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable)
            check_item.setCheckState(Qt.Unchecked)

            if hasattr(deleted_at, "strftime"):
                deleted_at_text = deleted_at.strftime("%Y-%m-%d %H:%M:%S")
            else:
                deleted_at_text = str(deleted_at)

            self.table.setItem(r, 0, check_item)
            self.table.setItem(r, 1, QTableWidgetItem(str(iid)))
            self.table.setItem(r, 2, QTableWidgetItem(name))
            self.table.setItem(r, 3, QTableWidgetItem(str(price)))
            self.table.setItem(r, 4, QTableWidgetItem(str(stock)))
            self.table.setItem(r, 5, QTableWidgetItem(deleted_at_text))
        self.table.resizeColumnsToContents()

    def set_all_checked(self, state):
        check_state = Qt.Checked if state == Qt.Checked else Qt.Unchecked

        for row in range(self.table.rowCount()):
            self.table.item(row, 0).setCheckState(check_state)

    def restore_selected_items(self):
        item_ids = self._get_checked_item_ids()

        if not item_ids:
            QMessageBox.warning(self, "오류", "복원할 상품을 선택하세요.")
            return

        if self.db.restore_items(self.user_id, item_ids):
            self.load_deleted_items()
        else:
            QMessageBox.critical(self, "실패", "복원 중 오류가 발생했습니다.")

    def permanently_delete_selected_items(self):
        item_ids = self._get_checked_item_ids()

        if not item_ids:
            QMessageBox.warning(self, "오류", "완전히 삭제할 상품을 선택하세요.")
            return

        answer = QMessageBox.question(
            self,
            "영구 삭제",
            f"선택한 상품 {len(item_ids)}개를 완전히 삭제하시겠습니까?\n"
            "이 작업은 되돌릴 수 없습니다.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if answer != QMessageBox.Yes:
            return

        if self.db.permanently_delete_items(self.user_id, item_ids):
            self.load_deleted_items()
        else:
            QMessageBox.critical(self, "실패", "영구 삭제 중 오류가 발생했습니다.")

    def _get_checked_item_ids(self):
        item_ids = []

        for row in range(self.table.rowCount()):
            check_item = self.table.item(row, 0)

            if check_item.checkState() == Qt.Checked:
                item_id = int(self.table.item(row, 1).text())
                item_ids.append(item_id)
        return item_ids