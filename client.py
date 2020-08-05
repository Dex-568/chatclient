# importing the whole fucking world

import socket
import select
import os
import sys
import random
import string
import datetime
import ssl


def usernamegen():
    # quick little username generator
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(5))


def main():

    # get the current date and time and format it all nice and shit
    dt = datetime.datetime.now()
    x = dt.strftime('%H:%M:%S')

    print('-----------------')
    print('Dex\'s Chat Client')
    print('Current Time: {}'.format(x))
    print('Enter \'connect\' or \'connectenc\' to get started or type help for a command list.')

    while True:
        menuinput = input('\n> ')
        # this is absolutely terrible and i am ashamed
        # probably should whack this in a command handler
        # or make a command list and iterate through
        if menuinput == 'help':
            help = comm_help()
            print(help)
        elif menuinput == 'connect':
            encstate = False
            conn_handle(encstate)
        elif menuinput == 'connectenc':
            encstate = True
            conn_handle(encstate)
        elif menuinput == 'exit':
            exit()
        elif menuinput == 'about':
            about()
        else:
            print('Unknown command!\nType help for a command list.\n')
            continue


def comm_help():

    help_list = {}
    help_list['help'] = 'Displays this help message.'
    help_list['about'] = 'Information about this program and its creator.'
    help_list['connect'] = '''Initialise a unencrypted connection to a chat room.
                            (IP Based for now)'''
    help_list['connectenc'] = '''Initialise an SSL/TLS encrypted connection
                                 to a chat room. (IP Based for now)'''

    help_list['exit'] = 'Exits the program.'

    # make a nice little top part to the help bar
    top = '\n Command ' + ' - '
    top += ' Description\n %s\n' % ('-' * 50)

    # do some fucking witchcraft to make it look good
    for x in sorted(help_list):
        dec = help_list[x]
        top += ' ' + x + ' - ' + dec + '\n'

    return top.rstrip('\n')


def conn_handle(encstate):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    ip = input('Enter IP:')
    if ip is None:
        ip = '127.0.0.1'

    port = input('Enter Port: ')
    port = int(port)

    if port < 1000 and os.geteuid() != 0:
        print('Binding to privileged ports requires root privileges. Goodbye!\n')
        sys.exit(1)

    username = input('Enter username to connect under:')

    if username is None:
        username = usernamegen()

    # start the whole tls/ssl shit
    if encstate is True:
        # quick little variable change due to ssl cert not liking numbers
        if ip == '127.0.0.1' or None:
            ip = 'localhost'

        context = ssl.create_default_context()
        # use the cert for now until i make this shit work
        context.load_verify_locations('servcert.pem')
        encsock = context.wrap_socket(s, server_hostname='localhost')

        try:
            print('Connecting to {}:{} using TLS'.format(ip, port))
            encsock.connect((ip, port))
        except Exception as e:
            print(e)

        print('Connected to {}:{} using {}'.format(ip, port, encsock.version()))
    else:

        try:
            print('Connecting to {}:{}'.format(ip, port))
            s.connect((ip, port))
        except Exception as e:
            print(e)

        print('Connected to {}:{}'.format(ip, port))

    if encstate is True:
        while True:
            # instead of just blindly sending and waiting for a response
            # which fucks things up after a while use select to make things fancy
            inputs = [sys.stdin, encsock]

            read_sock, write_sock, error_sock = select.select(inputs, [], [])
            # go through each possible sock and if a message is not
            # being broadcasted from server, send a message
            # select doesn't like python input and instead loves file objects
            # so sys.stdin it is
            for sock in read_sock:
                if sock == encsock:
                    servmessage = sock.recv(2048)
                    print(servmessage.decode())
                else:
                    message = sys.stdin.readline()
                    # slap the username onto the front of the message
                    message = username+':'+message
                    s.send(message.encode(encoding='utf-8'))

                    # replay the message back
                    # because it won't get broadcasted to the sender
                    print(message)
    else:
        while True:
            # instead of just blindly sending and waiting for a response
            # which fucks things up after a while use select to make things fancy
            inputs = [sys.stdin, s]

            read_sock, write_sock, error_sock = select.select(inputs, [], [])
            # go through each possible sock and if a message is not
            # being broadcasted from server, send a message
            # select doesn't like python input and instead loves file objects
            # so sys.stdin it is
            for sock in read_sock:
                if sock == s:
                    servmessage = sock.recv(2048)
                    print(servmessage.decode())
                else:
                    message = sys.stdin.readline()
                    # slap the username onto the front of the message
                    message = username+':'+message
                    s.send(message.encode(encoding='utf-8'))

                    # replay the message back
                    # because it won't get broadcasted to the sender
                    print(message)


def about():
    print('''This program was made by Dex\nAll Rights Reserved and all that shit\n
    Find me on Discord: Dex#0002 or on twitter: @Dex568''')
    return


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nKeyboard Interrupt Received, Exiting!\n')
        sys.exit(1)
