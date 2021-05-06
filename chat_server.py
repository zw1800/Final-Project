"""
Created on Tue Jul 22 00:47:05 2014

@author: alina, zzhang
"""
import Game
import time
import socket
import select
import sys
import string
import indexer
import json
import pickle as pkl
from chat_utils import *
import chat_group as grp


class Server:
    def __init__(self):
        self.new_clients = []  # list of new sockets of which the user id is not known
        self.logged_name2sock = {}  # dictionary mapping username to socket
        self.logged_sock2name = {}  # dict mapping socket to user name
        self.all_sockets = []
        self.group = grp.Group()
        # start server
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(SERVER)
        self.server.listen(5)
        self.all_sockets.append(self.server)
        # initialize past chat indices
        self.indices = {}
        # sonnet
        self.sonnet = indexer.PIndex("AllSonnets.txt")
        self.number_of_accept = 0
        self.game = 0
        self.speaker_index = 0
        self.stage = 0
        self.candidates = {}
        self.total_vote = 0
        self.victim = ''
        self.victim_role = ''
        

    def new_client(self, sock):
        # add to all sockets and to new clients
        print('new client...')
        sock.setblocking(0)
        self.new_clients.append(sock)
        self.all_sockets.append(sock)

    def login(self, sock):
        # read the msg that should have login code plus username
        try:
            msg = json.loads(myrecv(sock))
            if len(msg) > 0:

                if msg["action"] == "login":
                    name = msg["name"]
                    if self.group.is_member(name) != True:
                        # move socket from new clients list to logged clients
                        self.new_clients.remove(sock)
                        # add into the name to sock mapping
                        self.logged_name2sock[name] = sock
                        self.logged_sock2name[sock] = name
                        # load chat history of that user
                        if name not in self.indices.keys():
                            try:
                                self.indices[name] = pkl.load(
                                    open(name + '.idx', 'rb'))
                            except IOError:  # chat index does not exist, then create one
                                self.indices[name] = indexer.Index(name)
                        print(name + ' logged in')
                        self.group.join(name)
                        mysend(sock, json.dumps(
                            {"action": "login", "status": "ok"}))
                    else:  # a client under this name has already logged in
                        mysend(sock, json.dumps(
                            {"action": "login", "status": "duplicate"}))
                        print(name + ' duplicate login attempt')
                else:
                    print('wrong code received')
            else:  # client died unexpectedly
                self.logout(sock)
        except:
            self.all_sockets.remove(sock)

    def logout(self, sock):
        # remove sock from all lists
        name = self.logged_sock2name[sock]
        pkl.dump(self.indices[name], open(name + '.idx', 'wb'))
        del self.indices[name]
        del self.logged_name2sock[name]
        del self.logged_sock2name[sock]
        self.all_sockets.remove(sock)
        self.group.leave(name)
        sock.close()

# ==============================================================================
# main command switchboard
# ==============================================================================
    def handle_msg(self, from_sock):
        # read msg code
        msg = myrecv(from_sock)
        if len(msg) > 0:
            # ==============================================================================
            # handle connect request this is implemented for you
            # ==============================================================================
            msg = json.loads(msg)
            if msg["action"] == "connect":
                to_name = msg["target"]
                from_name = self.logged_sock2name[from_sock]
                if to_name == from_name:
                    msg = json.dumps({"action": "connect", "status": "self"})
                # connect to the peer
                elif self.group.is_member(to_name):
                    to_sock = self.logged_name2sock[to_name]
                    self.group.connect(from_name, to_name)
                    the_guys = self.group.list_me(from_name)
                    msg = json.dumps(
                        {"action": "connect", "status": "success"})
                    for g in the_guys[1:]:
                        to_sock = self.logged_name2sock[g]
                        mysend(to_sock, json.dumps(
                            {"action": "connect", "status": "request", "from": from_name}))
                else:
                    msg = json.dumps(
                        {"action": "connect", "status": "no-user"})
                mysend(from_sock, msg)
