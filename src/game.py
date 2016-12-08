from common import NO_SHIP, SHIP_NOT_SHOT, SHIP_SHOT, NO_SHIP_SHOT , NOT_SHOT, SHIP_SUNK
from player import Player

class Game:
    def __init__(self, owner, board_size, spec_exchange, game_exchange):
        """
        @param owner: owner of the game
        @return ?
        """
        self.player_list = [owner]
        self.owner = owner
        self.board_size = board_size
        self.spec_exchange = spec_exchange
        self.game_exchange = game_exchange

    def join(self, user):
        """
        @param user_name: adds player to game
        @return 
        @TODO: must notify other players
        """
        self.player_list.append(user)
        return self.game_exchange
        

    def create_boards(self):
        """
        Creates main board for each player
        """
        for player in self.player_list:
            player.self.main_board = generate_board()
    
    def shoot(self, player, x, y):
        """
        @param player: user_name of player who is shooting
        @param x: x coordinate
        @param y: y coordinate
        @TODO: must notify other players
        """
        hits = []
        
        if x >self.board_size or y > self.board_size:
            # TODO. out of the board
            return
        for player in self.player_list:
            # there is a hit
            if player.self.main_board[x][y] in [SHIP_NOT_SHOT, SHIP_SHOT]:
                # Need to notify suffering player
                player.self.main_board[x][y] = SHIP_SHOT
                hits.append(player.self.user_name)
        if len(hits) > 0:
            player.self.tracking_board[x][y] = SHIP_SHOT
        else:
            player.self.tracking_board[x][y] = NO_SHIP_SHOT
            
    def create_board():
        """
        @return: returns ships on board of size self.board_size
        """
        return
    
    def is_ship_sink(board):
        """
        @TODO: check is ship is sunk
        must notify all players and set tracking_board value to SHIP_SUNK
        """
        return
    
#pl = Player('tere')
#game = Game(pl, 7)