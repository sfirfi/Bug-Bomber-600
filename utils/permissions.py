import pymysql.cursors
import configparser

# creates a connection to the DB
def Connection():
    config = configparser.ConfigParser()
    config.read('config.ini')
    connection = pymysql.connect(host=config['Credentials']['host'],
                                 user=config['Credentials']['user'],
                                 password=config['Credentials']['password'],
                                 db=config['Credentials']['database'],
                                 charset='utf8',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection


# Receives a permissions and the roles of a user
# Checks if any of the roles as the needed Permission
def hasPermission(roles, permission):
    res = False
    conn = Connection()
    for crole in roles:
        if conn.cursor().execute("SELECT id, permission" +
                                 " FROM permissions where " +
                                 "id='" + str(crole.id) + "' AND permission = '" +
                                 permission + "'") is not 0:
            res = True
            break

    return res
