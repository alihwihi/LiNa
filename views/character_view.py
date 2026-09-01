import discord
from discord.ui import Button, View
from typing import Any

from config.constants import HASHTAG
from utils.character_helpers import get_element_color


class CharacterView(View):
    def __init__(self, original_embed: discord.Embed, character_data: dict[str, Any]) -> None:
        # Use a short timeout to avoid keeping view objects and payloads in memory
        # indefinitely in constrained environments.
        super().__init__(timeout=120)
        self.original_embed = original_embed
        # Store only minimal identifiers instead of the full character payload.
        self.character_id = character_data.get("id")
        self.element_color = get_element_color(character_data.get("element"))
        self.setup_main_buttons()

    def get_spd_embed(self, interaction: discord.Interaction):
        user = interaction.user
        embed = discord.Embed(
            title="<a:blueflowers:1527326419510624387> SPD Breakpoint Guide <a:blueflowers:1527326419510624387>",
            color=discord.Color.green(),
        )
        embed.description = "Here is a SPD guide to maximizing the number of actions in a cycle:"
        embed.add_field(name="120 SPD", value=f"{HASHTAG} 2 turns in the 2nd cycle (Total of 1 bonus turn within 5 cycles).", inline=False)
        embed.add_field(name="134 SPD", value=f"{HASHTAG} 2 turns in the 1st and 4th cycle (Total of 2 bonus turns within 5 cycles).", inline=False)
        embed.add_field(name="143 SPD", value=f"{HASHTAG} 2 turns in the 1st and 3rd cycle (2 bonus turns within 5 cycles).", inline=False)
        embed.add_field(name="146 SPD", value=f"{HASHTAG} 2 turns in the 1st, 3rd, and 5th cycle (3 bonus turns within 5 cycles).", inline=False)
        embed.add_field(name="156 SPD", value=f"{HASHTAG} 2 turns in the 1st, 3rd, and 4th cycle (3 bonus turns within 5 cycles).", inline=False)
        embed.add_field(name="160 SPD", value=f"{HASHTAG} 2 turns in the 1st, 2nd, and 4th cycle (3 bonus turns within 5 cycles).", inline=False)
        embed.add_field(name="164 SPD", value=f"{HASHTAG} 2 turns in the 1st, 2nd, 4th, and 5th cycle (4 bonus turns within 5 cycles).", inline=False)
        embed.add_field(name="172 SPD", value=f"{HASHTAG} 2 turns in the 1st, 2nd, 3rd, and 5th cycle (4 bonus turns within 5 cycles).", inline=False)
        embed.add_field(name="178 SPD", value=f"{HASHTAG} 2 turns in the 1st, 2nd, 3rd, and 4th cycle (4 bonus turns within 5 cycles).", inline=False)
        embed.add_field(name="182 SPD", value=f"{HASHTAG} 2 turns in all 5 cycles.", inline=False)
        embed.add_field(name="200 SPD", value=f"{HASHTAG} 3 turns in the first cycle and 2 turns in the four remaining cycles.", inline=False)
        embed.add_field(name="", value="Data referenced from [Game8.co](https://game8.co/games/Honkai-Star-Rail/archives/438178)")
        embed.set_footer(text=f"Requested by {user.name}", icon_url=user.display_avatar.url)
        return embed

    def get_disclaimer_embed(self, interaction: discord.Interaction):
        user = interaction.user
        embed = discord.Embed(
            title="<a:exclamation:1527326776676716574> Disclaimer <a:exclamation:1527326776676716574>",
            description="Please read the following information carefully regarding the data provided:",
            color=discord.Color.red(),
        )

        embed.add_field(
            name="`Community-Driven Data`",
            value="The information presented is curated based on general consensus within the Honkai: Star Rail community meta. Please use these suggestions as a reference rather than a definitive guide.",
            inline=False,
        )
        embed.add_field(
            name="`Personalized Optimization`",
            value="Character building is highly subjective and varies depending on individual accounts. Factors such as Light Cone availability, team composition, and resource constraints play a significant role in determining the most effective build for your specific situation.",
            inline=False,
        )
        embed.set_footer(text=f"Requested by {user.name}", icon_url=user.display_avatar.url)
        return embed

    def setup_main_buttons(self):
        self.clear_items()
        self.add_item(Button(label="SPD Breakpoint Guide", style=discord.ButtonStyle.primary, custom_id="penjelasan"))
        self.add_item(Button(label="Disclaimer", style=discord.ButtonStyle.danger, custom_id="disclaimer"))

    def setup_back_button(self):
        self.clear_items()
        self.add_item(Button(label="Back", style=discord.ButtonStyle.secondary, custom_id="kembali"))

    def create_dynamic_embed(self, title, description):
        return discord.Embed(title=title, description=description, color=self.element_color)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        custom_id = interaction.data["custom_id"]

        if custom_id == "penjelasan":
            embed = self.get_spd_embed(interaction)
            self.setup_back_button()
            await interaction.response.edit_message(embed=embed, view=self)
        elif custom_id == "disclaimer":
            embed = self.get_disclaimer_embed(interaction)
            self.setup_back_button()
            await interaction.response.edit_message(embed=embed, view=self)
        elif custom_id == "kembali":
            self.setup_main_buttons()
            await interaction.response.edit_message(embed=self.original_embed, view=self)

        return True
