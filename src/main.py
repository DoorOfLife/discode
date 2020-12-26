import discord
from discord.ext import commands
from interpreter import Interpreter

description = '''A bot that is actually the frontend of a script interpreter'''

intents = discord.Intents.default()

bot = commands.Bot(command_prefix='$', description=description, intents=intents)


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.command(description='Execute instructions')
async def exec(ctx, script_id: str, input_id: str):
    # reference to script post, and input post is needed
    # then we must fetch the contents of these
    script_src = await ctx.fetch_message(script_id)
    param_src = await ctx.fetch_message(input_id)
    interpret = Interpreter()

    output = interpret.execute(script_src.content, param_src.content)

    await ctx.send(output)


bot.run('NzkyMTI1ODE4NTA3MTAwMTgy.X-ZKqA.hW5Gdk9TqTrUwN-a7egUmpxxI5s')  # remember to remove this before pushing!!
