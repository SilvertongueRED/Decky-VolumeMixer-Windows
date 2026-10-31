import json
import asyncio
import logging
import os
import re
from asyncio.subprocess import Process
from typing import Coroutine, Any

import decky # type: ignore
from settings import SettingsManager # type: ignore

# Decky runs the same main.py on SteamOS (PipeWire) and on the unofficial
# Decky-Loader-For-Windows build. Pick the audio backend at import time.
IS_WINDOWS = os.name == "nt"


# ---------------------------------------------------------------------------
# Windows audio backend (Core Audio via raw ctypes/COM, no external deps)
# ---------------------------------------------------------------------------
if IS_WINDOWS:
    import ctypes
    from ctypes import wintypes, POINTER, byref, c_void_p, c_float, c_int, c_uint, c_long, c_ulong, c_wchar_p

    _ole32 = ctypes.windll.ole32
    _kernel32 = ctypes.windll.kernel32

    CLSCTX_ALL = 23

    class _GUID(ctypes.Structure):
        _fields_ = [
            ("Data1", c_ulong),
            ("Data2", ctypes.c_ushort),
            ("Data3", ctypes.c_ushort),
            ("Data4", ctypes.c_ubyte * 8),
        ]

    _ole32.CLSIDFromString.argtypes = [c_wchar_p, POINTER(_GUID)]
    _ole32.CLSIDFromString.restype = c_long
    _ole32.CoInitializeEx.argtypes = [c_void_p, c_uint]
    _ole32.CoInitializeEx.restype = c_long
    _ole32.CoUninitialize.restype = None
    _ole32.CoCreateInstance.argtypes = [POINTER(_GUID), c_void_p, c_uint, POINTER(_GUID), POINTER(c_void_p)]
    _ole32.CoCreateInstance.restype = c_long
    _ole32.CoTaskMemFree.argtypes = [c_void_p]
    _ole32.CoTaskMemFree.restype = None

    _kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    _kernel32.OpenProcess.restype = wintypes.HANDLE
    _kernel32.QueryFullProcessImageNameW.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, POINTER(wintypes.DWORD)]
    _kernel32.QueryFullProcessImageNameW.restype = wintypes.BOOL
    _kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    _kernel32.CloseHandle.restype = wintypes.BOOL
    _kernel32.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
    _kernel32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    _kernel32.Process32FirstW.argtypes = [wintypes.HANDLE, c_void_p]
    _kernel32.Process32FirstW.restype = wintypes.BOOL
    _kernel32.Process32NextW.argtypes = [wintypes.HANDLE, c_void_p]
    _kernel32.Process32NextW.restype = wintypes.BOOL

    def _guid(s: str) -> _GUID:
        g = _GUID()
        if _ole32.CLSIDFromString(s, byref(g)) != 0:
            raise OSError(f"CLSIDFromString failed for {s}")
        return g

    CLSID_MMDeviceEnumerator = _guid("{BCDE0395-E52F-467C-8E3D-C4579291692E}")
    IID_IMMDeviceEnumerator = _guid("{A95664D2-9614-4F35-A746-DE8DB63617E6}")
    IID_IAudioSessionManager2 = _guid("{77AA99A0-1BD6-484F-8BC7-2C654C9A9B6F}")
    IID_IAudioSessionControl2 = _guid("{BFB7FF88-7239-4FC9-8FA2-07C950BE9C6D}")
    IID_ISimpleAudioVolume = _guid("{87CE5498-68D6-44E5-9215-6DA47EF883D8}")

    def _vt(ptr: c_void_p, index: int):
        vtable = ctypes.cast(ptr, POINTER(c_void_p)).contents.value
        return ctypes.cast(vtable, POINTER(c_void_p))[index]

    def _call(ptr, index, restype, argtypes, *args):
        proto = ctypes.WINFUNCTYPE(restype, c_void_p, *argtypes)
        return proto(_vt(ptr, index))(ptr, *args)

    def _release(ptr):
        if ptr:
            _call(ptr, 2, c_ulong, [])

    def _proc_path(pid: int):
        """Full path of the process image, or None (e.g. protected/anti-cheat processes)."""
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        handle = _kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not handle:
            return None
        try:
            size = wintypes.DWORD(1024)
            buf = ctypes.create_unicode_buffer(1024)
            if _kernel32.QueryFullProcessImageNameW(handle, 0, buf, byref(size)):
                return buf.value or None
        finally:
            _kernel32.CloseHandle(handle)
        return None

    def _proc_name(pid: int):
        path = _proc_path(pid)
        if not path:
            return None
        base = path.replace("\\", "/").split("/")[-1]
        if base.lower().endswith(".exe"):
            base = base[:-4]
        return base or None

    # -- exe version resource (ProductName / FileDescription) ---------------
    try:
        _version = ctypes.windll.version
        _version.GetFileVersionInfoSizeW.argtypes = [c_wchar_p, POINTER(wintypes.DWORD)]
        _version.GetFileVersionInfoSizeW.restype = wintypes.DWORD
        _version.GetFileVersionInfoW.argtypes = [c_wchar_p, wintypes.DWORD, wintypes.DWORD, c_void_p]
        _version.GetFileVersionInfoW.restype = wintypes.BOOL
        _version.VerQueryValueW.argtypes = [c_void_p, c_wchar_p, POINTER(c_void_p), POINTER(c_uint)]
        _version.VerQueryValueW.restype = wintypes.BOOL
    except Exception:  # never let name lookup break the plugin
        _version = None

    def _exe_version_strings(path: str):
        """Return (ProductName, FileDescription) from the exe's version resource."""
        if _version is None:
            return None, None
        try:
            dummy = wintypes.DWORD(0)
            size = _version.GetFileVersionInfoSizeW(path, byref(dummy))
            if not size:
                return None, None
            data = ctypes.create_string_buffer(size)
            if not _version.GetFileVersionInfoW(path, 0, size, data):
                return None, None

            def query(sub_block):
                ptr = c_void_p()
                length = c_uint()
                if not _version.VerQueryValueW(data, sub_block, byref(ptr), byref(length)) or not ptr or not length.value:
                    return None
                return ptr, length.value

            langs = []
            tr = query("\\VarFileInfo\\Translation")
            if tr:
                ptr, n = tr
                raw = ctypes.string_at(ptr, n)
                for i in range(0, len(raw) - 3, 4):
                    lang = int.from_bytes(raw[i:i + 2], "little")
                    cp = int.from_bytes(raw[i + 2:i + 4], "little")
                    langs.append(f"{lang:04x}{cp:04x}")
            langs += ["040904b0", "040904e4", "000004b0"]

            def get(field):
                for lc in langs:
                    r = query(f"\\StringFileInfo\\{lc}\\{field}")
                    if r:
                        val = ctypes.wstring_at(r[0]).strip()
                        if val:
                            return val
                return None

            return get("ProductName"), get("FileDescription")
        except Exception:
            return None, None

    def _display_name(ctl2):
        p = c_wchar_p()
        if _call(ctl2, 4, c_long, [POINTER(c_wchar_p)], byref(p)) != 0:
            return None
        val = p.value
        if p.value:
            _ole32.CoTaskMemFree(ctypes.cast(p, c_void_p))
        if val and not val.startswith("@"):
            return val
        return None

    # Generic session display names that add no useful information
    _GENERIC_NAMES = frozenset({
        "game", "audio", "music", "sound", "sounds", "media",
        "playback", "stream", "application", "app", "process",
        "output", "render", "default",
    })

    class _PROCESSENTRY32W(ctypes.Structure):
        _fields_ = [
            ("dwSize", wintypes.DWORD),
            ("cntUsage", wintypes.DWORD),
            ("th32ProcessID", wintypes.DWORD),
            ("th32DefaultHeapID", ctypes.c_size_t),  # ULONG_PTR (pointer-sized)
            ("th32ModuleID", wintypes.DWORD),
            ("cntThreads", wintypes.DWORD),
            ("th32ParentProcessID", wintypes.DWORD),
            ("pcPriClassBase", ctypes.c_long),
            ("dwFlags", wintypes.DWORD),
            ("szExeFile", ctypes.c_wchar * 260),
        ]

    def _build_pid_name_map() -> dict:
        """Enumerate ALL processes via CreateToolhelp32Snapshot.
        Works even for anti-cheat-protected processes where OpenProcess fails."""
        TH32CS_SNAPPROCESS = 0x00000002
        snapshot = _kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
        INVALID = wintypes.HANDLE(-1).value
        if ctypes.cast(snapshot, c_void_p).value == INVALID:
            return {}
        result = {}
        try:
            entry = _PROCESSENTRY32W()
            entry.dwSize = ctypes.sizeof(_PROCESSENTRY32W)
            if _kernel32.Process32FirstW(snapshot, byref(entry)):
                while True:
                    exe = entry.szExeFile
                    if exe.lower().endswith(".exe"):
                        exe = exe[:-4]
                    if exe:
                        result[entry.th32ProcessID] = exe
                    if not _kernel32.Process32NextW(snapshot, byref(entry)):
                        break
        finally:
            _kernel32.CloseHandle(snapshot)
        return result

    def _best_name(exe_name, win_label):
        """Pick the most informative name.
        Prefer exe name unless it's generic, then try the Windows display name."""
        if exe_name and exe_name.lower() not in _GENERIC_NAMES:
            return exe_name
        if win_label and win_label.lower() not in _GENERIC_NAMES:
            return win_label
        return exe_name or win_label

    def _session_instance_id(ctl2):
        """Return the session instance identifier string, or None."""
        p = c_wchar_p()
        if _call(ctl2, 13, c_long, [POINTER(c_wchar_p)], byref(p)) != 0:
            return None
        val = p.value
        if p.value:
            _ole32.CoTaskMemFree(ctypes.cast(p, c_void_p))
        return val

    def _win_each_session(callback):
        """Walk every active render audio session, calling callback(ctl2, pid).
        Collect and return non-None callback results."""
        out = []
        hr_init = _ole32.CoInitializeEx(None, 0)  # COINIT_MULTITHREADED
        enumerator = c_void_p()
        device = c_void_p()
        manager = c_void_p()
        session_enum = c_void_p()
        try:
            if _ole32.CoCreateInstance(byref(CLSID_MMDeviceEnumerator), None, CLSCTX_ALL,
                                       byref(IID_IMMDeviceEnumerator), byref(enumerator)) != 0:
                raise OSError("CoCreateInstance(MMDeviceEnumerator) failed")
            # IMMDeviceEnumerator::GetDefaultAudioEndpoint(eRender=0, eConsole=0, **device)
            if _call(enumerator, 4, c_long, [c_int, c_int, POINTER(c_void_p)], 0, 0, byref(device)) != 0:
                raise OSError("GetDefaultAudioEndpoint failed")
            # IMMDevice::Activate(IID_IAudioSessionManager2, CLSCTX_ALL, NULL, **manager)
            if _call(device, 3, c_long, [POINTER(_GUID), c_uint, c_void_p, POINTER(c_void_p)],
                     byref(IID_IAudioSessionManager2), CLSCTX_ALL, None, byref(manager)) != 0:
                raise OSError("IMMDevice::Activate(IAudioSessionManager2) failed")
            # IAudioSessionManager2::GetSessionEnumerator(**session_enum)
            if _call(manager, 5, c_long, [POINTER(c_void_p)], byref(session_enum)) != 0:
                raise OSError("GetSessionEnumerator failed")

            count = c_int()
            _call(session_enum, 3, c_long, [POINTER(c_int)], byref(count))  # GetCount
            for i in range(count.value):
                ctl = c_void_p()
                if _call(session_enum, 4, c_long, [c_int, POINTER(c_void_p)], i, byref(ctl)) != 0 or not ctl:
                    continue
                ctl2 = c_void_p()
                try:
                    # IAudioSessionControl::QueryInterface(IID_IAudioSessionControl2, **ctl2)
                    if _call(ctl, 0, c_long, [POINTER(_GUID), POINTER(c_void_p)],
                             byref(IID_IAudioSessionControl2), byref(ctl2)) != 0 or not ctl2:
                        continue
                    # Skip the system-sounds session (IsSystemSoundsSession -> S_OK)
                    if _call(ctl2, 15, c_long, []) == 0:
                        continue
                    state = c_int()
                    _call(ctl2, 3, c_long, [POINTER(c_int)], byref(state))  # GetState
                    if state.value == 2:  # AudioSessionStateExpired
                        continue
                    pid = c_uint()
                    _call(ctl2, 14, c_long, [POINTER(c_uint)], byref(pid))  # GetProcessId
                    if pid.value == 0:
                        continue
                    result = callback(ctl2, pid.value)
                    if result is not None:
                        out.append(result)
                finally:
                    _release(ctl2)
                    _release(ctl)
        finally:
            _release(session_enum)
            _release(manager)
            _release(device)
            _release(enumerator)
            if hr_init in (0, 1):  # S_OK / S_FALSE -> we own an init to balance
                _ole32.CoUninitialize()
        return out

    def _session_volume(ctl2):
        """Return the 0..1 master volume for a session, or None."""
        vol = c_void_p()
        if _call(ctl2, 0, c_long, [POINTER(_GUID), POINTER(c_void_p)],
                 byref(IID_ISimpleAudioVolume), byref(vol)) != 0 or not vol:
            return None
        try:
            level = c_float()
            if _call(vol, 4, c_long, [POINTER(c_float)], byref(level)) != 0:  # GetMasterVolume
                return None
            return level.value
        finally:
            _release(vol)

    def _session_set_volume(ctl2, level: float):
        vol = c_void_p()
        if _call(ctl2, 0, c_long, [POINTER(_GUID), POINTER(c_void_p)],
                 byref(IID_ISimpleAudioVolume), byref(vol)) != 0 or not vol:
            return False
        try:
            # ISimpleAudioVolume::SetMasterVolume(level, NULL event context)
            return _call(vol, 3, c_long, [c_float, c_void_p], c_float(level), None) == 0
        finally:
            _release(vol)


