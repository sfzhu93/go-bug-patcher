import os
import subprocess
import time

# import statistics


go_project = "docker"
bug_id = 20
workdir = "."
go_get_url = "github.com/docker/docker"

group2bugno = {
    "1": [11, 12, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32],
    "2": [33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54],
    # 13,, 33, 34, 35, 36,
    # 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54
}

group2commit = {
    "1": "37defbfd9b968f38e8e15dfa5f06d9f878bd65ba",
}

bugno2testcases = {11: ['TestGetContainersAttachWebsocket'],
                   12: ['TestGetContainersAttachWebsocket'],
                   # 13: [''],
                   14: ['TestGetStoppedContainerStats'],
                   15: ['TestLogsAPIWithStdout'],
                   16: ['TestLogsAPIUntilFutureFollow'],
                   17: ['TestAttachTTYWithoutStdin'],
                   18: ['TestAttachClosedOnContainerStop'],
                   19: ['TestAttachAfterDetach'],
                   20: ['TestBuildAddSingleFileToWorkdir'],
                   21: ['TestBuildCopySingleFileToWorkdir'],
                   22: ['TestDaemonRestartKillWait'],
                   23: ['TestDaemonRestartWithPausedContainer'],
                   24: ['TestEventsOOMDisableFalse'],
                   25: ['TestEventsOOMDisableTrue'],
                   26: ['TestExecInteractive'],
                   27: ['TestExecTTYWithoutStdin'],
                   28: ['TestExecStopNotHanging'],
                   29: ['TestExecCgroup'],
                   30: ['TestExecInteractiveStdinClose'],
                   31: ['TestExecTTY'],
                   32: ['TestExternalVolumeDriverLookupNotBlocked'],
                   33: ['TestExternalVolumeDriverRetryNotImmediatelyExists'],
                   34: ['TestLogsFollowStopped'],
                   35: ['TestConcurrentPullWholeRepo'],
                   36: ['TestConcurrentFailingPull'],
                   37: ['TestConcurrentPullMultipleTags'],
                   38: ['TestConcurrentPush'],
                   39: ['TestRunExitOnStdinClose'],
                   40: ['TestRunTTYWithPipe'],
                   41: ['TestRunPIDHostWithChildIsKillable'],
                   42: ['TestRunStdinBlockedAfterContainerExit'],
                   43: ['TestRunRedirectStdout'],
                   44: ['TestRunAttachDetach'],
                   45: ['TestRunAttachDetachFromFlag'],
                   46: ['TestRunAttachDetachFromConfig'],
                   47: ['TestRunAttachDetachKeysOverrideConfig'],
                   48: ['TestRunOOMExitCode'],
                   49: ['TestServiceLogsFollow'],
                   50: ['TestStartAttachReturnsOnError'],
                   51: ['TestStatsNoStream'],
                   52: ['TestExecWithCloseStdin'],
                   53: ['TestContinueAfterPluginCrash'],
                   54: ['TestShmSizeReload', 'TestDaemonDiscoveryBackendConfigReload'],
                   }

bugno2testpath = {11: 'integration-cli',
                  12: 'integration-cli',
                  13: 'integration-cli',
                  14: 'integration-cli',
                  15: 'integration-cli',
                  16: 'integration-cli',
                  17: 'integration-cli',
                  18: 'integration-cli',
                  19: 'integration-cli',
                  20: 'integration-cli',
                  21: 'integration-cli',
                  22: 'integration-cli',
                  23: 'integration-cli',
                  24: 'integration-cli',
                  25: 'integration-cli',
                  26: 'integration-cli',
                  27: 'integration-cli',
                  28: 'integration-cli',
                  29: 'integration-cli',
                  30: 'integration-cli',
                  31: 'integration-cli',
                  32: 'integration-cli',
                  33: 'integration-cli',
                  34: 'integration-cli',
                  35: 'integration-cli',
                  36: 'integration-cli',
                  37: 'integration-cli',
                  38: 'integration-cli',
                  39: 'integration-cli',
                  40: 'integration-cli',
                  41: 'integration-cli',
                  42: 'integration-cli',
                  43: 'integration-cli',
                  44: 'integration-cli',
                  45: 'integration-cli',
                  46: 'integration-cli',
                  47: 'integration-cli',
                  48: 'integration-cli',
                  49: 'integration-cli',
                  50: 'integration-cli',
                  51: 'integration-cli',
                  52: 'integration/container',
                  53: 'integration/plugin/logging',
                  54: 'testutil/daemon',
                  }

