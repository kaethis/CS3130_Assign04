import socket

import struct

import dbmgr 


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
            'MSGDELV' : [ 0x1D, 'MESSAGE DELIVERED. ' ],
            'MSGPEND' : [ 0x1C, 'MESSAGE PENDING. ' ],
            'YESMSGS' : [ 0x1B, 'INCOMING PENDING MESSAGES.' ],
            'YESUSRS' : [ 0x1A, 'INCOMING USERS.' ] }

REQUEST = { 'LOGON'   : [ 0x0F, 'LOG ON...',       dbmgr.signOn ],
            'LOGOFF'  : [ 0x0E, 'LOG OFF...',      dbmgr.signOff ],
            'GETMSGS' : [ 0x0D, 'GET MESSAGES...', dbmgr.getMessages ],
            'GETUSRS' : [ 0x0C, 'GET USERS...',    dbmgr.getUsers ],
            'SENDMSG' : [ 0x0B, 'SEND MESSAGE...', dbmgr.sendMessage ] }

RECEIVE = { 'INCMSGS' : [ 0x2F, 'INCOMING PENDING MESSAGES.' ],
            'INCUSRS' : [ 0x2E, 'INCOMING ONLINE USERS.' ],
            'INCMSG'  : [ 0x2D, 'INCOMING MESSAGE.' ],
            'OUTMSG'  : [ 0x2C, 'OUTGOING MESSAGE.' ] } 
 

def logOn(args):

     ret = REQUEST['LOGON'][2](args)

     if str(ret) in ERROR:

        ret_code, ret_msg = ERROR[ret][0], ERROR[ret][1]

     else:

        ret_code, ret_msg = SUCCESS[ret][0], SUCCESS[ret][1]


     output = '[{}] : [{}] {} [{}] {}'

     output = output.format(args['username'],
                            REQUEST['LOGON'][0],
                            REQUEST['LOGON'][1],
                            ret_code,
                            ret_msg)

     print(output)


     return ret.encode('ascii')


def logOff(args):

    ret = REQUEST['LOGOFF'][2](args)

    if str(ret) in ERROR:

        ret_code, ret_msg = ERROR[ret][0], ERROR[ret][1]

    else:

        ret_code, ret_msg = SUCCESS[ret][0], SUCCESS[ret][1]


    output = '[{}] : [{}] {} [{}] {}'

    output = output.format(args['username'],
                           REQUEST['LOGOFF'][0],
                           REQUEST['LOGOFF'][1],
                           ret_code,
                           ret_msg)

    print(output)


    return ret.encode('ascii')


def getMessages(args):

    ret = REQUEST['GETMSGS'][2](args)

    if str(ret) in ERROR:

        ret_code, ret_msg = ERROR[ret][0], ERROR[ret][1]

    else:

        ret_code = SUCCESS['YESMSGS'][0]

        ret_msg = SUCCESS['YESMSGS'][1]


    output = '[{}] : [{}] {} [{}] {}'

    output = output.format(args['username'],
                           REQUEST['GETMSGS'][0],
                           REQUEST['GETMSGS'][1],
                           ret_code,
                           ret_msg)

    print(output)


    if ret_code == SUCCESS['YESMSGS'][0]:

        output = 'FROM [{}] TO [{}]: \"{}\"'

        text = ''

        for r in ret:

            print(output.format(r[0], args['username'], r[1]))

            text += '{}\n\n{}\n\n'.format(r[0], r[1])

        ret = '{}\n\n{}'.format('INCMSGS', text )

    return ret.encode('ascii')


def sendMessage(args):

    ret = REQUEST['SENDMSG'][2](args)

    if str(ret) in ERROR:

        ret_code, ret_msg = ERROR[ret][0], ERROR[ret][1]

    else:

        ret_code, ret_msg = SUCCESS[ret][0], SUCCESS[ret][1]


    output = '[{}]: [{}] {} [{}] {} \nFROM [{}] TO [{}]: \"{}\"'

    output = output.format(args['username'],
                           REQUEST['SENDMSG'][0],
                           REQUEST['SENDMSG'][1],
                           ret_code,
                           ret_msg,
                           args['username'],
                           args['receiver'],
                           args['message'])

    print(output)


    return ret.encode('ascii')


def getUsers(args):

    ret = REQUEST['GETUSRS'][2](args)

    if str(ret) in ERROR:

        ret_code, ret_msg = ERROR[ret][0], ERROR[ret][1]

    else:

        ret_code = SUCCESS['YESUSRS'][0]

        ret_msg = SUCCESS['YESUSRS'][1]


    output = '[{}] : [{}] {} [{}] {}'

    output = output.format(args['username'],
                           REQUEST['GETUSRS'][0],
                           REQUEST['GETUSRS'][1],
                           ret_code,
                           ret_msg)

    print(output)


    if ret_code == SUCCESS['YESUSRS'][0]:

        output = 'USER [{}]: {} [{}] [{}]'

        text = ''

        for r in ret:

            if r[1] == 1: status = 'ONLINE'

            else:         status = 'OFFLINE'


            ip_address, port = '', ''

            if status == 'ONLINE':

                ip_address = struct.pack('!I', dbmgr.getUser(r[0])[3])

                ip_address = socket.inet_ntoa(ip_address)


                port = dbmgr.getUser(r[0])[4]


            print(output.format(r[0], status, ip_address, port))

            text += '{}\n\n{}\n\n'.format(r[0], r[1])

        ret = '{}\n\n{}'.format('INCUSRS', text )


    return ret.encode('ascii')
