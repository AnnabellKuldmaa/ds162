from common import NO_SHIP, SHIP_NOT_SHOT, SHIP_SHOT, NO_SHIP_SHOT , NOT_SHOT, SHIP_SUNK, ONLINE, SPECTATOR, DISCONNECTED
from player import Player
from random import randint

class Ship():
    def __init__(self, x, y, is_vertical, size, is_sunk=False):
        """
        @param x: x coordinate
        @param y: y coordinate
        @param is_vertical: boolean
        @param size: size of ship ([1, 5]
        """
        self.x = x
        self.y = y
        self.is_vertical = is_vertical
        self.size = size
        self.is_sunk = False

class Game:
    def __init__(self, owner, board_size, spec_exchange, game_exchange):
        """
        @param owner: owner of the game
        @param board_size: board_size
        """
        self.player_list = [owner]
        self.owner = owner
        #Board size cannot be less than 10
        if board_size < 10:
            board_size = 10
        self.board_size = board_size
        self.spec_exchange = spec_exchange
        self.game_exchange = game_exchange

    def join(self, user):
        """
        @param user_name: adds player to game
        @return exchange
        @TODO: must notify owner players
        """
        self.player_list.append(user)
        return self.game_exchange

    def create_all_boards(self):
        """
        Creates a main board for each player and positions ships
        """
        
        for player in self.player_list:
            board = []
            for i in range(self.board_size):
                board.append([NOT_SHOT] * self.board_size)
            player.tracking_board = board
            player.main_board, player.ships = self.create_board()

    def shoot(self, shooter, x, y):
        """
        @param shooter: user_name of player who is shooting
        @param x: x coordinate
        @param y: y coordinate
        @TODO: must notify shooter, other players if sunk, if hit only suffering
        or we update everyone's tracking boards,
        should other people see the hit of player, currently not
        """
        hits = []
        sunk_ships = []
        
        if x > self.board_size or y > self.board_size:
            # Out of the board, do nothing
            return
        for player in self.player_list:
            print player.user_name
            # there is a hit 
            if player.user_name != shooter and player.mode == ONLINE:
                if player.main_board[y][x] in [SHIP_NOT_SHOT, SHIP_SHOT]:
                    # Updating board
                    print 'Hit!'
                    player.main_board[y][x] = SHIP_SHOT
                    # Check if ship is sunk
                    sunk = self.is_ship_sunk(player)
                    if sunk is not None:
                        print 'Sunked the ship'
                        sunk_ships.append([sunk, player])
                    hits.append(player.user_name)
        print 'Hits', hits
        if len(hits) > 0:
            if len(sunk_ships)>0:
                #Update all players' tracking board
                self.update_boards(sunk_ships)
        #Updating shooter's board and SPECTATOR (if hit, he should see it)
            else:
                for player in self.player_list:
                    if player.user_name == shooter or player.mode == SPECTATOR:
                        player.tracking_board[y][x] = SHIP_SHOT
        else:
             for player in self.player_list:
                if player.user_name == shooter:
                        player.tracking_board[y][x] = NO_SHIP_SHOT

    def create_board(self):
        """
        # Size
        1  5
        1  4
        1  3
        2  2
        2  1
        @return: returns ships on board of size self.board_size 
        and list of positioned ships
        """
        board = []
        for i in range(self.board_size):
            board.append([NO_SHIP] * self.board_size)
        ships = [[5, 1], [4, 1], [3, 1] , [2, 2], [1, 2]]
        #Use less ships for testing
        #ships =[[1, 2]]
        positioned_ships = []
        for s in ships:
            size = s[0]
            total = s[1]
            positioned = 0
            for i in range(total):
                while positioned < total:
                    no_ship_yet = True
                    is_vertical = randint(0, 1)
                    # vertical
                    if is_vertical:
                        x = randint(0, self.board_size - 1)
                        y = randint(0, self.board_size - size - 1)
                        # must check that there is no ship
                        for j in range(size):
                            if board[y + j][x] == 1:
                                no_ship_yet = False
                        if no_ship_yet:
                            for j in range(size):
                                board[y + j][x] = 1
                            positioned_ships.append(Ship(x, y, is_vertical, size))
                            positioned = positioned + 1
                    else:
                        # horisontal
                        x = randint(0, self.board_size - size - 1)
                        y = randint(0, self.board_size - 1)
                        # must check that there is no ship
                        for j in range(size):
                            if board[y][x + j] == 1:
                                no_ship_yet = False
                        if no_ship_yet:
                            for j in range(size):
                                board[y][x + j] = 1
                            positioned_ships.append(Ship(x, y, is_vertical, size))
                            positioned = positioned + 1
        return board, positioned_ships

    def is_ship_sunk(self, player):
        """
        Check there is a ship which is sunk
         @param: player whose not yet sunk ships will be checked
         @return: returns a sunk ship, otherwise None
        """
        for ship in player.ships:
            if not ship.is_sunk :
                sunked = True
                for i in range(ship.size):
                    if ship.is_vertical:
                        if player.main_board[ship.y + i][ship.x] == SHIP_NOT_SHOT:
                            sunked = False
                            break
                    else:
                        if player.main_board[ship.y][ship.x + i ] == SHIP_NOT_SHOT:
                            sunked = False
                            break
                if sunked:
                    for i in range(ship.size):
                        if ship.is_vertical:
                            player.main_board[ship.y + i][ship.x] = SHIP_SUNK
                        else:
                            player.main_board[ship.y][ship.x + i] = SHIP_SUNK
                    ship.is_sunk = True
                    return ship

    def update_boards(self,sunk):
        """
        Updates players' tracking boards if ship is sunk (does not update for owner himself)
        @param: sunk list of sunk ships and ship owner [ship, owner]
        """
        for s in sunk:
            sunk_ship = s[0]
            ship_owner = s[1]
            for player in self.player_list:
                if player != ship_owner:
                    for i in range(sunk_ship.size):
                        if sunk_ship.is_vertical:
                            player.tracking_board[sunk_ship.y + i][sunk_ship.x] = SHIP_SUNK
                        else:
                            player.tracking_board[sunk_ship.y][sunk_ship.x + i] = SHIP_SUNK

    def leave_game(self, user_name):
        """
        Player with user_name leaves: must remove all ships
        @param: user_name is user name of leaving player
        @TODO: must remove all ships, but what about already shot ships?!?
        """
        for player in self.player_list:
            if player.user_name == user_name:
                self.player_list.remove(player)
                #Set new owner
                if player.is_owner:
                    new_owner  = self.player_list[randint(0, len(self.player_list)-1)]
                    self.owner = new_owner
                    new_owner.is_owner = True

    def end_session(self):
        """
        Check session end condition
        @return: returns True if there exists only one player who is online
        """
        for player in self.player_list:
            if player.mode == ONLINE:
                return False
        return True
    
    def is_game_over(self):
        """
        Check game end condition
        @return: returns True if there exists only one ONLINE player who has ships remaining
        """
        in_game = 0
        for player in self.player_list:
            if player.mode == ONLINE and not player.all_ships_sunk():
                in_game = in_game + 1
        return (in_game <= 1)

    def set_as_spectator(self, player):
        """
        Player enters spectator mode: all ships are sunk and must see all ships
        Must see all ships on other players on tracing board
        @TODO: what about ships of disconnected users-should see them or not
        Annabell: No, but if disconnected user becomes online should exec  set_as_spectator again
        """
        if not player.all_ships_sunk():
            #Clear current tracking board
            board = []
            for i in range(self.board_size):
                board.append([NOT_SHOT] * self.board_size)
            player.tracking_board = board
            #loop main boards of all ONLINE players
            for pl in self.player_list:
                if pl != player:
                    for x in range(self.board_size):
                        for y in range(self.board_size):
                            #If ship damaged or sunk or just exists
                            if pl.main_board[y][x] in [SHIP_SUNK, SHIP_SHOT, SHIP_NOT_SHOT]:
                                 player.tracking_board[y][x] = pl.main_board[y][x]

#For testing purposes
"""
pl1 = Player('markus')
pl2 = Player('markus2')
pl3 = Player('markus3')
game = Game(pl1, 10, None, None)
game.join(pl2)
game.join(pl3)

game.create_all_boards()

print 'Player 1'
for line in pl1.main_board:
    print line

print 'Player 2'
for line in pl2.main_board:
    print line

print 'Player 2'
for line in pl2.main_board:
    print line

#print'Game over:', game.is_game_over()
#print'All sunk:', pl1.all_ships_sunk()
#print 'Setting as spectator'
#game.set_as_spectator(pl1)

#print 'Player 1 tracking should display player 2 ships'
#for line in pl1.tracking_board:
#    print line

print('1 is shooting 2')
while not game.is_game_over():
    x = raw_input('X coordinate')
    y = raw_input('Y coordinate')
    game.shoot('markus', int(x), int(y))
    print 'Player 1 shot'+ str(x) + str(y)
    print 'Player 1 tracking'
    for line in pl1.tracking_board:
        print line
    print 'Player 2'
    for line in pl2.main_board:
        print line
    print 'Player 3 tracking'
    for line in pl3.tracking_board:
        print line
"""




