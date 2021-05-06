class Game:
    def __init__(self, names):
        day = 1
        self.role = self.assign_role(names)
        status = {}
        for i in names:
            status[i] = "alive"
        
    def vote(self, candidates):
        lst1 = []
        max_vote = 0
        for i in candidates.keys():
            if candidates[i] >= max_vote:
                max_vote = candidates[i]
                temp = i
        status[temp] = "dead"

    def assign_role(names):
        
        
        
                
 
        
        
        
        
        
