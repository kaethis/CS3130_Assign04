#!/usr/bin/python3


import argparse

import hashlib

import socket

import struct

import threading 

import chatserver

import chatclient

import dbmgr

import ui

 
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
            'YESMSGS' : [ 0x1B, 'INCOMING PENDNG MESSAGES.' ],
            'YESUSRS' : [ 0x1A, 'INCOMING USERS.' ] }

REQUEST = { 'LOGON'   : [ 0x0F, 'LOG ON...',
                          chatserver.logOn,       chatclient.logOn ],
            'LOGOFF'  : [ 0x0E, 'LOG OFF...',
                          chatserver.logOff,      chatclient.logOff ],
            'GETMSGS' : [ 0x0D, 'GET MESSAGES...',
                          chatserver.getMessages, chatclient.getMessages ],
            'GETUSRS' : [ 0x0C, 'GET USERS...',
                          chatserver.getUsers,    chatclient.getUsers ],
            'SENDMSG' : [ 0x0B, 'SEND MESSAGE...',
                          chatserver.sendMessage, chatclient.sendMessage ] }

RECEIVE = { 'INCMSGS' : [ 0x2F, 'INCOMING PENDING MESSAGES.' ],
            'INCUSRS' : [ 0x2E, 'INCOMING ONLINE USERS.' ],
            'INCMSG'  : [ 0x2D, 'INCOMING MESSAGE.' ],
            'OUTMSG'  : [ 0x2C, 'OUTGOING MESSAGE.' ] }


MAX_BYTES = 65535


msg_events = {} # for server.

usr_event = [ [], threading.Event()] # for client.

msg_event = [ [], threading.Event()] # for client.

rdy_event = threading.Event() # for client.


def messagethread(sock, address):

    while True:

        if msg_events[(address[0], address[1])][1].is_set():

            msg = msg_events[(address[0], address[1])][0]

            msg_events[(address[0], address[1])][1] = threading.Event()

            sock.sendto(msg.encode('ascii'), address)


def serverthread(sock, address):

    t = threading.Thread(target=messagethread, args=(sock, address))

    t.is_daemon = True

    t.start()


    while True:

        data, tmp = sock.recvfrom(MAX_BYTES)

        if len(data) == 0: break;


        output = '\nREQUEST FROM [{}] [{}]'

        output = output.format(address[0], address[1])

        print(output)


        text = data.decode('ascii').split('\n\n')

        for req in REQUEST:

            if REQUEST[req][0] == int(text[0]):

                if req == 'LOGON':

                    ip_address = socket.inet_aton(address[0])

                    ip_address = int.from_bytes(ip_address, byteorder='big')

                    args = { 'username'   : text[1],
                             'password'   : text[2],
                             'ip_address' : ip_address,
                             'socket'     : address[1] }

                    data = REQUEST[req][2](args)

                    sock.sendto(data, address)


                elif req == 'LOGOFF':

                    args = { 'username'   : text[1],
                             'password'   : text[2] }
    
                    data = REQUEST[req][2](args)

                    sock.sendto(data, address)


                    break


                elif req == 'GETMSGS':

                    args = { 'username'   : text[1],
                             'password'   : text[2] }

                    data = REQUEST[req][2](args)

                    sock.sendto(data, address)


                elif req == 'SENDMSG':

                    args = { 'username'   : text[1],
                             'password'   : text[2],
                             'receiver'   : text[3],
                             'message'    : text[4],}

                    data = REQUEST[req][2](args)

                    sock.sendto(data, address)


                    if data.decode('ascii') == 'MSGDELV':

                        receiver = dbmgr.getUser(args['receiver'])

                        ip_address = struct.pack('!I', receiver[3])

                        ip_address = socket.inet_ntoa(ip_address)

                        port = receiver[4]


                        while msg_events[(ip_address, port)][1].is_set():

                           continue # wait for message thread.

                        msg_event = msg_events[(ip_address, port)][1]

                        msg_event.set()

                        msg = '{}\n\n{}\n\n{}\n\n'.format('INCMSG',
                                                          args['username'],
                                                          args['message'])

                        msg_events[(ip_address, port)][0] = msg;

                        msg_events[(ip_address, port)][1] = msg_event;


                        msg = '{}\n\n{}\n\n{}\n\n'.format('OUTMSG',
                                                          args['receiver'],
                                                          args['message'])
 
                        sock.sendto(msg.encode('ascii'), address)


                elif req == 'GETUSRS':

                    args = { 'username'   : text[1],
                             'password'   : text[2] }

                    data = REQUEST[req][2](args)

                    sock.sendto(data, address)


    output = '\nCONNECTION CLOSED [{}] [{}]'

    output = output.format(address[0], address[1])

    print(output)


    sock.close()


