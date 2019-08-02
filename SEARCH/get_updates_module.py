import database_module
import pandas as pd

OUT_XLSX_FILE = "./OUTPUT/OUTPUT_TABLE.xlsx"


class table_processing():
    def __init__(self, result_array):
        print("*Модуль определения обновлений таблицы*\nПроверяем дубликаты по БД..")
        formated_arr = []
        for user_arr in result_array:
            self.table_check_method(user_arr)
            if self.dbflag == True:
                formated_arr.append(self.buf_list)
        self.xlsx_writer(formated_arr)

    def table_check_method(self, a):
        self.dbflag = False
        obj = database_module.mysql_writer(
            "INSERT INTO table_updates (number, fio, contesttype, score) VALUES ('" + str(a[1]) + "','" + a[3] + "','" +
            a[5] + "'," + str(a[6]) + ")")
        if obj.result == True:
            self.dbflag = True
            self.buf_list = [str(a[1]), a[3], a[5], str(a[6])]

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
        pd.DataFrame(final_list).T.to_excel(OUT_XLSX_FILE, encoding='utf-8', index=False)
