#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, getopt, re, time
from ptt import Ptt
from math import ceil


def help():
    print ''
    print 'Extract Ptt users list from article and add to your Ptt special name list'
    print ''
    print 'Usage: %s <options>' % sys.argv[0]
    print '-i: Article file sent from Ptt email'
    print '-u: Your Ptt user id'
    print '-p: Your Ptt user password'
    print '-h: Show help message and exit'
    print ''


def get_users(file):
    """Extra Ptt users list from article file.

    Args:
        file: Article file.

    Returns:
        A list of Ptt users without ordering.
    """
    with open(file) as f:
        lines = f.readlines()

    # Examle:
    #  [1;37m推  [33mPPJJ [m [33m: +1                                   [m123.123.123.123 11/17 21:39
    users = []
    #comment_regex = re.compile(ur'^\s*\[1;3[0-9]m[\u2192\u4E00-\u9FFF]+\s+\[33m(\w+)\s+\[m\s+\[33m', re.UNICODE)
    comment_regex = re.compile(ur'^\s*\[1;3[0-9]m[\u2192噓推]+\s+\[33m(\w+)\s+\[m\s+\[33m', re.UNICODE)
    for index, line in enumerate(lines):
        result = comment_regex.search(line.decode('utf8'))
        if result:
            user = result.group(1)
            users.append(user)
            #print '%d: %s' % (index + 1, user)

    # Remove redundant users
    users = list(set(users))
    return users


if __name__ == '__main__':
    # Note: Options is the string of option letters that the script wants to recognize,
    #       e.g. "ch" means "-c" and "-h". For options that require an argument followed
    #       by a colon (':'), e.g. "i:" means "-i <filename>"
    try:
        myopts, args = getopt.getopt(sys.argv[1:], "i:u:p:h")
        if len(myopts) == 0:
            help()
            sys.exit(1)
    except getopt.GetoptError as e:
        print str(e)
        help()
        sys.exit(1)

    file, id, pwd = None, None, None
    for o, a in myopts:
        if o == '-i':
            file = a
        elif o == '-u':
            id = a
        elif o == '-p':
            pwd = a
        elif o == '-h':
            help()
            sys.exit(0)

    try:
        if not file:
            raise Exception('No article specified')
        if not id:
            raise Exception('No user id')
        if not pwd:
            raise Exception('No user password')
    except Exception as e:
        print '%s, quitted' % e
        sys.exit(1)

    start_time = time.time()
    ptt = Ptt()
    if ptt.login(id, pwd):
        # Get users
        filename, file_extension = os.path.splitext(file)
        users = get_users(file)

        # Enter name list
        ptt.send('n')

        max_list_len = 128
        for i in xrange(0, int(ceil( float(len(users)) / max_list_len) )):
            if i > 9:
                print 'Only 9 lists, too many users in article'
                break

            # Enter special list and select list number
            ptt.send_combo(['s', str(i)])

            # Add users
            for user in users[ max_list_len*i : max_list_len*(i+1) ]:
                msg = 'Adding %s...' % user
                print msg,
                ptt.send_combo(['a', user], wait=.3)
                if u'描述一下' in ptt.read(wait=0):
                    ptt.send('')
                print 'done'

            # Quit list
            ptt.send('q')
            # Save list name if be asked
            if u'簡短名稱' in ptt.read():
                # Delete list name if exists, the maximum list name length is 29
                for j in xrange(0, 29):
                    ptt.send_no_newline('\b')

                list_name = filename[:28] + str(i)
                print 'Save list to "%s"' % list_name
                ptt.send(list_name)

        # Log out
        ptt.send_no_newline('\x1b[D')  # left arrow
        ptt.send_combo(['g', 'y'])
        print 'Quit, the operation took %d seconds' % (time.time() - start_time)

    ptt.close()
