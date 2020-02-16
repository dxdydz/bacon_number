class Actor:
    def __init__(self, actor_id, parent, film):
        self.id = actor_id
        self.parent = parent
        self.film = film
    
    def __repr__(self):
        return str((self.id, self.parent, self.film))
    
    def __eq__(self, other):
        if self.id == other:
            return True
        return False
    
    def __hash__(self):
        return hash(self.id)

def keystr(category, identifier, dataname):
    '''
    Returns key scheme: "category:identifier:dataname"
    '''
    return ':'.join([str(category), str(identifier), str(dataname)])