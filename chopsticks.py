class Position:# position: [[playerA left hand, playerA right hand], [playerB left hand, playerB right hand], who's turn (0 or 1)]
	def __init__(self, playerA=None, playerB=None, turn=None, eval=None, depth=None):
		self.turn = turn
		self.playerA = playerA
		self.playerB = playerB
		self.eval = eval 
		self.depth = depth
		
	def getCurrentPlayer(self):
		if self.turn == 0:
			return self.playerA
		else:
			return self.playerB
	
	def getOtherPlayer(self):
		if self.turn == 1:
			return self.playerA
		else:
			return self.playerB
			
	def setPlayerA(self, player):
		self.playerA = player
		
	def setPlayerB(self, player):
		self.playerB = player
		
	def toString(self):
		return str(self.playerA)+str(self.playerB)+str(self.turn)
		

class Game:
	def __init__(self, ruleset, pos):
		self.ruleset = ruleset
		self.currentPosition = pos
		self.won = False
		
	def getWinner(self):
		winner = "no one yet"
		winNumber = self.checkForWin(self.pos)
		if winNumber == 1:
			winner = "Player A"
		if winNumber == -1:
			winner = "Player B"
		return winner
		
	def checkForWin(self, pos):
		if pos.playerA == [0,0]:
			return -1
		elif pos.playerB == [0,0]:
			return 1
		else:
			return 0
		
	def splitIsLegal(self, pos, currentPlayer):
		if currentPlayer[0] == 0 and currentPlayer[1] % 2 == 0: 
			return True
		elif currentPlayer[1] == 0 and currentPlayer[0] % 2 == 0:
			return True
		return False
			
	def moveIsLegal(self, pos, currentPlayer, sourceHand, otherPlayer, targetHand):
		if currentPlayer[sourceHand] != 0 and otherPlayer[targetHand] != 0:
			#print(pos.toString() + " L " + str([sourceHand, targetHand]))
			return True
		#print(pos.toString() + " I " + str([sourceHand, targetHand]))
		return False
		
	def split(self, currentPlayer): # returns number of fingers on each hand after splitting or -1 if splitting is impossible
		if currentPlayer[0] == 0 and currentPlayer[1] % 2 == 0: 
			return int(currentPlayer[1]/2)
		elif currentPlayer[1] == 0 and currentPlayer[0] % 2 == 0:
			return int(currentPlayer[0]/2)
		else:
			return -1
		
	def createNewPosition(self, currentPlayer, otherPlayer, turn): # turn should be the last turn number. It is iterated for the new position within this function
		newTurn = (turn+1)%2
		newPos = Position(turn=newTurn)
		if turn == 0:
			newPos.setPlayerA(currentPlayer.copy())
			newPos.setPlayerB(otherPlayer.copy())
		elif turn == 1:
			newPos.setPlayerB(currentPlayer.copy())
			newPos.setPlayerA(otherPlayer.copy())
			
		return newPos
		
	def getSplitPosition(self, pos, currentPlayer):
		splitNumber = self.split(currentPlayer)
		turn = pos.turn #0:A  1:B
		if splitNumber != -1:
			currentPlayer = [splitNumber, splitNumber]
			return self.createNewPosition(currentPlayer, pos.getOtherPlayer(), turn)
		else:
			return -1
		
	def translateHandByRuleset(self, hand):
		if self.ruleset == "spillover":
			return hand % 5
		elif self.ruleset == "cap":
			if hand < 5:
				return hand
			else:
				return 0
		
	def getMovePosition(self, pos, currentPlayer, sourceHand, otherPlayer, targetHand):
		newHandValue = self.translateHandByRuleset( otherPlayer[targetHand] + currentPlayer[sourceHand] )
		newOtherPlayer = otherPlayer.copy()
		newOtherPlayer[targetHand] = newHandValue
		return self.createNewPosition(currentPlayer, newOtherPlayer, pos.turn)
	
	def getResultingPosition(self, pos, move):
		if move == "split":
			return self.getSplitPosition(pos, pos.getCurrentPlayer())
		else:
			return self.getMovePosition(pos, pos.getCurrentPlayer(), move[0], pos.getOtherPlayer(), move[1])
		
