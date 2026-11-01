"""Show the Radical Pie editors a Word or PowerPoint pass starts minimized from their first frame.

Word and PowerPoint start the Radical Pie server through DCOM, so the `STARTUPINFO` that keeps a render's
window off the screen (`Tools.Render.Svg.Launch`) cannot reach it, and the editor used to open visible over
whatever the operator was doing, in pass one for as long as the document stayed open. The measurements are in
the module docstring of `Tools.Word.Docx` (2026-10-31): the editor is created hidden, renamed to its editor
title and shown a few tens of milliseconds later, and a `SW_SHOWMINNOACTIVE` sent while it is still hidden
shows it minimized, where the server's own show leaves it.

So `EditorHook` listens, out of context and on a thread of its own with its own message loop, for the
creation, the show and the name change of every window on the desktop, and shows the window minimized and
without activation the moment it is the editor of the caller's document: class `RadicalPie`, the whole title
`Radical Pie - Equation in <file name>` for that file and no other, owned by a `RadicalPie.exe`. That is the
title rule of `Tools.Word.Docx.AwaitEditor`, so an editor of another document, one of the operator's own
Radical Pies and a render of another agent are never touched. Each window is acted on once, and a window that
is destroyed is forgotten, so a later window that reuses its handle is acted on too.
"""

import ctypes
import threading
from ctypes import wintypes

import pywintypes
import win32con
import win32gui
import win32process

from Tools.Processes import ImagePids
from Tools.Render.Svg import Executable, WindowClass

EventObjectCreate = 0x8000
EventObjectDestroy = 0x8001
EventObjectShow = 0x8002
EventObjectNameChange = 0x800C
OutOfContext = 0x0000
SkipOwnProcess = 0x0002
ObjidWindow = 0
ChildidSelf = 0

# How long the pass waits for the hook to be installed, and for its thread to leave once told to.
StartSeconds = 5.0
StopSeconds = 5.0

WinEventProc = ctypes.WINFUNCTYPE(
    None,
    wintypes.HANDLE,
    wintypes.DWORD,
    wintypes.HWND,
    wintypes.LONG,
    wintypes.LONG,
    wintypes.DWORD,
    wintypes.DWORD,
)

# A user32 of this module's own, so the prototypes set here touch no other module's `ctypes.windll.user32`.
user32 = ctypes.WinDLL("user32", use_last_error=True)
user32.SetWinEventHook.restype = wintypes.HANDLE
user32.SetWinEventHook.argtypes = (
    wintypes.DWORD,
    wintypes.DWORD,
    wintypes.HMODULE,
    WinEventProc,
    wintypes.DWORD,
    wintypes.DWORD,
    wintypes.DWORD,
)
user32.UnhookWinEvent.argtypes = (wintypes.HANDLE,)
user32.GetMessageW.argtypes = (ctypes.POINTER(wintypes.MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT)
user32.PeekMessageW.argtypes = (
    ctypes.POINTER(wintypes.MSG),
    wintypes.HWND,
    wintypes.UINT,
    wintypes.UINT,
    wintypes.UINT,
)
user32.PostThreadMessageW.argtypes = (wintypes.DWORD, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)
user32.ShowWindowAsync.argtypes = (wintypes.HWND, ctypes.c_int)

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)


class EditorHook:
    """For the length of a `with`, every editor window titled `title` opens minimized and unfocused.

    The hook is installed before `__enter__` returns, so an editor the pass starts after that is seen from its
    creation. A hook Windows refuses leaves the pass as it was before this existed, with the minimize each
    pass sends to the editor it found (`QuietenEditor` in `Tools.Word.Docx` and `Tools.PowerPoint.Pptx`).
    """

    def __init__(self, title: str):
        self.title = title
        self.quietened = set()
        self.threadId = None
        self.ready = threading.Event()
        self.stopping = threading.Event()
        self.thread = threading.Thread(target=self.Listen, daemon=True)

    def __enter__(self):
        self.thread.start()

        try:
            # A thread that is slow to install its hooks is told to leave as soon as it is up, and the pass
            # goes on without them, as it does for a hook Windows refuses.
            if not self.ready.wait(StartSeconds):
                self.stopping.set()
        except BaseException:
            self.Stop()

            raise

        return self

    def __exit__(self, exceptionType, exceptionValue, traceback):
        self.Stop()

        return False

    def Stop(self) -> None:
        """Tell the thread to leave, whether or not it has finished starting, and wait for it."""

        self.stopping.set()
        self.ready.wait(StartSeconds)

        if self.threadId is not None:
            user32.PostThreadMessageW(self.threadId, win32con.WM_QUIT, 0, 0)

        self.thread.join(StopSeconds)

    def Listen(self) -> None:
        # The callback object is held for as long as the hooks are, or ctypes frees the thunk under them.
        callback = WinEventProc(self.OnEvent)
        flags = OutOfContext | SkipOwnProcess
        hooks = [
            user32.SetWinEventHook(event, event, None, callback, 0, 0, flags)
            for event in (EventObjectCreate, EventObjectDestroy, EventObjectShow, EventObjectNameChange)
        ]
        message = wintypes.MSG()

        # A thread has no message queue until it asks for one, and `PostThreadMessageW` to a thread without one
        # is lost, so the queue exists before `__exit__` can be told the thread id.
        user32.PeekMessageW(ctypes.byref(message), None, 0, 0, 0)
        self.threadId = kernel32.GetCurrentThreadId()
        self.ready.set()

        try:
            # A stop that came while the hooks were being installed is seen here, whether or not its WM_QUIT
            # found a thread id to go to.
            while not self.stopping.is_set() and user32.GetMessageW(ctypes.byref(message), None, 0, 0) > 0:
                user32.TranslateMessage(ctypes.byref(message))
                user32.DispatchMessageW(ctypes.byref(message))
        finally:
            for hook in hooks:
                if hook:
                    user32.UnhookWinEvent(hook)

    def OnEvent(self, hook, event, handle, idObject, idChild, eventThread, eventTime) -> None:
        if idObject != ObjidWindow or idChild != ChildidSelf or not handle:
            return

        # The destroy event is hooked for this alone: no `IsEditor` call is spent on it.
        if event == EventObjectDestroy:
            self.quietened.discard(handle)

            return

        if handle in self.quietened:
            return

        if not IsEditor(handle, self.title):
            return

        self.quietened.add(handle)
        user32.ShowWindowAsync(handle, win32con.SW_SHOWMINNOACTIVE)


def IsEditor(handle: int, title: str) -> bool:
    """True when `handle` is a window of class `RadicalPie` titled `title` whose process is a `RadicalPie.exe`.

    The tests go from the cheapest to the dearest, because the hook sees every name change on the desktop.
    `GetWindowText` on another process's window reads the title Windows keeps and sends that window nothing,
    so a hung server cannot hold the hook. A window that has gone in the meantime is not an editor.
    """

    try:
        if win32gui.GetClassName(handle) != WindowClass:
            return False

        if win32gui.GetWindowText(handle) != title:
            return False

        _, pid = win32process.GetWindowThreadProcessId(handle)
    except pywintypes.error:
        return False

    return pid in ImagePids(Executable.name)
