from sqlalchemy import select

from database import models


class Config:
    @staticmethod
    def get_fields(table):
        table_fields = {
            "streets": ["№", "Название"],
            "accounts": ["Код", "№", "№ улицы", "Дом", "Корпус", "Квартира", "ФИО"],
            "services": ["№", "Название", "Тариф"],
            "accruals": ["№", "№ счета", "№ услуги", "Количество"],
            "accounts_by_streets": ["№ счета", "Адрес"],
            "notice": ["№ счета", "Улица", "Дом", "Корпус", "Квартира", "ФИО", "Услуга", "Стоимость"]
        }

        return table_fields[table]

    @staticmethod
    def get_table_fields(table):
        table_field_models = {
            "streets": {
                "default": models.Street,
                "name": models.Street.name
            },
            "accounts": {
                "default": models.Account,
                "number": models.Account.number,
                "street_id": models.Account.street_id,
                "house": models.Account.house,
                "frame": models.Account.frame,
                "flat": models.Account.flat,
                "full_name": models.Account.full_name
            },
            "services": {
                "default": models.Service,
                "name": models.Service.name,
                "rate": models.Service.rate
            },
            "accruals": {
                "default": models.Accrual,
                "account_id": models.Accrual.account_id,
                "service_id": models.Accrual.service_id,
                "quantity": models.Accrual.quantity
            }
        }

        return table_field_models[table]

    def get_output_templates(self, database, select_table, select_extension, select_output_type):
        stmt = select(self.get_table_fields(select_table)["default"])

        output_templates = {
            "JSON": {
                "Лицевые счета": (database.get_accounts_by_streets(), self.get_fields("accounts_by_streets")),
                "Извещение": (database.get_notice(), self.get_fields("notice")),
                "Таблица": (database.select_query(stmt, 3), self.get_fields(select_table))
            },
            "EXCEL": {
                "Лицевые счета": (database.get_accounts_by_streets(), "Лицевые счета",
                                  self.get_fields("accounts_by_streets")),

                "Извещение": (database.get_notice(), "Извещение", self.get_fields("notice")),
                "Таблица": (database.select_query(stmt, 3), "Таблица", self.get_fields(select_table))
            }
        }

        return output_templates[select_extension][select_output_type]