class Solver:
		
	def __init__(self, ruleset, pos):
		self.game = Game(ruleset, pos)
		#self.positionsEvaluated = set()
		self.depth = 10
	
	def removeIllegalPositions(positions):
		legalPositions = positions
		while -1 in legalPositions:
			legalPositions.remove(-1)
		return legalPositions
		
	def getAllLegalMoves(self, pos): # returns a list of positions that can be reached from the current position this move 
		legalMoves = []
		currentPlayer = pos.getCurrentPlayer()
		otherPlayer = pos.getOtherPlayer()
		## check if position is lost or won
		##check if splitting is possible
		#splitPosition = self.game.getSplitPosition(pos, currentPlayer)
		
		if self.game.splitIsLegal(pos, currentPlayer):
			legalMoves.append("split")
			
		for sourceHand in [0,1]:
			for targetHand in [0,1]:
				if self.game.moveIsLegal(pos, currentPlayer, sourceHand, otherPlayer, targetHand):
					legalMoves.append( [sourceHand, targetHand] )
					#legalMoves.append( self.game.getMovePosition(pos, currentPlayer, sourceHand, otherPlayer, targetHand) )
				
		return legalMoves
		
	def evaluateMove(self, pos, move, d): 
		resultingPosition = self.game.getResultingPosition(pos, move)
		eval = self.game.checkForWin(resultingPosition)
		if eval == 0:
			posString = pos.toString()
			if d == self.depth:#posString in self.positionsEvaluated or d == self.depth:
				pos.eval = 0
				return [move, 0]
			else:
				#self.positionsEvaluated.add(posString)
				return self.getBestMove(resultingPosition, d+1)
		else:
			return [move, eval]
		
		
	def getGoodEval(self, pos):
		if pos.turn == 0:
			return 1
		else:
			return -1
		
	def getEvalDistance(self, eval, targetEval):
		return abs(targetEval-eval)
		
	def getBestMove(self, pos, d):
		legalMoves = self.getAllLegalMoves(pos)
		bestMove = None
		bestEval = None
		targetEval = self.getGoodEval(pos)
		for move in legalMoves:
			a, eval = self.evaluateMove(pos, move, d)
			#print(move)
			#print(resultingPosition)
			
			if bestMove == None:
				bestMove = move
				bestEval = eval
			elif self.getEvalDistance(eval, targetEval) < self.getEvalDistance(bestEval, targetEval):
				bestMove = move
				bestEval = eval
				
		return [bestMove, bestEval]
		
		
class Engine:
	
	def __init__(self, player = 1, startingPosition = Position([1,1], [1,1], 0)):
		self.player = player
		self.solver = Solver("spillover", startingPosition)
		self.currentPosition = startingPosition
		self.maxDepth = 10
		
	def play(self):
		while self.solver.game.checkForWin(self.currentPosition) == 0:
			print(self.currentPosition.toString())
			if self.currentPosition.turn == self.player: #engines turn
				move = None
				eval = None
				depthSearched = self.maxDepth
				for depth in range(10):
					self.solver.depth = depth
					move, eval = self.solver.getBestMove(self.currentPosition, 0)
					if eval != 0:
						depthSearched = depth
						break
				
				print(move)
				print(eval)
				print("depth searched: "+str(depthSearched))
				self.currentPosition = self.solver.game.getResultingPosition(self.currentPosition, move)
			else:
				rawMove = input("make a move > ")
				move = rawMove.rstrip()
				if rawMove != "split":
					move = rawMove.replace(" ","").split(",")
					move = [int(move[0]), int(move[1])]
				self.currentPosition = self.solver.game.getResultingPosition(self.currentPosition, move)
		
	
			
# gamea = Game("spillover")
# posa = Position([3,1], [4,1], 0)
# currentPlayera = posa.getCurrentPlayer()
# otherPlayera = posa.getOtherPlayer()
# sourceHand = 0
# targetHand = 0
# print(gamea.getMovePosition(posa, currentPlayera, sourceHand, otherPlayera, targetHand).toString())


initialPosition = Position([1,1], [1,1], 0)
#solver = Solver("spillover", initialPosition)
#print(solver.evaluatePosition(initialPosition))

engine = Engine(1, initialPosition)
engine.play()
