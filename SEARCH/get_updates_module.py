import database_module
import pandas as pd

OUT_XLSX_FILE = "./OUTPUT/OUTPUT_TABLE.xlsx"


class TableClass:
    def __init__(self, result_list):
        print("*Модуль определения обновлений таблицы*\nПроверяем дубликаты по БД..")
        formated_arr = []
        for user_arr in result_list:
            self.table_check_method(user_arr)
            if self.dbflag:
                formated_arr.append(self.buf_list)

        print("Занесли {} новых людей".format(len(formated_arr)))
        self.xlsx_writer(formated_arr)

    def table_check_method(self, a):
        self.dbflag = False
        obj = database_module.MySQLClass(
            "INSERT INTO table_updates (number, fio, contesttype, score) VALUES ('"
            + str(a[2])
            + "','"
            + a[3]
            + "','"
            + a[5]
            + "',"
            + str(a[7])
            + ")",
            1,
        )

        if obj.result:
            self.dbflag = True
            self.buf_list = [str(a[2]), a[3], a[5], str(a[7])]

    def xlsx_writer(self, l):

        # Хэх мда, пересортировка - дичь
        number_list = []
        fio_list = []
        contesttype_list = []
        score_list = []
        for u in l:
            number_list.append(u[0])
            fio_list.append(u[1])
            contesttype_list.append(u[2])
            score_list.append(u[3])

        final_list = [number_list, fio_list, contesttype_list, score_list]
        print("Заносим данные в Excel..")
        pd.DataFrame(final_list).T.to_excel(
            OUT_XLSX_FILE, encoding="utf-8", index=False
        )
