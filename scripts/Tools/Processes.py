"""The processes the pipelines launch, held in one registry until each has been seen to exit.

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
"""

import threading
import time

import pywintypes
import win32api
import win32con
import win32event

ProcessAccess = win32con.PROCESS_TERMINATE | win32con.SYNCHRONIZE | win32con.PROCESS_QUERY_INFORMATION

Lock = threading.Lock()
Launched = set()


def Register(pid: int) -> None:
    """Record a process this tooling started."""

    with Lock:
        Launched.add(pid)


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
    try:
        handle = win32api.OpenProcess(ProcessAccess, False, pid)
    except pywintypes.error:
        return

    try:
        win32api.TerminateProcess(handle, 1)
    finally:
        win32api.CloseHandle(handle)
