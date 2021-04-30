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
        del self.role[temp]

    def assign_role(names):
        
        
        
                
 
        
        
        
        
        
