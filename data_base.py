import logging
import sqlite3
from typing import List, Tuple


class UsersDatabaseManager:
    """
    A class to manage the database of SqlLite3
    Was writen by Me :D
    Its made for Users
    """

    def __init__(self, database: str):
        """
        Initialize a new or connect to an existing database.
        :param database: the database filename
        :return: none
        """
        self.conn = sqlite3.connect(database)
        self.cursor = self.conn.cursor()

    def add_data(self, user_id: int, age: int = None, 
                 gender: str = None, picture: str = None,
                 name: str = None, gender_search: str = None,
                 text: str = None, chat_id: int = None, user_id_search: int = None) -> None:
        
        logging.debug(f"Adding user {user_id}")
        self.cursor.execute(
            'INSERT INTO users (id_tg, age, gender, picture, name, gender_search, text, chat_id, user_id_search) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (user_id, age, gender, picture, name, gender_search, text, chat_id, user_id_search)
        )
        self.conn.commit()

    def get_data(self, user_id: int) \
            -> Tuple[int, int | None, str | None, str | None, str | None, str | None, str | None, int | None, int | None,]:
        
        logging.debug(f"Getting user with user_id={user_id}")
        self.cursor.execute('SELECT * FROM users WHERE id_tg = ?', (user_id,))
        return self.cursor.fetchone()

    def is_in_table(self, user_id: int, table: str) -> bool:

        logging.debug(f"Checking if user with user_id={user_id} is in the table")
        self.cursor.execute(f'SELECT * FROM {table} WHERE id_tg = ?', (user_id,))
        return self.cursor.fetchone() is not None
    
    def execute_cursor(self, query: str, datas: tuple = None) -> None:
        """
        Execute the specified query
        :param query: Your query
        :return: None
        """
        try:
            if "SELECT" in query:
                list = []
                ex = self.cursor.execute(query, datas).fetchall()
                for i in ex:
                    for j in i:
                        list.append(j)
                return list
            
            logging.debug(f"Executing query {query}")
            self.cursor.execute(query, datas)
            self.conn.commit()
        except Exception as e:
            logging.error(f"Happend this error:{e}")
        
    def delete_data(self, user_id: int) -> None:
        """
        Delete a row from the table.
        :param user_id: User's identifier
        """
        logging.debug(f"Deleting user with user_id={user_id}")
        self.cursor.execute('DELETE FROM users WHERE id_tg = ?', (user_id,))
        self.conn.commit()

    def __del__(self):
        """
        Close the database connection upon object deletion.
        """
        self.conn.close()