class Player():
    def __init__(self, user_name, owner = False):
        """
        @main_board: board for player's own ships
        @tracking_board: board where player shoots
        @is_online: True if player is active
        @user_name: user name of the player
        @ships: list of player's ships (of type Ship)
        """
        self.main_board = []
        self.tracking_board  = []
        self.is_online = True
        self.is_owner = owner
        self.user_name = user_name
        self.ships = []
        
    def all_ships_sunk(self):
        """
        @return: returns True if all player's ships are sunk
        """
        for ship in self.ships:
            if not ship.is_sunk:
                return False
        return True
