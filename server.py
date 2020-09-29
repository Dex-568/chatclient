import socket
import threading
import sys
import datetime
import ssl
import os


def main():

    dt = datetime.datetime.now()
    x = dt.strftime('%H:%M:%S')

    print('------------------')
    print('Dex\'s Chat Server')
    print('Current Time: {}'.format(x))
    print('\nEnter \'new\' or \'newenc\' to get started or type help for a command list.')

    while True:
        menuinput = input('\n> ')

        if menuinput == 'help':
            help = comm_help()
            print(help)
        elif menuinput == 'new':
            encstate = False
            serv_handle(encstate)
        elif menuinput == 'newenc':
            encstate = True
            serv_handle(encstate)
        elif menuinput == 'exit':
            exit()
        elif menuinput == 'about':
            about()
        else:
            print('[!] Unknown command!\nType help for a command list.\n')
            continue


def comm_help():

    help_list = {}
    help_list['help'] = 'Displays this help message.'
    help_list['about'] = 'Information about this program and its creator.'
    help_list['new'] = '''Host a chat room for multiple users to connect
       to.'''
    help_list['newenc'] = '''Host a chat room with SSL/TLS encryption for
          multiple users to connect to.'''
    help_list['exit'] = 'Exits the program.'

    # make a nice little top part to the help bar
    top = '\n Command ' + ' - '
    top += ' Description\n %s\n' % ('-' * 50)

    # do some fucking witchcraft to make it look good
    for x in sorted(help_list):
        dec = help_list[x]
        top += ' ' + x + ' - ' + dec + '\n'

    return top.rstrip('\n')


def handle_conn(conn, clientlist):
    # gets the connection and then spits it back out for everyone
    while True:
        res = conn.recv(1024)

        # stops it from spamming the server when a disconnect occurs
        if not res.decode():
            remove(conn, clientlist)
        else:
            print(res.decode())
            messagebroadcast(res, conn, clientlist)


def serv_handle(encstate):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    ip = input('Enter an IP to host your chat room on. (Leave blank for localhost): ')

    if ip == "":
        ip = 'localhost'

    try:
        port = input('Enter port: ')
        port = int(port)
    except ValueError:
        print('[!] Port empty or not valid.')
        # recursion probably isn't a good idea
        # but let's just assume the user can type in a port
        serv_handle(encstate)

    if port < 1000 and os.geteuid() != 0:
        print('[!] Binding to privileged ports requires root privileges. Goodbye!')
        sys.exit(1)

    # stops that shitty 'address already in use' shit
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    if encstate is True:
        # all of this assumes that the user hasn't already made a self signed cert
        # checking if a cert exists and making a new one if not

        if os.path.isfile('servcert.pem'):
            print('An SSL Certificate has been found. Using this.')
        else:
            print('Creating a new SSL Certificate for authentication (this only works on local machines for now)')
            os.system("openssl req -x509 -newkey rsa:4096 -keyout servkey.key -out servcert.pem -days 4 -nodes -subj '/CN=localhost'")

        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain('servcert.pem', 'servkey.key')

    try:
        s.bind((ip, port))
    except Exception as e:
        print(e)

    s.listen(5)  # probably going to change this
    clientlist = []

    print('\n[*] Listening on {}:{}\n'.format(ip, port))

    if encstate is True:
        encsock = context.wrap_socket(s, server_side=True)

        while True:
            conn, addr = encsock.accept()
            clientlist.append(conn)
            print('Connection from {}:{}\n'.format(addr[0], addr[1]))

            # make it fancy and threaded,
            # then people can simultaneously connect
            c_handle = threading.Thread(
                target=handle_conn,
                args=(conn, clientlist,)
            )
            # have a sort of p2p model or server? fuck knows
            c_handle.start()

    else:
        # i do love writing the same code again just for unencrypted traffic
        while True:
            conn, addr = s.accept()
            clientlist.append(conn)
            print('Connection from {}:{}\n'.format(addr[0], addr[1]))

            c_handle = threading.Thread(
                target=handle_conn,
                args=(conn, clientlist,)
            )

            c_handle.start()


def messagebroadcast(message, connection, clientlist):
    # my dumb ass thought it would just magically send it to everyone so here
    # i am with this fucking function
    for clients in clientlist:
        # uses the conn object to check if it is different, if so broadcast
        if clients != connection:
            try:
                clients.send(message)
            except socket.error:
                clients.close()
                # if no answer, remove the client from list
                remove(clients, clientlist)


def remove(connection, clientlist):
    print(clientlist)
    if connection in clientlist:
        clientlist.remove(connection)
        print(clientlist)

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
