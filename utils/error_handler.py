import traceback
import sys
from discord.ext import commands
from sentry_sdk import capture_exception, configure_scope
import json

"""
If you are not using this inside a cog, add the event decorator e.g:
@bot.event
async def on_command_error(ctx, error)
For examples of cogs see:
Rewrite:
https://gist.github.com/EvieePy/d78c061a4798ae81be9825468fe146be
Async:
https://gist.github.com/leovoel/46cd89ed6a8f41fd09c5
This example uses @rewrite version of the lib. For the async version of the lib, simply swap the places of ctx, and error.
e.g: on_command_error(self, error, ctx)
For a list of exceptions:
http://discordpy.readthedocs.io/en/rewrite/ext/commands/api.html#errors
"""


class CommandErrorHandler:
    def __init__(self, bot):
        self.bot = bot

    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command.
        ctx   : Context
        error : Exception"""

        # This prevents any commands with local handlers being handled here in on_command_error.
        if hasattr(ctx.command, 'on_error'):
            return

        ignored = (commands.CommandNotFound, commands.UserInputError)

        # Allows us to check for original exceptions raised and sent to CommandInvokeError.
        # If nothing is found. We keep the exception passed to on_command_error.
        original_error = getattr(error, 'original', error)

        # Anything in ignored will return and prevent anything happening.
        if isinstance(original_error, ignored):
            return

        elif isinstance(original_error, commands.DisabledCommand):
            return await ctx.send(f'{ctx.command} has been disabled.')

        elif isinstance(original_error, commands.NoPrivateMessage):
            try:
                return await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
            except:
                pass

        # All other Errors not returned come here... And we can just print the default TraceBack.
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(original_error), original_error, original_error.__traceback__, file=sys.stderr)

        with configure_scope() as scope:
            scope.set_extra('channel.name', ctx.channel.name)
            scope.set_extra('author.name', ctx.author.name)
            scope.set_extra('author.nick', ctx.author.nick)
            scope.set_extra('author.discriminator', ctx.author.discriminator)
            scope.set_extra('author.display_name', ctx.author.display_name)
            scope.set_extra('message.id', ctx.message.id)
            scope.set_extra('message.content', ctx.message.content)
            scope.set_extra('message.jump_url', ctx.message.jump_url)
            scope.set_extra('prefix', ctx.prefix)
            scope.set_extra('invoked_with', ctx.invoked_with)
        
        await (await ctx.author.create_dm()).send('Hmm, er is een fout opgetreden bij het uitvoeren van jouw commando.')

        capture_exception(original_error)
