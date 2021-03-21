import time
import sys
sys.setrecursionlimit(2000)

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
		
	def __init__(self, ruleset="spillover", pos=Position([1,1], [1,1], 0)):
		self.game = Game(ruleset, pos)
		self.ruleset = ruleset
		self.startingPosition = pos
		#self.positionsEvaluated = set()
		self.depth = 10
		self.depthSearched = 0
		self.linesAnalyzed = 0
		self.evaluatedPositions = {}
	
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
		
	def updateDepthSearched(self, d):
		if d > self.depthSearched:
			self.depthSearched = d
		
	def addPositionEvaluation(self, pos, eval):
		self.linesAnalyzed += 1
		self.evaluatedPositions[pos.toString()] = eval
		
	def evaluateMove(self, pos, move, d, currentLine): 
		self.updateDepthSearched(d)
		resultingPosition = self.game.getResultingPosition(pos, move)
		
		if resultingPosition.toString() in self.evaluatedPositions:
			return [move, self.evaluatedPositions[resultingPosition.toString()]]
		
		if resultingPosition.toString() in currentLine:
			#print(True)
			return [move, 0]
		else:
			currentLine.add(resultingPosition.toString())
		eval = self.game.checkForWin(resultingPosition)
		if eval == 0:
			posString = pos.toString()
			if d == self.depth:#posString in self.positionsEvaluated or d == self.depth:
				pos.eval = 0
				return [move, 0]
			else:
				#self.positionsEvaluated.add(posString)
				return self.getBestMove(resultingPosition, d+1, currentLine.copy())
		else:
			return [move, eval]
		
		
	def getGoodEval(self, pos):
		if pos.turn == 0:
			return 1
		else:
			return -1
		
	def getEvalDistance(self, eval, targetEval):
		return abs(targetEval-eval)
		
	def getBestMove(self, pos, d, currentLine):
		legalMoves = self.getAllLegalMoves(pos)
		bestMove = None
		bestEval = None
		targetEval = self.getGoodEval(pos)
		#print(currentLine)
		for move in legalMoves:
			a, eval = self.evaluateMove(pos, move, d, currentLine.copy())
			resultingPosition = self.game.getResultingPosition(pos, move)
			self.addPositionEvaluation(resultingPosition, eval)
			#print(move)
			#print(resultingPosition)
			
			if bestMove == None:
				bestMove = move
				bestEval = eval
			elif self.getEvalDistance(eval, targetEval) < self.getEvalDistance(bestEval, targetEval):
				bestMove = move
				bestEval = eval
				
			#print(eval)
			#print(self.getEvalDistance(eval, targetEval))# - self.getEvalDistance(bestEval, targetEval))
			if self.getEvalDistance(eval, targetEval) == 0:
				break #prune the rest of the branch
				
		return [bestMove, bestEval]
		
	def convertTimeToReadable(self, sec): # from https://www.journaldev.com/44690/python-convert-time-hours-minutes-seconds
	   #sec = sec % (24 * 3600)
	   day = sec // 86400
	   sec %= 86400
	   hour = sec // 3600
	   sec %= 3600
	   min = sec // 60
	   sec %= 60
	   return "%02d:%02d:%02d:%02d" % (day, hour, min, sec) 
		
	def play(self, player = 1, startingPosition = Position([1,1], [1,1], 0), depthCap = 10):
		while self.game.checkForWin(self.game.currentPosition) == 0:
			print(self.game.currentPosition.toString())
			if self.game.currentPosition.turn == player: #engines turn
				move = None
				eval = None
				depthSearched = depthCap
				startTime = time.time()
				for depth in range(depthSearched):
					self.depth = depth
					move, eval = self.getBestMove(self.game.currentPosition, 0, set())
					if eval != 0:
						depthSearched = depth
						break
				
				print(move)
				print(eval)
				timeElapsed = time.time() - startTime
				print("depth searched: "+str(depthSearched) + " in " + self.convertTimeToReadable(timeElapsed))
				self.game.currentPosition = self.game.getResultingPosition(self.game.currentPosition, move)
			else:
				rawMove = input("make a move > ")
				move = rawMove.rstrip()
				if rawMove != "split":
					move = rawMove.replace(" ","").split(",")
					move = [int(move[0]), int(move[1])]
				self.game.currentPosition = self.game.getResultingPosition(self.game.currentPosition, move)
		
	def solve(self, startingPosition = Position([1,1], [1,1], 0)):
		print(startingPosition.toString())
		move = None
		eval = None
		depth = float('inf')
		startTime = time.time()
		self.depth = depth
		move, eval = self.getBestMove(startingPosition, 0, set())
		depthSearched = depth
		
		print(eval)
		timeElapsed = time.time() - startTime
		print("depth searched: "+str(self.depthSearched) + " | positions analyzed: " + str(len(self.evaluatedPositions)) + " | lines analyzed: " + str(self.linesAnalyzed) + " | in " + self.convertTimeToReadable(timeElapsed))
		return eval
		
		
# class Engine:
	
	# def __init__(self, player = 1, startingPosition = Position([1,1], [1,1], 0)):
		# self.player = player
		# self.solver = Solver("spillover", startingPosition)
		# self.game.currentPosition = startingPosition
		# self.maxDepth = 10
		
	
			
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

engine = Solver("spillover")
#engine.play(depthCap=13)
engine.solve(startingPosition=initialPosition)
