import psycopg2
import logging

logger = logging.getLogger()

class DataSource:
    def __init__(self, database_url):
        self.database_url = database_url

    def get_connection(self):
        return psycopg2.connect(self.database_url, sslmode='allow')

    @staticmethod
    def close_connection(conn):
        if conn is not None:
            conn.close()

    def create_tables(self):
        commands = (
            """create table if not exists client(
                NAME VARCHAR(40) not null,
                PHONE_NUMBER varchar(10) primary key,
                club_member bit default '0'
                );

            """,
            """create table if not exists order_(
                 order_number serial primary key,
                 Shipping bit not null,
                 client_number varchar(10) references client(phone_number),
                 order_time date default CURRENT_TIMESTAMP,
                 Remarks varchar(100)
                );
              """,
            """create table IF NOT EXISTS dish(
                dish_number serial primary key,
                dish_name varchar(50) not null,
                price int not null,
                dish_type varchar(32),
                chiken bit default '0',
                spicy bit default '0',
                pastry bit default '0',
                fish bit default '0',
                tofu bit default '0',
                beef bit default '0',
                rice bit default '0',
                Coconut_cream bit default '0',
                eggs bit default '0',
                sea_food bit default '0',
                curry bit default '0',
                fried bit default '0',
                vegetarian bit default '0',
                vegan bit default '0'
               );
            """,

            """create table if not exists dish_in_order(
                dish_number int references dish(dish_number),
                order_number int references order_(order_number),
                Quantity int
                    );
                  """,
            """create table if not exists delivery_person(
                name varchar(20),
                phone_number varchar(10) primary key
                );
                """,
            """create table if not exists delivery_person_in_order(
                order_number int references order_(order_number),
                delivery_person varchar(10) references delivery_person(phone_number),
                primary key(order_number, delivery_person)
                )
                """,
        )

        conn = None
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            for command in commands:
                cur.execute(command)
            cur.close()
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            raise error
        finally:
            self.close_connection(conn)

    def get_all_reminders(self):
        conn = None
        reminders = list()
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute(SELECT_ALL_REMINDERS_STATEMENT)
            for row in cur.fetchall():
                reminders.append(ReminderData(row))
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            raise error
        finally:
            self.close_connection(conn)
            return reminders
