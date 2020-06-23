import socket, argparse, select, sys, random, string
parser = argparse.ArgumentParser(description = 'TCP Client')

parser.add_argument('ip', type=str,
                    help='The IP to connect to.')

parser.add_argument('port', type=int,
                    help='The port to use.')

parser.add_argument('-u', '--username', type=str,
                    help='The username to connect under (if none is given, one will be randomly generated')
args = parser.parse_args()

def usernamegen():
    # quick little username generator

    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(5))

if args.username == None:
    args.username = usernamegen()

def main(ip, port, username):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.connect((args.ip, args.port))

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
                message = sock.recv(2048)
                print(message.decode())

            else:
                print("sending message")
                message = sys.stdin.readline()
                s.send(message.encode(encoding='utf-8'))
                sys.stdout.write("you:")
                sys.stdout.write(message)
                sys.stdout.flush()

if __name__ == '__main__':
    try:
        main(args.ip, args.port, args.username)
    except KeyboardInterrupt as e:
        print(e)
        sys.exit(1)
