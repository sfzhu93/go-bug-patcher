import os
import subprocess
import time
#import statistics


go_project = "etcd"
bug_id = 20
workdir = "."
go_get_url = "go.etcd.io/etcd"

group2bugno = {
    "1": [19, 20, 21, 22, 24, 25],
    '2': [26, 27, 28, 29, 30, 31],
    '3': [32, 33, 34, 35, 36, 37, 38, 39, 40, 41],
    '4': [42, 43, 44, 45, 46, 47, 48],
    '5': [49, 50, 51, 52],
    'test': [44,45,46],
    'GL1-1': [7, 8],
    'GL1-2': [24],
    'GL1-3': [26, 27, 28, 29, 30, 31],
    'GL1-4': [32, 33, 34, 35, 36, 37, 38, 39, 40],
    'GL1-5': [42, 43, 44, 45, 47],
}

group2commit = {
    "1": "fd2dddb39f6afd88878daf140e1573df118eb98a",
    "2": '53f15caf73b9285d6043009fa64c925d5a8f573c',
    "3": 'cad92706cfca4a01c513e13c87570fefbf9dbe28',
    "4": 'a8b04b17fd37ed797e34bea6534d307929c6337b',
    "5": 'a8b04b17fd37ed797e34bea6534d307929c6337b',
    'GL1-1': 'e745649cce1b745277d6b919ac068b32844d5b65',
    'GL1-2': 'fd2dddb39f6afd88878daf140e1573df118eb98a',
    'GL1-3': '53f15caf73b9285d6043009fa64c925d5a8f573c',
    'GL1-4': 'cad92706cfca4a01c513e13c87570fefbf9dbe28',
    'GL1-5': '6991f619f21375aac310aba4b5934105b2fbff9e',
}


bugno2testcases = {19: ['BarrierSingleNode', 'BarrierMultiNode'],
                   20: ['MoveLeader', 'MoveLeaderService'],
                   21: ['MutexLockMultiNode', 'MutexLockSingleNode'],#BenchmarkMutex4Waiters
                   22: ['MutexTryLockSingleNode', 'MutexTryLockMultiNode'],
                   24: ['V3WatchWithPrevKV'],
                   25: ['V3ElectionObserve'],
                   26: ['KVGetRetry'],
                   27: ['TxnReadRetry'],
                   28: ['Sync'],
                   29: ['SyncTimeout'],
                   30: ['ConcurrentReadNotBlockingWrite'],
                   31: ['WatcherWatchWithFilter'],
                   32: ['SimpleHTTPClientDoHeaderTimeout'],
                   33: ['HTTPClusterClientDoDeadlineExceedContext'],
                   34: ['HTTPClusterClientDoCanceledContext'],
                   35: ['DialTimeout'],
                   36: ['TxnPanics'],
                   37: ['LessorExpire'],
                   38: ['LessorExpireAndDemote'],
                   39: ['Server_PauseTx'],
                   40: ['Server_BlackholeTx'],
                   41: ['Server_Unix_Insecure',
                        'Server_TCP_Insecure',
                        'Server_Unix_Secure',
                        'Server_TCP_Secure',
                        'Server_Unix_Insecure_DelayTx',
                        'Server_TCP_Insecure_DelayTx',
                        'Server_Unix_Secure_DelayTx',
                        'Server_TCP_Secure_DelayTx'
                        ],
                   42: ['NewListenerTLSInfoSkipClientSANVerify'],
                   43: ['NewListenerTLSInfoSkipClientSANVerify'],
                   44: ['NewListenerTLSInfoSkipClientSANVerify'],
                   45: ['ReadWriteTimeoutDialer'],
                   46: ['ReadWriteTimeoutDialer'],
                   47: ['WriteReadTimeoutListener'],
                   48: ['WriteReadTimeoutListener'],
                   49: ['ElectionFailover'],
                   50: ['V3TxnCmpHeaderRev'],
                   51: ['LeasingTxnAtomicCache'],
                   52: ['LeaseRevokeNewAfterClose']
                   }

