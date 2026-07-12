"""Binary Validator — validate browser executables without launching them."""

import os
import sys
from browser.binaries.models import BrowserBinary, BinaryStatus, ValidationResult
from browser.binaries.version import VersionResolver


class BinaryValidator:
    """Validate browser binaries by checking existence, permissions, platform."""

    def validate(self, binary: BrowserBinary) -> ValidationResult:
        result = ValidationResult(binary=binary)
        errors = []

        # Exists
        result.executable_exists = os.path.isfile(binary.executable_path)
        if not result.executable_exists:
            errors.append(f"Executable not found: {binary.executable_path}")

        # Platform match
        result.platform_match = (binary.platform == sys.platform
                                or not binary.platform)
        if not result.platform_match:
            errors.append(
                f"Platform mismatch: binary={binary.platform}, host={sys.platform}"
            )

        # Architecture match
        from browser.binaries.discovery import _detect_arch
        host_arch = _detect_arch()
        result.arch_match = (binary.architecture == host_arch
                            or not binary.architecture)
        if not result.arch_match:
            errors.append(f"Arch mismatch: binary={binary.architecture}, host={host_arch}")

        # Version parseable
        result.version_parsed = VersionResolver.is_valid(binary.version)

        result.valid = (result.executable_exists and result.platform_match
                       and result.arch_match and not errors)
        result.errors = errors
        return result

    async def validate_and_update(self, binary: BrowserBinary) -> ValidationResult:
        """Validate and update the binary's status."""
        result = self.validate(binary)
        binary.status = BinaryStatus.VALID if result.valid else BinaryStatus.INVALID
        return result
