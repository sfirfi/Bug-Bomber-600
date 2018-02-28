import pymysql


# Exceptions class
class SQLException(Exception):
    pass


# Create the class
class SQLDB:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

        self.connection = None

    # Perform a database connection
    def connect(self):
        try:
            self.connection = pymysql.connect(host=self.host, user=self.user, password=self.password,
                                              database=self.database, charset='utf8',
                             cursorclass=pymysql.cursors.DictCursor, autocommit=True)
        except pymysql.Error as error:
            raise SQLException("The database connection failed: " + str(error))



    # Perform an SQL query
    # Parameters:
    #
    # * sql = The query you want to perform
    def query(self, sql):
        # Check if it's connected
        if self.connection is None:
            self.connect()

        # Try to execute the SQL query
        try:
            self.cursor = self.connection.cursor()
            res = self.cursor.execute(sql)
        # Failed, maybe the server is "away"?
        except (AttributeError, pymysql.OperationalError):
            self.connect()
            self.cursor = self.connection.cursor()
            res = self.cursor.execute(sql)
        # Failed, maybe it's a general problem?
        except pymysql.Error as error:
            raise SQLException("Returned General Error " + str(error))

        # Return the result
        return res

    # Fetch all rows
    def fetch_rows(self):
        res = self.cursor.fetchall()
        return res

    # Fetch just one row
    def fetch_onerow(self):
        res = self.cursor.fetchone()
        return res

    # Get column names
    def fetch_columns(self):
        res = self.cursor.description
        return res