import asyncio
import praw
import discord
from discord.ext import commands


class Announcements:
    def __init__(self, bot, utils):
        self.bot = bot
        self.utils = utils

        if 'announcements' not in self.utils.settings:
            self.utils.settings['announcements'] = {}
        if 'client_id' not in self.utils.settings['announcements']:
            self.utils.settings['announcements']['client_id'] = None
        if 'client_secret' not in self.utils.settings['announcements']:
            self.utils.settings['announcements']['client_secret'] = None
        if 'announcement_channel' not in self.utils.settings['announcements']:
            self.utils.settings['announcements']['announcement_channel'] = None
        if 'vote_channel' not in self.utils.settings['announcements']:
            self.utils.settings['announcements']['vote_channel'] = None
        if 'media_channel' not in self.utils.settings['announcements']:
            self.utils.settings['announcements']['media_channel'] = None
        if 'entries' not in self.utils.settings['announcements']:
            self.utils.settings['announcements']['entries'] = []

        self.utils.save_settings()

        self.flairs_normal = {
                        'MOTIE': {'channel': 'announcement_channel', 'color': '50004F'},
                        'WETSVOORSTEL': {'channel': 'announcement_channel', 'color': 'E39088'},
                        'KAMERSTUK': {'channel': 'announcement_channel', 'color': '048ABF'},
                        'META': {'channel': 'announcement_channel', 'color': 'B9005C'},
                        'PARLEMENT': {'channel': 'announcement_channel', 'color': 'D8C50F'},
                        'DEBAT': {'channel': 'announcement_channel', 'color': 'CD392F'},
                        'VRAGENUUR': {'channel': 'announcement_channel', 'color': 'ADD4D6'}
                        }
        self.flairs_stemmingen = {
                        'EK STEMMING': {'channel': 'vote_channel', 'color': '7FD47F'},
                        'TK STEMMING': {'channel': 'vote_channel', 'color': '7FD47F'}
                        }
        self.flairs_resultaten = {
                        'UITSLAGEN': {'channel': 'vote_channel', 'color': '6E7B04'}
                        }
        self.channels = {
                         'vote_channel': self.utils.settings['announcements']['vote_channel'],
                         'announcement_channel': self.utils.settings['announcements']['announcement_channel'],
                         'media_channel': self.utils.settings['announcements']['media_channel']
                        }

        client_id = 'xBtJB0-uZBsEDQ'
        client_secret = 'gbcQeXIszJFAjjiY3JYP-ptedkQ'

        self.subreddit = 'rmtk'
        self.media_subreddit = 'rmtkmedia'

        self.entries = self.utils.settings['announcements']['entries']

        self.reddit = praw.Reddit(client_id=client_id,
                                  client_secret=client_secret,
                                  user_agent='Griffier/1.0')

        bot.loop.create_task(self.read_feeds())

    @commands.group(name='announcement')
    @commands.is_owner()
    async def announcement(self, context):
        '''Instellingen voor aankondigingen'''
        if not context.invoked_subcommand:
            await self.utils.send_cmd_help(context)

    @announcement.command(name='vote', aliases=['stemmingen'])
    async def set_vote_announcement(self, context, channel: discord.TextChannel):
        '''Stel een kanaal in waar de stemmingen moeten worden gedeeld'''
        self.utils.settings['announcements']['vote_channel'] = channel.id
        self.channels['vote_channel'] = self.utils.settings['announcements']['vote_channel']
        self.utils.save_settings()
        await context.message.add_reaction('\U0001F44D')

    @announcement.command(name='announcements', aliases=['mededelingen'])
    async def set_announcement(self, context, channel: discord.TextChannel):
        '''Stel een kanaal in waar de mededelingen moeten worden gedeeld'''
        self.utils.settings['announcements']['announcement_channel'] = channel.id
        self.channels['announcement_channel'] = self.utils.settings['announcements']['announcement_channel']
        self.utils.save_settings()
        await context.message.add_reaction('\U0001F44D')

    @announcement.command(name='media')
    async def set_media_announcement(self, context, channel: discord.TextChannel):
        '''Stel een kanaal in waar de media berichten moet worden gedeeld'''
        self.utils.settings['announcements']['media_channel'] = channel.id
        self.channels['media_channel'] = self.utils.settings['announcements']['media_channel']
        self.utils.save_settings()
        await context.message.add_reaction('\U0001F44D')

    async def read_feeds(self):
        await asyncio.sleep(10)
        while True:
            try:
                if self.channels['media_channel']:
                    for submission in self.reddit.subreddit(self.media_subreddit).new(limit=5):
                        if submission.id not in self.entries:
                            if submission.link_flair_text:
                                title = '[{}] {}'.format(submission.link_flair_text, submission.title)
                            else:
                                title = '{}'.format(submission.title)

                            shortlink = submission.shortlink

                            channel = self.bot.get_channel(self.channels['media_channel'])

                            self.entries.append(submission.id)
                            self.utils.settings['announcements']['entries'] = self.entries
                            self.utils.save_settings()

                            embed = discord.Embed(title=title,
                                                  url=shortlink,
                                                  color=discord.Color(int('6E7B04', 16)))

                            await channel.send(embed=embed)
                if self.channels['vote_channel'] and self.channels['media_channel']:
                    for submission in self.reddit.subreddit(self.subreddit).new(limit=5):
                        if submission.id not in self.entries:
                            if str(submission.link_flair_text) in self.flairs_normal:
                                shortlink = submission.shortlink
                                title = submission.title

                                title = title.split(':')
                                event = self.flairs_normal[str(submission.link_flair_text)]
                                channel = self.bot.get_channel(self.channels[event['channel']])
                                if len(title) > 1:
                                    title = '[{}] {}'.format(title[0], title[1])
                                else:
                                    title = title[0]
                                embed = discord.Embed(title=title,
                                                      url=shortlink,
                                                      color=discord.Color(int(event['color'], 16)))
                                await channel.send(embed=embed)

                                self.entries.append(submission.id)
                                self.utils.settings['announcements']['entries'] = self.entries
                                self.utils.save_settings()

                                await asyncio.sleep(2)
                            elif str(submission.link_flair_text) in self.flairs_stemmingen:
                                shortlink = submission.shortlink
                                title = submission.title

                                event = self.flairs_stemmingen[str(submission.link_flair_text)]
                                channel = self.bot.get_channel(self.channels[event['channel']])

                                if str(submission.link_flair_text) == 'EK STEMMING':
                                    embed = discord.Embed(title=title,
                                                          url=shortlink,
                                                          description="Er is een nieuwe stemming voor alle Eerste Kamerleden.",
                                                          color=discord.Color(int(event['color'], 16)))
                                    await channel.send(content="<@&488369937505845261>", embed=embed)
                                else:
                                    embed = discord.Embed(title=title,
                                                          url=shortlink,
                                                          description="Er is een nieuwe stemming voor alle Tweede Kamerleden.",
                                                          color=discord.Color(int(event['color'], 16)))
                                    await channel.send(content="<@&488369887824052227>", embed=embed)



                                self.entries.append(submission.id)
                                self.utils.settings['announcements']['entries'] = self.entries
                                self.utils.save_settings()

                                await asyncio.sleep(2)
                            elif str(submission.link_flair_text) in self.flairs_resultaten:
                                shortlink = submission.shortlink
                                title = submission.title

                                event = self.flairs_resultaten[str(submission.link_flair_text)]
                                channel = self.bot.get_channel(self.channels[event['channel']])

                                embed = discord.Embed(title=title,
                                                      url=shortlink,
                                                      color=discord.Color(int(event['color'], 16)))

                                await channel.send(embed=embed)

                                self.entries.append(submission.id)
                                self.utils.settings['announcements']['entries'] = self.entries
                                self.utils.save_settings()

                                await asyncio.sleep(2)
            except Exception:
                pass
            await asyncio.sleep(10)