# ==============================================================================
# handle messeage exchange: IMPLEMENT THIS
# ==============================================================================
            elif msg["action"] == "exchange":
                
                from_name = self.logged_sock2name[from_sock]
                """
                Finding the list of people to send to and index message
                """
                # IMPLEMENTATION
                # ---- start your code ---- #
                etime = time.strftime('%d.%m.%y,%H:%M', time.localtime())
                msg_content = msg["message"]
                self.indices[from_name].add_msg(etime + " " + msg_content)
                self.indices[from_name].indexing(msg_content, self.indices[from_name].total_msgs - 1)
                # ---- end of your code --- #
                the_guys = self.group.list_me(from_name)[1:]
                if self.stage == 0:
                    if msg_content == "gaming":
                        if len(self.group.list_me(from_name)) != 5:
                            mysend(self.logged_name2sock[from_name], json.dumps({"action": "exchange", "status": "number error"}))
                        else:
                            mysend(self.logged_name2sock[from_name], json.dumps({"action": "exchange", "status": "successfully sent"}))
                            for g in the_guys:
                                to_sock = self.logged_name2sock[g]
                                mysend(to_sock, json.dumps({"action": "gaming request"}))
                    else: 
                        for g in the_guys:
                            to_sock = self.logged_name2sock[g]
                            mysend(to_sock, json.dumps({"action": "exchange", "from":from_name, "message":msg_content}) )
                
                #stage 1 conversation                   
                elif self.stage == 1:
                    if msg_content == "Finished":
                        if self.speaker_index == (len(self.game.role.keys())-1):
                            self.speaker_index = 0
                            self.stage += 1
                            for j in self.game.role.keys():
                                mysend(self.logged_name2sock[j], json.dumps({"status": "start voting!"}))
                                           
                        else:           
                            self.speaker_index += 1
                            temp = list(self.game.role.keys())[self.speaker_index]
                            the_guys = self.group.list_me(temp)
                            mysend(self.logged_name2sock[temp], json.dumps({"speaker": temp, "status": "speaking"}))
                            for n in the_guys[1:]:
                                mysend(self.logged_name2sock[n], json.dumps({"speaker": temp, "status": "listening"}))
                    else: 
                        for g in the_guys:
                            to_sock = self.logged_name2sock[g]
                            mysend(to_sock, json.dumps({"status": "exchange", "from":from_name, "message":msg_content}))
                       
                elif self.stage == 2:
                   try:
                       vote_id = msg_content.split()[1]
                   except IndexError:
                       vote_id = ""
                       
                   if vote_id in self.game.role.keys():
                       if vote_id in self.candidates.keys():
                           self.candidates[vote_id] += 1
                       else:
                           self.candidates[vote_id] = 1
                       mysend(from_sock, json.dumps({"status": "vote received"}))
                       self.total_vote += 1
                       if self.total_vote == len(self.game.role.keys()):
                           werewolf_name = self.game.get_roletype("werewolf")[0]
                           result = self.game.vote(self.candidates)
                           for i in self.game.status.keys():
                               mysend(self.logged_name2sock[i], json.dumps({"status": "voting result", "result": result[0], "role": result[1]}))
                           if werewolf_name == result[0]:
                               for j in self.game.status.keys():     
                                   mysend(self.logged_name2sock[j], json.dumps({"status": "human wins!"}))
                               self.stage = 0
                               self.game = 0
                               self.total_vote = 0
                               self.candidates = {}
                           elif len(self.game.role.keys()) == 2 and self.game.status[werewolf_name] == "alive":
                               for m in self.game.status.keys(): 
                                   mysend(self.logged_name2sock[m], json.dumps({"status": "werewolf wins!"}))
                               self.stage = 0
                               self.game = 0
                               self.total_vote = 0
                               self.candidates = {}
                           else:
                               self.stage += 1
                               self.total_vote = 0
                               self.candidates = {}
                               for n in self.game.role.keys():
                                   mysend(self.logged_name2sock[n], json.dumps({"status": "night falls"}))
                               mysend(self.logged_name2sock[werewolf_name], json.dumps({"status": "werewolf's turn"}))
                     
                   else:
                       mysend(from_sock, json.dumps({"status": "invalid vote, try again"}))
                                       
                elif self.stage == 3:
                   seer_name = self.game.get_roletype("seer")[0]
                   try:
                       kill_id = msg_content.split()[1]
                   except IndexError:
                       kill_id = ""              
                   if kill_id in self.game.role.keys():
                       if kill_id == from_name:
                           mysend(from_sock, json.dumps({"status": "victim error"}))
                       else:
                           self.victim = kill_id
                           self.victim_role = self.game.role[kill_id]
                           mysend(from_sock, json.dumps({"status": "victim killed"}))
                           self.game.kill(kill_id)
                           self.stage += 1
                           mysend(self.logged_name2sock[seer_name], json.dumps({"status": "seer's turn"}))
                              
                   elif kill_id == "none":
                       mysend(from_sock, json.dumps({"status": "no one killed"}))
                       self.stage += 1
                       mysend(self.logged_name2sock[seer_name], json.dumps({"status": "seer's turn"}))
                                 
                   else:
                       mysend(from_sock, json.dumps({"status": "victim error"})) 
                   
                elif self.stage == 4:
                   try:
                       check_id = msg_content.split()[1]
                   except IndexError:
                       check_id = ""
                       
                   if check_id in self.game.status.keys():
                       if check_id in self.game.role.keys():
                           mysend(from_sock, json.dumps({"status": "check role", "role": self.game.role[check_id]}))         
                       else:
                           mysend(from_sock, json.dumps({"status": "check role", "role": check_id + " is dead"}))

                       self.game.day += 1
                       
                       for i in self.game.status.keys():
                           mysend(self.logged_name2sock[i], json.dumps({"status": "sun rises", "victim": self.victim, "victim role": self.victim_role, "Day": self.game.day}))
                       if len(self.game.role.keys()) == 2 and self.game.status[werewolf_name] == "alive":
                           for m in self.game.status.keys(): 
                               mysend(self.logged_name2sock[m], json.dumps({"status": "werewolf wins!"}))
                               self.stage = 0
                               self.game = 0
                       else:
                           for j in self.game.role.keys():
                               mysend(self.logged_name2sock[j], json.dumps({"status": "conversation start!"}))
                           self.stage = 1
                           temp = list(self.game.role.keys())[self.speaker_index]
                           the_guys = self.group.list_me(temp)
                           mysend(self.logged_name2sock[temp], json.dumps({"speaker": temp, "status": "speaking"}))
                           for n in the_guys[1:]:
                               mysend(self.logged_name2sock[n], json.dumps({"speaker": temp, "status": "listening"}))
 
                   else:
                       mysend(from_sock, json.dumps({"status": "check error"}))
                              

