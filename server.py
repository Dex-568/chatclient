import socket
import threading
import sys
import datetime


def main():

    dt = datetime.datetime.now()
    x = dt.strftime('%H:%M:%S')

    print('------------------')
    print('Dex\'s Chat Server')
    print('Current Time: {}'.format(x))
    print('Enter a command below or type help for a command list')

    while True:
        menuinput = input('\n> ')

        if menuinput == 'help':
            help = comm_help()
            print(help)
        elif menuinput == 'new':
            serv_handle()
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
    help_list['connect'] = '''Host a chat room for multiple users to connect
                            to.'''
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
    not_fucked_to_all_shit = True  # fuck sake
    # gets the connection and then spits it back out for everyone
    while not_fucked_to_all_shit:
        res = conn.recv(1024)

        # stops it from spamming the server when a disconnect occurs
        if not res.decode():
            print('Client returned empty string, breaking thread')
            remove(conn, clientlist)
            not_fucked_to_all_shit = False  # oh fuck
        else:
            messagebroadcast(res, conn, clientlist)


def serv_handle():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    ip = input('Enter an IP to host your chat room on. (Leave blank for localhost): ')
    if ip is None:
        ip = '127.0.0.1'
        print(ip)

    port = input('Enter port: ')
    port = int(port)

    # stops that shitty 'address already in use' shit while testing
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        s.bind((ip, port))
    except Exception as e:
        print(e)

    s.listen(3)  # probably going to change this
    clientlist = []

    print('listening on {}:{}\n'.format(ip, port))

    while True:
        conn, addr = s.accept()
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
    if connection in clientlist:
        clientlist.remove(connection)


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
