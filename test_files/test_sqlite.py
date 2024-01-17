import sqlite3
from sqlite3 import Error
from os import path
from pyddl import State
import dill as pickle
from time import time


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
        return conn
    except Error as e:
        print(e)

    return None


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def create_level(conn, level):
    """
    Create a new project into the projects table
    :param conn:
    :param project:
    :return: project id
    """
    sql = ''' INSERT INTO game_levels(name,plan_length) VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, level)
    return cur.lastrowid


def add_node(conn, fringe):
    """
    Create a new task
    :param conn:
    :param task:
    :return:
    """

    sql = ''' INSERT INTO fringe(name,f_value,cost,state,level_id)
              VALUES(?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, fringe)
    return cur.lastrowid

# def select_all_tasks(conn):
#     """
#     Query all rows in the tasks table
#     :param conn: the Connection object
#     :return:
#     """
#     cur = conn.cursor()
#     cur.execute("SELECT * FROM tasks")
#
#     rows = cur.fetchall()
#
#     for row in rows:
#         print(row)


def select_node_by_priority(conn):
    """
    Query tasks by priority
    :param conn: the Connection object
    :param priority:
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM fringe WHERE f_value = (SELECT min(f_value) FROM fringe)")

    rows = cur.fetchone()
    return rows


def main():
    dirname = path.dirname(__file__)
    database = "pythonsqlite.db"

    # create a database connection
    # with conn:
    #     print("1. Query task by priority:")
    #     select_task_by_priority(conn, 1)
    #
    #     print("2. Query all tasks")
    #     select_all_tasks(conn)

    s1 = State([('qwqwqw', 'qw', 'qw', 2)], {'asas': 4})
    s2 = pickle.dumps(s1)

    sql_create_projects_table = """ CREATE TABLE IF NOT EXISTS game_levels (
                                            id integer PRIMARY KEY,
                                            name text NOT NULL,
                                            plan_length integer
                                        ); """

    sql_create_tasks_table = """CREATE TABLE IF NOT EXISTS fringe (
                                        id integer PRIMARY KEY,
                                        name text NOT NULL,
                                        f_value integer NOT NULL,
                                        cost integer NOT NULL,
                                        state BLOB NOT NULL,
                                        level_id integer NOT NULL,
                                        FOREIGN KEY (level_id) REFERENCES game_levels (id)
                                    );"""

    # create a database connection
    conn = create_connection(database)



    if conn is not None:
        # create projects table
        create_table(conn, sql_create_projects_table)
        # create tasks table
        create_table(conn, sql_create_tasks_table)
    else:
        print("Error! cannot create the database connection.")

    with conn:
        t1 = time()
        level = ('config_B5_C14_P3_D2_17', 43)
        level_id = create_level(conn, level)

        fringe_1 = ('node1', 25, 12, 'asdadad', level_id)
        fringe_2 = ('node2', 24, 113, 'qweadsxzfxcvasdadad', level_id)
        fringe_3 = ('node3', 27, 1123, 'qweaasxcdsfxcvasdadad', level_id)
        fringe_4 = ('node4', 14, 123, 'qweadsxz fxcvasdadad', level_id)
        fringe_5 = ('node5', 13, 1233, s2, level_id)

        add_node(conn, fringe_1)
        add_node(conn, fringe_2)
        add_node(conn, fringe_3)
        add_node(conn, fringe_4)
        add_node(conn, fringe_5)

        print("1. Query task by priority:")
        node = select_node_by_priority(conn)

        state = pickle.loads(node[4])
        print(time() - t1)

    t=1

if __name__ == '__main__':
    main()