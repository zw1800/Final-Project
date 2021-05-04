import random
import chat_group as grp
import chat_server

class Game:
    def __init__(self, names):
    #names is a list of the names of the players
        self.day = 1
        self.role = self.assign_role(names)
        self.status = {}
        for i in names:
            self.status[i] = "alive"
        
    def vote(self, candidates):
    #candidates is a dictionary of the players who are voted by others, key = name, value = number of votes
        max_vote = 0
        for i in candidates.keys():
            if candidates[i] >= max_vote:
                max_vote = candidates[i]
                temp = i
        self.status[temp] = "dead"
        identity = self.role[temp]
        del self.role[temp]
        return temp, identity

    def assign_role(self, names):
       #return a dictionary: key = name of the player, value = characrer
        chr_dict = {}
        N = names[:]
        random.shuffle(N)
        for i in range(len(N)):
            if i == 0:
                chr_dict[N[i]] = "werewolf"
            elif i == 4:
                chr_dict[N[i]] = "seer"
            else:
                chr_dict[N[i]] = "villiger"
        return chr_dict
        
        
   def get_roletype(self, type):
       result = []
       for i in self.role.keys():
           if self.role[i] = type:
                result.append(i)
       return result
       
  
 
        
        
        
        
        
