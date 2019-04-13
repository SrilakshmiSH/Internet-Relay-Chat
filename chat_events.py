
# Different helper functions to handle chat room events for server-client communciation
# Events such as join room, leave room, switch rooms
# send general and personal messages

import socket, pdb

# define maximum number of clients, port number and quit message string
MAX_CLIENTS = 30
PORT = 22221
QUIT_STRING = '<$quit$>'

# create socket 
def create_socket(address):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setblocking(0)
    s.bind(address)
    s.listen(MAX_CLIENTS)
    print("Listening at port number - ", address)
    return s

# class to handle the room operations
class Room:
    def __init__(self, name):
        self.active_room_members = []
        self.member_name = member_name
    
# function to broadcast messages from the client to the members in the room
    def broadcast(self, from_member, message):
        message = from_member.member_name.encode() + b":" + message
        for member in self.active_room_members:
            member.socket.sendall(message)
			
# function to welcome the new client to begin chat
    def welcome_new(self, from_member):
        message = self.member_name + " welcomes: " + from_member.member_name + " to chat room "+ '\n'
        for member in self.active_room_members:
            member.socket.sendall(message.encode())
			
# function to remove a client from the connection
# and broadcast leave message to all the members in the room
    def remove_member(self, member):
        self.active_room_members.remove(member)
        leave_message = member.member_name.encode() + b"has left the chat room\n"
        self.broadcast(member, leave_message)
	
# class to maintain list of client present in the room
class ChatMember:
    def __init__(self, socket, name = "new" , currentroomname = "new"):
        socket.setblocking(0)
        self.socket = socket
        self.member_name = member_name
        self.currentroomname = currentroomname
    def fileno(self):
        return self.socket.fileno()
	
# class to define the chat hall with different actions
class ChatHall:
    def __init__(self):
        self.rooms = {} 
        self.room_member_map = {}
        self.active_room_members_map = {} 
	
# function to welcome the new client
    def welcome_new(self, new_member):
        new_member.socket.sendall(b'Welcome to chat room.\nPlease tell us your name:\n')
    
# function to describe instructions to be displayed in the chat hall
    def message_handler(self, member, message):
        instructions = b'List of options:\n'\
            + b'[<manual>] to display the options\n' \
            + b'[<list>] to list the available rooms\n'\
            + b'[<join> room_name] to join or create a new room\n' \
            + b'[<switch>] to switch room\n' \
            + b'[<leave>] to leave the current room\n'\
	        + b'[<personal> member_name] to send personal messages\n'\
            + b'[<quit>] to quit the chat\n' \
            + b'Begin chat now - ' \
            + b'\n'

        print(member.member_name + " says: " + message)
        if "member_name:" in message:
            member_name = message.split()[1]
            member.member_name = member_name
            print("New connection request from - ", member.member_name)
            self.active_room_members_map[member.member_name]=member
            member.socket.sendall(instructions)

# action - quit the chat room
        elif "<quit>" in message:
            member.socket.sendall(QUIT_STRING.encode())
            self.remove_member(member)

# action - list the available rooms
        elif "<list>" in message:
            print self.rooms
            print self.room_member_map
            self.list_rooms(member) 

# action - join the chat room
        elif "<join>" in message:
            same_room = False
            if len(message.split()) >= 2:
                room_name = message.split()[1]
                member.currentroomname = room_name
                if member.name+"-"+room_name in self.room_member_map: 
                    if self.room_member_map[member.name+"-"+room_name] == room_name:
                        member.socket.sendall(b'You are already in room: ' + room_name.encode())
                        same_room = True
                    else:
                        old_room = self.room_member_map[member.name+"-"+room_name]
                if not same_room:
                    if not room_name in self.rooms:
                        new_room = Room(room_name)
                        self.rooms[room_name] = new_room
                    self.rooms[room_name].active_room_members.append(member)
                    self.rooms[room_name].welcome_new(member)
                    self.room_member_map[member.name+"-"+room_name] = room_name
            else:
                member.socket.sendall(instructions)

