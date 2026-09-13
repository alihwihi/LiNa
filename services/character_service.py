from typing import Any, Optional

from config.constants import CHARACTER_ALIASES
from services.data_service import get_stat_entry


def normalize_character_input(name: str) -> tuple[str, str]:
    raw_input = name.strip().lower()
    normalized_input = CHARACTER_ALIASES.get(raw_input, raw_input)
    return raw_input, normalized_input


def resolve_character(input_name: str, chars_dict: dict[str, Any]) -> Optional[dict[str, Any]]:
    raw_input, normalized_input = normalize_character_input(input_name)

    karakter_api: Optional[dict[str, Any]] = None

    if "hunt" in normalized_input or "hm7" in raw_input:
        karakter_api = chars_dict.get("1224")
    elif "physical" in normalized_input or raw_input == "dmc":
        karakter_api = chars_dict.get("8001")
    elif "fire" in normalized_input or raw_input == "pmc":
        karakter_api = chars_dict.get("8003")
    elif "harmony" in normalized_input or raw_input == "hmc":
        karakter_api = chars_dict.get("8005")
    elif "remembrance" in normalized_input or raw_input == "rmc":
        karakter_api = chars_dict.get("8007")
    elif "elation" in normalized_input or raw_input == "emc":
        karakter_api = chars_dict.get("8009")
    elif normalized_input in ["march 7th (preservation)", "march 7th", "march"]:
        karakter_api = chars_dict.get("1001")

    if karakter_api is None:
        for _, char_data in chars_dict.items():
            nama_api_lower = char_data.get("name", "").lower()
            if normalized_input == nama_api_lower or (
                len(normalized_input) >= 4 and nama_api_lower.startswith(normalized_input)
            ):
                return char_data

    return karakter_api


def get_character_display_name(karakter_api: dict[str, Any]) -> str:
    if karakter_api.get("name") == "{NICKNAME}":
        path_name = karakter_api.get("path", "")
        return f"Trailblazer ({path_name})"
    return karakter_api.get("name", "")


def get_local_character_info(char_id_str: str, nama_asli_relic: str) -> Any:
    # Retrieve only the specific stat entry from disk (or from a small in-memory
    # cache) to avoid holding the full `stat_ideal.json` in RAM.
    if char_id_str == "1213":
        return get_stat_entry("DHIL")
    if char_id_str == "1414":
        return get_stat_entry("DHPT")
    if char_id_str == "1512":
        return get_stat_entry("Robin Summeretto")
    if char_id_str == "1305":
        return get_stat_entry("Dr. Ratio")
    if char_id_str == "1510":
        return get_stat_entry("Himeko Nova")
    if char_id_str == "1001":
        return get_stat_entry("March 7th")
    if char_id_str == "1224":
        return get_stat_entry("March Hunt")
    if char_id_str == "1508":
        return get_stat_entry("Rin Tohsaka")
    if char_id_str == "1506":
        return get_stat_entry("SW 99")
    if char_id_str == "1321":
        return get_stat_entry("The Dahlia")
    if char_id_str == "1513":
        return get_stat_entry("Aventurine Waveflair")
    if char_id_str == "1112":
        return get_stat_entry("Topaz")
    if char_id_str in ["8001", "8002"]:
        return get_stat_entry("Trailblazer (Physical)")
    if char_id_str in ["8003", "8004"]:
        return get_stat_entry("Trailblazer (Fire)")
    if char_id_str in ["8005", "8006"]:
        return get_stat_entry("Trailblazer (Harmony)")
    if char_id_str in ["8007", "8008"]:
        return get_stat_entry("Trailblazer (Remembrance)")
    if char_id_str in ["8009", "8010"]:
        return get_stat_entry("Trailblazer (Elation)")
    return get_stat_entry(nama_asli_relic.title())
