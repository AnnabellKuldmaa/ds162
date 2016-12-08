class Game:
    def __init__(self, owner):
        """
        @param owner: owner of the game
        @return ?
        """
        self.player_list = [owner]
        self.owner = owner
            
    def join(self, user_name):
        """
        @param user_name: adds player with user_name to game
        @return ?
        """
        self.player_list.append(Player(user_name))

    def create_boards(self):
        """
        Create board for each player
        """
        return

