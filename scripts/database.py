import mysql.connector
import configparser
import os


def getpath():
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config')


c_parser = configparser.ConfigParser()
c_parser.read(getpath()+'/config.ini')

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
