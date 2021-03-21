def isLegal(al,ar,bl,br,turn):
	if turn == 1 and al == 0 and ar == 0:
		return False
	if turn == 0 and bl == 0 and br == 0:
		return False
		
	return True

positionCount = 0
for al in range(5):
	for ar in range(5):
		for bl in range(5):
			for br in range(5):
				for turn in range(2):
					if isLegal(al,ar,bl,br,turn):
						positionCount+=1
						
print(positionCount)