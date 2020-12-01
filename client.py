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
        # probably should whack this in a command handler
        # or make a command list and iterate through
        if menuinput == 'help':
            helpmenu = comm_help()
            print(helpmenu)
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
    help_list = {'help': 'Displays this help message.',
                 'about': 'Information about this program and its creator.',
                 'connect': 'Initialise a unencrypted connection to a chat room. (IP Based for now)',
                 'connectenc': 'Initialise an SSL/TLS encrypted connection to a chat room. (IP Based for now)',
                 'exit': 'Exits the program.'}

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

    ip = input('Enter IP to connect to. (Leave blank for localhost): ')
    if ip == "" or '127.0.0.1':
        ip = 'localhost'

    port = input('Enter Port: ')
    try:
        port = int(port)
    except ValueError:
        print("Port needs to be a number!\n")
        # who doesn't love a bit of recursion
        conn_handle(encstate)

    if port < 1000 and os.geteuid() != 0:
        print('Binding to privileged ports requires root privileges. Goodbye!\n')
        sys.exit(1)

    username = input('Enter username to connect under (If none is given, one will be randomly generated):')
    if not username:
        username = usernamegen()

    # start the whole tls/ssl shit
    if encstate is True:
        # quick little variable change due to ssl cert not liking numbers

        context = ssl.create_default_context()
        # use the cert for now until i make this shit work
        context.load_verify_locations('servcert.pem')
        encsock = context.wrap_socket(s, server_hostname=ip)

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
        except OSError as e:
            if e.errno == 111:
                print('[!] Connection Refused. Check IP and port and try again.')
                # just having it exit instead of recursing back
                sys.exit(1)
            else:
                print(e)
                sys.exit(1)

        print('Connected to {}:{}'.format(ip, port))

    commands = ['sslinfo', 'exit', 'help']

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
                if sock == s:
                    # the server will send empty strings when it get closed
                    # interpreting these as the server closing
                    servmessage = encsock.recv(1024)
                    if not servmessage:
                        print("Client received empty string, disconnecting.")
                        sys.exit(1)
                    else:
                        print(servmessage.decode())

                else:
                    message = sys.stdin.readline()
                    # fucking newlines
                    message = message.strip('\n')

                    # treat the message like a command if recognised
                    if message in commands:

                        # grabs the certificate from the server and parses
                        # the information to be read by the user
                        if message == 'sslinfo':
                            cert = encsock.getpeercert()

                            certkeys = list(cert.keys())
                            certvalues = list(cert.values())

                            # take the two commonname bits because there's no
                            # way in hell im trying to parse them
                            del certvalues[0:2]
                            del certkeys[0:2]

                            # do some wack shit i found on stackoverflow
                            for v, k in zip(certvalues, certkeys):
                                print('\n'+str(k)+":"+str(v))

                        # jesus looking at this shit a few months later racks the brain
                        elif message == 'help':
                            help_list = {'help': 'Displays this help message.'}

                            # do the same shit for the main menu help
                            top = '\n Command ' + ' - '
                            top += ' Description\n %s\n' % ('-' * 50)

                            for x in sorted(help_list):
                                dec = help_list[x]
                                top += ' ' + x + ' - ' + dec + '\n'

                            print(top.rstrip('\n'))


                    # otherwise ship it off to the server
                    else:

                        # slap the username onto the front of the message
                        message = username+':'+message
                        encsock.send(message.encode(encoding='utf-8'))

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
                    servmessage = s.recv(2048)
                    if not servmessage:
                        print("Client received empty string, disconnecting.")
                        sys.exit(1)
                    else:
                        print(servmessage.decode())
                else:
                    # slap the username onto the front of the message
                    message = sys.stdin.readline()
                    message = message.strip("\n")
                    if message in commands:
                        # sslinfo isn't used for an unencrypted connection, lets hope the user knows that

                        if message == 'help':
                            help_list = {'help': 'Displays this help message.'}

                            # do the same shit for the main menu help
                            top = '\n Command ' + ' - '
                            top += ' Description\n %s\n' % ('-' * 50)

                            for x in sorted(help_list):
                                dec = help_list[x]
                                top += ' ' + x + ' - ' + dec + '\n'

                            print(top.rstrip('\n'))
                    else:
                        message = username + ':' + message
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
