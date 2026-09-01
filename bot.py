import logging
import os
import json

import discord 
from discord import app_commands
import discord.ext.commands as commands
from dotenv import load_dotenv

from config.constants import LINE_EMOJI
from services.character_service import get_character_display_name, get_local_character_info, resolve_character
from services.data_service import cache, load_data, fetch_remote
from utils.character_helpers import get_element_color, get_preview_url
from views.character_view import CharacterView

load_dotenv()

token = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
# We only need message content for prefixed commands; keep other intents disabled
intents.message_content = True

bot = commands.Bot(command_prefix="D!", intents=intents)

def load_characters():
    try:
        with open("stat_ideal.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Peringatan: File stat_ideal.json tidak ditemukan!")
        return []

HSR_CHARACTERS = load_characters()

async def hsr_character_autocomplete(
    interaction: discord.Interaction,
    current: str
) -> list[app_commands.Choice[str]]:
    # Menyaring karakter yang mengandung teks yang diketik oleh pengguna
    return [
        app_commands.Choice(name=char, value=char.lower().replace(" ", "_"))
        for char in HSR_CHARACTERS
        if current.lower() in char.lower()
    ][:25]

@bot.event
async def on_ready() -> None:

    bot.tree.remove_command("active-dev-badge")
    # Load only small, local datasets at startup. Large remote JSONs are fetched
    # when needed (on-demand) to minimize RAM usage during startup.
    await load_data()
    try:
        synced = await bot.tree.sync()
        print(f"Berhasil meng-sync {len(synced)} Slash Command.")
    except Exception as e:
        print(f"Gagal meng-sync commands: {e}")
        
    print(f"Bot Sudah Aktif {bot.user.name}")


@bot.event
async def on_message(message: discord.Message) -> None:
    if message.author == bot.user:
        return

    await bot.process_commands(message)


@bot.tree.command(name="ping", description="Test command")
async def ping(ctx: commands.Context) -> None:
    await ctx.send("Pong!")


@bot.tree.command(name="hsr", description="Lihat panduan build karakter Honkai: Star Rail")
@app_commands.describe(nama_karakter="Ketik dan pilih karakter HSR")
@app_commands.autocomplete(nama_karakter=hsr_character_autocomplete)
async def hsr(interaction: discord.Interaction, *, nama_karakter: str) -> None:
    await interaction.response.defer()

    user = interaction.user
    avatar_url = user.avatar.url if user.avatar else user.default_avatar.url
    nama_karakter = nama_karakter.replace("_", " ").title()
    try:
        chars_dict = await fetch_remote("characters")
    except Exception:
        chars_dict = {}

    if not isinstance(chars_dict, dict):
        print(f"DEBUG: chars_dict bukan dict, tapi: {type(chars_dict)}")
        return await interaction.followup.send("Error: Database karakter belum dimuat dengan benar.")

    karakter_api = resolve_character(nama_karakter, chars_dict)
    if not karakter_api:
        return await interaction.followup.send(f"Karakter **{nama_karakter}** tidak ditemukan di database game.")

    nama_asli_relic = karakter_api.get("name", "")
    char_id_str = str(karakter_api.get("id"))
    nama_tampilan = get_character_display_name(karakter_api)
    # `get_local_character_info` now loads only the required stat from disk
    # on-demand to avoid holding the full `stat_ideal.json` in memory.
    info_lokal = get_local_character_info(char_id_str, nama_asli_relic)

    element_name = karakter_api.get("element")
    embed_color = get_element_color(element_name)

    embed = discord.Embed(
        title=f" <a:sparkles:1526910240581353604> {nama_tampilan} <a:sparkles:1526910240581353604>",
        color=embed_color,
    )

    char_id = karakter_api.get("id")
    if char_id:
        preview_url = get_preview_url(char_id)
        embed.set_thumbnail(url=preview_url)

    if info_lokal:
        embed.add_field(name="`Recommended Main Stats`", value="", inline=False)
        embed.add_field(name="👕 Body", value=info_lokal.get("body", "Data tidak tersedia"), inline=True)
        embed.add_field(name="🔮 Sphere", value=info_lokal.get("planar sphere", "Data tidak tersedia"), inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=True)
        embed.add_field(name="👟 Feet", value=info_lokal.get("feet", "Data tidak tersedia"), inline=True)
        embed.add_field(name="🪢 Link Rope", value=info_lokal.get("link rope", "Data tidak tersedia"), inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=True)
        embed.add_field(name="", value=f"{LINE_EMOJI}{LINE_EMOJI}{LINE_EMOJI}{LINE_EMOJI}{LINE_EMOJI}{LINE_EMOJI}{LINE_EMOJI}{LINE_EMOJI}{LINE_EMOJI}{LINE_EMOJI}", inline=False)
        embed.add_field(name="`Recommended Endgame Stats`", value=info_lokal.get("stats", "Data tidak tersedia"), inline=False)
        embed.add_field(name="", value=f"{LINE_EMOJI}{LINE_EMOJI}{LINE_EMOJI}{LINE_EMOJI}{LINE_EMOJI}{LINE_EMOJI}{LINE_EMOJI}{LINE_EMOJI}{LINE_EMOJI}{LINE_EMOJI}", inline=False)
        embed.add_field(name="`Recommended Light Cone`", value=info_lokal.get("lightcone", "Data tidak tersedia"), inline=False)
        embed.add_field(name="", value=f"{LINE_EMOJI}{LINE_EMOJI}{LINE_EMOJI}{LINE_EMOJI}{LINE_EMOJI}{LINE_EMOJI}{LINE_EMOJI}{LINE_EMOJI}{LINE_EMOJI}{LINE_EMOJI}", inline=False)
        embed.add_field(name="`Recommended Relic Set`", value=info_lokal.get("relic", "Data tidak tersedia"), inline=False)
        embed.add_field(name="", value=f"{LINE_EMOJI}{LINE_EMOJI}{LINE_EMOJI}{LINE_EMOJI}{LINE_EMOJI}{LINE_EMOJI}{LINE_EMOJI}{LINE_EMOJI}{LINE_EMOJI}{LINE_EMOJI}", inline=False)
        embed.add_field(name="`Recommended Ornament`", value=info_lokal.get("ornament", "Data tidak tersedia"), inline=False)
        embed.add_field(name="", value=f"{LINE_EMOJI}{LINE_EMOJI}{LINE_EMOJI}{LINE_EMOJI}{LINE_EMOJI}{LINE_EMOJI}{LINE_EMOJI}{LINE_EMOJI}{LINE_EMOJI}{LINE_EMOJI}", inline=False)
        embed.add_field(name="`Recommended Trace Order`", value=info_lokal.get("trace", "Data tidak tersedia"), inline=False)
        embed.set_footer(text=f"Requested by {user.name}", icon_url=avatar_url)
        embed.timestamp = interaction.created_at
    else:
        embed.add_field(name="Panduan", value="Data panduan untuk karakter ini belum tersedia.", inline=False)

    view = CharacterView(embed, karakter_api)
    await interaction.followup.send(embed=embed, view=view)


if __name__ == "__main__":
    bot.run(token)
