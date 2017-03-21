import pymysql

import socket

import hashlib

from struct import pack


ERROR = { 'INVUSR' : [ 0xFF, 'INVALID USERNAME!' ],
          'NOCONN' : [ 0xFB, 'DB CONNECTION FAILURE!' ] }

 
DB_AUTH = { 'host'       : 'localhost',
            'port'       : 3306,
            'user'       : 'CHAT_ADMIN',
            'passwd'     : 'Password1234',
            'db'         : 'CHAT_DB',
            'autocommit' : True }


def signOn(args):

    try:    conn = pymysql.connect(host =       DB_AUTH['host'],
                                   port =       DB_AUTH['port'],
                                   user =       DB_AUTH['user'],
                                   passwd =     DB_AUTH['passwd'],
                                   db =         DB_AUTH['db'],
                                   autocommit = DB_AUTH['autocommit'])

    except: conn = 'NOCONN' # error.


    if str(conn) in ERROR.keys(): return conn # as error.

    else:                         cur = conn.cursor()


    user = getUser(args['username'])

    if user in ERROR.keys():          return user # as error.

    elif user[1] != args['password']: return 'INVPWD' # error.

    elif user[2] != 0:                return 'USRON' # error.


    query = '''UPDATE USERS
               SET    USERS.online=1,
                      USERS.ip_address={},
                      USERS.socket={}
               WHERE  USERS.username=\'{}\'
            '''

    query = query.format(args['ip_address'],
                         args['socket'],
                         args['username'])

    cur.execute(query)


    return 'SIGNON' # success.


def signOff(args):

    try:    conn = pymysql.connect(host =       DB_AUTH['host'],
                                   port =       DB_AUTH['port'],
                                   user =       DB_AUTH['user'],
                                   passwd =     DB_AUTH['passwd'],
                                   db =         DB_AUTH['db'],
                                   autocommit = DB_AUTH['autocommit'])

    except: conn = 'NOCONN' # error.


    if str(conn) in ERROR.keys(): return conn # as error.

    else:                         cur = conn.cursor()


    user = getUser(args['username'])

    if user in ERROR.keys():          return user # as error.

    elif user[1] != args['password']: return 'INVPWD' # error.

    elif user[2] != 1:                return 'USROFF' # error.


    query = '''UPDATE USERS
               SET    USERS.online=0
               WHERE  USERS.username=\'{}\'
            '''

    query = query.format(args['username'])

    cur.execute(query)

    cur.close()

    conn.close()


    return 'SIGNOFF' # success.


def getMessages(args):

    try:    conn = pymysql.connect(host =       DB_AUTH['host'],
                                   port =       DB_AUTH['port'],
                                   user =       DB_AUTH['user'],
                                   passwd =     DB_AUTH['passwd'],
                                   db =         DB_AUTH['db'],
                                   autocommit = DB_AUTH['autocommit'])

    except: conn = 'NOCONN' # error.


    if str(conn) in ERROR.keys(): return conn # as error.

    else:                         cur = conn.cursor()


    user = getUser(args['username'])

    if str(user) in ERROR.keys():     return user # as error.

    elif user[1] != args['password']: return 'INVPWD' # error.

    elif user[2] != 1:                return 'USROFF' # error.


    query = '''SELECT sender, message
               FROM   MESSAGES
               WHERE  MESSAGES.delivered=0
                 AND  MESSAGES.receiver='\{}\'
            '''

    query = query.format(args['username'])

    cur.execute(query)


    messages = []

    for msg in cur: messages.append(msg)


    query = '''UPDATE MESSAGES 
               SET    MESSAGES.delivered=1
               WHERE  MESSAGES.receiver=\'{}\'
            '''

    query = query.format(args['username'])

    cur.execute(query)

    cur.close()

    conn.close()


    if len(messages) == 0: return 'NOMSGS' # error.

    else:                  return messages


