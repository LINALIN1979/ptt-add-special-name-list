#!/usr/bin/env python
# -*- coding: utf-8 -*-
import telnetlib
import re
from time import sleep


class Ptt:
    def __init__(self):
        self.tn = telnetlib.Telnet('ptt.cc')
        self.buf = None
        self.ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')

    def send_no_newline(self, cmd):
        """Send command without new line as postfix.

        Args:
            cmd: Command.

        Returns:
            None.
        """
        self.tn.write( cmd.encode('big5') )

    def send(self, cmd):
        """Send command with new line as postfix.

        Args:
            cmd: Command.

        Returns:
            None.
        """
        self.send_no_newline(cmd + '\r\n')

    def send_combo(self, cmd_list, wait=.7):
        """Send a list of commands. The command starts with '~' would send without new
        line.

        Args:
            cmd_list: A list of commands.
            wait: How many seconds to wait before read data from socket. The default is
                  0.7 second.

        Returns:
            None.
        """
        old_screen = self.read(wait=0)
        for cmd in cmd_list:
            if cmd.startswith('~'):
                self.send_no_newline(cmd[1:])
            else:
                self.send(cmd)

            # Wait for screen change
            new_screen = self.read(wait=wait)
            while new_screen == old_screen:
                #print self.pure_text(new_screen)
                new_screen = self.read(wait=wait)
            old_screen = new_screen

    def read(self, wait=.7):
        """Read screen.

        Args:
            wait: How many seconds to wait before read data from socket. The default is
                  0.7 second.

        Returns:
            Screen.
        """
        sleep(wait)
        screen = self.tn.read_very_eager().decode('big5','ignore')
        if (len(screen) > 0):
            self.buf = screen
            #print self.pure_text(self.buf)
        return self.buf

    def pure_text(self, screen):
        """Translate screen into text and remove color code.

        Args:
            screen: Screen.

        Returns:
            Text of screen without color code.
        """
        return self.ansi_escape.sub('', screen)

    def login(self, id, pwd):
        """Login PTT with user id and password, return when stops at main menu.

        Args:
            id: User id.
            pwd: User password.

        Returns:
            Return True when login success, otherwise False.
        """
        max_retry = 3
        retry = max_retry
        state = 0
        try:
            while state >= 0:
                screen = self.read()
                #print ptt.pure_text(screen)

                if state == 0:
                    if u'請輸入代號' in screen:
                        print 'Input user id'
                        self.send(id)
                        state, retry = 1, max_retry
                    elif retry > 0:
                        retry -= 1
                    else:
                        raise Exception('No way to input account')

                elif state == 1:
                    if u'請輸入您的密碼' in screen:
                        print 'Input user password'
                        self.send(pwd)
                        state, retry = 2, max_retry
                    elif retry > 0:
                        retry -= 1
                    else:
                        raise Exception('No way to input password')

                elif state == 2:
                    if u'密碼不對' in screen:
                        raise Exception('Password incorrect')
                    elif u'您想刪除其他重複登入的連線嗎' in screen:
                        #print 'Kick out previous login'
                        #self.send('y')
                        #sleep(10)
                        print 'Allow duplicated login'
                        self.send('n')
                        sleep(5)
                        state = 3
                    else:
                        state = 3

                elif state == 3:
                    if u'按任意鍵繼續' in screen:
                        print 'Bypass welcome screen'
                        self.send('')
                    elif u'鴻雁往返' in screen:
                        print 'Bypass mailbox over quota message'
                        self.send_no_newline('q')
                    else:
                        state = 4

                elif state == 4:
                    if u'主功能表' in screen:
                        print 'Login success'
                        return True
                    elif retry > 0:
                        retry -= 1
                    else:
                        raise Exception('Failed to reach main menu')

        except Exception as e:
            print '%s, login failed' % e
            return False
        return True if state > 0 else False

    def close(self):
        """Close connection.

        Args:
            None.

        Returns:
            None.
        """
        self.tn.close()
