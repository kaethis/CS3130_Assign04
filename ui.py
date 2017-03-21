import curses

import re


keyboard = { 'ENTER'  : 10,
             'ESC'    : 27,
             'BACKSP' : curses.KEY_BACKSPACE,
             'UP'     : curses.KEY_UP,
             'DOWN'   : curses.KEY_DOWN,
             'LEFT'   : curses.KEY_LEFT,
             'RIGHT'  : curses.KEY_RIGHT,
             'A'      : 0x61,
             'D'      : 0x64,
             'N'      : 0x6E,
             'S'      : 0x73,
             'Y'      : 0x79,
             'U'      : 0x75 }

regex = { 'VARCHAR' : re.compile("^[A-Za-z0-9 =,!.?']+$"),
          'ALPHA'   : re.compile("^[A-Za-z]+$"),
          'NUM'     : re.compile("^[0-9]+$") }

colors = { 'W/BK' : 1,
           'BK/W' : 2 }


stdscr = curses.initscr()

curses.start_color()

curses.init_pair(colors['W/BK'],
                 curses.COLOR_WHITE,
                 curses.COLOR_BLACK)

curses.init_pair(colors['BK/W'],
                 curses.COLOR_BLACK,
                 curses.COLOR_WHITE)

curses.endwin()


def init():

    stdscr = curses.initscr()

    stdscr.keypad(True)


    curses.noecho()

    curses.cbreak()

    curses.curs_set(0)


    stdscr.refresh()


def menuwin(y, x, height, focus, schema, collect):

    curs_y, curs_x = y, x

    curs_height = height

    width = (len(schema)+3)

    for i in range(len(schema)): width += (int(schema[i][1])+1)


    color = curses.color_pair(colors['W/BK'])

    window(curs_y, curs_x, height, width, color, True)


    curs_y += 1;

    curs_x += 2;

    curs_height -= 2;

    ret = menu(curs_y, curs_x, curs_height, focus, schema, collect)


    clear(y, x, height, width)


    return ret


def menu(y, x, height, focus, schema, collect):

    curs_y, curs_x = y, x

    width = 0

    for i in range(len(schema)): width += (int(schema[i][1])+1)

    width += (len(schema)-1)

    color = curses.color_pair(colors['W/BK'])

    window(curs_y, curs_x, height, width, color, False)


    pos, scroll = 0, 0

    for i in range(focus):

        if pos < (height-1): pos += 1

        else:                scroll += 1


    for i in range(len(schema)):

        stdscr.addstr((curs_y-1), curs_x, '|'+schema[i][0]+'|', color)

        stdscr.refresh()


        if i == 0 and len(schema) > 1: curs_x += 1

        curs_x += (int(schema[i][1])+1)


    while True:

        curs_y, curs_x = y, x

        for i in range(height):

            if (i + scroll) == focus:

                color = curses.color_pair(colors['BK/W'])

            else:

                color = curses.color_pair(colors['W/BK'])


            curs_x = x

            for j in range(width):

                stdscr.addch(curs_y, curs_x, '_', color)

                curs_x += 1


            curs_x = x

            if not i > (len(collect) - 1):

                for j in range(len(schema)):

                    field = collect[(i+scroll)][schema[j][0]]

                    if not j == 0 or j == (len(schema)-1) and\
                                     len(schema) > 1:

                        field = ("_|_"+field);

                        stdscr.addstr(curs_y, curs_x, field, color)

                        curs_x += (int(schema[j][1])+1)

                    else:

                        stdscr.addstr(curs_y, curs_x, field, color)

                        curs_x += int(schema[j][1])


            curs_y += 1


        stdscr.refresh()


        cmd = [ keyboard['ESC'], keyboard['ENTER'] ]

        while True:

            key = stdscr.getch();

            if key in cmd:

                return key 

            else:

                if key == keyboard['DOWN']: 

                    if pos < (height-1): pos += 1

                    else:                scroll += 1


                    if focus < (len(collect)-1):

                        focus += 1

                    else:

                        focus, pos, scroll = 0, 0, 0


                    break;

                elif key == keyboard['UP'] and not len(collect) == 0:

                    if pos > 0: pos -= 1

                    else:       scroll -= 1


                    if focus == 0:

                        focus = (len(collect)-1)


                        if len(collect) > (height-1):

                            pos = (height-1)

                        else:

                            pos = (len(collect)-1)


                        scroll = focus - pos

                    else:

                        focus -= 1


                    break;


def message(y, x, msg):

    curs_y, curs_x = y, x

    height, width = 1, (len(msg)+1)


    color = curses.color_pair(colors['BK/W'])

    stdscr.addstr(curs_y, curs_x, msg, color)

    window(curs_y, curs_x, height, width, color, False)


