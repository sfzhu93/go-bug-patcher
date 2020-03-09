import sys

def parseTimeFile(sFile):

	resultList = []
	with open(sFile) as f:
		while True:
			line = f.readline()
			if not line:
				break

			tmpList = line.split()
			if len(tmpList) != 3:
				continue

			if tmpList[0] != 'ok':
				continue

			if tmpList[2].endswith('s'):
				resultList.append(float(tmpList[2][:-1]))

	return resultList



if __name__=='__main__':
	raw = sys.argv[1]
	change = sys.argv[2]
	num = int(sys.argv[3])

	rawList = parseTimeFile(raw)
	changeList = parseTimeFile(change)

	assert(len(rawList) % num == 0)
	assert(len(changeList) % num == 0)
	assert(len(rawList) == len(changeList))

	print 'overhead:', (sum(changeList) - sum(rawList))/sum(rawList)