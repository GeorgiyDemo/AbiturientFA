import pymysql.cursors
import yaml

class MySQLClass():
    """Базовый класс"""
    def __init__(self):
        with open("./yaml/DBlist.yaml", 'r') as stream:
            DBLogin = yaml.safe_load(stream)
        connection = pymysql.connect(host=DBLogin[0], port=DBLogin[1], user=DBLogin[2], password=DBLogin[3],
                db=DBLogin[4], cursorclass=pymysql.cursors.DictCursor)
        self.connection = connection
        self.cursor = connection.cursor()
        self.result = None


class MySQLWriter(MySQLClass):
    """Запись данных в СУБД"""
    def __init__(self, sql_string):
        super().__init__()
        self.sql_string = sql_string
        self.processing()

    def processing(self):
        cursor = self.cursor
        cursor.execute(self.sql_string)
        self.connection.commit()
        self.connection.close()

class MySQLReaderOne(MySQLClass):
    """Получение одного значения с СУБД"""
    def __init__(self, sql_string):
        super().__init__()
        self.sql_string = sql_string
        self.processing()

    def processing(self):
        cursor = self.cursor
        cursor.execute(self.sql_string)
        result = cursor.fetchone()
        self.result = result

class MySQLReaderAll(MySQLClass):
    """Получение всех значение с СУБД"""
    def __init__(self, sql_string):
        super().__init__()
        self.sql_string = sql_string
        self.processing()

    def processing(self):
        cursor = self.cursor
        cursor.execute(self.sql_string)
        result = cursor.fetchall()
        self.result = result