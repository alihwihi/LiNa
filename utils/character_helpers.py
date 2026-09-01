from typing import Any

import discord


def get_element_color(element_name: str) -> discord.Color:
    mapping = {
        "Thunder": 0xA256E0,
        "Ice": 0x4FA9FF,
        "Fire": 0xF04747,
        "Wind": 0x42DBA2,
        "Quantum": 0x6E39E0,
        "Imaginary": 0xF5C744,
        "Physical": 0xC2C2C2,
    }
    return discord.Color(mapping.get(element_name, 0x3498DB))


def get_preview_url(char_id: Any) -> str:
    return f"https://raw.githubusercontent.com/Mar-7th/StarRailRes/master/image/character_preview/{char_id}.png"