def server(interface, port):

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    sock.bind((interface, port))

    sock.listen(1)


    output = '\nLISTENING AT [{}] [{}]'

    output = output.format(interface, port)

    print(output)


    while True:

        sc, sockname = sock.accept()

        msg_events[(sockname[0], sockname[1])] = [ '', threading.Event() ]


        t = threading.Thread(target=serverthread, args=(sc, sockname))

        t.is_daemon = True;

        t.start()


        output = '\nCONNECTION ESTABLISHED [{}] [{}] [{}]'

        output = output.format(sockname[0], sockname[1], t.name)

        print(output)


def clientthread(y, x, height, width, sock):

    color = ui.curses.color_pair(ui.colors['BK/W'])

    color_alt = ui.curses.color_pair(ui.colors['W/BK'])

    ui.window(y, x, height, width, color, False)


    sock.settimeout(0)


    rdy_event.set()


    curs_y, curs_x = y, x

    while True:

        try:    data = sock.recv(MAX_BYTES)

        except: continue

        else:

            ret = data.decode('ascii')

            ret_msg = ''

            if str(ret) in SUCCESS:

                ret_code, ret_msg = SUCCESS[ret][0], SUCCESS[ret][1]

                ui.clear(28, 3, 3, 50)

                ui.message(28, 3, ret_msg)

            elif str(ret) in ERROR:

                ret_code, ret_msg = ERROR[ret][0], ERROR[ret][1]

                ui.clear(28, 3, 3, 50)

                ui.message(28, 3, ret_msg)


                if ret == 'NOMSGS':

                    msg_event[0] = 'NOMSGS'

                    msg_event[1].set()

            else:

                ret = ret.split('\n\n')

                if str(ret[0]) == 'INCMSG':

                    ret = ret[1:]

                    user, msg = ret[0], ret[1]

                    if curs_y > (y+height-1):

                        curs_y = y

                        ui.window(y, x, height, width, color, False)

                    ui.stdscr.addstr(curs_y, curs_x, 'FROM '+user, color_alt)

                    curs_x += len('FROM '+user)

                    ui.stdscr.addstr(curs_y, curs_x, ' '+msg, color)
                    
                    ui.stdscr.refresh()


                    curs_y, curs_x = (curs_y+1), x


                elif str(ret[0]) == 'OUTMSG':

                    ret = ret[1:]

                    user, msg = ret[0], ret[1]

                    if curs_y > (y+height-1):

                        curs_y = y

                        ui.window(y, x, height, width, color, False)


                    ui.stdscr.addstr(curs_y, curs_x, 'TO '+user, color_alt)

                    curs_x += len('TO '+user)

                    ui.stdscr.addstr(curs_y, curs_x, ' '+msg, color)
                    
                    ui.stdscr.refresh()


                    curs_y, curs_x = (curs_y+1), x


                elif str(ret[0]) == 'INCUSRS':

                    ret = ret[1:]

                    users, status = ret[0::2], ret[1::2]

                    users = users[:-1]


                    collect = []

                    for i in range(len(users)):

                        if int(status[i]): collect.append({ 'USER' : users[i] })


                    usr_event[0] = collect

                    usr_event[1].set()


                elif str(ret[0]) == 'INCMSGS':

                    ret = ret[1:]

                    users, msgs = ret[0::2], ret[1::2]

                    users = users[:-1]


                    collect = []

                    for i in range(len(msgs)):

                        collect.append({ 'FROM'    : users[i],
                                         'MESSAGE' : msgs[i] })


                    msg_event[0] = collect

                    msg_event[1].set()