def alert(y, x, msg):

    msg += '  '

    choice = 'RET'


    curs_y, curs_x = y, x

    height, width = 1, (len(msg)+len(choice)+1)


    color = curses.color_pair(colors['BK/W'])

    stdscr.addstr(curs_y, curs_x, msg, color)

    window(curs_y, curs_x, height, width, color, False)


    curs_x = (x+width-1-len(choice))


    color = curses.color_pair(colors['BK/W'])

    stdscr.addstr(curs_y, (curs_x-1), '[', color)

    stdscr.addstr(curs_y, (curs_x+len(choice)), ']', color)


    color = curses.color_pair(colors['W/BK'])

    stdscr.addstr(curs_y, curs_x, choice, color)



    cmd = [ keyboard['ESC'],
            keyboard['ENTER'] ]

    while True:

            key = stdscr.getch();

            if key in cmd:

                clear(y, x, height, width)

                return key


def confirm(y, x, msg):

    msg += '  '

    choices = ['YES', 'NO']


    curs_y, curs_x = y, x

    height, width = 1, (len(msg)+1)

    for choice in choices: width += len(choice)


    color = curses.color_pair(colors['BK/W'])

    stdscr.addstr(curs_y, curs_x, msg, color)

    window(curs_y, curs_x, height, width, color, False)


    toggle = lambda x: x^1


    focus = 0

    while True:

        curs_x = (x+width-1)

        for choice in choices: curs_x -= len(choice)


        for i in range(len(choices)):
 
            if focus == i: color = curses.color_pair(colors['W/BK'])

            else:          color = curses.color_pair(colors['BK/W'])


            stdscr.addstr(curs_y, curs_x, choices[i], color)

            if not i == (len(choices)-1):

                curs_x += len(choices[i])

                color = curses.color_pair(colors['BK/W'])

                stdscr.addch(curs_y, curs_x, '/', color)

                curs_x += 1


        stdscr.refresh()


        cmd = { keyboard['ESC']   :    -1,
                keyboard['N']     :     1,
                keyboard['Y']     :     0,
                keyboard['ENTER'] : focus }

        ctrl = { keyboard['LEFT']  : toggle,
                 keyboard['RIGHT'] : toggle }

        while True:

            key = stdscr.getch();

            if key in cmd.keys():

                clear(y, x, height, width)

                return cmd[key]

            elif key in ctrl.keys():

                focus = ctrl[key](focus)

                break


def optionwinv(y, x, height, width, options):

    color = curses.color_pair(colors['W/BK'])

    color_alt = curses.color_pair(colors['BK/W'])

    window(y, x, height, width, color, True)


    curs_y, curs_x = y, (x+1)

    for i in range(len(options)):

        stdscr.addstr(curs_y, curs_x, '     ', color)

        stdscr.addstr(curs_y, curs_x, '['+options[i][0]+']', color_alt)

        curs_x += 5

        stdscr.addstr(curs_y, curs_x, '        ', color)

        stdscr.addstr(curs_y, curs_x, ' '+options[i][1], color)

        curs_y, curs_x = (curs_y+2), (x+1)


    stdscr.refresh()


def optionwinh(y, x, height, width, options):

    color = curses.color_pair(colors['W/BK'])

    color_alt = curses.color_pair(colors['BK/W'])

    window(y, x, height, width, color, True)


    curs_y, curs_x = y, (x+1)

    for i in range(len(options)):

        stdscr.addstr(curs_y, curs_x, '     ', color)

        stdscr.addstr(curs_y, curs_x, '['+options[i][0]+']', color_alt)

        curs_x += 5

        stdscr.addstr(curs_y, curs_x, '        ', color)

        stdscr.addstr(curs_y, curs_x, ' '+options[i][1], color)

        if i % 2 == 0: curs_y, curs_x = (curs_y+2), (x+1)

        else:          curs_y, curs_x = y, (curs_x+8)


    stdscr.refresh()


def multitextwinv(y, x, typechs, lengths, titles, is_hiddens):

    curs_y, curs_x = y, x;

    color = curses.color_pair(colors['W/BK'])

    height, width = (len(titles)*3), (max(lengths)+4)

    window(curs_y, curs_x, height, width, color, True)


    height, width = 1, max(lengths)

    curs_y, curs_x = (y+1), (x+2)


    for i in range(len(titles)):

        stdscr.addstr((curs_y-1), curs_x, '|'+titles[i]+'|')

        window(curs_y, curs_x, height, width, color, False)

        curs_y += 3


    curs_y = (y+1)


    buffers = []

    for i in range(len(titles)):

        ret = textbox(curs_y, curs_x,\
                      height, width,\
                      typechs[i], lengths[i], titles[i],\
                      is_hiddens[i]);
   
        if ret == keyboard['ESC']:

            height, width = (len(titles)*3), (max(lengths)+4)

            clear(y, x, height, width)


            return ret # as ESC key.

        else:

            buffers.append(ret)

        curs_y += 3


    height, width = (len(titles)*3), (max(lengths)+4)

    clear(y, x, height, width)


    return buffers 


