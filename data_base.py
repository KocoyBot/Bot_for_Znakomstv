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

        """
        This function `add_data` is used to insert user data into a database table called `users`. 
        It takes various input parameters such as user_id, age, gender, picture, name, gender_search, text, chat_id, and user_id_search. 
        The function then executes an SQL query to insert this data into the respective columns of the table. 
        Finally, it commits the changes to the database.
        """
        
        logging.debug(f"Adding user {user_id}")
        self.cursor.execute(
            'INSERT INTO users (id_tg, age, gender, picture, name, gender_search, text, chat_id, user_id_search) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (user_id, age, gender, picture, name, gender_search, text, chat_id, user_id_search)
        )
        self.conn.commit()

    def get_data(self, user_id: int) \
            -> Tuple[int, int | None, str | None, str | None, str | None, str | None, str | None, int | None, int | None,]:

        """
        This `get_data` function retrieves user data from the database based on the provided user_id. 
        It executes a SELECT query to fetch all columns of the user with the given user_id from the 'users' table. 
        The function then returns a tuple containing the retrieved data which includes user_id, age, gender, picture, name, gender_search, text, chat_id, and user_id_search. 
        The function also includes a logging statement to debug the process of fetching user data.
        """
        
        logging.debug(f"Getting user with user_id={user_id}")
        self.cursor.execute('SELECT * FROM users WHERE id_tg = ?', (user_id,))
        return self.cursor.fetchone()

    def is_in_table(self, user_id: int, table: str) -> bool:

        """
        The `is_in_table` function checks whether a user with a specific user_id exists in a specified table in the database. 
        It utilizes logging to track the process of checking user presence in the table. 
        The function executes a SELECT query to search for a row in the specified table where the 'id_tg' column matches the provided user_id. 
        If the query result is not empty (i.e., the user is found in the table), the function returns True; otherwise, it returns False.
        """

        logging.debug(f"Checking if user with user_id={user_id} is in the table")
        self.cursor.execute(f'SELECT * FROM {table} WHERE id_tg = ?', (user_id,))
        return self.cursor.fetchone() is not None
    
    def execute_cursor(self, query: str, datas: tuple = None) -> None:
        """
        The execute_cursor function is a method that performs a database query using the provided query and data tuple. 
        If the query contains the keyword "SELECT," the function retrieves and returns a list of results fetched from the database. 
        It also logs the execution of the query for debugging purposes. If the query is not a SELECT query, it executes the query and commits the changes to the database connection. 
        In case of any exceptions during the execution, the function logs the error using the logging.error() method.
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
        The `delete_data` function is a method that deletes a user record from the database based on the `user_id` provided as an argument. 
        It logs the deletion operation for debugging purposes using the `logging.debug()` method. 
        The function constructs a SQL query to delete the user from the "users" table where the `id_tg` column matches the given user_id. After executing the deletion query, it commits the changes to the database. 
        This function does not return any value upon successful deletion.
        """
        logging.debug(f"Deleting user with user_id={user_id}")
        self.cursor.execute('DELETE FROM users WHERE id_tg = ?', (user_id,))
        self.conn.commit()

    def __del__(self):
        """
        Close the database connection upon object deletion.
        """
        self.conn.close()
