
# Client script 
# allows to connect maximum of 30 clients to the server for communication

import select, socket, sys
from chat_events import Room, ChatHall, ChatMember
import chat_events

# buffer to store messages
buffer = 4096

# check the number of arguments
if len(sys.argv) < 2:
    print("Requried arguments - python client_chat.py [host ip address]")
    sys.exit(1)

# if the input is correct, establish connection to the server
else:
    connect_to_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connect_to_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    connect_to_server.connect((sys.argv[1], chat_events.PORT))

print("Successfully connected to the server\n")
message_prefix = ''

socket_list = [sys.stdin, server_connection]

def prompt():
    sys.stdout.write('<Me>')
    sys.stdout.flush()
try:
	while True:
	    read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])
	    for s in read_sockets:
			if s is server_connection:  
		    	message = s.recv(buffer) # to receive the data from the client socket
		    	if not message: # if incorrect message
					print("Server down!")
					sys.exit(2)
		    	else: # if client wants to quit the connection
					if message == chat_events.QUIT_STRING.encode():
			    		sys.stdout.write('Bye\n')
			    		sys.exit(2)
					else: #start the connection by sending name in the message			
			    		sys.stdout.write(message.decode())
			    		if 'Please tell us your name - ' in message.decode():
							message_prefix = 'name: '
			    		else:
							message_prefix = ''
			    			prompt()

			else:
		    	message = message_prefix + sys.stdin.readline()
		    	server_connection.sendall(message.encode())
finally:
    sys.exit(2)
		
