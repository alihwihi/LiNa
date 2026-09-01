import json
import os
from typing import Any

import httpx

from config.constants import DATA_URLS

# Global cache holds only the small, local stat data by default.
# Remote JSON (potentially large) is fetched on-demand via `fetch_remote`.
cache: dict[str, Any] = {}

# Simple bounded in-memory cache for at-most-one remote payload.
# This avoids unbounded global growth in memory-constrained environments.
_remote_cache: dict[str, Any] = {}
_MAX_REMOTE_CACHE = 1


async def load_data() -> None:
    """Load only small, local data at startup (avoid loading large remote JSONs).

    This keeps RAM usage predictable. Remote resources are fetched on demand
    with `fetch_remote` and are not accumulated indefinitely.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "..", "stat_ideal.json")

    try:
        with open(file_path, "r", encoding="utf-8") as handle:
            cache["stat_ideal"] = json.load(handle)
        print("Data stat_ideal berhasil dimuat dari:", file_path)
    except FileNotFoundError:
        print(f"File tidak ditemukan di: {file_path}")


async def fetch_remote(key: str) -> Any:
    """Fetch remote JSON for `key` on demand and return its parsed content.

    The function uses a tiny bounded cache (size=_MAX_REMOTE_CACHE) to avoid
    repeatedly downloading while also preventing unbounded memory growth.
    """
    if key in _remote_cache:
        return _remote_cache[key]

    url = DATA_URLS.get(key)
    if not url:
        raise KeyError(f"Unknown remote data key: {key}")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0)
            data = response.json()
        except Exception as exc:  # pragma: no cover - defensive fallback
            raise

    # Enforce tiny bounded cache to avoid holding many large objects in RAM.
    if len(_remote_cache) >= _MAX_REMOTE_CACHE:
        _remote_cache.pop(next(iter(_remote_cache)))
    _remote_cache[key] = data
    return data


def _stat_file_path() -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "..", "stat_ideal.json")


def get_stat_entry(entry_name: str) -> Any:
    """Return a single entry from the `stat_ideal.json` file without
    permanently loading the entire file into memory.

    Implementation notes:
    - If `ijson` is installed, this will stream-parse the JSON and stop when
      the requested top-level key is found (minimal memory usage).
    - Otherwise it falls back to loading the file into memory briefly and
      returning the requested entry, then clearing the temporary object so
      it can be garbage-collected.
    """
    # Fast path: if the small local stat is already in memory, use it.
    stat_map = cache.get("stat_ideal")
    if isinstance(stat_map, dict):
        return stat_map.get(entry_name)

    file_path = _stat_file_path()

    try:
        import ijson  # type: ignore

        with open(file_path, "rb") as fh:
            # kvitems yields (key, value) pairs for the top-level object.
            for key, value in ijson.kvitems(fh, ""):
                if key == entry_name:
                    return value
    except Exception:
        # If ijson is not installed or streaming failed, fall back.
        pass

    # Fallback: load the file briefly and extract the requested key.
    try:
        with open(file_path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
            result = data.get(entry_name)
        # Help GC by dropping the large temporary object immediately.
        del data
        return result
    except FileNotFoundError:
        return None
