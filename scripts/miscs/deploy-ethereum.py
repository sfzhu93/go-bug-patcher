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
    "GL1-2": [13, 14, 16, 17],

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
    make_run_script_GL1(os.path.join(bug_path, "run-"+go_project+"-"+str(bug_id)+"-perf.sh"),
                        buggy_commit,
                        bugno2buggyfiles[bug_id],
                        bugno2testcases[bug_id],
                        bugno2testpath[bug_id]
                        )
    make_inject_script_GL1(os.path.join(bug_path, "run-"+go_project+"-"+str(bug_id)+"-inject.sh"),
                           buggy_commit,
                           bugno2buggyfiles[bug_id],
                           bugno2testcases[bug_id],
                           bugno2testpath[bug_id]
                           )

    make_copy_inject(os.path.join(bug_path, "run-"+go_project+"-"+str(bug_id)+"-helper.sh"),
                           buggy_commit,
                           bugno2buggyfiles[bug_id],
                           bugno2testcases[bug_id],
                           bugno2testpath[bug_id]
                     )
    os.environ["GOPATH"] = bug_path
    src_path = os.path.join(bug_path, 'src')
    create_if_not_exist(src_path)
    os.chdir(src_path)
    print("go get...")
    os.system("go get "+go_get_url)
    src_path = os.path.join(src_path, go_get_url)
    os.chdir(src_path)
    print("git reset...")
    os.system("git reset --hard "+buggy_commit)
    print(bug_id, bugno2buggyfiles[bug_id])
    os.chdir(os.path.join(src_path, bugno2testpath[bug_id]))
    executeBugNo(bug_id)
    patch(src_path, bug_id)

def make_copy_inject(filename, buggy_commit, buggyfiles, testcases, testpaths):
    with open(filename, 'w') as fd:
        fd.write("""GOPATH=${PWD}
export GOPATH=${GOPATH}
#export PATH=$GOPATH/bin:$GOROOT/bin:$PATH
echo 'getting leak test tool...'
go get github.com/sfzhu93/leaktest
go version

PATCHER=/data/suz305/go-workspace/my-tools/bin/gl-1-patcher
TMPPATH=${GOPATH}/tmp


PROPATH=${GOPATH}/src/""" + go_get_url + "/" + testpaths + """
BUGGY_VERSION=""" + buggy_commit + """
BUGFILE=${GOPATH}/src/""" + go_get_url + "/" + buggyfiles + """

echo 'bugfile: ' $BUGFILE

INJECTBUGFILE=${GOPATH}/inject.go
echo 'inject file: ' $INJECTBUGFILE"""
                 )


def make_inject_script_GL1(filename, buggy_commit, buggyfiles, testcases, testpaths):
    with open(filename, 'w') as fd:
        fd.write("""GOPATH=${PWD}
export GOPATH=${GOPATH}
#export PATH=$GOPATH/bin:$GOROOT/bin:$PATH
echo 'getting leak test tool...'
go get github.com/sfzhu93/leaktest
go version

PATCHER=/data/suz305/go-workspace/my-tools/bin/gl-1-patcher
TMPPATH=${GOPATH}/tmp


PROPATH=${GOPATH}/src/""" + go_get_url + "/" + testpaths + """
BUGGY_VERSION=""" + buggy_commit + """
BUGFILE=${GOPATH}/src/""" + go_get_url + "/" + buggyfiles + """

echo 'bugfile: ' $BUGFILE

INJECTBUGFILE=${GOPATH}/inject.go
INJECTBUGLINE=

TESTNAME=""" + testcases[0] + """
export GOPATH=$GOPATH
mkdir -p ${TMPPATH}
echo 'removing tmp files...'
rm -rf ${TMPPATH}/*.inject

cd ${PROPATH}

echo 'reseting to the buggy version...'

git reset --hard ${BUGGY_VERSION}

cat ${INJECTBUGFILE} > ${BUGFILE}
echo 'run the original' ${TESTNAME} '...'
cd ${PROPATH}
echo ${PROPATH}
go test -run $TESTNAME >> ${TMPPATH}/buggy.inject


echo 'patching...'

${PATCHER} ${BUGFILE} ${INJECTBUGLINE}


echo 'run the patched' ${TESTNAME} '...'
cd ${PROPATH}
go test -run ${TESTNAME} >> ${TMPPATH}/patch.inject
cd ${GOPATH}
""")


def make_run_script_GL1(filename, buggy_commit, buggyfiles, testcases, testpaths):
    with open(filename, 'w') as fd:
        fd.write("""GOPATH=${{PWD}}
PATCHER=/data/suz305/go-workspace/my-tools/bin/gl-1-patcher
TMPPATH=${{GOPATH}}/tmp
OVERSCR=/data/suz305/go-workspace/my-tools/src/github.com/sfzhu93/go-bug-patcher/scripts/overhead.py

PROPATH=${{GOPATH}}/src/{0}
BUGGY_VERSION={1}
BUGFILE=${{PROPATH}}/{2}
BUGLINE=

""".format(go_get_url, buggy_commit, buggyfiles))

        fd.write("""export GOPATH=$GOPATH
mkdir -p ${TMPPATH}
rm -rf ${TMPPATH}/*.*
rm -rf ${TMPPATH}/*


cd ${PROPATH}

echo 'reseting to the buggy version...'

git reset --hard ${BUGGY_VERSION}

""")

        for i, testcase in enumerate(testcases):
            #print(testpaths[i])
            fd.write("""echo 'reseting to the buggy version...'

git reset --hard ${{BUGGY_VERSION}}

for ((n=0;n<10;n++))
do
        echo 'run the original' {1}/{0} '...'
        cd {1}
        go test -run {0} >> ${{TMPPATH}}/buggy.time
        cd ${{PROPATH}}
done

echo 'patching...'

${{PATCHER}} ${{BUGFILE}} ${{BUGLINE}}

for ((n=0;n<10;n++))
do
        echo 'run the patched' {1}/{0} '...'
        cd {1}
        go test -run {0} >> ${{TMPPATH}}/patch.time
        cd ${{PROPATH}}
done

echo
echo

python ${{OVERSCR}} ${{TMPPATH}}/buggy.time ${{TMPPATH}}/patch.time 10
""".format(testcase, testpaths))
        fd.write("cd ${GOPATH}\n")

if __name__ == "__main__":
    """groupname = 'GL1-1'
    for bugno in group2bugno[groupname]:
        deploy(bugno, group2commit[groupname])

    groupname = 'GL1-2'
    for bugno in group2bugno[groupname]:
        deploy(bugno, group2commit[groupname])"""
    deploy(15, '5f2002bbcc1ad21818d9b08badea84acac6d0481')
