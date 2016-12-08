class Player():
    def __init__(self, user_name, owner = False):
        self.main_board = []
        self.tracking_board  = []
        self.is_online = True
        self.is_owner = owner
        self.user_name = user_name
