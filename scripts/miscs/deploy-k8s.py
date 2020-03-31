import os
import subprocess
import time
import statistics


go_project = "kubernetes"
bug_id = 1
workdir = "."
go_get_url = "k8s.io/kubernetes"
buggy_commit = "a10eced56b9100c30489b10c7a01e685735f6f0b"

group2bugno = {
    "1": [1,2],
    "test": [13],
    "GL": [13, 14, 15, 16, 17]
}

group2commit = {
    "1": "a10eced56b9100c30489b10c7a01e685735f6f0b",
}

bugno2testcases = {1: ['Dynamic'],
                   2: [],#too many calls
                   5: ['UpdateCapacityAllocatable',   #direct test
                       'DevicePreStartContainer',     #1-indrect test
                       'PodContainerDeviceAllocation',  #1-indrect test
                       ],
                   8: ['GracefulDeleteRS'],
                   13: ['RegisterWithApiServer'],
                   14: ['SchedulerNoPhantomPodAfterExpire'],
                   15: ['BoundedFrequencyRunnerNoBurst'],
                   16: ['BoundedFrequencyRunnerNoBurst'],
                   17: ['ConnectionCloseIsImmediateThroughAProxy'],
                   }

bugno2testpath = {1: 'staging/src/k8s.io/apiserver/plugin/pkg/audit/dynamic',
                  2: 'test/e2e/framework',
                  5: 'pkg/kubelet/cm/devicemanager/',
                  8: 'pkg/proxy/ipvs',
                  13: 'pkg/kubelet',
                  14: 'pkg/scheduler',
                  15: 'pkg/util/async',
                  16: 'pkg/util/async',
                  17: 'staging/src/k8s.io/apimachinery/pkg/util/httpstream/spdy',
                  }

bugno2buggyfiles = {1: 'staging/src/k8s.io/apiserver/plugin/pkg/audit/dynamic/dynamic.go',
2: 'test/e2e/framework/resource_usage_gatherer.go',
                    5: 'pkg/kubelet/cm/devicemanager/manager.go',
                    8: 'pkg/proxy/ipvs/graceful_termination.go',
                    13: 'pkg/kubelet/kubelet_node_status_test.go',
                    14: 'pkg/scheduler/scheduler_test.go',
                    15: 'pkg/util/async/bounded_frequency_runner_test.go',
                    16: 'pkg/util/async/bounded_frequency_runner_test.go',
                    17: 'staging/src/k8s.io/apimachinery/pkg/util/httpstream/spdy/connection_test.go'
}

bugno2buggyfuncname = {
    1: 'testBarrier',
    5: 'isDevicePluginResource',
    8: 'flushList',
    13:'TestRegisterWithApiServer',
    14:'TestSchedulerNoPhantomPodAfterExpire',
    15: 'Test_BoundedFrequencyRunnerNoBurst',
    16: 'Test_BoundedFrequencyRunnerNoBurst',
    17: 'TestConnectionCloseIsImmediateThroughAProxy'
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
        for i in range(1, 5):
            start_time = time.time()
            stdoutstr = subprocess.check_output("go test -run "+testcases, shell=True)
            end_time = time.time()
            #times.append(end_time-start_time)
            print(stdoutstr.decode())
            exe_time = parseExecutionTime(stdoutstr)
            times.append(exe_time)
            print(exe_time)
            #print()
        print(statistics.mean(times), " ".join([str(x) for x in times]))


def patch(basedir, bugno):
    #TODO: insert patch command here
    #os.system()
    if os.path.exists(os.path.join(basedir, bugno2buggyfiles[bugno])):
        print('ok')


def read_dispatch_result(dispath_result_path):
    ret = []
    with open(dispath_result_path) as fd:
        for line in fd:
            items = line.split(',')
            items = map(lambda x: x.strip(), items)
            ret.append(items)

def get_function_code_range(file, funcname):
    startline = 0
    endline = 0
    with open(file) as fd:
        for index, line in fd:
            if 'func' in line and funcname in line:
                startline = index + 1
            if startline != 0 and line.startswith("{"):
                endline = index + 1
    return startline, endline

#should switch to the home dir of the project src as the workdir
def is_GL1(dispatch_result, bugno):
    buggyfile = bugno2buggyfiles[bugno]
    funcname = bugno2buggyfuncname
    startline, endline = get_function_code_range(buggyfile, funcname)
    for line in dispatch_result:
        path_match = False
        line_match = False
        type_match = line[0]=='1'
        for x in line:
            if x.startswith('path=') and x.endswith(buggyfile):
                path_match = True
            if 'lineno' in x:
                lineno = int(x.split('=')[1])
                if startline <= lineno <= endline:
                    line_match = True
        if path_match and line_match:
            return True


def deploy(bug_id):
    global workdir
    os.chdir(workdir)
    workdir = os.getcwd()
    bug_path = os.path.join(workdir, go_project+"-"+str(bug_id))
    create_if_not_exist(bug_path)
    make_run_script_GL1(os.path.join(bug_path, "run-"+go_project+"-"+str(bug_id)+"-perf.sh"),
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


def make_run_script_GL1(filename, buggyfiles, testcases, testpaths):
    with open(filename) as fd:
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

        for i, testcase in testcases:
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
""".format(testcase, testpaths[i]))


if __name__ == "__main__":
    for bugno in group2bugno["GL"]:
        deploy(bugno)
    #read_dispatch_result()
