from __future__ import print_function
from discord.ext import commands
import discord


class Voting(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client
        super().__init__()

    @commands.hybrid_command(name="poll")
    async def poll(self, ctx: commands.Context, option1: str, option2: str, option3: str=None, option4: str=None, option5: str=None, option6: str=None, option7: str=None, option8: str=None, option9: str=None):
        emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣','8️⃣','9️⃣']
        items = [option1, option2, option3, option4, option5, option6, option7, option8, option9]
        items = list(filter(None, items))
        # Format string
        items_text = ''
        for n in range(len(items)):
            items_text += f"{emojis[n]} - {items[n]}\n"
        # Send Message
        sent_message = await ctx.send(f'> <@{str(ctx.author.id)}> has initiated a poll!\n{items_text}')
        # Add Reactions
        for i in emojis[:len(items)]:
            await sent_message.add_reaction(i)
            
    @commands.hybrid_command(name="vote")
    async def vote(self, ctx: commands.Context, question: str):
        # Send message
        sent_message = await ctx.send(f'> <@{str(ctx.author.id)}> has initiated a vote! \n{question}')
        # React
        await sent_message.add_reaction(r"<:PositiveOne:880321561884753941>")
        await sent_message.add_reaction(r"<:NeutralOne:880321613235630101>")
        await sent_message.add_reaction(r"<:NegativeOne:880321676846440451>")

# Setup Function          
async def setup(client: commands.Bot) -> None:
    await client.add_cog(Voting(client))