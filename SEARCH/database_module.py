import pymysql.cursors
import yaml


class mysql_writer():
    def __init__(self, sql_string):
        with open("./yaml/DBlist.yaml", 'r') as stream:
            self.DBLogin = yaml.safe_load(stream)
        self.sql_string = sql_string
        self.result = True
        self.mysql_writer()

    def mysql_writer(self):
        """
        Запись данных в БД
        """
        DBLogin = self.DBLogin
        connection = pymysql.connect(host=DBLogin[0], port=DBLogin[1], user=DBLogin[2], password=DBLogin[3],
                                     db=DBLogin[4], cursorclass=pymysql.cursors.DictCursor, autocommit=False)
        try:
            cursor = connection.cursor()
            cursor.execute(self.sql_string)
        except pymysql.err.IntegrityError:
            self.result = False
        except:
            connection.rollback()
            connection.close()
            raise
        else:
            connection.commit()
            connection.close()
