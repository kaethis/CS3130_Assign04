import socket

 
ERROR = {   'INVUSR'  : [ 0xFF, 'INVALID USERNAME!' ],
            'INVPWD'  : [ 0xFE, 'INVALID PASSWORD!' ],
            'USRON'   : [ 0xFD, 'USER CURRENTLY ONLINE!' ],
            'USROFF'  : [ 0xFC, 'USER CURRENTLY OFFLINE!' ],
            'NOCONN'  : [ 0xFB, 'DB CONNECTION FAILURE!' ],
            'NOUSRS'  : [ 0xFA, 'NO USERS SIGNED ON!' ],
            'CONNREF' : [ 0xF9, 'CONNECTION REFUSED!' ],
            'TIMEOUT' : [ 0xF8, 'CONNECTION TIMED OUT!' ],
            'INVREQ'  : [ 0xF7, 'INVALID REQUEST!' ],
            'NOMSGS'  : [ 0xF6, 'NO MESSAGES PENDING!' ], }

SUCCESS = { 'SIGNON'  : [ 0x1F, 'USER SIGNED ON.' ],
            'SIGNOFF' : [ 0x1E, 'USER SIGNED OFF.' ],
            'MSGDELV' : [ 0x1D, 'MESSAGE DELIVERED. '],
            'MSGPEND' : [ 0x1C, 'MESSAGE PENDING. '],
            'YESMSGS' : [ 0x1B, 'INCOMING PENDNG MESSAGES.' ] }

REQUEST = { 'LOGON'   : [ 0x0F, 'LOG ON...', ],
            'LOGOFF'  : [ 0x0E, 'LOG OFF...', ],
            'GETMSGS' : [ 0x0D, 'GET MESSAGES...', ],
            'GETUSRS' : [ 0x0C, 'GET USERS...', ],
            'SENDMSG' : [ 0x0B, 'SEND MESSAGE...', ] }
 
RECEIVE = { 'INCMSGS' : [ 0x2F, 'INCOMING PENDING MESSAGES.' ],
            'INCUSRS' : [ 0x2E, 'INCOMING ONLINE USERS.' ],
            'INCMSG'  : [ 0x2D, 'INCOMING MESSAGE.' ],
            'OUTMSG'  : [ 0x2C, 'OUTGOING MESSAGE.' ] } 


MAX_BYTES = 65535


def sendData(sock, data):

    timeout = 10  # seconds

    while True:

        sock.send(data)

        sock.settimeout(timeout)

        try:

            data = sock.recv(MAX_BYTES)

        except socket.timeout as exc: return 'TIMEOUT'

        except:                       return 'CONNREF'

        else:                         return data.decode('ascii')


def logOn(sock, args):

    text = '{}\n\n'.format(REQUEST['LOGON'][0])

    text += '{}\n\n'.format(args['username'])

    text += '{}\n\n'.format(args['password'])


    return sendData(sock, text.encode('ascii'))


def getMessages(sock, args):

    text = '{}\n\n'.format(REQUEST['GETMSGS'][0])

    text += '{}\n\n'.format(args['username'])

    text += '{}\n\n'.format(args['password'])


    sock.send(text.encode('ascii'))


def getUsers(sock, args):

    text = '{}\n\n'.format(REQUEST['GETUSRS'][0])

    text += '{}\n\n'.format(args['username'])

    text += '{}\n\n'.format(args['password'])


    sock.send(text.encode('ascii'))


def sendMessage(sock, args):

    text = '{}\n\n'.format(REQUEST['SENDMSG'][0])

    text += '{}\n\n'.format(args['username'])

    text += '{}\n\n'.format(args['password'])

    text += '{}\n\n'.format(args['receiver'])

    text += '{}\n\n'.format(args['message'])


    sock.send(text.encode('ascii'))


def logOff(sock, args):

    text = '{}\n\n'.format(REQUEST['LOGOFF'][0])

    text += '{}\n\n'.format(args['username'])

    text += '{}\n\n'.format(args['password'])


    sock.send(text.encode('ascii'))
