# nexus/constants.py

import platform

system = platform.system()

# --- Coherent platform selection ---

if system == "Darwin":
    platform_part = "Macintosh; Intel Mac OS X 10_15_7"

elif system == "Windows":
    platform_part = "Windows NT 10.0; Win64; x64"

elif system == "Linux":
    platform_part = "X11; Linux x86_64"

else:
    platform_part = "X11; Linux x86_64"

CHROME_UA = (
    f"Mozilla/5.0 ({platform_part}) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/140.0.0.0 Safari/537.36"
).encode()

FIREFOX_TOR_UA = (
    b"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) "
    b"Gecko/20100101 Firefox/115.0"
)

WEBKIT_UA = (
    b"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    b"AppleWebKit/605.1.15 (KHTML, like Gecko)"
)
