from time import time

import psycopg2
from psycopg2 import sql
from psycopg2.extras import DictCursor

from app.config import config

class Database:
    conn = None

    def __init__(self):
        conn = self.connect(config)
        if conn:
            self.conn = conn
        else:
            print("Нет подключения к БД")
            raise TypeError

    def __init_cursor(func):
        def the_wrapper_around_the_original_function(self, *args, **kwargs):
            cursor = None
            try:
                cursor = self.conn.cursor(cursor_factory=DictCursor)
            except AttributeError:
                return "Нет подключения к БД"

            try:
                return func(self, *args, **kwargs, cursor=cursor)
            except AttributeError:
                return "Нет подключения к БД"
            except Exception as e:
                bad_query = None
                if type(args[0]) == sql.Composed:
                    bad_query = args[0].as_string(self.conn)
                elif type(args[0]) == str:
                    bad_query = args[0]
                text_error = f"type: {type(e)}\narguments: {e.args}\ntext: {e}"
                self.__write_logs(bad_query, text_error, cursor=cursor)

                print(f"""
================POSTGRES_ERROR================
    type: {type(e)},
    arguments: {e.args},
    text: {e},
    time: {time()},
    bad_query: {bad_query}
==============================================
                """)

                return "Ошибка при обращении к БД"

        return the_wrapper_around_the_original_function

    def __write_logs(self, bad_query, textError, cursor):
        query = "INSERT INTO {table}({fields}, time) VALUES({values}, now());"
        values = {
            "table": sql.Identifier("logs_bad_query"),
            "fields": sql.SQL(',').join(sql.Identifier(i) for i in ["query", "text_error"]),
            "values": sql.SQL(',').join(sql.Literal(i) for i in [bad_query, textError])
        }
        print(sql.SQL(query).format(**values).as_string(self.conn))
        cursor.execute(sql.SQL(query).format(**values))

    def connect(self, config):
        """Connect to database PostgreSQL"""
        try:
            conn = psycopg2.connect(
                dbname=str(config['POSTGRES']['POSTGRES_DATABASE_NAME']),
                user=str(config['POSTGRES']['POSTGRES_USERNAME']),
                password=str(config['POSTGRES']['POSTGRES_PASSWORD']),
                host=str(config['POSTGRES']['POSTGRES_HOST']),
                port=str(config['POSTGRES']['POSTGRES_PORT']))
            conn.autocommit = True
            return conn
        except psycopg2.OperationalError:
            return False

    def close(self):
        """Close connect with database"""
        if self.conn:
            self.conn.close()
        return True

    @__init_cursor
    def select_data(self, execute, cursor):
        # Если присылаемым значение было error, то вызывается исключение
        if execute == "error":
            raise AttributeError
        cursor.execute(execute)

        return cursor.fetchall()

    @__init_cursor
    def insert_data(self, execute, cursor, name_file=None):
        try:
            # Если присылаемым значение было error, то вызывается исключение
            if execute == "error":
                raise AttributeError

            cursor.execute(execute)
        except psycopg2.errors.UniqueViolation:
            if str(name_file).find('.') != -1:
                if name_file.split('.')[-1] == 'registration':
                    return "Пользователь с таким никнеймом уже существует"

        return True

    @__init_cursor
    def login(self, login, cursor):
        """
            Returned: {id, password, status_active, title, salt}
        """

        # Структура содержащая значения для отправки
        values_data = {
            "email": sql.Literal(login),
            "username": sql.Literal(login)
        }
        # Структура содержащая поля для отправки
        columns = {
            "email": sql.Identifier("email"),
            "username": sql.Identifier("username")
        }

        # Формирование выражения для условия
        conditions = []
        for key in columns:
            conditions.append(sql.SQL("=").join(
                val for val in [columns[key], values_data[key]]
            ))

        # Формирование структуры для подстановке к запросу
        values = {
            "fields": sql.SQL(",").join(sql.Identifier(i[0], i[1]) for i in [
                    ('u', 'id'), ('u', 'username'), 
                    ('u', 'password'), ('u', 'status_active'),
                    ('u', 'role'), ('us', 'salt')]),
            "conditions": sql.SQL(" or ").join(cond for cond in conditions)
        }

        query = """
                SELECT 
                    {fields} 
                FROM users u
                    LEFT JOIN users_salt us on u.id = us.user_id 
                WHERE {conditions};"""

        cursor.execute(sql.SQL(query).format(**values))
        psw = cursor.fetchone()
        return (psw if psw != None else False)