# action - switch from one room to another
        elif "<switch>" in message:
            if len(message.split()) >= 2:
                switchroomname=message.split()[1]
                if member.name+"-"+switchroomname in self.room_member_map:
                    member.currentroomname = switchroomname
                else:
                    message = "you are not in entered room please join"
                    member.socket.sendall(message.encode())
            else:
                member.socket.sendall(instructions)

# action -leave the chat room
        elif "<leave>" in message:
            if len(message.split()) >= 2: 
                leaveroomname=message.split()[1]
                if member.name+"-"+leaveroomname in self.room_member_map:
                    del self.room_member_map[member.name+"-"+member.currentroomname]
                    self.rooms[leaveroomname].remove_member(member)
                    print("ChatMember: " + member.name + " has left"+leaveroomname+"\n")
                if len(self.rooms[leaveroomname].active_room_members)==0:
                    del self.rooms[leaveroomname]
                else :
                    message = "you entered wrong room name please try again\n"
                    member.socket.sendall(message.encode())
            else:
                member.socket.sendall(instructions)

# action - send personal message 
        elif "<personal>" in message:
            if len(message.split()) >= 2:
                membername = message.split()[1]
                if membername in self.active_room_members_map:
                    newmember = self.active_room_members_map[membername]
                    personal_room = Room("personal-"+member.name+"-"+membername)
                    self.rooms["personal-"+member.name+"-"+membername] = personal_room
                    self.rooms["personal-"+member.name+"-"+membername].active_room_members.append(member)
                    self.rooms["personal-"+member.name+"-"+membername].active_room_members.append(newmember)
                    self.room_member_map[member.name+"-"+"personal-"+member.name+"-"+membername] = "personal-"+member.name+"-"+membername
                    self.room_member_map[membername+"-"+"personal-"+member.name+"-"+membername] = "personal-"+member.name+"-"+membername
                    member.currentroomname = "personal-"+member.name+"-"+membername
                    newmember.currentroomname = "personal-"+member.name+"-"+membername
                else:
                    message = "Entered member does not exsist!!"
                    member.socket.sendall(message.encode())
            else:
                member.socket.sendall(instructions)

# action - manual listing of rooms
        elif "<manual>" in message:
            member.socket.sendall(instructions)

# action - remove member from the room
        elif not message:
            self.remove_member(member)

        else:
# action - check if client is present in a room or not
            if member.name+"-"+member.currentroomname in self.room_member_map:
                self.rooms[self.room_member_map[member.name+"-"+member.currentroomname]].broadcast(member, message.encode())
            else:
                message = 'You are currently not in any room! \n' \
                    + 'Use [<list>] to see available rooms! \n' \
                    + 'Use [<join> room_name] to join a room! \n'
                member.socket.sendall(message.encode())
    
# function to remove a client from the connection
    def remove_member(self, member):
        if member.name +"-"+member.currentroomname in self.room_member_map:
            self.rooms[self.room_member_map[member.name+"-"+member.currentroomname]].remove_member(member)
            del self.room_member_map[member.name+"-"+member.currentroomname]
        print("ChatMember: " + member.name + " has left\n")

# function to handle the listing of rooms
    def list_rooms(self, member):
        if len(self.rooms) == 0:
            message = 'Currently no active rooms. Create your own room by using [<join> room_name].\n'
            member.socket.sendall(message.encode())
        else:
            message = 'List current rooms and active room members - \n'
            for room in self.rooms:
                if 'personal' not in room:
                    print (self.rooms[room].active_room_members)
                    message += room + ": " + str(len(self.rooms[room].active_room_members)) + " member(s)\n"
                    for member1 in self.rooms[room].active_room_members:
                        message += member1.name +"\n"
                        member.socket.sendall(message.encode())

                        
