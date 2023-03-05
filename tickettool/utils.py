import discord  # isort:skip
import typing  # isort:skip
from redbot.core import commands  # isort:skip
from redbot.core.i18n import Translator  # isort:skip

import re

try:
    from emoji import UNICODE_EMOJI_ENGLISH as EMOJI_DATA  # emoji<2.0.0
except ImportError:
    from emoji import EMOJI_DATA  # emoji>=2.0.0


_ = Translator("ApplicationTool", __file__)


class utils:
    async def get_overwrites(self, application):
        config = await application.bot.get_cog("ApplicationTool").get_config(application.guild, application.panel)
        overwrites = {
            application.owner: discord.PermissionOverwrite(
                view_channel=True,
                read_messages=True,
                read_message_history=True,
                send_messages=True,
                attach_files=True,
            ),
            application.guild.me: discord.PermissionOverwrite(
                view_channel=True,
                read_messages=True,
                read_message_history=True,
                send_messages=True,
                attach_files=True,
                manage_messages=True,
                manage_channels=True,
                manage_permissions=True,
            ),
            application.guild.default_role: discord.PermissionOverwrite(
                view_channel=False,
            ),
        }
        if application.claim is not None:
            overwrites[application.claim] = discord.PermissionOverwrite(
                view_channel=True,
                read_messages=True,
                read_message_history=True,
                send_messages=True,
                attach_files=True,
            )
        if config["gov_role"] is not None:
            overwrites[config["gov_role"]] = discord.PermissionOverwrite(
                view_channel=True,
                read_messages=True,
                read_message_history=True,
                send_messages=True,
                attach_files=True,
                manage_messages=True,
            )
        if config["ia_role"] is not None:
            overwrites[config["ia_role"]] = discord.PermissionOverwrite(
                view_channel=True,
                read_messages=True,
                read_message_history=True,
                send_messages=True,
                attach_files=True,
            )
        if config["view_role"] is not None:
            overwrites[config["view_role"]] = discord.PermissionOverwrite(
                view_channel=True,
                read_messages=True,
                read_message_history=True,
                add_reactions=False,
            )
        return overwrites


class Emoji(commands.EmojiConverter):
    async def convert(
        self, ctx: commands.Context, argument: str
    ) -> typing.Union[discord.PartialEmoji, str]:
        argument = str(argument)
        argument = argument.strip("\N{VARIATION SELECTOR-16}")
        if argument in EMOJI_DATA:
            return argument
        return await super().convert(ctx, argument)


class EmojiLabelDescriptionValueConverter(discord.ext.commands.Converter):
    async def convert(
        self, ctx: commands.Context, argument: str
    ) -> typing.Tuple[str, typing.Union[discord.PartialEmoji, str]]:
        arg_split = re.split(r";|,|\||-", argument)
        try:
            try:
                emoji, label, description, value = arg_split
            except Exception:
                try:
                    emoji, label, description = arg_split
                    value = label
                except Exception:
                    emoji, label = arg_split
                    description = None
                    value = label
        except Exception:
            raise discord.ext.commands.BadArgument(
                _(
                    "Emoji Label must be An emoji followed by an string, and optionnaly by a description and a value (for rename application channel), separated by either `;`, `,`, `|`, or `-`."
                )
            )
        emoji = await Emoji().convert(ctx, emoji)
        label = str(label)
        return emoji, label, description, value
