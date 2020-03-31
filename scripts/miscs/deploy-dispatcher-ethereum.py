import os
import subprocess
import time

# import statistics


go_project = "ethereum"
bug_id = 20
workdir = "."
go_get_url = "github.com/ethereum/go-ethereum"

group2bugno = {
    "GL1-1": [10],#, 11
    "GL1-2": [13, 14, 15, 16, 17],

}

group2commit = {
    'GL1-1': '34bb132b108e0c17c079d6b24524c2958306a009',
    'GL1-2': '57d4898e2992a46fc2deab93a2666a2979b6704c',
}

bugno2testcases = {10: ['TestResubscribe'],
                   #11:
                   13: ['TestSimulatedSleep'],
                   14: ['TestBroadcastMalformedBlock'],
                   15: ['TestServerDial'],
                   16: ['TestServerInboundThrottle'],
                   17: ['TestClientSubscribeClose'],
                   }

bugno2testpath = {10:'event',
                   #11:
                   13: 'common',
                   14: 'eth',
                   15: 'p2p',
                   16: 'p2p',
                   17: 'rpc',
                  }

bugno2buggyfiles = {10: 'event/subscription.go',
                   #11:
                   13: 'common/mclock/simclock_test.go',
                   14: 'eth/handler_test.go',
                   15: 'p2p/server_test.go',
                   16: 'p2p/server_test.go',
                   17: 'rpc/client_test.go',
}


#TODO: add information for patch

def create_if_not_exist(path):
    if not os.path.exists(path):
        os.mkdir(path)


def parseExecutionTime(stdout):
    return float(stdout.decode("utf-8").split()[-1].strip().replace('s', ''))


def executeBugNo(bugno):
    for testcases in bugno2testcases[bugno]:
        times = []
        for i in range(1, 10):
            start_time = time.time()
            stdout = subprocess.check_output("go test -run "+testcases, shell=True)
            end_time = time.time()
            #times.append(end_time-start_time)
            exe_time = parseExecutionTime(stdout)
            times.append(exe_time)
            print(exe_time)
            #print()
        #print(statistics.mean(times), " ".join([str(x) for x in times]))


def patch(basedir, bugno):
    #TODO: insert patch command here
    #os.system()
    if os.path.exists(os.path.join(basedir, bugno2buggyfiles[bugno])):
        print('ok')


def deploy(bug_id, buggy_commit):
    global workdir
    os.chdir(workdir)
    workdir = os.getcwd()
    bug_path = os.path.join(workdir, go_project+"-"+str(bug_id))
    create_if_not_exist(bug_path)
    make_dispatch_script(os.path.join(bug_path, "run-"+go_project+"-"+str(bug_id)+"-dispatch.sh"),
                        buggy_commit,
                        bugno2buggyfiles[bug_id],
                        bugno2testcases[bug_id],
                        bugno2testpath[bug_id]
                        )


def make_dispatch_script(filename, buggy_commit, buggyfiles, testcases, testpaths):
    with open(filename, 'w') as fd:
        fd.write("""GOPATH=${PWD}
BUGFILE=""" + buggyfiles + """
LINENO=123
COMMITNO=""" + buggy_commit + """

PROJ_REL_PATH=""" + go_get_url + """
EXE=/data/suz305/go-workspace/my-tools/bin/staticchecker

cd ${GOPATH}/src/${PROJ_REL_PATH}
git reset --hard $COMMITNO
cd ${GOPATH}

#${EXE} -path=${GOPATH}/src/${PROJ_REL_PATH}/${BUGFILE} -include=${PROJ_REL_PATH} -r -lineno=${LINENO}
${EXE} -path=${GOPATH}/src/${PROJ_REL_PATH}/${BUGFILE} -lineno=${LINENO}
""")



if __name__ == "__main__":
    groupname = 'GL1-1'
    for bugno in group2bugno[groupname]:
        deploy(bugno, group2commit[groupname])

    groupname = 'GL1-2'
    for bugno in group2bugno[groupname]:
        deploy(bugno, group2commit[groupname])

