import os
import sys
import sqlite3

class DBConnection():
    def __init__(self):
        self.db_file = "passages_CDI.db" # the sqlite database file
        self.sql_file = "passages_CDI.sql" # the file used for dumps and import
        self.sql_init_file = "passages_CDI-init.sql" # the database initialization sql file

        self.conn = self.connect()

    def connect(self):
        """
            Creates (and returns) a connection to the database. 
            If the database does not exist, it is created from 
            "passages_CDI.sql", if this file does not exist, 
            it is created from "passages_CDI-init.sql"
            ------
            Crée (et retourne) une connection vers la base de donnée. 
            Si la base de donnée n'existe pas, elle est crée à partir de 
            "passages_CDI.sql", si ce fichier n'existe pas, 
            elle est crée à partir de "passages_CDI-init.sql"
        """

        # chdir to current file dir
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

        need_dump = False
        if not os.path.exists(self.db_file):
            need_dump = True

        try:
            conn = sqlite3.connect(self.db_file)
            # Activate foreign keys
            conn.execute("PRAGMA foreign_keys = 1")
            
            if need_dump:
                sql_file_to_use = self.sql_init_file

                if os.path.exists(self.sql_file):
                    sql_file_to_use = self.sql_file

                createFile = open(sql_file_to_use, 'r')
                createSql = createFile.read()
                createFile.close()
                sqlQueries = createSql.split(";")

                cursor = conn.cursor()
                for query in sqlQueries:
                    cursor.execute(query)

                conn.commit()

            return conn
        except sqlite3.Error as e:
            print("db : " + str(e))

        return None

    def dump(self):
        """
            Creates a dump of the database 
            and writes it in "passages_CDI.sql"
            ------
            Crée un dump de la base de donnée 
            et l'écrit dans "passages_CDI.sql"
        """

        # chdir to current file dir
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

        with open(self.sql_file, 'w') as f:
            for line in self.conn.iterdump():
                f.write('%s\n' % line)