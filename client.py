import socket, argparse, select, sys, random, string, datetime


'''
parser = argparse.ArgumentParser(description = 'TCP Client')

parser.add_argument('ip', type=str,
                    help='The IP to connect to.')

parser.add_argument('port', type=int,
                    help='The port to use.')

parser.add_argument('-u', '--username', type=str,
                    help='The username to connect under (if none is given, one will be randomly generated')
args = parser.parse_args()
'''

def usernamegen():
    # quick little username generator
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(5))


def main():

    command_list = ['help','about','connect','exit']

    # get the current date and time and format it all nice and shit
    dt = datetime.datetime.now()
    x = dt.strftime('%H:%M:%S')

    print('-----------------')
    print('Dex\'s Chat Client')
    print('Current Time: {}'.format(x))
    print('Enter a command below or type help for a command list.')

    while True:
        menuinput = input('\n> ')
        # this is absolutely terrible and i am ashamed
        # probably should whack this in a command handler
        # or make a command list and iterate through
        if menuinput == 'help':
            x = comm_help()
            print(x)
        elif menuinput == 'connect':
            conn_handle()
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
    help_list['connect'] = 'Initialise a connection to a chat room (IP Based for now).'
    help_list['exit'] = 'Exits the program.'

    # make a nice little top part to the help bar
    top = '\n Command ' + ' - '
    top += ' Description\n %s\n' % ('-' * 50)

    # do some fucking witchcraft to make it look good
    for x in sorted(help_list):
        dec = help_list[x]
        top += ' ' + x + ' - ' + dec + '\n'

    return top.rstrip('\n')

def conn_handle():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    ip = input('Enter IP:')
    port = input ('Enter Port: ')
    port = int(port)
    username = input('Enter username to connect under:\n(If none is given, one will be randomly generated.)')


    try:
        print('Connecting to {}:{}'.format(ip, port))
        s.connect((ip, port))
    except Exception as e:
        print(e)

    while True:
        # instead of just blindly sending and waiting for a response
        # which fucks things up after a while use select to make things fancy
        inputs = [sys.stdin, s]

        read_sock, write_sock, error_sock = select.select(inputs,[],[])
        # go through each possible sock and if a message is not
        # being broadcasted from server, send a message
        # select doesn't like python native input and instead loves file objects
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

                # replay the message back because it won't get broadcasted to the sender
                print(message)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as e:
        print(e)
        sys.exit(1)