# ---------------------------------------------------------------------------
# Real application name resolution (Windows)
# ---------------------------------------------------------------------------
# Raw exe names are often internal codenames (The Finals runs as "Discovery.exe").
# We resolve a friendlier name from, in order:
#   1. Steam: the game's appmanifest (steamapps/common/<installdir> -> "name")
#   2. The exe's version resource (ProductName / FileDescription)
#   3. The raw exe name, then the Windows session display name
import time

# Version-resource strings that describe the framework/OS rather than the app
_GENERIC_PRODUCT_NAMES = frozenset({
    "unreal engine", "unity", "unity player", "electron", "chromium", "cef",
    "chromium embedded framework", "godot engine", "game", "launcher",
    "application", "microsoft windows operating system",
})
_GENERIC_PRODUCT_FRAGMENTS = ("operating system", "unreal engine", "epic games launcher")

# exe names that should always be shown under a fixed, friendly name
_KNOWN_EXE_NAMES = {
    "steamwebhelper": "Steam",
    "steam": "Steam",
}

_NAME_CACHE: dict = {}      # key -> (value, timestamp)
_NAME_MISS_TTL = 300        # seconds before retrying a lookup that found nothing
_steam_index_cache = {"ts": 0.0, "games": {}, "common_dirs": []}
_STEAM_INDEX_TTL = 60
_NAME_RE = re.compile(r'"name"\s+"((?:[^"\\]|\\.)*)"')
_INSTALLDIR_RE = re.compile(r'"installdir"\s+"((?:[^"\\]|\\.)*)"')
_LIBPATH_RE = re.compile(r'"path"\s+"((?:[^"\\]|\\.)*)"')


