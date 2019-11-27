import math
from copy import deepcopy
import logging
import random

class Player:
	""" Squeleton for humain and agent player """
	def play(self, *board):
		pass
	def receiveReward(self, reward):
		pass

class HumanPlayer(Player):
	def play(self, board):
		try:
			while True:
				print("Entrer un entier entre 0 et 2 pour x")
				x = int(input())
				print("Entrer un entier entre 0 et 2 pour y")
				y = int(input())
				# no cheat
				if (x > -1 and x < 3) and (y > -1 and y < 3) and  board[x][y] == " ":
					return x,y
		except:
			print('saisir de bonne valeur')
			return self.play(board)

class Agent(Player):
	def __init__(self, pion, alpha, gamma):
		self.pion = pion
		self.alpha = alpha
		self.gamma = gamma
		self.policie = {} # q_tables
		self.oldBoards = []

	def play(self, board):
		""" Returns the coordonates of player next move """
		nextMove = []
		# find all the empty case to play
		avaiblePositions = self.findAvaiblePositions(board)
		# indicate the scoring for the next move
		letsGo = - math.inf # - infinity to init the next action to a minimal value
		unknowPosition = []
		for position in avaiblePositions:
			nextBoard = deepcopy(board)# make a copy else change the board
			nextBoard[position[0]][position[1]] = self.pion
			scoringMove = 0
			# calculates the value of the current position
			if str(nextBoard) not in self.policie.keys() :
				 unknowPosition.append(position)
			else :
				scoringMove = self.policie[str(nextBoard)]
			if scoringMove > letsGo: # better case to play
				letsGo = scoringMove
				nextMove = [position[0], position[1]]
		# a little of random if no data existing
		if letsGo ==  0 and len(unknowPosition) > 0:
			nextPosition = random.randint(0, len(unknowPosition)-1)
			nextMove = [unknowPosition[nextPosition][0], unknowPosition[nextPosition][1]]
		logging.info('player '+self.pion+' play ' +str(nextMove)+' with value '+str(letsGo))
		return nextMove[0],nextMove[1]

	def saveNewBoard(self, board):
		self.oldBoards.append(deepcopy(board))

	def receiveReward(self, reward):
		""" Defines the policie, Q_table, with calculated q_value"""
		for board in self.oldBoards[::-1]:
			if str(board) not in self.policie.keys():
				self.policie[str(board)] = 0
			else:
				self.policie[str(board)] += self.alpha * (reward - self.policie[str(board)])

	def findAvaiblePositions(self, board): 
		""" Returns all the coordonates of all empty case of the board """
		avaiblePositions = []
		for i,line in enumerate(board):
			for j,case in enumerate(line):
				if case == ' ':
					avaiblePositions.append((i,j))
		return avaiblePositions

class Environment:
	def __init__(self, player1,player2, withHuman = False):
		self.board = []
		self.player1 = player1
		self.player2 = player2
		self.canPlay = True
		self.playerWinner = ''
		self.withHuman = withHuman

	def initGame(self):
		"""  Defines a bard with 9 empty case, ie a space 
			and indicates if a player can play
		"""
		self.board = [[' ' for i in range(3)] for j in range(3)]
		self.canPlay = True
		self.playerWinner = ''
		self.player1.oldBoards=[]
		if not self.withHuman:
			self.player2.oldBoards = []

	def launchGame(self):
		""" Alternate the move between the two player """
		self.initGame()
		currentPlayer = 'X'
		continueGame = True
		while continueGame :
			# print for human
			if self.withHuman:
				print(self)
			if currentPlayer == 'X':
				x,y = self.player1.play(self.board)
				self.board[x][y] = currentPlayer
				currentPlayer = 'O'
			else :
				x,y = self.player2.play(self.board)
				self.board[x][y] = currentPlayer
				currentPlayer = 'X'
			# give the new state to agents	
			self.player1.saveNewBoard(self.board)
			if not self.withHuman:
				self.player2.saveNewBoard(self.board)
			if self.winner() or not self.playerCanPlay():
				if self.withHuman:
					print(self)
				logging.info('*** End game *** \n' + self.__str__())
				if self.playerWinner != '' :
					if self.withHuman:
						print(self.playerWinner, 'win')
					logging.info('winner is '+self.playerWinner)
				else :
					if self.withHuman:
						print('null game')
					logging.info('null game')
				continueGame = False
				self.giveRewards()


	def winner(self): 
		""" Returns True if a winner exists or False
		"""
		# check the rows
		for i in range(3):
			if self.board[i][0] == self.board[i][1] and self.board[i][0] == self.board[i][2] and self.board[i][0] != " ":
				self.playerWinner = self.board[i][0]
				return True
		# check the colunms
		for i in range(3):
			if self.board[0][i] == self.board[1][i] and self.board[0][i] == self.board[2][i] and self.board[0][i] != " ":
				self.playerWinner =  self.board[0][i]
				return True
		# check diagonales
		if self.board[0][0] == self.board[1][1] and self.board[0][0] == self.board[2][2] and self.board[0][0] != " ":
			self.playerWinner =  self.board[i][0]
			return True
		if self.board[0][2] == self.board[1][1] and self.board[0][2] == self.board[2][0] and self.board[0][2] != " ":
			self.playerWinner = self.board[i][0]
			return True
		return False

	def playerCanPlay(self):
		""" Use to determine null game """
		for row in self.board:
			if row.count(' ') > 0:
				return True
		return False

	def giveRewards(self):
		""" Give rewards for all player """
		end = self.playerWinner if self.winner() else ''
		# you can change rewards to test and improve learning
		if end == 'X':	# player1 win
			self.player1.receiveReward(1)
			self.player2.receiveReward(0)
		elif end == 'O':	# player2 win
			self.player1.receiveReward(0)
			self.player2.receiveReward(1)
		else : # nul game
			self.player1.receiveReward(0.5)
			self.player2.receiveReward(0.5)

	def __str__(self):
		s = ''
		for i in range(3):
			s += "|"
			for j in range(3):
				s += self.board[i][j] + "|"
			s += '\n'
		return s

if __name__ == '__main__':
	print('*** TRAININ PERIOD ***')
	# to log each action of agent 
	logging.basicConfig(filename='game.log',level=logging.DEBUG)
	# change param to improve learning
	agent1 = Agent('X',0.2,0.9)
	agent2 = Agent('O',0.2,0.9)
	game = Environment(agent1, agent2)
	for i in range (10000):
		game.launchGame()
	# play with the agent
	print(" Let's go now !!! ")
	continuePlay = 'y'
	human = HumanPlayer()
	game = Environment(agent1, human, True)
	while continuePlay == 'y' : 
		game.launchGame()
		continuePlay = input('Again?(y/n')