# ==============================================================================
# the "from" guy has had enough (talking to "to")!
# ==============================================================================
            elif msg["action"] == "disconnect":
                from_name = self.logged_sock2name[from_sock]
                the_guys = self.group.list_me(from_name)
                self.group.disconnect(from_name)
                the_guys.remove(from_name)
                if len(the_guys) == 1:  # only one left
                    g = the_guys.pop()
                    to_sock = self.logged_name2sock[g]
                    mysend(to_sock, json.dumps(
                        {"action": "disconnect", "msg": "everyone left, you are alone"}))
# ==============================================================================
#                 listing available peers: IMPLEMENT THIS
# ==============================================================================
            elif msg["action"] == "list":

                # IMPLEMENTATION
                # ---- start your code ---- #
                msg = str(self.group.members)
                # ---- end of your code --- #
                mysend(from_sock, json.dumps(
                    {"action": "list", "results": msg}))
# ==============================================================================
#             retrieve a sonnet : IMPLEMENT THIS
# ==============================================================================
            elif msg["action"] == "poem":

                # IMPLEMENTATION
                # ---- start your code ---- #
                sonnet_number = msg["target"]
                poem = str(self.sonnet.get_poem(int(sonnet_number)))
                print('here:\n', poem)
                # ---- end of your code --- #

                mysend(from_sock, json.dumps(
                    {"action": "poem", "results": poem}))
# ==============================================================================
#                 time
# ==============================================================================
            elif msg["action"] == "time":
                ctime = time.strftime('%d.%m.%y,%H:%M', time.localtime())
                mysend(from_sock, json.dumps(
                    {"action": "time", "results": ctime}))
# ==============================================================================
#                 search: : IMPLEMENT THIS
# ==============================================================================
            elif msg["action"] == "search":

                # IMPLEMENTATION
                # ---- start your code ---- #
                search_rslt = []
                for i in self.indices.keys():
                    for j in self.indices[i].index.keys():
                        if msg["target"] == j:
                            for m in self.indices[i].index[j]:
                                search_rslt.append("(" + i + ")" + self.indices[i].msgs[m])
                            
                print('server side search: ' + str(search_rslt))

                # ---- end of your code --- #
                mysend(from_sock, json.dumps(
                    {"action": "search", "results": str(search_rslt)}))
            
            elif msg["action"] == "accept":
                self.number_of_accept += 1
                if self.number_of_accept == 4:
                    from_name = self.logged_sock2name[from_sock]
                    the_guys = self.group.list_me(from_name)
                    self.game = Game.Game(the_guys)
                    for i in self.game.role.keys():
                        mysend(self.logged_name2sock[i], json.dumps({"results": "start game!", "Your role": self.game.role[i], "Day": self.game.day}))
                        
                    for j in self.game.role.keys():
                        mysend(self.logged_name2sock[j], json.dumps({"status": "conversation start!"}))
                    self.stage += 1
                    temp = list(self.game.role.keys())[self.speaker_index]
                    the_guys = self.group.list_me(temp)
                    mysend(self.logged_name2sock[temp], json.dumps({"speaker": temp, "status": "speaking"}))
                    for n in the_guys[1:]:
                        mysend(self.logged_name2sock[n], json.dumps({"speaker": temp, "status": "listening"}))
                    self.number_of_accept = 0
                else:
                    mysend(from_sock, json.dumps({"results": "waiting for others to respond"}))
                    
                    

            elif msg["action"] == "reject":
                from_name = self.logged_sock2name[from_sock]
                the_guys = self.group.list_me(from_name)
                for g in the_guys:
                    to_sock = self.logged_name2sock[g]
                    mysend(to_sock, json.dumps({"results": "Request rejected. Fail to start!"}))
                self.number_of_accept = 0
# ==============================================================================
#                 the "from" guy really, really has had enough
# ==============================================================================

        else:
            # client died unexpectedly
            self.logout(from_sock)

# ==============================================================================
# main loop, loops *forever*
# ==============================================================================
    def run(self):
        print('starting server...')
        while(1):
            read, write, error = select.select(self.all_sockets, [], [])
            print('checking logged clients..')
            for logc in list(self.logged_name2sock.values()):
                if logc in read:
                    self.handle_msg(logc)
            print('checking new clients..')
            for newc in self.new_clients[:]:
                if newc in read:
                    self.login(newc)
            print('checking for new connections..')
            if self.server in read:
                # new client request
                sock, address = self.server.accept()
                self.new_client(sock)
                               

def main():
    server = Server()
    server.run()


if __name__ == '__main__':
    main()  
