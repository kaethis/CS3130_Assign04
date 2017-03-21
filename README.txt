-----------------------------------------------------------------
          _          _                         _    __  _ _  
         /_\   _____(_)__ _ _ _  _ __  ___ _ _| |_ /  \| | | 
        / _ \ (_-<_-< / _` | ' \| '  \/ -_) ' \  _| () |_  _|
       /_/ \_\/__/__/_\__, |_||_|_|_|_\___|_||_\__|\__/  |_| 
                      |___/                                  
-----------------------------------------------------------------

[AUTHOR]  Matt W. Martin, 4374851
          kaethis@tasmantis.net

[VERSION] 1.0

[PROJECT] CS3130, Assign04
          TCP CHAT PROGRAM

          A simple TCP Python chat program.

          Chat is performed between clients, with the server
          acting as the intermediary.  Although communication is
          bidirectional, the server can accomodate multiple users
          at a time.  After LOGIN, hit the [U] key for a list of
          online users to whom you may chat with.  If sending a
          message to an offline user, the message will be
          delivered upon his or her next LOGIN.  Follow on-screen
          instructions for context.

          IMPORTANT: I'm including this warnining in advance of
                     the ISSUES section because it's incredibly
                     important.  To my chagrin, there's a pretty
                     awful bug that occurs seemingly randomly
                     that obscures/corrupts the console user
                     interface after logging in -- the extent of
                     which can vary from only slightly annoying
                     to absolutely unusable.

                     If this occurs, LOGOUT normally and try
                     again (awful advice, I know, but it'll have
                     to do before I can isolate the cause).
                     LOGOUT is performed by pressing the [ESC]
                     key and hitting [RET].  Sorry in advance for
                     the inconvenience.

          IMPORTANT: Also, please modify the size of your console
                     window to accomodate the user interface: at
                     minimum, the client requires 99x36 chars,
                     otherwise the curses library will fail to
                     print to certain areas of the console.
 
[DATE]    20-Mar-2017

[ISSUED]  XX-Feb-2017

[USAGE]   See 'python3 driver.py -h' for program execution
          instructions.

[SETUP]   SERVER: Setting up the server requires some database
                  configuration beforehand.  This program uses
                  MariaDB as its database management system;
                  'dbmgr.py' interfaces with the DBMS.

                  For first-time installation instructions, refer
                  to this tutorial:

                      https://tinyurl.com/n6ow6qq

                  It's advised you review the 'mysql_create.txt'
                  file before piping into mysql.  These lines
                  serve as queries to the DBMS for creating the
                  database.

                  Optionally, you may wish to change the default
                  username and password for the database user
                  assigned in the DBMS; by default, they are
                  'DB_USER' and 'Password1234', respectively.

                  There are several samples for registering users
                  that may serve as a template; passwords are
                  hashed using SHA-224, so ensure you insert the
                  hashed password rather than its plain-text
                  counterpart (the 'hashlib' Python module can
                  serve this purpose).

                  After MariaDB has been successfully installed
                  and configured, pipe 'mysql_create.txt' into
                  mysql by entering:

                      'sudo mysql < mysql_create.txt'

                  Finally, execute the server application (see
                  USAGE).

          CLIENT: After the server has been fully configured and
                  brought online, execute the client application
                  (again, see USAGE).
                     
[MODULES] > argparse
          > hashlib
          > socket
          > struct
          > threading
          > curses
          > re
          > pymysql

[FILES]   ./README.txt
          ./driver.py
          ./chatserver.py
          ./chatclient.py
          ./dbmgr.py
          ./ui.py
          ./mysql_create.txt

[ISSUES]  - 'UI CORRUPTION AFTER LOGIN' [1.0]
            As mentioned previously, there's a bug that occurs
            seemingly randomly after LOGIN that causes the user
            interface to go haywire (at best, trailing characters
            may sometimes follow console output on certain areas
            of the screen, or a portion of the chat window may
            appear to be missing; at worst, a volley of unicode
            characters may litter the entire console window!).
            I'm going to take a guess that this is the infamous
            producer-consumer problem at play, two different
            threads (the main thread, and the one that evokes
            the clientthread function) share the console at the
            same time in order to achieve asynchronous input and
            output to and from the user (as in, waiting for user
            input won't block the chat window from displaying
            incoming messages and so forth).  At this time, I'm
            not going to consider this critical (although it
            arguably is at its worst), but I'll investigate the
            true cause of the issue at a later time.  For now,
            please LOGOUT as you normally would and try again
            until the issue doesn't manifest.  This only appears
            to happen after branching off from the main thread
            shortly after LOGIN.

          - 'USER LOCKOUT' [1.0]
            After LOGIN, attempting to log in with the same
            credentials will result in an error stating that the
            user has already been logged in.  Technically, this
            is because the entry corresponding to that user in
            the database has been modified to read as logged-in.
            Logistically, this is to prevent user sessions from
            being hyjacked from another client with the user has
            signed on, or to accomodate guest accounts where user
            credentials may be widely known.  That said, if the
            client disconnects from the server without logging
            out proper, this will prevent the user from signing
            on again, as the database still lists them as being
            online.  I'm still deciding how I'm going to solve
            this, but for now: PLEASE, PLEASE LOGOUT PROPERLY!

          - 'CONSOLE WINDOW SIZE' [1.0]
            The client application requires a minimum console
            size of 99x36 in order to accomodate the interface.
            Otherwise, printing to certain areas of the console
            will fail.  I'm currently looking into an elegant
            solution for adjusting the console window size prior
            to invoking curses, but for now, I kindly ask you
            make your console window large enough before running
            the client application.

[REPO]    https://github.com/kaethis/CS3130_Assign04
