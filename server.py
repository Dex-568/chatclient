
import socket, argparse, threading

# stick this in a function or some shit?
parser = argparse.ArgumentParser(description = 'TCP Server')

parser.add_argument('ip', type=str,
                    help='The IP to bind (usually localhost or your local IP address).')

parser.add_argument('port', type=int,
                    help='The port to use.')
args = parser.parse_args()


def handle_conn(conn, clientlist):
    not_fucked_to_all_shit = True # fuck sake
    # add an interface like the client, give things like clients connected and shit?
    # probably add a sleep for the receive so i dont receive every tick or some dumb shit
    # gets the connection and then spits it back out for everyone
    while not_fucked_to_all_shit:
        print("at handle_conn")
        res = conn.recv(1024)

        # stops it from spamming the server when a disconnect occurs
        if not res.decode():
            print("Client returned empty string, breaking thread")
            remove(conn, clientlist)
            not_fucked_to_all_shit = False # oh fuck
        else:
            print(res.decode()+" from handle_conn")
            print(type(res))
            print(res)
            broadcast(res, conn, clientlist)

def main(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # stops that shitty 'address already in use' shit while testing
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s.bind((ip, port))
    s.listen(3) # probably going to change this
    clientlist = []

    print('listening on {}:{}\n'.format(ip,port))

    while True:
        conn, addr = s.accept()
        clientlist.append(conn)
        print('Connection from {}:{}\n'.format(addr[0], addr[1]))
        # make it fancy and threaded,
        # then people can simultaneously connect
        c_handle = threading.Thread(
            target = handle_conn,
            args = (conn,clientlist,)
        )
        # have a sort of p2p model or server? fuck knows
        c_handle.start()

def broadcast(message, connection, clientlist):
    print('at broadcast')
    # my dumb ass thought it would just magically send it to everyone so here
    # i am with this fucking function
    for clients in clientlist:
        # uses the conn object to check if it is different, if so broadcast
        if clients != connection:
            try:
                print('client message broadcasted')
                # somehow its getting fucked up from the creation to here
                clients.send(message)
            except:
                print('client removed')
                clients.close()
                # if no answer, remove the client from list
                remove(clients,clientlist)

def remove(connection, clientlist):
    if connection in clientlist:
        clientlist.remove(connection)

main(args.ip, args.port)
