# nexus/tor.py

import os
import socket
import shutil
import subprocess
import time

from stem.control import Controller


# ---------------- CONFIG ----------------

TOR_SOCKS_PORT = 9052
TOR_CONTROL_PORT = 9051

LAST_NEWNYM = 0
NEWNYM_INTERVAL = 15  # seconds (safer)

TOR_READY = False


# ---------------- CORE ----------------

def _tor_running_ok():
    try:
        s = socket.create_connection(("127.0.0.1", TOR_SOCKS_PORT), timeout=2)
        s.close()
        return True
    except:
        return False


def _tor_port_open(port):
    try:
        s = socket.create_connection(("127.0.0.1", port), timeout=1)
        s.close()
        return True
    except:
        return False


def _find_tor_binary():
    tor_path = shutil.which("tor")

    if not tor_path:
        candidates = [
            "/opt/homebrew/bin/tor",
            "/usr/local/bin/tor",
            "/usr/bin/tor",
        ]
        for path in candidates:
            if os.path.isfile(path) and os.access(path, os.X_OK):
                tor_path = path
                break

    if not tor_path:
        raise RuntimeError("Tor binary not found")

    return tor_path


def _kill_existing_tor():
    pkill_bin = shutil.which("pkill") or "/usr/bin/pkill"

    try:
        subprocess.run(
            [pkill_bin, "-f", "tor"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False
        )
        time.sleep(0.5)
    except Exception as e:
        print("[Tor] pkill failed:", e)


# ---------------- PUBLIC API ----------------

def ensure_tor():
    """
    Start Tor if not already running.
    Blocks until BOTH SOCKS and CONTROL ports are ready.
    """

    global TOR_READY

    # ✅ If already running correctly → reuse
    if _tor_running_ok() and _tor_port_open(TOR_CONTROL_PORT):
        TOR_READY = True
        return None

    # 🔥 Kill stale instance if needed
    if _tor_port_open(TOR_SOCKS_PORT):
        print("[Tor] Stale instance detected, cleaning up...")
        _kill_existing_tor()
        time.sleep(1.0)  # 🔥 give OS time to release port

    tor_bin = _find_tor_binary()

    # 🔥 FIX: use full environment (CRITICAL)
    safe_env = os.environ.copy()

    # Optional: ensure HOME exists (macOS safety)
    safe_env.setdefault("HOME", os.path.expanduser("~"))

    try:
        proc = subprocess.Popen(
            [
                tor_bin,
                "SocksPort", str(TOR_SOCKS_PORT),
                "ControlPort", str(TOR_CONTROL_PORT),
                "CookieAuthentication", "1",
            ],
            stdout=None,   # 🔥 show logs (for debugging)
            stderr=None,
            env=safe_env
        )

    except Exception as e:
        raise RuntimeError(f"Failed to start Tor: {e}")

    # 🔥 WAIT FOR FULL READINESS
    timeout = 30
    start = time.time()

    while time.time() - start < timeout:
        if _tor_running_ok() and _tor_port_open(TOR_CONTROL_PORT):
            TOR_READY = True
            print("[Tor] Fully ready (SOCKS + CONTROL)")
            return proc
        time.sleep(0.2)

    # ❌ Timeout → clean shutdown
    TOR_READY = False
    print("[Tor] Startup timeout, terminating...")

    try:
        proc.terminate()
        proc.wait(timeout=3)
    except:
        pass

    try:
        proc.kill()
    except:
        pass

    raise RuntimeError("Tor failed to start")


def tor_new_identity():
    """
    Safely request a new Tor circuit.
    No spam, no race conditions.
    """

    global LAST_NEWNYM, TOR_READY

    if not TOR_READY:
        return  # silent skip

    now = time.time()

    # 🔥 throttle
    if now - LAST_NEWNYM < NEWNYM_INTERVAL:
        return

    # 🔥 ensure control port is actually reachable
    for _ in range(10):
        if _tor_port_open(TOR_CONTROL_PORT):
            break
        time.sleep(0.2)
    else:
        print("[Tor] NEWNYM skipped (control not ready)")
        return

    try:
        with Controller.from_port(port=TOR_CONTROL_PORT) as c:
            c.authenticate()
            c.signal("NEWNYM")

            LAST_NEWNYM = now
            print("[Tor] New identity requested")

    except Exception as e:
        print("[Tor] NEWNYM failed:", e)