def client(hostname, port):

    ui.init()


    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try: sock.connect((hostname, port))

    except:

        ui.alert(2, 2, ERROR['CONNREF'][1])

        ui.exit()

        quit()


    ret = ''

    while not ret == 'SIGNON':

        ret = ui.multitextwinv(2, 2,\
                               [ 'VARCHAR', 'VARCHAR' ],\
                               [ 10, 20 ],\
                               [ 'USERNAME', 'PASSWORD' ],\
                               [ False, True ])

        if ret == ui.keyboard['ESC']:

            ui.exit()

            quit()

        else:

            username = ret[0]

            password = hashlib.sha224(ret[1].encode('ascii')).hexdigest()

            args = { 'username' : username,
                     'password' : password }


        ui.message(2, 2, REQUEST['LOGON'][1])

        ret = REQUEST['LOGON'][3](sock, args)

        ret_msg = ''

        if str(ret) in SUCCESS:

            ret_code, ret_msg = SUCCESS[ret][0], SUCCESS[ret][1]

        elif str(ret) in ERROR:

            ret_code, ret_msg = ERROR[ret][0], ERROR[ret][1]


        ui.alert(2, 2, ret_msg)

        break;


    t = threading.Thread(target=clientthread, args=(9, 3, 16, 75, sock))

    t.daemon = True

    t.start()


    while not rdy_event.is_set():

        continue # wait for client thread.


    ui.window(2, 81, 22, 15,\
              ui.curses.color_pair(ui.colors['W/BK']),\
              True)

    ui.window(2, 2, 3, 75,\
              ui.curses.color_pair(ui.colors['W/BK']),\
              True)




    ui.message(3, 4, REQUEST['GETMSGS'][1])

    REQUEST['GETMSGS'][3](sock, args)

    while not msg_event[1].is_set(): continue # wait for client thread.

    if not str(msg_event[0]) == 'NOMSGS':

        msg_event[1] = threading.Event()

        ui.optionwinh(2, 2, 3, 75,\
                      [ [ '\u25B2/\u25BC', 'SELECT' ],\
                        [ 'RET', 'CLOSE' ],\
                        [ 'ESC', 'CLOSE' ] ])

        ui.menuwin(28, 2, 5, 0,\
                   [ [ 'FROM', '11', 'VARCHAR' ],
                     [ 'MESSAGE', '76', 'VARCHAR' ] ],\
                   msg_event[0])


    while True:

        ui.window(2, 2, 3, 75,\
                  ui.curses.color_pair(ui.colors['W/BK']),\
                  True)

        ui.optionwinv(2, 81, 22, 15,\
                      [ [ 'RET', 'INPUT' ],\
                        [ 'U',   'USERS' ],\
                        [ 'ESC', 'LOGOUT' ] ])


        key = ui.stdscr.getch()

        if key == ui.keyboard['ESC']:

            ui.optionwinv(2, 81, 22, 15,\
                          [ [ '\u25C0/\u25B6', 'SELECT' ],\
                            [ 'RET', 'SUBMIT' ],\
                            [ 'ESC', 'CANCEL' ] ])

            if ui.confirm(3, 4, 'LOG OUT?') == 0: break


        elif key == ui.keyboard['ENTER']:

            ui.optionwinv(2, 81, 22, 15,\
                          [ ['RET', 'SUBMIT'],\
                            ['ESC', 'CANCEL' ] ])

            ret = ui.multitextwinh(2, 2,\
                                   [ 'VARCHAR', 'VARCHAR' ],\
                                   [ 10, 57 ],\
                                   [ 'TO', 'MESSAGE' ],\
                                   [ False, False ])

            if not ret == ui.keyboard['ESC']:

                args['receiver'], args['message'] = ret[0], ret[1]

                ui.window(2, 2, 3, 75,\
                          ui.curses.color_pair(ui.colors['W/BK']),\
                          True)

                ui.message(3, 4, REQUEST['SENDMSG'][1])

                REQUEST['SENDMSG'][3](sock, args)


        elif key == ui.keyboard['U']:

            ui.window(2, 81, 22, 15,\
                      ui.curses.color_pair(ui.colors['W/BK']),\
                      True)

            ui.message(3, 4, REQUEST['GETUSRS'][1])

            REQUEST['GETUSRS'][3](sock, args)

            while not usr_event[1].is_set():

                continue # wait for client thread.

            usr_event[1] = threading.Event()

            ui.optionwinh(2, 2, 3, 75,\
                          [ [ '\u25B2/\u25BC', 'SELECT' ],\
                            [ 'RET', 'CLOSE' ],\
                            [ 'ESC', 'CLOSE' ] ])

            ui.menuwin(2, 81, 22, 0,\
                       [ ['USER', '10', 'VARCHAR' ] ],\
                       usr_event[0])


    ui.message(3, 4, REQUEST['LOGOFF'][1])

    REQUEST['LOGOFF'][3](sock, args)


    sock.close()


    ui.exit()

    quit()


if __name__ == '__main__':

    choices = { 'client' : client,
                'server' : server }


    description = '''A simple TCP Python chat program.
                  '''

    parser = argparse.ArgumentParser(description=description)


    parser.add_argument('role',
                        choices=choices,
                        help='which role to take')

    parser.add_argument('host',
                        help='''if client, host the client connects to;
                                else if server, interface the server
                                listens at''')

    parser.add_argument('-p',
                        metavar='port',
                        type=int,
                        default=1060,
                        help='TCP port (default 1060)')

    args = parser.parse_args()


    function = choices[args.role]

    function(args.host, args.p)