bugno2buggyfiles = {
    11: 'integration-cli/docker_api_attach_test.go',
    12: 'integration-cli/docker_api_attach_test.go',
    13: 'integration-cli/docker_api_attach_test.go',
    14: 'integration-cli/docker_api_containers_test.go',
    15: 'integration-cli/docker_api_logs_test.go',
    16: 'integration-cli/docker_api_logs_test.go',
    17: 'integration-cli/docker_cli_attach_test.go',
    18: 'integration-cli/docker_cli_attach_unix_test.go',
    19: 'integration-cli/docker_cli_attach_unix_test.go',
    20: 'integration-cli/docker_cli_build_test.go',
    21: 'integration-cli/docker_cli_build_test.go',
    22: 'integration-cli/docker_cli_daemon_test.go',
    23: 'integration-cli/docker_cli_daemon_test.go',
    24: 'integration-cli/docker_cli_events_unix_test.go',
    25: 'integration-cli/docker_cli_events_unix_test.go',
    26: 'integration-cli/docker_cli_exec_test.go',
    27: 'integration-cli/docker_cli_exec_test.go',
    28: 'integration-cli/docker_cli_exec_test.go',
    29: 'integration-cli/docker_cli_exec_test.go',
    30: 'integration-cli/docker_cli_exec_unix_test.go',
    31: 'integration-cli/docker_cli_exec_unix_test.go',
    32: 'integration-cli/docker_cli_external_volume_driver_test.go',
    33: 'integration-cli/docker_cli_external_volume_driver_test.go',
    34: 'integration-cli/docker_cli_logs_test.go',
    35: 'integration-cli/docker_cli_pull_local_test.go',
    36: 'integration-cli/docker_cli_pull_local_test.go',
    37: 'integration-cli/docker_cli_pull_local_test.go',
    38: 'integration-cli/docker_cli_push_test.go',
    39: 'integration-cli/docker_cli_run_test.go',
    40: 'integration-cli/docker_cli_run_test.go',
    41: 'integration-cli/docker_cli_run_test.go',
    42: 'integration-cli/docker_cli_run_test.go',
    43: 'integration-cli/docker_cli_run_unix_test.go',
    44: 'integration-cli/docker_cli_run_unix_test.go',
    45: 'integration-cli/docker_cli_run_unix_test.go',
    46: 'integration-cli/docker_cli_run_unix_test.go',
    47: 'integration-cli/docker_cli_run_unix_test.go',
    48: 'integration-cli/docker_cli_run_unix_test.go',
    49: 'integration-cli/docker_cli_service_logs_test.go',
    50: 'integration-cli/docker_cli_start_test.go',
    51: 'integration-cli/docker_cli_stats_test.go',
    52: 'integration/container/exec_test.go',
    53: 'integration/plugin/logging/logging_linux_test.go',
    54: 'testutil/daemon/daemon.go',
}

bugno2buggyfuncname = {
    11: 'TestGetContainersAttachWebsocket',
    12: 'TestGetContainersAttachWebsocket',
    13: '',
    14: 'TestGetStoppedContainerStats',
    15: 'TestLogsAPIWithStdout',
    16: 'TestLogsAPIUntilFutureFollow',
    17: 'TestAttachTTYWithoutStdin',
    18: 'TestAttachClosedOnContainerStop',
    19: 'TestAttachAfterDetach',
    20: 'TestBuildAddSingleFileToWorkdir',
    21: 'TestBuildCopySingleFileToWorkdir',
    22: 'TestDaemonRestartKillWait',
    23: 'TestDaemonRestartWithPausedContainer',
    24: 'TestEventsOOMDisableFalse',
    25: 'TestEventsOOMDisableTrue',
    26: 'TestExecInteractive',
    27: 'TestExecTTYWithoutStdin',
    28: 'TestExecStopNotHanging',
    29: 'TestExecCgroup',
    30: 'TestExecInteractiveStdinClose',
    31: 'TestExecTTY',
    32: 'TestExternalVolumeDriverLookupNotBlocked',
}

bugno2buggyline = {
    11: 46,
    12: 53,
    13: 281,
    14: 341,
    15: 33,
    16: 118,
    17: 105,
    18: 36,
    19: 71,
    20: 493,
    21: 836,
    22: 1249,
    23: 1602,
    24: 54,
    25: 84,
    26: 56,
    27: 173,
    28: 233,
    29: 259,
    30: 29,
    31: 59,
    32: 368,
}


