"""The processes the pipelines launch, held in one registry and in one job object until each has exited.

The standing ruling of 2026-09-10 is that every process the tooling launches is terminated by the tooling on
success and on failure. A process listing read before and after a test cannot check that ruling exactly: a
Radical Pie another test worker launched reads as a stray of this test, one the operator opened by hand reads
the same way, and one the tooling has just killed is still listed by `tasklist` for a moment while it exits,
which is the "still listed afterwards" fact `Tools.Word.Docx.WordSession.Terminate` records. So each pipeline
registers the pid it launched here and drops it once the process has been seen to exit; what is left in the
registry is what the tooling failed to end, whoever else was running the same program at the time.

The registry is a module-level set guarded by a lock, because the Word pipeline's guard thread terminates
processes while the main thread is inside a COM call. It lives in one process: a pipeline run in a child
process, which is what the command-line tests do, keeps its own registry and empties it on its own exit path,
so a leak inside such a child is invisible to the parent's registry.

Registration also puts the process in a job object of this interpreter's own, created with
`JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`, which is what covers the end the registry cannot reach: an interrupt
that runs no Python at all. Ctrl-Break, a closed console and a killed interpreter unwind nothing and leave no
cleanup to run, and the kernel then closes the last handle to the job and ends every process in it. All four
launch routes the tooling uses accept the assignment by pid, `OpenProcess` with
`PROCESS_SET_QUOTA | PROCESS_TERMINATE` and then `AssignProcessToJobObject` (measured 2026-09-19): the
`RadicalPie.exe` `Tools.Render.Svg` starts with `Popen`, the one the COM launcher starts for
`RadicalPie.Application.1`, which is the editor an activation opens, and the `POWERPNT.EXE` and `WINWORD.EXE`
that `DispatchEx` starts. Only a pid a pipeline registers as its own is assigned, so the Radical Pie of
another agent and the Word the operator is typing in are never touched.
"""

import threading
import time

import pywintypes
import win32api
import win32con
import win32event
import win32job

ProcessAccess = win32con.PROCESS_TERMINATE | win32con.SYNCHRONIZE | win32con.PROCESS_QUERY_INFORMATION

# What `AssignProcessToJobObject` asks for on the process handle.
AssignAccess = win32con.PROCESS_SET_QUOTA | win32con.PROCESS_TERMINATE

Lock = threading.Lock()
Launched = set()

# The job every registered process goes into, made on the first registration and held open until this
# interpreter ends. Nothing closes it by hand: the handle closing is what kills the processes in it.
Job = None


def Register(pid: int) -> None:
    """Record a process this tooling started, and put it in the job that ends with this interpreter."""

    with Lock:
        Launched.add(pid)
        Adopt(pid)


def Adopt(pid: int) -> None:
    """Assign one process to the job. Called with `Lock` held, because the job is made on first use.

    A process that has already gone cannot be assigned, and neither can one this interpreter has no right to,
    so a failure here is passed over: the assignment is the cleanup for an interrupt that runs no Python, and
    the pipeline's own termination steps, which the registry above is the check on, run either way.
    """

    global Job

    if Job is None:
        Job = win32job.CreateJobObject(None, "")
        limits = win32job.QueryInformationJobObject(Job, win32job.JobObjectExtendedLimitInformation)
        limits["BasicLimitInformation"]["LimitFlags"] |= win32job.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        win32job.SetInformationJobObject(Job, win32job.JobObjectExtendedLimitInformation, limits)

    try:
        handle = win32api.OpenProcess(AssignAccess, False, pid)
    except pywintypes.error:
        return

    try:
        win32job.AssignProcessToJobObject(Job, handle)
    except pywintypes.error:
        pass
    finally:
        win32api.CloseHandle(handle)


def Release(pid: int) -> None:
    """Drop a process whose exit has been confirmed."""

    with Lock:
        Launched.discard(pid)


def Strays(graceSeconds: float) -> list:
    """The registered pids still running, each given up to `graceSeconds` between them to finish exiting.

    A pid that goes within the grace is dropped from the registry rather than reported: a process that was
    still exiting when the check ran was terminated by the tooling, which is what the ruling asks.
    """

    with Lock:
        pending = sorted(Launched)

    deadline = time.monotonic() + graceSeconds
    strays = []

    for pid in pending:
        if AwaitProcessExit(pid, max(deadline - time.monotonic(), 0.0)):
            Release(pid)
        else:
            strays.append(pid)

    return strays


def AwaitProcessExit(pid: int, seconds: float) -> bool:
    """True when the process is gone within `seconds`. A handle that cannot be opened means it is gone."""

    try:
        handle = win32api.OpenProcess(ProcessAccess, False, pid)
    except pywintypes.error:
        return True

    try:
        return win32event.WaitForSingleObject(handle, int(max(seconds, 0.0) * 1000)) == win32event.WAIT_OBJECT_0
    finally:
        win32api.CloseHandle(handle)


def KillProcess(pid: int) -> None:
    """Terminate one process, tolerating one that has gone already.

    `TerminateProcess` answers `Access is denied` for a process that has exited while a handle to it is still
    open, and a pid stays openable that way as long as anything holds one (measured 2026-09-19). That is the
    ordinary case here: a process that exited in the gap between `EndProcess`'s wait and this call, and one the
    job object ended when the interpreter that registered it was killed. A refusal this does hide is reported
    by the wait that follows it, which sees the process still running and leaves it in the registry.
    """

    try:
        handle = win32api.OpenProcess(ProcessAccess, False, pid)
    except pywintypes.error:
        return

    try:
        win32api.TerminateProcess(handle, 1)
    except pywintypes.error:
        pass
    finally:
        win32api.CloseHandle(handle)
