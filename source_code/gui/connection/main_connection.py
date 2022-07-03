from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from database import models
from gui.windows import main_window


class MainWindow(QtWidgets.QMainWindow, main_window.Ui_MainWindow):
    def __init__(self, database, config, utils, excel):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        self.database = database
        self.config = config
        self.utils = utils
        self.excel = excel

        self.add_table.clicked.connect(self.show_add_page)
        self.open_table.clicked.connect(self.show_table)
        self.change_table.clicked.connect(self.show_choice_page)

        self.back_button.clicked.connect(self.to_back_page)
        self.back_button_2.clicked.connect(self.to_back_page)
        self.back_button_3.clicked.connect(self.to_back_page)
        self.back_button_4.clicked.connect(self.to_back_page)
        self.back_button_5.clicked.connect(self.to_back_page)
        self.back_button_6.clicked.connect(self.to_back_page)
        self.back_button_7.clicked.connect(self.to_back_page)
        self.back_button_8.clicked.connect(self.to_back_page)

        self.select_table.clear()
        self.select_table.addItems(self.database.get_tables_name())

        self.add_street_button.clicked.connect(self.add_elements)
        self.add_account_button.clicked.connect(self.add_elements)
        self.add_service_button.clicked.connect(self.add_elements)
        self.add_accrual_button.clicked.connect(self.add_elements)

        self.delete_table.clicked.connect(self.fill_list)
        self.delete_button.clicked.connect(self.delete_by_id)

        self.open_change.clicked.connect(self.show_change_page)
        self.change_button.clicked.connect(self.change_elements)

        self.save_table.clicked.connect(self.show_output_page)
        self.output_button.clicked.connect(self.output_to_file)

    def to_back_page(self):
        self.stackedWidget.setCurrentIndex(0)

    def show_output_page(self):
        self.stackedWidget.setCurrentIndex(8)

    def output_to_file(self):
        select_extension = self.select_extension.currentText()
        select_output_type = self.select_output_type.currentText()
        select_table = self.select_table.currentText()
        output_templates = self.config.get_output_templates(self.database, select_table, select_extension,
                                                            select_output_type)

        if select_extension == "EXCEL":
            self.output_to_excel(*output_templates)
        elif select_extension == "JSON":
            self.output_to_json(*output_templates)

    def output_to_json(self, data_from_database, fields):
        data = []

        for row in data_from_database:
            data.append({key: value for key, value in zip(tuple(fields), row)})

        file_path = QFileDialog.getOpenFileName(self, "Выбор JSON-файла", "./", "Image(*.json)")[0]

        if file_path:
            self.utils.save_to_json(file_path, data)
            self.stackedWidget.setCurrentIndex(0)

    def output_to_excel(self, data_from_database, header, fields):
        self.excel.create_workbook()
        file_path = QFileDialog.getOpenFileName(self, "Выбор EXCEL-файла", "./", "Image(*.xlsx)")[0]

        if file_path:
            self.excel.sheet.title = header
            self.excel.sheet.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(data_from_database[0]))

            self.excel.sheet["A1"] = header
            self.excel.set_sheet_styles(1)

            self.excel.sheet.append(fields)
            self.excel.set_sheet_styles(2)

            for index, value in enumerate(data_from_database, 3):
                self.excel.sheet.append(tuple(map(str, value)))

                for cell in self.excel.sheet[index]:
                    cell.border = self.excel.full_border
                    cell.alignment = self.excel.alignment_center

            try:
                self.excel.workbook.save(filename=file_path)
                self.stackedWidget.setCurrentIndex(0)
            except PermissionError:
                QMessageBox.warning(self, "ОШИБКА", "Закройте выбранный файл")

    def change_elements(self):
        table = self.config.get_table_fields(self.select_table.currentText())
        type_change = table[self.type_change.currentText()]
        id_change = int(self.id_change.currentText())
        new_change = self.new_change.toPlainText()

        with Session(self.database.engine) as session:
            session.query(table["default"]).filter(table["default"].id == id_change).update({type_change: new_change})
            session.commit()
        self.stackedWidget.setCurrentIndex(0)

    def show_change_page(self):
        self.id_select_change.clear()
        self.type_select_change.clear()
        self.new_change.clear()

        id_change = self.id_change.currentText()
        select_table = self.select_table.currentText()
        type_change = self.type_change.currentText()
        current_table = self.config.get_table_fields(select_table)
        new_change_text = self.database.select_query(select(current_table[type_change]
                                                            ).where(current_table["default"].id == id_change), 2)

        self.new_change.setText(str(new_change_text))
        self.id_select_change.setText(f"ID: {id_change}")
        self.type_select_change.setText(f"Изменяемое поле: {type_change}")

        self.stackedWidget.setCurrentIndex(7)

    def show_choice_page(self):
        self.id_change.clear()
        self.type_change.clear()

        select_table = self.select_table.currentText()
        current_table = self.config.get_table_fields(select_table)["default"]

        ids = [str(index) for index in self.database.select_query(select(current_table.id), 1)]
        types = [column.key for column in current_table.__table__.columns if column.key.find("id") == -1]

        self.id_change.addItems(ids)
        self.type_change.addItems(types)

        self.stackedWidget.setCurrentIndex(6)

    def delete_by_id(self):
        select_table = self.select_table.currentText()
        current_table = self.config.get_table_fields(select_table)["default"]
        id_input_delete = self.id_input_delete.text()

        self.database.engine_connect(delete(current_table).where(current_table.id == id_input_delete))
        self.stackedWidget.setCurrentIndex(0)

    def fill_list(self):
        self.id_list_delete.clear()

        select_table = self.select_table.currentText()
        current_table = self.config.get_table_fields(select_table)["default"]

        self.id_list_delete.addItems([str(index) for index in self.database.select_query(select(current_table.id), 1)])
        self.stackedWidget.setCurrentIndex(5)

    def show_table(self):
        if self.select_table.currentText() == "streets":
            self.table_data.clear()

            ids = self.database.select_query(select(models.Street.id), 1)
            names = self.database.select_query(select(models.Street.name), 1)

            self.table_data.setColumnCount(2)
            self.table_data.setRowCount(len(ids))

            self.utils.fill_table(self.table_data, ids, 0)
            self.utils.fill_table(self.table_data, names, 1)

        elif self.select_table.currentText() == "accounts":
            self.table_data.clear()

            ids = self.database.select_query(select(models.Account.id), 1)
            numbers = self.database.select_query(select(models.Account.number), 1)
            street_ids = self.database.select_query(select(models.Account.street_id), 1)
            houses = self.database.select_query(select(models.Account.house), 1)
            frames = self.database.select_query(select(models.Account.frame), 1)
            flats = self.database.select_query(select(models.Account.flat), 1)
            full_names = self.database.select_query(select(models.Account.full_name), 1)

            self.table_data.setColumnCount(7)
            self.table_data.setRowCount(len(ids))

            self.utils.fill_table(self.table_data, ids, 0)
            self.utils.fill_table(self.table_data, numbers, 1)
            self.utils.fill_table(self.table_data, street_ids, 2)
            self.utils.fill_table(self.table_data, houses, 3)
            self.utils.fill_table(self.table_data, frames, 4)
            self.utils.fill_table(self.table_data, flats, 5)
            self.utils.fill_table(self.table_data, full_names, 6)

        elif self.select_table.currentText() == "services":
            self.table_data.clear()

            ids = self.database.select_query(select(models.Service.id), 1)
            names = self.database.select_query(select(models.Service.name), 1)
            rates = self.database.select_query(select(models.Service.rate), 1)

            self.table_data.setColumnCount(3)
            self.table_data.setRowCount(len(ids))

            self.utils.fill_table(self.table_data, ids, 0)
            self.utils.fill_table(self.table_data, names, 1)
            self.utils.fill_table(self.table_data, rates, 2)

        elif self.select_table.currentText() == "accruals":
            self.table_data.clear()

            ids = self.database.select_query(select(models.Accrual.id), 1)
            accounts_ids = self.database.select_query(select(models.Accrual.account_id), 1)
            service_ids = self.database.select_query(select(models.Accrual.service_id), 1)
            quantities = self.database.select_query(select(models.Accrual.quantity), 1)

            self.table_data.setColumnCount(4)
            self.table_data.setRowCount(len(ids))

            self.utils.fill_table(self.table_data, ids, 0)
            self.utils.fill_table(self.table_data, accounts_ids, 1)
            self.utils.fill_table(self.table_data, service_ids, 2)
            self.utils.fill_table(self.table_data, quantities, 3)

    def show_add_page(self):
        if self.select_table.currentText() == "streets":
            self.id_street.clear()
            self.name_street.clear()

            self.id_street.setText(self.database.get_last_index(models.Street.id))

            self.stackedWidget.setCurrentIndex(1)

        elif self.select_table.currentText() == "accounts":
            self.id_account.clear()
            self.number_account.clear()
            self.id_street_account.clear()
            self.house_account.clear()
            self.frame_account.clear()
            self.flat_account.clear()
            self.full_name_account.clear()

            self.id_account.setText(self.database.get_last_index(models.Account.id))
            self.id_street_account.addItems(self.database.select_query(select(models.Street.name), 1))

            self.stackedWidget.setCurrentIndex(2)

        elif self.select_table.currentText() == "services":
            self.id_service.clear()
            self.name_service.clear()
            self.rate_service.clear()

            self.id_service.setText(self.database.get_last_index(models.Service.id))

            self.stackedWidget.setCurrentIndex(3)

        elif self.select_table.currentText() == "accruals":
            self.id_accrual.clear()
            self.id_account_accrual.clear()
            self.id_service_accrual.clear()
            self.quantity_accrual.clear()

            self.id_accrual.setText(self.database.get_last_index(models.Accrual.id))
            self.id_account_accrual.addItems(self.database.select_query(select(models.Account.number), 1))
            self.id_service_accrual.addItems(self.database.select_query(select(models.Service.name), 1))

            self.stackedWidget.setCurrentIndex(4)

    def add_elements(self):
        try:
            if self.select_table.currentText() == "streets":
                id_street = self.id_street.text()
                name = self.name_street.text()

                self.database.insert_query(models.Street, id_street, name)
                self.stackedWidget.setCurrentIndex(0)
                self.show_table()

            elif self.select_table.currentText() == "accounts":
                id_account = self.id_account.text()
                number = self.number_account.text()
                id_street = int(self.database.select_query(
                    select(models.Street.id).where(models.Street.name == self.id_street_account.currentText()), 2))
                house = self.house_account.text()
                frame = self.frame_account.text()
                flat = self.flat_account.text()
                full_name = self.full_name_account.text()

                self.database.insert_query(models.Account, id_account, number, id_street, house, frame, flat, full_name)
                self.stackedWidget.setCurrentIndex(0)
                self.show_table()

            elif self.select_table.currentText() == "services":
                id_service = self.id_service.text()
                name = self.name_service.text()
                rate = self.rate_service.text()

                self.database.insert_query(models.Service, id_service, name, rate)
                self.stackedWidget.setCurrentIndex(0)
                self.show_table()

            elif self.select_table.currentText() == "accruals":
                id_accrual = self.id_accrual.text()

                id_account = int(self.database.select_query(
                    select(models.Account.id).where(models.Account.number == self.id_account_accrual.currentText()), 2))

                id_service = int(self.database.select_query(
                    select(models.Service.id).where(models.Service.name == self.id_service_accrual.currentText()), 2))

                quantity = self.quantity_accrual.text()
                self.database.insert_query(models.Accrual, id_accrual, id_account, id_service, quantity)

                self.stackedWidget.setCurrentIndex(0)
                self.show_table()
        except TypeError:
            QMessageBox.warning(self, "ОШИБКА", "Заполните все поля")
