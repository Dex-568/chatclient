# chatclient

- [x] get threading working and have multiple clients able to connect
- [x] clean up the code a bit and make it look a bit more user friendly
- [x] add ssl support without it breaking
- [x] make it a bit more verbose and fix the flow control
- [x] handle thread ending when disconnect occurs so it doesn't shit itself and die
- [x] help command when connecting (client + server?)
- [ ] instead of just catching the keyboard interrupt, go back to the main menu (make sure the thread ends or else we'll be in for a world of pain)
- [ ] add kick/ban features? idk

This is a little side hobby of mine to expand my knowledge of python with differerent libraries like threading and ssl.

To use it simply run server.py and follow the instructions, then connect a few client.py's and it's all smooth sailing from there.

## server.py

The server takes two arguments when choosing either an unencrypted (new) or encrypted (newenc) sessions. These would be the IP and port to listen on.

Right now the server holds a sort of spectator role in that no commands can be issued from the server (mainly because I have no fucking clue) but it holds a log of messages sent.

The server is multithreaded and can allow up to 3 clients (changeable in the code).

## client.py

The client takes 3 arguments when choosing either a unencrypted (connect) or encrypted (connectenc) sessions. These would be the IP, port and the username to connect under.

The client can both receive messages from other clients and issue commands to the server/get information about the client.


## SSL

The ssl option first checks if you have already got a certificate saved within the directory, if none is found one will be generated with a time expiry of 4 days (changeable in the code).

*Right now the SSL function only works on local machines due to the self signed certs and how they are set up*