def _norm_key(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def _is_generic_product(name) -> bool:
    if not name:
        return True
    low = name.strip().lower()
    return (low in _GENERIC_PRODUCT_NAMES or low in _GENERIC_NAMES
            or any(frag in low for frag in _GENERIC_PRODUCT_FRAGMENTS))


def _steam_roots() -> list:
    roots = []
    try:
        import winreg  # type: ignore
        for hive, sub, val in (
            (winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam", "SteamPath"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam", "InstallPath"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Valve\Steam", "InstallPath"),
        ):
            try:
                with winreg.OpenKey(hive, sub) as k:
                    roots.append(winreg.QueryValueEx(k, val)[0])
            except OSError:
                pass
    except ImportError:
        pass
    return roots


def _steam_library_steamapps_dirs() -> list:
    """All steamapps directories across every Steam library folder."""
    dirs = []

    def add(d):
        d = os.path.normpath(d)
        if os.path.isdir(d) and d.lower() not in (x.lower() for x in dirs):
            dirs.append(d)

    for root in _steam_roots():
        add(os.path.join(root, "steamapps"))
        vdf = os.path.join(root, "steamapps", "libraryfolders.vdf")
        try:
            with open(vdf, encoding="utf-8", errors="replace") as f:
                for m in _LIBPATH_RE.finditer(f.read()):
                    add(os.path.join(m.group(1).replace("\\\\", "\\"), "steamapps"))
        except OSError:
            pass
    return dirs


def _read_acf_fields(path: str):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            text = f.read()
    except OSError:
        return None, None
    n = _NAME_RE.search(text)
    d = _INSTALLDIR_RE.search(text)
    return (n.group(1) if n else None), (d.group(1) if d else None)


def _steam_games() -> dict:
    """installdir (lowercase) -> (game name, absolute install path). Refreshed every minute."""
    now = time.time()
    c = _steam_index_cache
    if c["games"] and now - c["ts"] < _STEAM_INDEX_TTL:
        return c["games"]
    games = {}
    try:
        for steamapps in _steam_library_steamapps_dirs():
            try:
                entries = os.listdir(steamapps)
            except OSError:
                continue
            for fn in entries:
                if not (fn.startswith("appmanifest_") and fn.endswith(".acf")):
                    continue
                name, installdir = _read_acf_fields(os.path.join(steamapps, fn))
                if name and installdir:
                    games[installdir.lower()] = (name, os.path.join(steamapps, "common", installdir))
    except Exception:
        pass
    c["ts"], c["games"] = now, games
    return games


def _steam_name_from_path(exe_path: str):
    """If exe lives under steamapps/common/<installdir>/..., return the Steam game name."""
    parts = os.path.normpath(exe_path).replace("\\", "/").split("/")
    lowered = [p.lower() for p in parts]
    for i in range(len(lowered) - 2):
        if lowered[i] == "steamapps" and lowered[i + 1] == "common":
            hit = _steam_games().get(lowered[i + 2])
            return hit[0] if hit else None
    return None


def _steam_name_from_exe_name(exe_name: str):
    """Fallback when the process path is hidden (anti-cheat): find which installed
    Steam game ships '<exe_name>.exe' (searched a few folders deep). Unique match only."""
    target = (exe_name + ".exe").lower()
    matches = set()
    for name, install_path in _steam_games().values():
        stack = [(install_path, 0)]
        seen = 0
        while stack and seen < 4000:
            d, depth = stack.pop()
            try:
                with os.scandir(d) as it:
                    for e in it:
                        seen += 1
                        if e.is_file(follow_symlinks=False):
                            if e.name.lower() == target:
                                matches.add(name)
                        elif depth < 3 and e.is_dir(follow_symlinks=False):
                            stack.append((e.path, depth + 1))
            except OSError:
                continue
        if len(matches) > 1:
            return None
    return next(iter(matches)) if len(matches) == 1 else None


def _resolve_app_name(exe_name, exe_path, win_label):
    """Best-effort 'real' application name. Falls back to the old exe/label behaviour."""
    if exe_name and exe_name.lower() in _KNOWN_EXE_NAMES:
        return _KNOWN_EXE_NAMES[exe_name.lower()]

    key = (exe_path or exe_name or "").lower()
    if key:
        hit = _NAME_CACHE.get(key)
        if hit and (hit[0] is not None or time.time() - hit[1] < _NAME_MISS_TTL):
            if hit[0] is not None:
                return hit[0]
        else:
            hit = None
    found = None
    try:
        if exe_path:
            found = _steam_name_from_path(exe_path)
            if not found and IS_WINDOWS:
                product, desc = _exe_version_strings(exe_path)
                for cand in (product, desc):
                    if not _is_generic_product(cand):
                        found = cand
                        break
        elif exe_name and exe_name.lower() not in _GENERIC_NAMES:
            found = _steam_name_from_exe_name(exe_name)
    except Exception:
        found = None
    if key:
        _NAME_CACHE[key] = (found, time.time())
    if found:
        return found
    return _best_name(exe_name, win_label)


def _cap(name: str) -> str:
    return name[0].upper() + name[1:] if name else name


class Plugin:
    _logger: logging.Logger
    _settings: SettingsManager
    _filters: list
    _excluded: set

    # -- Windows (Core Audio) ------------------------------------------------

    def _win_collect_playbacks(self) -> list:
        sessions: list = []
        pid_names = _build_pid_name_map()  # kernel snapshot, works for protected processes

        def reader(ctl2, pid):
            level = _session_volume(ctl2)
            if level is None:
                return None
            exe_name = pid_names.get(pid) or _proc_name(pid)
            exe_path = _proc_path(pid)
            win_label = _display_name(ctl2)
            legacy_name = _best_name(exe_name, win_label) or f"PID {pid}"
            name = _resolve_app_name(exe_name, exe_path, win_label) or legacy_name
            # Filters/excludes written against the old exe-based name keep working
            if any(f.fullmatch(name) or f.fullmatch(legacy_name) for f in self._filters):
                return None
            disp = _cap(name)
            inst_id = _session_instance_id(ctl2) or ""
            # Show win_label as subtitle only when it differs and adds real context
            subtitle = win_label if (win_label and win_label.lower() != name.lower()
                                     and win_label.lower() not in _GENERIC_NAMES) else None
            # List the underlying exe too when the friendly name differs (e.g. THE FINALS / Discovery)
            if not subtitle and exe_name and _norm_key(exe_name) != _norm_key(name):
                subtitle = exe_name
            sessions.append({
                "_legacy": _cap(legacy_name),
                "_disp": disp,
                "_inst": inst_id,
                "_subtitle": subtitle,
                "pid": pid,
                "volume": int(round(level * 100)),
            })
            return None

        _win_each_session(reader)

        # Disambiguate sessions that share a display name.
        from collections import defaultdict
        by_name: dict = defaultdict(list)
        for s in sessions:
            by_name[s["_disp"]].append(s)

        result = []
        for disp, group in by_name.items():
            if len(group) == 1:
                s = group[0]
                final_name = disp
                media_name = s["_subtitle"]
                legacy_excluded = s["_legacy"] in self._excluded
            else:
                # Multiple sessions for same app name - try to distinguish.
                subtitles = [s["_subtitle"] for s in group]
                for i, s in enumerate(group):
                    if s["_subtitle"] and subtitles.count(s["_subtitle"]) == 1:
                        # App set a unique display name - use it directly
                        final_name = _cap(s["_subtitle"])
                        media_name = None
                    else:
                        # Fall back to numbered labels (1-indexed)
                        final_name = f"{disp} ({i + 1})"
                        media_name = s["_subtitle"]
                    result.append({
                        "id": s["pid"],
                        "name": final_name,
                        "mediaName": media_name,
                        "volume": s["volume"],
                        "excluded": final_name in self._excluded,
                    })
                continue

            result.append({
                "id": s["pid"],
                "name": final_name,
                "mediaName": media_name,
                "volume": s["volume"],
                "excluded": final_name in self._excluded or legacy_excluded,
            })

        return sorted(result, key=lambda p: p["name"].lower())

    def _win_apply_volume(self, target_pid: int, level: float) -> bool:
        def setter(ctl2, pid):
            if pid != target_pid:
                return None
            return _session_set_volume(ctl2, level)

        results = _win_each_session(setter)
        return any(results)

    # -- public callable API (shared by both platforms) ----------------------

    async def get_playbacks(self) -> list:
        if IS_WINDOWS:
            try:
                playbacks = await asyncio.to_thread(self._win_collect_playbacks)
                self._logger.debug(f"Found {len(playbacks)} playbacks")
                return playbacks
            except Exception as e:
                self._logger.error(f"failed to get playbacks via Core Audio: {e}")
                return []

        proc = await self._create_subprocess_exec(self._pw_dump_bin)
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            self._logger.error(f"failed to get playbacks! pw-dump failed with code {proc.returncode}: {stderr.decode()}\n{stdout.decode()}")
            return []

        pw_dump = json.loads(stdout.decode())
        found_playbacks = []
        for node in pw_dump:
            if node.get("type") != "PipeWire:Interface:Node":
                continue

            info = node.get("info", {})
            props = info.get("props", {})
            if props.get("media.class") != "Stream/Output/Audio":
                continue

            if props.get("application.process.binary", "").lower() == "steamwebhelper" and props.get("application.name", "").lower() == "chromium":
                name = "Steam"
            else:
                name = (props.get("node.description")
                        or props.get("node.nick")
                        or props.get("application.name")
                        or props.get("node.name"))
            if not name or any(_filter.fullmatch(name) for _filter in self._filters):
                continue

            media_name = props.get("media.name", "")
            if media_name.lower() in [name.lower(), "playback", "playback stream", "output"]:
                media_name = None
            if not media_name and props.get("pipewire.client.access") == "flatpak":
                media_name = props.get("pipewire.access.portal.app_id")

            params_props = info.get("params", {}).get("Props", [])
            if len(params_props) == 0:
                continue
            volumes = params_props[0].get("channelVolumes", [])
            if len(volumes) == 0:
                continue
            volume = volumes[0]
            if props.get("client.api") == "pipewire-pulse": # convert pulse-audio cubic scaling to linear
                max_vol = 1.0 + round(self._settings.getSetting("boostLimit", 0) / 100, 2)
                volume = round(max(0.0, min(max_vol, volume ** (1/3))), 2)

            disp = name[0].upper() + name[1:]
            found_playbacks.append({
                "id": node["id"],
                "name": disp,
                "mediaName": media_name,
                "volume": int(volume * 100),
                "excluded": disp in self._excluded
            })

        self._logger.debug(f"Found {len(found_playbacks)} playbacks")
        return sorted(
            found_playbacks,
            key=lambda playback: (playback["name"] == "Steam", -playback["id"])
        )

    async def set_volume(self, id: int, volume: int):
        if IS_WINDOWS:
            volume = max(0, min(100, volume))
            try:
                ok = await asyncio.to_thread(self._win_apply_volume, id, volume / 100)
            except Exception as e:
                self._logger.error(f"failed to set volume of {id} via Core Audio: {e}")
                return False
            if ok:
                self._logger.info(f"Set volume of playback {id} to {volume}")
            else:
                self._logger.error(f"failed to set volume of {id}: no matching audio session")
            return ok

        volume = max(0, min(100 + self._settings.getSetting("boostLimit", 0), volume))
        vol_str = f"{volume / 100:.2f}"
        proc = await self._create_subprocess_exec(self._wpctl_bin, "set-volume", str(id), vol_str)
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            self._logger.error(f"failed to set volume of {id}! wpctl failed with code {proc.returncode}: {stderr.decode()}\n{stdout.decode()}")
            return False

        self._logger.info(f"Set volume of playback {id} to {vol_str}")
        return True

    async def get_settings(self):
        return {
            "filters": self._settings.getSetting("filters", []),
            "boostLimit": self._settings.getSetting("boostLimit", 0),
            "excludedApps": self._settings.getSetting("excludedApps", []),
        }

    async def save_settings(self, settings: dict):
        compiled_filters = []
        for _filter in settings["filters"]:
            try:
                compiled_filters.append(re.compile(_filter))
            except re.error:
                return False

        self._settings.setSetting("filters", settings["filters"])
        self._filters = compiled_filters
        self._settings.setSetting("boostLimit", settings["boostLimit"])
        if "excludedApps" in settings:
            self._excluded = set(settings["excludedApps"])
            self._settings.setSetting("excludedApps", sorted(self._excluded))
        self._settings.commit()

        return True

    async def set_excluded(self, name: str, excluded: bool):
        """Hide (or unhide) a single app from the mixer by its display name."""
        apps = set(self._settings.getSetting("excludedApps", []))
        if excluded:
            apps.add(name)
        else:
            apps.discard(name)
        self._excluded = apps
        self._settings.setSetting("excludedApps", sorted(apps))
        self._settings.commit()
        self._logger.info(f"{'Hid' if excluded else 'Restored'} app '{name}'")
        return True

    async def reset_volumes(self):
        playbacks = await self.get_playbacks()
        for playback in playbacks:
            await self.set_volume(playback["id"], 100)

    async def _main(self):
        self._logger = decky.logger
        self._settings = SettingsManager(name="settings", settings_directory=decky.DECKY_PLUGIN_SETTINGS_DIR)
        self._filters = []
        self._excluded = set(self._settings.getSetting("excludedApps", []))

        for _filter in self._settings.getSetting("filters", []):
            try:
                self._filters.append(re.compile(_filter))
            except re.error as e:
                self._logger.error(f"Failed to compile filter '{_filter}': {e}")

        if IS_WINDOWS:
            self._logger.info("Volume Mixer running on Windows: using Core Audio (ctypes/COM) backend")
            return

        import shutil
        import os as _os
        from helpers import get_user_id  # type: ignore

        self._pw_dump_bin = shutil.which("pw-dump") or ""
        if not self._pw_dump_bin:
            raise Exception("pw-dump not found in PATH, plugin cannot work without it")
        self._wpctl_bin = shutil.which("wpctl") or ""
        if not self._wpctl_bin:
            raise Exception("wpctl not found in PATH, plugin cannot work without it")
        self._logger.info(f"found pw-dump at {self._pw_dump_bin} and wpctl at {self._wpctl_bin}")

        self._xdg_runtime_dir = _os.environ.get("XDG_RUNTIME_DIR") or ""
        if not self._xdg_runtime_dir:
            self._xdg_runtime_dir = f"/run/user/{get_user_id()}"
            self._logger.info(f"XDG_RUNTIME_DIR is not set, using {self._xdg_runtime_dir}")
        else:
            self._logger.info(f"found XDG_RUNTIME_DIR={self._xdg_runtime_dir}")

    async def _unload(self):
        pass

    def _create_subprocess_exec(self, *args, **kwargs) -> Coroutine[Any, Any, Process]:
        return asyncio.create_subprocess_exec(
            *args, **kwargs,
            env={**os.environ, "XDG_RUNTIME_DIR": self._xdg_runtime_dir},
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
