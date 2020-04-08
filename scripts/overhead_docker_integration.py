import sys


def parseInput(file, testcasename):
    testcasename = '/' + testcasename + ' '
    durations = []
    with open(file) as f:
        for line in f:
            if testcasename in line:
                if 'PASS' in line:
                    _, tmp = line.split('(')
                    tmp = tmp.split('s')[0]
                    durations.append(float(tmp))
    return durations


if __name__ == '__main__':
    raw = sys.argv[1]
    change = sys.argv[2]
    num = int(sys.argv[3])
    testcasename = sys.argv[4]

    rawList = parseInput(raw, testcasename)
    changeList = parseInput(change, testcasename)

    assert (len(rawList) % num == 0)
    assert (len(changeList) % num == 0)
    assert (len(rawList) == len(changeList))

    print('overhead:', (sum(changeList) - sum(rawList)) / sum(rawList))
