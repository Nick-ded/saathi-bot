from disnake.ext import commands
from .AI import AI


class AICog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        # just so you still see this in console
        print("AICog is ready")


def setup(bot):
    # add the main AI cog (with /mhr + mental health logic)
    bot.add_cog(AI(bot))
    # add this small cog only for the "AICog is ready" log
    bot.add_cog(AICog(bot))