def getUsers(args):

    try:    conn = pymysql.connect(host =       DB_AUTH['host'],
                                   port =       DB_AUTH['port'],
                                   user =       DB_AUTH['user'],
                                   passwd =     DB_AUTH['passwd'],
                                   db =         DB_AUTH['db'],
                                   autocommit = DB_AUTH['autocommit'])

    except: conn = 'NOCONN' # error.


    if str(conn) in ERROR.keys(): return conn # as error.

    else:                         cur = conn.cursor()


    user = getUser(args['username'])

    if str(user) in ERROR.keys():     return user # as error.

    elif user[1] != args['password']: return 'INVPWD' # error.

    elif user[2] != 1:                return 'USROFF' # error.


    query = '''SELECT USERS.username,
                      USERS.online
               FROM   USERS
            '''

    cur.execute(query)


    users = []

    for usr in cur: users.append(usr)


    cur.close()

    conn.close()


    if len(users) == 0: return 'NOUSRS' # error.

    else:               return users # success.


def sendMessage(args):

    try:    conn = pymysql.connect(host =       DB_AUTH['host'],
                                   port =       DB_AUTH['port'],
                                   user =       DB_AUTH['user'],
                                   passwd =     DB_AUTH['passwd'],
                                   db =         DB_AUTH['db'],
                                   autocommit = DB_AUTH['autocommit'])

    except: conn = 'NOCONN' # error.


    if str(conn) in ERROR.keys(): return conn # as error.

    else:                         cur = conn.cursor()


    sender = getUser(args['username'])

    receiver = getUser(args['receiver'])


    if sender[1] != args['password']:

        return 'INVPWD' # error.

    elif sender in ERROR.keys() or receiver in ERROR.keys():

        return 'INVUSR' # error.


    if receiver[2] == 1: delivered = 1;

    else:                delivered = 0;


    query = '''INSERT INTO
               MESSAGES  (sender, receiver, message, delivered)
               VALUES (\'{}\',\'{}\',\'{}\',{})
            '''

    query = query.format(sender[0],
                         receiver[0],
                         args['message'],
                         delivered);

    cur.execute(query)

    cur.close()

    conn.close()


    if delivered: return 'MSGDELV' # success;

    else:         return 'MSGPEND' # success;


def getUser(username):

    try:    conn = pymysql.connect(host =       DB_AUTH['host'],
                                   port =       DB_AUTH['port'],
                                   user =       DB_AUTH['user'],
                                   passwd =     DB_AUTH['passwd'],
                                   db =         DB_AUTH['db'],
                                   autocommit = DB_AUTH['autocommit'])

    except: conn = 'NOCONN' # error.


    if str(conn) in ERROR.keys(): return conn # as error.

    else:                         cur = conn.cursor()


    query = '''SELECT *
               FROM   USERS
               WHERE  USERS.username=\'{}\'
            '''

    query = query.format(username)

    cur.execute(query)


    users = []

    for usr in cur: users.append(usr)


    cur.close()

    conn.close()


    if len(users) == 0: return 'INVUSR' # error.

    else:               return users[0] # success.


#def registerUser(username, password):
#
#    try:    conn = pymysql.connect(host =       DB_AUTH['host'],
#                                   port =       DB_AUTH['port'],
#                                   user =       DB_AUTH['user'],
#                                   passwd =     DB_AUTH['passwd'],
#                                   db =         DB_AUTH['db'],
#                                   autocommit = DB_AUTH['autocommit'])
#
#    except: conn = 'NOCONN' # error.
#
#
#    if conn in ERROR.keys(): return conn # as error.
#
#    else:                    cur = conn.cursor()
#
#
#    password = hashlib.sha224(password.encode('ascii')).hexdigest()
#
#    online = 0
#
#    ip_address = socket.inet_aton('127.0.0.1')
#
#
#    query = '''INSERT INTO
#               USERS  (username, password, online, ip_address)
#               VALUES (\'{}\',\'{}\',{},{})
#            '''
#
#    query = query.format(username,
#                         password,
#                         online,
#                         int.from_bytes(ip_address, byteorder='big'))
#
#    cur.execute(query)
#
#    cur.close()
#
#    conn.close()