# TODO: add information for patch

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
            stdout = subprocess.check_output("go test -run " + testcases, shell=True)
            end_time = time.time()
            # times.append(end_time-start_time)
            exe_time = parseExecutionTime(stdout)
            times.append(exe_time)
            print(exe_time)
            # print()
        # print(statistics.mean(times), " ".join([str(x) for x in times]))


def patch(basedir, bugno):
    # TODO: insert patch command here
    # os.system()
    if os.path.exists(os.path.join(basedir, bugno2buggyfiles[bugno])):
        print('ok')


def deploy(bug_id, buggy_commit):
    global workdir
    os.chdir(workdir)
    workdir = os.getcwd()
    bug_path = os.path.join(workdir, go_project + "-" + str(bug_id))
    create_if_not_exist(bug_path)
    make_run_script_GL1(os.path.join(bug_path, "run-" + go_project + "-" + str(bug_id) + "-perf.sh"),
                        buggy_commit,
                        bugno2buggyfiles[bug_id],
                        bugno2testcases[bug_id],
                        bugno2testpath[bug_id],
                        bugno2buggyline[bug_id]
                        )
    """make_inject_script_GL1(os.path.join(bug_path, "run-" + go_project + "-" + str(bug_id) + "-inject.sh"),
                           buggy_commit,
                           bugno2buggyfiles[bug_id],
                           bugno2testcases[bug_id],
                           bugno2testpath[bug_id]
                           )

    make_copy_inject(os.path.join(bug_path, "run-" + go_project + "-" + str(bug_id) + "-helper.sh"),
                     buggy_commit,
                     bugno2buggyfiles[bug_id],
                     bugno2testcases[bug_id],
                     bugno2testpath[bug_id]
                     )"""
    os.environ["GOPATH"] = bug_path
    src_path = os.path.join(bug_path, 'src')
    create_if_not_exist(src_path)
    os.chdir(src_path)
    print("go get...")
    # os.system("go get " + go_get_url)
    # src_path = os.path.join(src_path, go_get_url)
    # os.chdir(src_path)
    # print("git reset...")
    # os.system("git reset --hard " + buggy_commit)
    print(bug_id, bugno2buggyfiles[bug_id])
    # os.chdir(os.path.join(src_path, bugno2testpath[bug_id]))
    # executeBugNo(bug_id)
    # patch(src_path, bug_id)


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


def make_run_script_GL1(filename, buggy_commit, buggyfiles, testcases, testpaths, buggyline):
    with open(filename, 'w') as fd:
        fd.write("""GOPATH=${{PWD}}
PATCHER=/data/suz305/go-workspace/my-tools/bin/gl-1-patcher
TMPPATH=${{GOPATH}}/tmp
OVERSCR=/data/suz305/go-workspace/my-tools/src/github.com/sfzhu93/go-bug-patcher/scripts/overhead_docker_integration.py

PROPATH=${{GOPATH}}/src/{0}
BUGGY_VERSION={1}
BUGFILE=${{PROPATH}}/{2}
BUGLINE={3}
HELPERFILE=hack/make/.integration-test-helpers
""".format(go_get_url, buggy_commit, buggyfiles, buggyline))

        fd.write("""export GOPATH=$GOPATH
mkdir -p ${TMPPATH}
rm -rf ${TMPPATH}/*.*
rm -rf ${TMPPATH}/*


cd ${PROPATH}

""")

        for i, testcase in enumerate(testcases):
            # print(testpaths[i])
            fd.write("""echo 'reseting to the buggy version...'

git reset --hard ${{BUGGY_VERSION}}

sed '16 s/\\:\\=1\\}}/\\:\\=10\\}}/' $HELPERFILE > ${{TMPPATH}}/helper.tmp #set the number of repeating test

mv ${{TMPPATH}}/helper.tmp $HELPERFILE
TESTNAME={0}

echo 'run the original' {1}/{0} '...'
make TEST_FILTER=${{TESTNAME}} test-integration >> ${{TMPPATH}}/buggy.time

echo 'patching...'

${{PATCHER}} ${{BUGFILE}} ${{BUGLINE}}

echo 'run the patched' {1}/{0} '...'
make TEST_FILTER=${{TESTNAME}} test-integration >> ${{TMPPATH}}/patch.time

echo
echo

python ${{OVERSCR}} ${{TMPPATH}}/buggy.time ${{TMPPATH}}/patch.time 10 $TESTNAME
""".format(testcase, testpaths))


if __name__ == "__main__":
    groupname = '2'
    for bugno in group2bugno[groupname]:
        deploy(bugno, group2commit[groupname])
