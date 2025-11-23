import random
import disnake
from disnake.ext import commands
import os
import json


class GoodCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # project root (…/sokudo)
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.mhr_path = os.path.join(project_root, "mhr.json")

        # pre-set affirmations
        self.affirmations = [
            "You are capable of amazing things.",
            "Believe in yourself and all that you are.",
            "You are stronger than you think.",
            "Every day is a second chance.",
            "You are worthy of all the good things in life.",
            "You are enough just as you are.",
            "Your potential is endless.",
            "You are doing your best, and that's enough.",
            "You have the power to create change.",
            "You are loved, you are valued, you are important.",
            "You are resilient, brave, and strong.",
            "You are appreciated more than you know.",
            "You are growing and becoming your best self.",
        ]

    @commands.Cog.listener()
    async def on_ready(self):
        print("GoodCog is ready")

    # /affirmation (prefix command – type /affirmation as a message)
    @commands.command()
    async def affirmation(self, ctx):
        affirmation = random.choice(self.affirmations)
        await ctx.send(affirmation)

    # /mhr (prefix command – type /mhr india, /mhr singapore, etc.)
    @commands.command()
    async def mhr(self, ctx, *, nation: str = "singapore"):
        try:
            with open(self.mhr_path, "r", encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            await ctx.send("⚠️ mhr.json not found on the server.")
            return

        query = nation.lower().strip()
        title = "Mental Health Resources in "
        description = "Here are some mental health resources you can use in "

        for country_name, info in data.items():
            aliases = [a.lower() for a in info.get("Aliases", [])]
            if query == country_name.lower() or query in aliases:
                title += country_name
                description += country_name

                datab = info["Data"]
                for name, value in datab.items():
                    description += f"\n**{name}**\n{value}\n"

                embed = disnake.Embed(
                    title=title,
                    description=description,
                    color=0xff87d4
                )
                embed.set_footer(
                    text="If you are in immediate danger, please contact your local emergency number."
                )
                await ctx.send(embed=embed)
                return

        await ctx.send(
            f"Sorry, I don't have data for **{nation}** yet. "
            f"Available countries: {', '.join(data.keys())}"
        )


def setup(bot):
    bot.add_cog(GoodCog(bot))