def multitextwinh(y, x, typechs, lengths, titles, is_hiddens):

    curs_y, curs_x = y, x;

    color = curses.color_pair(colors['W/BK'])

    height, width = 3, (sum(lengths)+(len(lengths)*3)+2)

    window(curs_y, curs_x, height, width, color, True)


    height = 1

    curs_y, curs_x = (y+1), (x+2)


    for i in range(len(titles)):

        width = (lengths[i]+1)

        stdscr.addstr((curs_y-1), curs_x, '|'+titles[i]+'|')

        window(curs_y, curs_x, height, width, color, False)

        curs_x += (width + 2)


    curs_x = (x+2)


    buffers = []

    for i in range(len(titles)):

        width = (lengths[i]+1)

        ret = textbox(curs_y, curs_x,\
                      height, width,\
                      typechs[i], lengths[i], titles[i],\
                      is_hiddens[i]);
   
        if ret == keyboard['ESC']:

            height, width = 3, (sum(lengths)+(len(lengths)*3)+2)

            clear(y, x, height, width)


            return ret # as ESC key.

        else:

            buffers.append(ret)

        curs_x += (width + 2)


    height, width = 3, (sum(lengths)+(len(lengths)*3)+2)

    clear(y, x, height, width)


    return buffers 


def textwin(y, x, typech, length, title, is_hidden):

    curs_y, curs_x = y, x

    height, width = 3, ((length+1)+4)

    color = curses.color_pair(colors['W/BK'])

    window(curs_y, curs_x, height, width, color, True)


    height, width = 1, (length+1)

    curs_y, curs_x = (y+1), (x+2)


    buffer = textbox(curs_y, curs_x,\
                     height, width,\
                     typech, length, title,\
                     is_hidden)


    height, width = 3, ((length+1)+4)

    clear(y, x, height, width)


    return buffer


def textbox(y, x, height, width, typech, length, title, is_hidden):

    curs_y, curs_x = y, x

    stdscr.addstr((curs_y-1), curs_x, '|'+title+'|')

    color = curses.color_pair(colors['W/BK'])

    window(curs_y, curs_x, height, width, color, False)


    stdscr.move(curs_y, curs_x)

    stdscr.refresh();


    return input(curs_y, curs_x,\
                 typech, length,\
                 is_hidden)


def window(y, x, height, width, color, is_drop):

    if is_drop:

        drop = curses.color_pair(colors['BK/W'])

        shadow(y, x, height, width, drop)


    win = curses.newwin((height+2), (width+2), (y-1), (x-1))

    win.bkgd(color)

    win.box(0, 0)

    win.refresh()


    stdscr.refresh()


def shadow(y, x, height, width, color):

    curs_y, curs_x = y, (x+width+1)
 
    for i in range(height+1):

        stdscr.addch(curs_y, curs_x, ' ', color)

        curs_y += 1


    curs_y, curs_x = (y+height+1), x

    for i in range(width+2):

        stdscr.addch(curs_y, curs_x, ' ', color)

        curs_x += 1


def clear(y, x, height, width):

    clr = curses.newwin((height+3), (width+3), (y-1), (x-1))

    color = curses.color_pair(colors['W/BK'])

    clr.bkgd(color)

    clr.refresh()


    stdscr.refresh()


def input(y, x, typech, length, is_hidden):

    curs_y, curs_x = y, x


    buffer = ''

    while True:

        curses.curs_set(1)

        key = stdscr.getch()

        stdscr.move(curs_y, curs_x)


        if key == keyboard['ESC']:

            curses.curs_set(0)

            return key

        elif key == keyboard['ENTER'] and not len(buffer) == 0:

            curses.curs_set(0)

            return buffer 

        elif key == keyboard['BACKSP'] and len(buffer) > 0:

            ret = backsp(curs_y, curs_x, buffer)

            if not ret == -1:

                buffer = ret
   
                curs_x -= 1

        elif regex['VARCHAR'].match(chr(key)) and len(buffer) < length:

            ret = addchr(curs_y, curs_x,\
                         typech, chr(key), buffer,\
                         is_hidden)

            if not ret == -1:

                buffer = ret

                curs_x += 1


def backsp(y, x, buffer):

    curses.curs_set(1)


    if len(buffer) == 0:

        return -1

    else:

        x -= 1

        stdscr.move(y, x)
 
        stdscr.addch(' ')

        stdscr.move(y, x)

        stdscr.refresh()


        return buffer[:-1]


def addchr(y, x, typech, ch, buffer, is_hidden):

    curses.curs_set(1)


    if not regex[typech].match(ch):

        return -1

    else:

        if not is_hidden: stdscr.addch(ch)

        else:             stdscr.addch('*')

        x += 1

        stdscr.move(y, x)

        stdscr.refresh();

        
        return (buffer + ch)


def exit():

    stdscr.keypad(True)


    curses.echo()

    curses.endwin()
