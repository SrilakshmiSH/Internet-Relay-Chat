
# Server script to host the communication for a maximum of 30 clients

import select, socket, sys, pdb
from chat_events import ChatHall, Room, ChatMember
import chat_events

# buffer to store the messages
buffer = 4096

# obtain the server IP address 
if (len(sys.argv) >= 2):
    host = sys.argv[1] 
else:
    host = ''

# listen to the newly created socket
listensocket = chat_events.create_socket((host, chat_events.PORT))

# assign the server socket to start connection and maintain a connection list
serversocket = listensocket
chat_hall_list = ChatHall()
connection_list = []
connection_list.append(listensocket)

while True:
    read_sockets, write_sockets, error_sockets = select.select(connection_list, [], []) 
	    
    for member in read_sockets:
	# add new socket to the list of clients
        if member is listensocket: # new connection, member is a socket
            new_socket, add = member.accept()
            new_member = ChatMember(new_socket)
            connection_list.append(new_member)
            chat_hall_list.welcome_new(new_member)
	# receive message from client
        else: 
            message = member.socket.recv(buffer)
	    
	    if not message:
		chat_hall_list.remove_member(member)
            if message:
                message = message.decode().lower()
                chat_hall_list.message_handler(member, message)
            else:
                member.socket.close()
                connection_list.remove(member)
    
# error in sockets
# remove error socket from client list    
    for sock in error_sockets: 
        sock.close()
        connection_list.remove(sock)
