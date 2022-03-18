import mysql.connector
import configparser
import os
import platform


def getpath():
    config_path = None

    if platform.system() == "Windows":
        config_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "\\config\\config.ini"
    elif platform.system() == "Linux":
        config_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/config/config.ini"
    return config_path


c_parser = configparser.ConfigParser()
c_parser.read(getpath())

host = c_parser.get('Database', 'host')
user = c_parser.get('Database', 'user')
password = c_parser.get('Database', 'pass')
db = c_parser.get('Database', 'db')


class Connector:
    def __init__(self, host, user, password, db):
        self.database = mysql.connector.connect(host=host, user=user, password=password, autocommit=True)
        self.cursor = self.database.cursor()
        self.cursor.execute(f"USE {db}")

    def fetchall(self):
        return self.cursor.fetchall()

    def execute(self, script):
        self.cursor.execute(script)



database = Connector(host, user, password, db)