bugno2testpath = {19: 'integration', 20: 'integration', 21: 'integration',
                  22: 'integration', 24: 'integration', 25: 'integration',
                  26: 'clientv3/integration', 27: 'clientv3/integration', 28: 'etcdserver',
                  29: 'etcdserver', 30: 'mvcc', 31: 'mvcc', 32: 'client',
                  33: 'client', 34: 'client', 35: 'clientv3', 36: 'clientv3',
                  37: 'lease', 38: 'lease', 39: 'pkg/proxy', 40: 'pkg/proxy', 41: 'pkg/proxy',
                  42: 'pkg/transport', 43: 'pkg/transport', 44: 'pkg/transport',
                  45: 'pkg/transport', 46: 'pkg/transport', 47: 'pkg/transport',
                  48: 'pkg/transport', 49: 'integration', 50: 'integration',
                  51: 'clientv3/integration', 52: 'clientv3/integration'
                  }


bugno2buggyfiles = {
    19: 'integration/v3_barrier_test.go',
    20: 'integration/v3_leadership_test.go',
    21: 'integration/v3_lock_test.go',
    22: 'integration/v3_lock_test.go',
    24: 'integration/v3_watch_test.go',
    25: 'integration/v3election_grpc_test.go',
    26: 'clientv3/integration/kv_test.go',
    27: 'clientv3/integration/txn_test.go',
    28: 'etcdserver/server_test.go',
    29: 'etcdserver/server_test.go',
    30: 'mvcc/kvstore_test.go',
    31: 'mvcc/watcher_test.go',
    32: 'client/client_test.go',
    33: 'client/client_test.go',
    34: 'client/client_test.go',
    35: 'clientv3/client_test.go',
    36: 'clientv3/txn_test.go',
    37: 'lease/lessor_test.go',
    38: 'lease/lessor_test.go',
    39: 'pkg/proxy/server_test.go',
    40: 'pkg/proxy/server_test.go',
    41: 'pkg/proxy/server_test.go',
    42: 'pkg/transport/listener_test.go',
    43: 'pkg/transport/listener_test.go',
    44: 'pkg/transport/listener_test.go',
    45: 'pkg/transport/timeout_dialer_test.go',
    46: 'pkg/transport/timeout_dialer_test.go',
    47: 'pkg/transport/timeout_listener_test.go',
    48: 'pkg/transport/timeout_listener_test.go',
    49: 'integration/v3_election_test.go',
    50: 'integration/v3_grpc_test.go',
    51: 'integration/leasing_test.go',
    52: 'integration/lease_test.go'
}

bugno2buggyfuncname = {
    19: 'testBarrier',
    20: 'testMoveLeader',
    21: 'testMutexLock',
    22: 'testMutexTryLock',
    24: 'TestV3WatchWithPrevKV',
    25: 'TestV3ElectionObserve',
    26: 'KVGetRetry',
    27: 'TestTxnReadRetry',
    28: 'TestSync',
    29: 'TestSyncTimeout',
    30: 'TestConcurrentReadNotBlockingWrite',
    31: 'TestWatcherWatchWithFilter',
    32: 'TestSimpleHTTPClientDoHeaderTimeout',
    33: 'TestHTTPClusterClientDoDeadlineExceedContext',
    34: 'TestHTTPClusterClientDoCanceledContext',
    35: 'TestDialTimeout',
    36: 'TestTxnPanics',
    37: 'TestLessorExpire',
    38: 'TestLessorExpireAndDemote',
    39: 'TestServer_PauseTx',
    40: 'TestServer_BlackholeTx',
    41: 'testServer',
    42: 'TestReadWriteTimeoutDialer',
    43: 'TestReadWriteTimeoutDialer',
    44: 'testNewListenerTLSInfoClientCheck',
    45: 'testNewListenerTLSInfoClientCheck',
    46: 'testNewListenerTLSInfoClientCheck',
    47: 'TestWriteReadTimeoutListener',
    48: 'TestWriteReadTimeoutListener',
    49: 'TestElectionFailover',
    50: 'TestV3TxnCmpHeaderRev',
    51: 'TestLeasingTxnAtomicCache',
    52: 'TestLeaseRevokeNewAfterClose'
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


if __name__ == "__main__":
    groupname = 'GL1-5'
    for bugno in group2bugno[groupname]:
        deploy(bugno, group2commit[groupname])
