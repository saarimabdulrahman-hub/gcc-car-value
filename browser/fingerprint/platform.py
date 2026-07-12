"""Platform consistency rules."""

# OS → platform string (navigator.platform)
OS_PLATFORM = {
    "Windows": "Win32",
    "macOS": "MacIntel",
    "Linux": "Linux x86_64",
}

# OS → architecture
OS_ARCH = {
    "Windows": "x64",
    "macOS": "x64",
    "Linux": "x64",
}


def platform_for_os(os_name: str) -> str:
    return OS_PLATFORM.get(os_name, "Win32")


def arch_for_os(os_name: str) -> str:
    return OS_ARCH.get(os_name, "x64")
