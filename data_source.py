import psycopg2
import logging
import pandas as pd

logger = logging.getLogger()

ADD_NEW_CLIENT = """insert into client(phone_number, name) values(%s, %s)"""

ADD_NEW_ORDER = """insert into order_(order_number, shipping, client_number, delivery_phone_number)
                    values(%s, %s, %s, %s)"""

ADD_NEW_DISH_IN_ORDER = """insert into dish_in_order(order_number, dish_number, quantity)
                            values(%s, %s, %s)"""

SELECT_DISHES = """SELECT * FROM dish where dish_type like %s"""

GET_LAST_ORDER_NUMBER = """select max(order_number) from order_"""

GET_DISH_NUMBER = """select dish_number from dish where dish_name = %s"""


class DataSource:
    def __init__(self, database_url):
        self.database_url = database_url

    def get_connection(self):
        return psycopg2.connect(self.database_url, sslmode='allow')

    @staticmethod
    def close_connection(conn):
        if conn is not None:
            conn.close()

    def new_row(self, query, *args):
        conn = None
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute(query, args)
            cur.close()
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
        finally:
            self.close_connection(conn)

    def new_client(self, phone_number, name):
        self.new_row(ADD_NEW_CLIENT, phone_number, name)

    def new_order(self, order_number, shipping, client_number, delivery_phone_number):
        self.new_row(ADD_NEW_ORDER, order_number, shipping, client_number, delivery_phone_number)

    def new_dish_in_order(self, order_number, dish_number, quantity):
        self.new_row(ADD_NEW_DISH_IN_ORDER, order_number, dish_number, quantity)

    def get_last_order(self):
        conn = None
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute(GET_LAST_ORDER_NUMBER)
            number = cur.fetchall()[0]
            cur.close()
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
        finally:
            self.close_connection(conn)
            return number[0]


    def get_dishes(self, dish_type):
        conn = None
        dishes = list()
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute(SELECT_DISHES, (dish_type,))
            for row in cur.fetchall():
                dishes.append(row[1])
            cur.close()
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
        finally:
            self.close_connection(conn)
            return dishes

    def get_dish_number(self, dish_name):
        conn = None
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute(GET_DISH_NUMBER, (dish_name,))
            dish_number = cur.fetchall()[0]
            cur.close()
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
        finally:
            self.close_connection(conn)
            return dish_number[0]
