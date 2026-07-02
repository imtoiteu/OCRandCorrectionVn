from __future__ import annotations

from .base import CorrectionProvider

PROVIDER_NAMES = ["protonx", "mrlasdt", "bmd1905", "mock"]


def get_provider(name: str, **kwargs) -> CorrectionProvider:
    key = (name or "").strip().lower()
    if key in ("protonx", "proton", "px"):
        from .protonx_provider import ProtonxProvider
        return ProtonxProvider(**kwargs)
    if key in ("mrlasdt", "a"):
        from .mrlasdt_provider import MrlasdtProvider
        return MrlasdtProvider(**kwargs)
    if key in ("bmd1905", "bmd", "b"):
        from .bmd1905_provider import Bmd1905Provider
        return Bmd1905Provider(**kwargs)
    if key in ("mock", "noop", "dict"):
        from .mock_provider import MockProvider
        return MockProvider(**kwargs)
    raise ValueError(f"Unknown provider {name!r}. Choices: {', '.join(PROVIDER_NAMES)}")
