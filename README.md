# chatclient

- [x] get threading working and have multiple clients able to connect
- [x] clean up the code a bit and make it look a bit more user friendly
- [x] add ssl support without it breaking
- [x] make it a bit more verbose and fix the flow control
- [ ] handle thread ending when disconnect occurs so it doesn't shit itself and die
- [ ] help command when connecting (client + server?)
- [ ] instead of just catching the keyboard interrupt, go back to the main menu (make sure the thread ends or else we'll be in for a world of pain)
- [ ] add kick/ban features? idk

This is a little side hobby of mine to expand my knowledge of python with differerent libraries like threading and ssl.

--- Right now the SSL function only works on local machines due to the self signed certs and how they are set up ---

To use it simply run server.py and follow the instructions, then connect a few client.py's and it's all smooth sailing from there.
