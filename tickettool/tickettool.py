from .AAA3A_utils import CogsUtils, Settings  # isort:skip
from redbot.core import commands  # isort:skip
from redbot.core.i18n import Translator, cog_i18n  # isort:skip
from redbot.core.bot import Red  # isort:skip
import discord  # isort:skip
import typing  # isort:skip*

if CogsUtils().is_dpy2:
    from .AAA3A_utils import Buttons, Dropdown, Modal  # isort:skip
else:
    from dislash import (
        MessageInteraction,
        ResponseType,
    )  # isort:skip

import datetime
import io
from copy import deepcopy

import chat_exporter
from redbot.core import Config, modlog

from .settings import settings
from .application import Application

# Credits:
# General repo credits.
# Thanks to Yami for the technique in the init file of some cogs to load the interaction client only if it is not already loaded! Before this fix, when a user clicked a button, the actions would be run about 10 times, causing a huge spam and loop in the channel.

_ = Translator("ApplicationTool", __file__)

if CogsUtils().is_dpy2:
    from functools import partial

    hybrid_command = partial(commands.hybrid_command, with_app_command=False)
    hybrid_group = partial(commands.hybrid_group, with_app_command=False)
else:
    hybrid_command = commands.command
    hybrid_group = commands.group


@cog_i18n(_)
class ApplicationTool(settings, commands.Cog):
    """A cog to manage an application system!"""

    def __init__(self, bot: Red) -> None:
        self.bot: Red = bot

        self.config: Config = Config.get_conf(
            self,
            identifier=205192943327321000143939875896557571750,  # 937480369417
            force_registration=True,
        )
        self.CONFIG_SCHEMA: int = 2
        self.applicationtool_global: typing.Dict[str, typing.Optional[int]] = {
            "CONFIG_SCHEMA": None,
        }
        self.applicationtool_guild: typing.Dict[
            str,
            typing.Union[
                typing.Dict[
                    str,
                    typing.Dict[
                        str, typing.Union[bool, str, typing.Optional[str], typing.Optional[int]]
                    ],
                ],
                typing.Dict[
                    str, typing.Union[bool, str, typing.Optional[str], typing.Optional[int]]
                ],
            ],
        ] = {
            "panels": {},
            "default_profile_settings": {
                "enable": False,
                "logschannel": None,
                "category_open": None,
                "category_close": None,
                "gov_role": None,
                "ia_role": None,
                "application_role": None,
                "view_role": None,
                "ping_role": None,
                "nb_max": 5,
                "create_modlog": False,
                "close_on_leave": False,
                "create_on_react": False,
                "user_can_close": True,
                "delete_on_close": False,
                "color": 0x01D758,
                "audit_logs": False,
                "close_confirmation": False,
                "emoji_open": "⚔️",
                "emoji_close": "🔒",
                "dynamic_channel_name": "{owner_name}-application-from-{shortdate}",
                "last_nb": 0000,
                "custom_message": None,
                "embed_button": {
                    "title": "Open an application here!",
                    "description": _(
                        "To join Rome you may open an application by pressing the button below!.\n"
                    ),
                    "image": None,
                    "placeholder_dropdown": "Choose the reason to open an application.",
                    "rename_channel_dropdown": False,
                },
            },
            "applications": {},
            "buttons": {},
            "dropdowns": {},
        }
        self.config.register_global(**self.applicationtool_global)
        self.config.register_guild(**self.applicationtool_guild)

        self.cogsutils: CogsUtils = CogsUtils(cog=self)

        _settings: typing.Dict[
            str, typing.Dict[str, typing.Union[typing.List[str], typing.Any, str]]
        ] = {
            "enable": {"path": ["enable"], "converter": bool, "description": "Enable the system."},
            "logschannel": {
                "path": ["logschannel"],
                "converter": discord.TextChannel,
                "description": "Set the channel where the logs will be saved.",
            },
            "category_open": {
                "path": ["category_open"],
                "converter": discord.CategoryChannel,
                "description": "Set the category where the opened applications will be.",
            },
            "category_close": {
                "path": ["category_close"],
                "converter": discord.CategoryChannel,
                "description": "Set the category where the closed applications will be.",
            },
            "gov_role": {
                "path": ["gov_role"],
                "converter": discord.Role,
                "description": "Users with this role will have full permissions for applications, but will not be able to set up the cog.",
            },
            "ia_role": {
                "path": ["ia_role"],
                "converter": discord.Role,
                "description": "Users with this role will be able to participate and claim the application.",
            },
            "view_role": {
                "path": ["ia_role"],
                "converter": discord.Role,
                "description": "Users with this role will only be able to read messages from the application, but not send them.",
            },
            "ping_role": {
                "path": ["ping_role"],
                "converter": discord.Role,
                "description": "This role will be pinged automatically when the application is created, but does not give any additional permissions.",
            },
            "dynamic_channel_name": {
                "path": ["dynamic_channel_name"],
                "converter": str,
                "description": "Set the template that will be used to name the channel when creating an application.\n\n`{application_id}` - Application number\n`{owner_display_name}` - user's nick or name\n`{owner_name}` - user's name\n`{owner_id}` - user's id\n`{guild_name}` - guild's name\n`{guild_id}` - guild's id\n`{bot_display_name}` - bot's nick or name\n`{bot_name}` - bot's name\n`{bot_id}` - bot's id\n`{shortdate}` - mm-dd\n`{longdate}` - mm-dd-yyyy\n`{time}` - hh-mm AM/PM according to bot host system time\n\nIf, when creating the application, an error occurs with this name, another name will be used automatically.",
            },
            "nb_max": {
                "path": ["nb_max"],
                "converter": int,
                "description": "Sets the maximum number of open applications a user can have on the system at any one time (for the profile only).",
            },
            "custom_message": {
                "path": ["custom_message"],
                "converter": str,
                "description": "This message will be sent in the application channel when the application is opened.\n\n`{application_id}` - Application number\n`{owner_display_name}` - user's nick or name\n`{owner_name}` - user's name\n`{owner_id}` - user's id\n`{guild_name}` - guild's name\n`{guild_id}` - guild's id\n`{bot_display_name}` - bot's nick or name\n`{bot_name}` - bot's name\n`{bot_id}` - bot's id\n`{shortdate}` - mm-dd\n`{longdate}` - mm-dd-yyyy\n`{time}` - hh-mm AM/PM according to bot host system time",
                "style": 2,
            },
            "user_can_close": {
                "path": ["user_can_close"],
                "converter": bool,
                "description": "Can the author of the application, if he/she does not have a role set up for the system, close the application himself?",
            },
            "close_confirmation": {
                "path": ["close_confirmation"],
                "converter": bool,
                "description": "Should the bot ask for confirmation before closing the application (deletion will necessarily have a confirmation)?",
            },
            "close_on_leave": {
                "path": ["close_on_leave"],
                "converter": bool,
                "description": "If a user leaves the server, will all their open applications be closed?\n\nIf the user then returns to the server, even if their application is still open, the bot will not automatically add them to the application.",
            },
            "delete_on_close": {
                "path": ["delete_on_close"],
                "converter": bool,
                "description": "Does closing the application directly delete it (with confirmation)?",
            },
            "modlog": {
                "path": ["create_modlog"],
                "converter": bool,
                "description": "Does the bot create an action in the bot modlog when an application is created?",
            },
            "audit_logs": {
                "path": ["audit_logs"],
                "converter": bool,
                "description": "On all requests to the Discord api regarding the application (channel modification), does the bot send the name and id of the user who requested the action as the reason?",
                "no_slash": True,
            },
            "create_on_react": {
                "path": ["create_on_react"],
                "converter": bool,
                "description": "Open an application when the reaction 🎟️ is set on any message on the server.",
                "no_slash": True,
            },
        }
        self.settings: Settings = Settings(
            bot=self.bot,
            cog=self,
            config=self.config,
            group=self.config.GUILD,
            settings=_settings,
            global_path=["panels"],
            use_profiles_system=True,
            can_edit=True,
            commands_group=self.configuration,
        )

    async def cog_load(self):
        await self.edit_config_schema()
        await self.settings.add_commands()
        if self.cogsutils.is_dpy2:
            await self.load_buttons()

    async def edit_config_schema(self):
        CONFIG_SCHEMA = await self.config.CONFIG_SCHEMA()
        if CONFIG_SCHEMA is None:
            CONFIG_SCHEMA = 1
            await self.config.CONFIG_SCHEMA(CONFIG_SCHEMA)
        if CONFIG_SCHEMA == self.CONFIG_SCHEMA:
            return
        if CONFIG_SCHEMA == 1:
            guild_group = self.config._get_base_group(self.config.GUILD)
            async with guild_group.all() as guilds_data:
                _guilds_data = deepcopy(guilds_data)
                for guild in _guilds_data:
                    if "settings" not in _guilds_data[guild]:
                        continue
                    if "main" in _guilds_data[guild].get("panels", []):
                        continue
                    if "panels" not in guilds_data[guild]:
                        guilds_data[guild]["panels"] = {}
                    guilds_data[guild]["panels"]["main"] = self.config._defaults[
                        self.config.GUILD
                    ]["default_profile_settings"]
                    for key, value in _guilds_data[guild]["settings"].items():
                        guilds_data[guild]["panels"]["main"][key] = value
                    del guilds_data[guild]["settings"]
            CONFIG_SCHEMA = 2
            await self.config.CONFIG_SCHEMA.set(CONFIG_SCHEMA)
        if CONFIG_SCHEMA < self.CONFIG_SCHEMA:
            CONFIG_SCHEMA = self.CONFIG_SCHEMA
            await self.config.CONFIG_SCHEMA.set(CONFIG_SCHEMA)
        self.log.info(
            f"The Config schema has been successfully modified to {self.CONFIG_SCHEMA} for the {self.qualified_name} cog."
        )

    async def load_buttons(self) -> None:
        try:
            view = Buttons(
                timeout=None,
                buttons=[
                    {
                        "style": 2,
                        "label": _("Open Application"),
                        "emoji": "⚔️",
                        "custom_id": "create_application_button",
                        "disabled": False,
                    }
                ],
                function=self.on_button_interaction,
                infinity=True,
            )
            self.bot.add_view(view)
            self.cogsutils.views.append(view)
            view = Buttons(
                timeout=None,
                buttons=[
                    {
                        "style": 2,
                        "label": _("Close"),
                        "emoji": "🔒",
                        "custom_id": "close_application_button",
                        "disabled": False,
                    },
                    {
                        "style": 2,
                        "label": _("Claim"),
                        "emoji": "🙋‍♂️",
                        "custom_id": "claim_application_button",
                        "disabled": False,
                    },
                ],
                function=self.on_button_interaction,
                infinity=True,
            )
            self.bot.add_view(view)
            self.cogsutils.views.append(view)
        except Exception as e:
            self.log.error(f"The Buttons View could not be added correctly.", exc_info=e)
        all_guilds = await self.config.all_guilds()
        for guild in all_guilds:
            for dropdown in all_guilds[guild]["dropdowns"]:
                try:
                    view = Dropdown(
                        timeout=None,
                        placeholder=_("Choose the reason for open an application."),
                        options=[
                            {
                                "label": reason_option["label"],
                                "value": reason_option.get("value", reason_option["label"]),
                                "description": reason_option.get("description", None),
                                "emoji": reason_option["emoji"],
                                "default": False,
                            }
                            for reason_option in all_guilds[guild]["dropdowns"][dropdown]
                        ],
                        function=self.on_dropdown_interaction,
                        infinity=True,
                        custom_id="create_application_dropdown",
                    )
                    self.bot.add_view(view, message_id=int((str(dropdown).split("-"))[1]))
                    self.cogsutils.views.append(view)
                except Exception as e:
                    self.log.error(
                        f"The Dropdown View could not be added correctly for the {guild}-{dropdown} message.",
                        exc_info=e,
                    )

    async def get_config(self, guild: discord.Guild, panel: str) -> typing.Dict[str, typing.Any]:
        config = await self.config.guild(guild).panels.get_raw(panel)
        for key, value in self.config._defaults[Config.GUILD]["default_profile_settings"].items():
            if key not in config:
                config[key] = value
        if config["logschannel"] is not None:
            config["logschannel"] = guild.get_channel(config["logschannel"])
        if config["category_open"] is not None:
            config["category_open"] = guild.get_channel(config["category_open"])
        if config["category_close"] is not None:
            config["category_close"] = guild.get_channel(config["category_close"])
        if config["gov_role"] is not None:
            config["gov_role"] = guild.get_role(config["gov_role"])
        if config["ia_role"] is not None:
            config["ia_role"] = guild.get_role(config["ia_role"])
        if config["application_role"] is not None:
            config["application_role"] = guild.get_role(config["application_role"])
        if config["view_role"] is not None:
            config["view_role"] = guild.get_role(config["view_role"])
        if config["ping_role"] is not None:
            config["ping_role"] = guild.get_role(config["ping_role"])
        for key, value in self.config._defaults[self.config.GUILD][
            "default_profile_settings"
        ].items():
            if key not in config:
                config[key] = value
        if len(config["embed_button"]) == 0:
            config["embed_button"] = self.config._defaults[self.config.GUILD][
                "default_profile_settings"
            ]["embed_button"]
        else:
            for key, value in self.config._defaults[self.config.GUILD]["default_profile_settings"][
                "embed_button"
            ].items():
                if key not in config:
                    config[key] = value
        return config

    async def get_application(self, channel: discord.TextChannel) -> Application:
        config = await self.config.guild(channel.guild).applications.all()
        if str(channel.id) in config:
            json = config[str(channel.id)]
        else:
            return None
        if "panel" not in json:
            json["panel"] = "main"
        application: Application = Application.from_json(json, self.bot, self)
        application.bot = self.bot
        application.cog = self
        application.guild = application.bot.get_guild(application.guild) or application.guild
        application.owner = application.guild.get_member(application.owner) or application.owner
        application.channel = application.guild.get_channel(application.channel) or application.channel
        application.claim = application.guild.get_member(application.claim) or application.claim
        application.created_by = application.guild.get_member(application.created_by) or application.created_by
        application.opened_by = application.guild.get_member(application.opened_by) or application.opened_by
        application.closed_by = application.guild.get_member(application.closed_by) or application.closed_by
        application.deleted_by = application.guild.get_member(application.deleted_by) or application.deleted_by
        application.renamed_by = application.guild.get_member(application.renamed_by) or application.renamed_by
        members = application.members
        application.members = []
        for m in members:
            application.members.append(channel.guild.get_member(m))
        if application.created_at is not None:
            application.created_at = datetime.datetime.fromtimestamp(application.created_at)
        if application.opened_at is not None:
            application.opened_at = datetime.datetime.fromtimestamp(application.opened_at)
        if application.closed_at is not None:
            application.closed_at = datetime.datetime.fromtimestamp(application.closed_at)
        if application.deleted_at is not None:
            application.deleted_at = datetime.datetime.fromtimestamp(application.deleted_at)
        if application.renamed_at is not None:
            application.renamed_at = datetime.datetime.fromtimestamp(application.renamed_at)
        if application.first_message is not None:
            application.first_message = application.channel.get_partial_message(application.first_message)
        return application

    async def get_audit_reason(
        self,
        guild: discord.Guild,
        panel: str,
        author: typing.Optional[discord.Member] = None,
        reason: typing.Optional[str] = None,
    ) -> str:
        if reason is None:
            reason = _("Action taken for the application system.")
        config = await self.get_config(guild, panel)
        if author is None or not config["audit_logs"]:
            return f"{reason}"
        else:
            return f"{author.name} ({author.id}) - {reason}"

    async def get_embed_important(
        self, application, more: bool, author: discord.Member, title: str, description: str
    ) -> discord.Embed:
        config = await self.get_config(application.guild, application.panel)
        actual_color = config["color"]
        actual_thumbnail = config["thumbnail"]
        embed: discord.Embed = discord.Embed()
        embed.title = f"{title}"
        embed.description = f"{description}"
        embed.set_thumbnail(url=actual_thumbnail)
        embed.color = actual_color
        embed.timestamp = datetime.datetime.now(tz=datetime.timezone.utc)
        embed.set_author(
            name=author,
            url=author.display_avatar if self.cogsutils.is_dpy2 else author.avatar_url,
            icon_url=author.display_avatar if self.cogsutils.is_dpy2 else author.avatar_url,
        )
        embed.set_footer(
            text=application.guild.name,
            icon_url=application.guild.icon or ""
            if self.cogsutils.is_dpy2
            else application.guild.icon_url or "",
        )
        embed.add_field(inline=True, name=_("Application ID:"), value=f"[{application.panel}] {application.id}")
        embed.add_field(
            inline=True,
            name=_("Owned by:"),
            value=f"{application.owner.mention} ({application.owner.id})"
            if not isinstance(application.owner, int)
            else f"<@{application.owner}> ({application.owner})",
        )
        embed.add_field(
            inline=True,
            name=_("Channel:"),
            value=f"{application.channel.mention} - {application.channel.name} ({application.channel.id})",
        )
        if more:
            if application.closed_by is not None:
                embed.add_field(
                    inline=False,
                    name=_("Closed by:"),
                    value=f"{application.closed_by.mention} ({application.closed_by.id})"
                    if not isinstance(application.closed_by, int)
                    else f"<@{application.closed_by}> ({application.closed_by})",
                )
            if application.deleted_by is not None:
                embed.add_field(
                    inline=True,
                    name=_("Deleted by:"),
                    value=f"{application.deleted_by.mention} ({application.deleted_by.id})"
                    if not isinstance(application.deleted_by, int)
                    else f"<@{application.deleted_by}> ({application.deleted_by})",
                )
            if application.closed_at:
                embed.add_field(
                    inline=False,
                    name=_("Closed at:"),
                    value=f"{application.closed_at}",
                )
        embed.add_field(inline=False, name=_("Reason:"), value=f"{application.reason}")
        return embed

    async def get_embed_action(self, application, author: discord.Member, action: str) -> discord.Embed:
        config = await self.get_config(application.guild, application.panel)
        actual_color = config["color"]
        embed: discord.Embed = discord.Embed()
        embed.title = _("Application [{application.panel}] {application.id} - Action taken").format(application=application)
        embed.description = f"{action}"
        embed.color = actual_color
        embed.timestamp = datetime.datetime.now(tz=datetime.timezone.utc)
        embed.set_author(
            name=author,
            url=author.display_avatar if self.cogsutils.is_dpy2 else author.avatar_url,
            icon_url=author.display_avatar if self.cogsutils.is_dpy2 else author.avatar_url,
        )
        embed.set_footer(
            text=application.guild.name,
            icon_url=application.guild.icon or ""
            if self.cogsutils.is_dpy2
            else application.guild.icon_url or "",
        )
        embed.add_field(inline=False, name=_("Reason:"), value=f"{application.reason}")
        return embed

    async def check_limit(self, member: discord.Member, panel: str) -> bool:
        config = await self.get_config(member.guild, panel)
        data = await self.config.guild(member.guild).applications.all()
        to_remove = []
        count = 1
        for id in data:
            channel = member.guild.get_channel(int(id))
            if channel is not None:
                application: Application = await self.get_application(channel)
                if not application.panel == panel:
                    continue
                if application.created_by == member and application.status == "open":
                    count += 1
            else:
                to_remove.append(id)
        if not to_remove == []:
            data = await self.config.guild(member.guild).applications.all()
            for id in to_remove:
                del data[str(id)]
            await self.config.guild(member.guild).applications.set(data)
        if count > config["nb_max"]:
            return False
        else:
            return True

    async def create_modlog(
        self, application, action: str, reason: str
    ) -> typing.Optional[modlog.Case]:
        config = await self.get_config(application.guild, application.panel)
        if config["create_modlog"]:
            case = await modlog.create_case(
                application.bot,
                application.guild,
                application.created_at,
                action_type=action,
                user=application.created_by,
                moderator=None,
                reason=reason,
            )
            return case
        return

    def decorator(
        application_check: typing.Optional[bool] = False,
        status: typing.Optional[str] = None,
        application_owner: typing.Optional[bool] = False,
        gov_role: typing.Optional[bool] = False,
        ia_role: typing.Optional[bool] = False,
        application_role: typing.Optional[bool] = False,
        view_role: typing.Optional[bool] = False,
        guild_owner: typing.Optional[bool] = False,
        claim: typing.Optional[bool] = None,
        claim_staff: typing.Optional[bool] = False,
        members: typing.Optional[bool] = False,
    ) -> None:
        async def pred(ctx) -> bool:
            if application_check:
                application: Application = await ctx.bot.get_cog("ApplicationTool").get_application(ctx.channel)
                if application is None:
                    return False
                config = await ctx.bot.get_cog("ApplicationTool").get_config(application.guild, application.panel)
                if status is not None:
                    if not application.status == status:
                        return False
                if claim is not None:
                    if application.claim is not None:
                        check = True
                    elif application.claim is None:
                        check = False
                    if not check == claim:
                        return False
                if ctx.author.id in ctx.bot.owner_ids:
                    return True
                if application_owner:
                    if not isinstance(application.owner, int):
                        if ctx.author == application.owner:
                            if not ctx.command.name == "close" or config["user_can_close"]:
                                return True
                if gov_role and config["gov_role"] is not None:
                    if ctx.author in config["gov_role"].members:
                        return True
                if ia_role and config["ia_role"] is not None:
                    if ctx.author in config["ia_role"].members:
                        return True
                if application_role and config["application_role"] is not None:
                    if ctx.author in config["application_role"].members:
                        return True
                if view_role and config["view_role"] is not None:
                    if ctx.author in config["view_role"].members:
                        return True
                if guild_owner:
                    if ctx.author == ctx.guild.owner:
                        return True
                if claim_staff:
                    if ctx.author == application.claim:
                        return True
                if members:
                    if ctx.author in application.members:
                        return True
                return False
            return True

        return commands.check(pred)

    class PanelConverter(commands.Converter):
        async def convert(self, ctx: commands.Context, argument: str) -> str:
            if len(argument) > 10:
                raise commands.BadArgument(_("This panel does not exist."))
            panels = await ctx.bot.get_cog("ApplicationTool").config.guild(ctx.guild).panels()
            if argument.lower() not in panels:
                raise commands.BadArgument(_("This panel does not exist."))
            return argument.lower()

    @commands.guild_only()
    @hybrid_group(name="application")
    async def application(self, ctx: commands.Context) -> None:
        """Commands for using the application system."""

    @application.command(name="create")
    async def command_create(
        self,
        ctx: commands.Context,
        panel: typing.Optional[PanelConverter] = "main",
        *,
        reason: typing.Optional[str] = "No reason provided.",
    ) -> None:
        """Open an application."""
        panels = await self.config.guild(ctx.guild).panels()
        if panel not in panels:
            raise commands.UserFeedbackCheckFailure(_("This panel does not exist."))
        config = await self.get_config(ctx.guild, panel)
        category_open = config["category_open"]
        category_close = config["category_close"]
        if not config["enable"]:
            raise commands.UserFeedbackCheckFailure(
                _(
                    "The application system is not enabled on this server. Please ask an administrator of this server to use the `{ctx.prefix}applicationset` subcommands to configure it."
                ).format(ctx=ctx)
            )
        if category_open is None or category_close is None:
            raise commands.UserFeedbackCheckFailure(
                _(
                    "The category `open` or the category `close` have not been configured. Please ask an administrator of this server to use the `{ctx.prefix}applicationset` subcommands to configure it."
                ).format(ctx=ctx)
            )
        if not await self.check_limit(ctx.author, panel):
            limit = config["nb_max"]
            raise commands.UserFeedbackCheckFailure(
                _("Sorry. You have already reached the limit of applications you can open to join Rome.").format(
                    limit=limit
                )
            )
        if (
            not category_open.permissions_for(ctx.guild.me).manage_channels
            or not category_close.permissions_for(ctx.guild.me).manage_channels
        ):
            raise commands.UserFeedbackCheckFailure(
                _(
                    "The bot does not have `manage_channels` permission on the 'open' and 'close' categories to allow the application system to function properly. Please notify an administrator of this server."
                )
            )
        application: Application = Application.instance(ctx, panel, reason)
        await application.create()
        ctx.application = application

    @decorator(
        application_check=True,
        status=None,
        application_owner=True,
        gov_role=True,
        ia_role=False,
        application_role=False,
        view_role=False,
        guild_owner=True,
        claim=None,
        claim_staff=True,
        members=False,
    )
    @application.command(name="export")
    async def command_export(self, ctx: commands.Context) -> None:
        """Export all the messages of an existing application in html format.
        Please note: all attachments and user avatars are saved with the Discord link in this file.
        """
        application: Application = await self.get_application(ctx.channel)
        if application.cog.cogsutils.is_dpy2:
            transcript = await chat_exporter.export(
                channel=application.channel,
                limit=None,
                tz_info="UTC",
                guild=application.guild,
                bot=application.bot,
            )
        else:
            transcript = await chat_exporter.export(
                channel=application.channel, guild=application.guild, limit=None
            )
        if transcript is not None:
            file = discord.File(
                io.BytesIO(transcript.encode()),
                filename=f"transcript-application-{application.panel}-{application.id}.html",
            )
        message = await ctx.send(
            _(
                "Here is the html file of the transcript of all the messages in this application.\nPlease note: all attachments and user avatars are saved with the Discord link in this file."
            ),
            file=file,
        )
        embed = discord.Embed(
            title="Transcript Link",
            description=(
                f"[Click here to view the transcript.](https://mahto.id/chat-exporter?url={message.attachments[0].url})"
            ),
            colour=discord.Colour.green(),
        )
        await message.edit(embed=embed)

    @decorator(
        application_check=True,
        status="close",
        application_owner=True,
        gov_role=True,
        ia_role=False,
        application_role=False,
        view_role=False,
        guild_owner=True,
        claim=None,
        claim_staff=True,
        members=False,
    )
    @application.command(name="open")
    async def command_open(
        self, ctx: commands.Context, *, reason: typing.Optional[str] = "No reason provided."
    ) -> None:
        """Open an existing application."""
        application: Application = await self.get_application(ctx.channel)
        config = await ctx.bot.get_cog("ApplicationTool").get_config(application.guild, application.panel)
        if not config["enable"]:
            raise commands.UserFeedbackCheckFailure(
                _("The application system is not enabled on this server.")
            )
        application.reason = reason
        await application.open(ctx.author)

    @decorator(
        application_check=True,
        status="open",
        application_owner=True,
        gov_role=True,
        ia_role=True,
        application_role=False,
        view_role=False,
        guild_owner=True,
        claim=None,
        claim_staff=True,
        members=False,
    )
    @application.command(name="close")
    async def command_close(
        self,
        ctx: commands.Context,
        confirmation: typing.Optional[bool] = None,
        *,
        reason: typing.Optional[str] = _("No reason provided."),
    ) -> None:
        """Close an existing application."""
        application: Application = await self.get_application(ctx.channel)
        config = await self.get_config(application.guild, application.panel)
        if config["delete_on_close"]:
            await self.command_delete(ctx, confirmation=confirmation, reason=reason)
            return
        if confirmation is None:
            config = await self.get_config(application.guild, application.panel)
            confirmation = not config["close_confirmation"]
        if not confirmation:
            embed: discord.Embed = discord.Embed()
            embed.title = _("Do you really want to close the application {application.id}?").format(
                application=application
            )
            embed.color = config["color"]
            embed.set_author(
                name=ctx.author.name,
                url=ctx.author.display_avatar if self.cogsutils.is_dpy2 else ctx.author.avatar_url,
                icon_url=ctx.author.display_avatar
                if self.cogsutils.is_dpy2
                else ctx.author.avatar_url,
            )
            response = await self.cogsutils.ConfirmationAsk(ctx, embed=embed)
            if not response:
                return
        application.reason = reason
        await application.close(ctx.author)

    @decorator(
        application_check=True,
        status=None,
        application_owner=True,
        gov_role=True,
        ia_role=True,
        application_role=False,
        view_role=False,
        guild_owner=True,
        claim=None,
        claim_staff=True,
        members=False,
    )
    @application.command(name="rename")
    async def command_rename(
        self,
        ctx: commands.Context,
        new_name: str,
        *,
        reason: typing.Optional[str] = _("No reason provided."),
    ) -> None:
        """Rename an existing application."""
        application: Application = await self.get_application(ctx.channel)
        application.reason = reason
        await application.rename(new_name, ctx.author)

    @decorator(
        application_check=True,
        status=None,
        application_owner=False,
        gov_role=True,
        ia_role=False,
        application_role=False,
        view_role=False,
        guild_owner=True,
        claim=None,
        claim_staff=True,
        members=False,
    )
    @application.command(name="delete")
    async def command_delete(
        self,
        ctx: commands.Context,
        confirmation: typing.Optional[bool] = False,
        *,
        reason: typing.Optional[str] = _("No reason provided."),
    ) -> None:
        """Delete an existing application.
        If a log channel is defined, an html file containing all the messages of this application will be generated.
        (Attachments are not supported, as they are saved with their Discord link)
        """
        application: Application = await self.get_application(ctx.channel)
        config = await self.get_config(application.guild, application.panel)
        if not confirmation:
            embed: discord.Embed = discord.Embed()
            embed.title = _(
                "Do you really want to delete all the messages of the application {application.id}?"
            ).format(application=application)
            embed.description = _(
                "If a log channel is defined, an html file containing all the messages of this application will be generated. (Attachments are not supported, as they are saved with their Discord link)"
            )
            embed.color = config["color"]
            embed.set_author(
                name=ctx.author.name,
                url=ctx.author.display_avatar if self.cogsutils.is_dpy2 else ctx.author.avatar_url,
                icon_url=ctx.author.display_avatar
                if self.cogsutils.is_dpy2
                else ctx.author.avatar_url,
            )
            response = await self.cogsutils.ConfirmationAsk(ctx, embed=embed)
            if not response:
                return
        application.reason = reason
        await application.delete(ctx.author)

    @decorator(
        application_check=True,
        status="open",
        application_owner=False,
        gov_role=True,
        ia_role=True,
        application_role=False,
        view_role=False,
        guild_owner=True,
        claim=False,
        claim_staff=False,
        members=False,
    )
    @application.command(name="claim")
    async def command_claim(
        self,
        ctx: commands.Context,
        member: typing.Optional[discord.Member] = None,
        *,
        reason: typing.Optional[str] = _("No reason provided."),
    ) -> None:
        """Claim an existing application."""
        application: Application = await self.get_application(ctx.channel)
        application.reason = reason
        if member is None:
            member = ctx.author
        await application.claim_application(member, ctx.author)

    @decorator(
        application_check=True,
        status=None,
        application_owner=False,
        gov_role=True,
        ia_role=False,
        application_role=False,
        view_role=False,
        guild_owner=True,
        claim=True,
        claim_staff=True,
        members=False,
    )
    @application.command(name="unclaim")
    async def command_unclaim(
        self, ctx: commands.Context, *, reason: typing.Optional[str] = _("No reason provided.")
    ) -> None:
        """Unclaim an existing application."""
        application: Application = await self.get_application(ctx.channel)
        application.reason = reason
        await application.unclaim_application(application.claim, ctx.author)

    @decorator(
        application_check=True,
        status="open",
        application_owner=True,
        gov_role=True,
        ia_role=False,
        application_role=False,
        view_role=False,
        guild_owner=True,
        claim=None,
        claim_staff=False,
        members=False,
    )
    @application.command(name="owner")
    async def command_owner(
        self,
        ctx: commands.Context,
        new_owner: discord.Member,
        *,
        reason: typing.Optional[str] = _("No reason provided."),
    ) -> None:
        """Change the owner of an existing application."""
        application: Application = await self.get_application(ctx.channel)
        application.reason = reason
        if new_owner is None:
            new_owner = ctx.author
        await application.change_owner(new_owner, ctx.author)

    @decorator(
        application_check=True,
        status="open",
        application_owner=True,
        gov_role=True,
        ia_role=False,
        application_role=False,
        view_role=False,
        guild_owner=True,
        claim=None,
        claim_staff=True,
        members=False,
    )
    @application.command(name="add")
    async def command_add(
        self,
        ctx: commands.Context,
        members: commands.Greedy[discord.Member],
        reason: typing.Optional[str] = _("No reason provided."),
    ) -> None:
        """Add a member to an existing application."""
        application: Application = await self.get_application(ctx.channel)
        application.reason = reason
        members = [member for member in members]
        await application.add_member(members, ctx.author)

    @decorator(
        application_check=True,
        status=None,
        application_owner=True,
        gov_role=True,
        ia_role=False,
        application_role=False,
        view_role=False,
        guild_owner=True,
        claim=None,
        claim_staff=True,
        members=False,
    )
    @application.command(name="remove")
    async def command_remove(
        self,
        ctx: commands.Context,
        members: commands.Greedy[discord.Member],
        reason: typing.Optional[str] = _("No reason provided."),
    ) -> None:
        """Remove a member to an existing application."""
        application: Application = await self.get_application(ctx.channel)
        application.reason = reason
        members = [member for member in members]
        await application.remove_member(members, ctx.author)

    if CogsUtils().is_dpy2:

        async def on_button_interaction(
            self, view: Buttons, interaction: discord.Interaction
        ) -> None:
            permissions = interaction.channel.permissions_for(interaction.user)
            if not permissions.read_messages and not permissions.send_messages:
                return
            permissions = interaction.channel.permissions_for(interaction.guild.me)
            if not permissions.read_messages and not permissions.read_message_history:
                return
            if (
                not interaction.response.is_done()
                and not interaction.data["custom_id"] == "create_application_button"
            ):
                await interaction.response.defer(ephemeral=True)
            if interaction.data["custom_id"] == "create_application_button":
                buttons = await self.config.guild(interaction.guild).buttons.all()
                if f"{interaction.message.channel.id}-{interaction.message.id}" in buttons:
                    panel = buttons[f"{interaction.message.channel.id}-{interaction.message.id}"][
                        "panel"
                    ]
                else:
                    panel = "main"
                modal = Modal(
                    title="Open ab Application",
                    inputs=[
                        {
                            "label": "Panel",
                            "style": discord.TextStyle.short,
                            "default": "main",
                            "max_length": 10,
                            "required": True,
                        },
                        {
                            "label": "Why are you creating this application?",
                            "style": discord.TextStyle.long,
                            "max_length": 1000,
                            "required": False,
                            "placeholder": "No reason provided.",
                        },
                    ],
                )
                await interaction.response.send_modal(modal)
                try:
                    interaction, inputs, function_result = await modal.wait_result()
                except TimeoutError:
                    return
                else:
                    if not interaction.response.is_done():
                        await interaction.response.defer(ephemeral=True)
                panel = inputs[0].value
                reason = inputs[1].value or ""
                panels = await self.config.guild(interaction.guild).panels()
                if panel not in panels:
                    await interaction.followup.send(
                        _("The panel for which this button was configured no longer exists."),
                        ephemeral=True,
                    )
                    return
                ctx = await self.cogsutils.invoke_command(
                    author=interaction.user,
                    channel=interaction.channel,
                    command=f"application create {panel}" + (f" {reason}" if not reason == "" else ""),
                )
                if not await ctx.command.can_run(
                    ctx, change_permission_state=True
                ):  # await discord.utils.async_all(check(ctx) for check in ctx.command.checks)
                    await interaction.followup.send(
                        _("You are not allowed to execute this command."), ephemeral=True
                    )
                else:
                    await interaction.followup.send(
                        _("You have chosen to open an application."), ephemeral=True
                    )
            if interaction.data["custom_id"] == "close_application_button":
                ctx = await self.cogsutils.invoke_command(
                    author=interaction.user, channel=interaction.channel, command="application close"
                )
                await interaction.followup.send(
                    _(
                        "You have chosen to close this application. If this is not done, you do not have the necessary permissions to execute this command."
                    ),
                    ephemeral=True,
                )
            if interaction.data["custom_id"] == "claim_application_button":
                ctx = await self.cogsutils.invoke_command(
                    author=interaction.user, channel=interaction.channel, command="application claim"
                )
                await interaction.followup.send(
                    _(
                        "You have chosen to claim this application. If this is not done, you do not have the necessary permissions to execute this command."
                    ),
                    ephemeral=True,
                )
            return

        async def on_dropdown_interaction(
            self, view: Dropdown, interaction: discord.Interaction, options: typing.List
        ) -> None:
            if len(options) == 0:
                if not interaction.response.is_done():
                    await interaction.response.defer()
                return
            permissions = interaction.channel.permissions_for(interaction.user)
            if not permissions.read_messages and not permissions.send_messages:
                return
            permissions = interaction.channel.permissions_for(interaction.guild.me)
            if not permissions.read_messages and not permissions.read_message_history:
                return
            if not interaction.response.is_done():
                await interaction.response.defer(ephemeral=True)
            dropdowns = await self.config.guild(interaction.guild).dropdowns()
            if f"{interaction.message.channel.id}-{interaction.message.id}" not in dropdowns:
                await interaction.followup.send(
                    _("This message is not in ApplicationTool config."), ephemeral=True
                )
                return
            panel = dropdowns[f"{interaction.message.channel.id}-{interaction.message.id}"][0].get(
                "panel", "main"
            )
            panels = await self.config.guild(interaction.guild).panels()
            if panel not in panels:
                await interaction.followup.send(
                    _("The panel for which this dropdown was configured no longer exists."),
                    ephemeral=True,
                )
                return
            option = [option for option in view.options if option.value == options[0]][0]
            reason = f"{option.emoji} - {option.label}"
            ctx = await self.cogsutils.invoke_command(
                author=interaction.user,
                channel=interaction.channel,
                command=f"application create {panel} {reason}",
            )
            if not await discord.utils.async_all(
                check(ctx) for check in ctx.command.checks
            ) or not hasattr(ctx, "application"):
                await interaction.followup.send(
                    _("You are not allowed to execute this command."), ephemeral=True
                )
                return
            config = await self.get_config(interaction.guild, panel)
            if config["embed_button"]["rename_channel_dropdown"]:
                try:
                    application: Application = await self.get_application(
                        ctx.guild.get_channel(ctx.application.channel)
                    )
                    if application is not None:
                        await application.rename(
                            new_name=f"{option.emoji}-{option.value}_{interaction.user.id}".replace(
                                " ", "-"
                            ),
                            author=None,
                        )
                except discord.HTTPException:
                    pass
            await interaction.followup.send(
                _("You have chosen to open an application with the reason `{reason}`.").format(
                    reason=reason
                ),
                ephemeral=True,
            )

    else:

        @commands.Cog.listener()
        async def on_button_click(self, inter: MessageInteraction) -> None:
            permissions = inter.channel.permissions_for(inter.author)
            if not permissions.read_messages and not permissions.send_messages:
                return
            permissions = inter.channel.permissions_for(inter.guild.me)
            if not permissions.read_messages and not permissions.read_message_history:
                return
            if not getattr(inter, "_sent", False) and not inter.expired:
                try:
                    await inter.respond(type=ResponseType.DeferredUpdateMessage, ephemeral=True)
                except discord.HTTPException:
                    pass
            if inter.clicked_button.custom_id == "create_application_button":
                buttons = await self.config.guild(inter.guild).buttons.all()
                if f"{inter.message.channel.id}-{inter.message.id}" in buttons:
                    panel = buttons[f"{inter.message.channel.id}-{inter.message.id}"]["panel"]
                else:
                    panel = "main"
                panels = await self.config.guild(inter.guild).panels()
                if panel not in panels:
                    await inter.followup(
                        _("The panel for which this button was configured no longer exists."),
                        ephemeral=True,
                    )
                    return
                ctx = await self.cogsutils.invoke_command(
                    author=inter.author, channel=inter.channel, command=f"application create {panel}"
                )
                if not await ctx.command.can_run(
                    ctx, change_permission_state=True
                ):  # await discord.utils.async_all(check(ctx) for check in ctx.command.checks)
                    await inter.followup(
                        _("You are not allowed to execute this command."), ephemeral=True
                    )
                else:
                    await inter.followup(_("You have chosen to open an application."), ephemeral=True)
            elif inter.clicked_button.custom_id == "close_application_button":
                ctx = await self.cogsutils.invoke_command(
                    author=inter.author, channel=inter.channel, command="application close"
                )
                await inter.followup(
                    _(
                        "You have chosen to close this application. If this is not done, you do not have the necessary permissions to execute this command."
                    ),
                    ephemeral=True,
                )
            elif inter.clicked_button.custom_id == "claim_application_button":
                ctx = await self.cogsutils.invoke_command(
                    author=inter.author, channel=inter.channel, command="application claim"
                )
                await inter.followup(
                    _(
                        "You have chosen to claim this application. If this is not done, you do not have the necessary permissions to execute this command."
                    ),
                    ephemeral=True,
                )
            return

        @commands.Cog.listener()
        async def on_dropdown(self, inter: MessageInteraction) -> None:
            if not inter.select_menu.custom_id == "create_application_dropdown":
                return
            if len(inter.select_menu.selected_options) == 0:
                return
            permissions = inter.channel.permissions_for(inter.author)
            if not permissions.read_messages and not permissions.send_messages:
                return
            permissions = inter.channel.permissions_for(inter.guild.me)
            if not permissions.read_messages and not permissions.read_message_history:
                return
            if not getattr(inter, "_sent", False) and not inter.expired:
                try:
                    await inter.respond(type=ResponseType.DeferredUpdateMessage, ephemeral=True)
                except discord.HTTPException:
                    pass
            dropdowns = await self.config.guild(inter.guild).dropdowns()
            if f"{inter.message.channel.id}-{inter.message.id}" not in dropdowns:
                await inter.followup(
                    _("This message is not in ApplicationTool Config."), ephemeral=True
                )
                return
            panel = dropdowns[f"{inter.message.channel.id}-{inter.message.id}"][0].get(
                "panel", "main"
            )
            panels = await self.config.guild(inter.guild).panels()
            if panel not in panels:
                await inter.followup(
                    _("The panel for which this button was configured no longer exists."),
                    ephemeral=True,
                )
                return
            option = inter.select_menu.selected_options[0]
            reason = f"{option.emoji} - {option.label}"
            ctx = await self.cogsutils.invoke_command(
                author=inter.author,
                channel=inter.channel,
                command=f"application create {panel} {reason}",
            )
            if not await discord.utils.async_all(
                check(ctx) for check in ctx.command.checks
            ) or not hasattr(ctx, "application"):
                await inter.followup(
                    _("You are not allowed to execute this command."), ephemeral=True
                )
                return
            config = await self.get_config(inter.guild, panel)
            if config["embed_button"]["rename_channel_dropdown"]:
                try:
                    application: Application = await self.get_application(
                        ctx.guild.get_channel(ctx.application.channel)
                    )
                    if application is not None:
                        await application.rename(
                            new_name=(
                                f"{option.emoji}-{option.value}_{inter.author.id}".replace(
                                    " ", "-"
                                )
                            )[:99],
                            author=None,
                        )
                except discord.HTTPException:
                    pass
            await inter.followup(
                _("You have chosen to open an application with the reason `{reason}`.").format(
                    reason=reason
                ),
                ephemeral=True,
            )

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent) -> None:
        if not payload.guild_id:
            return
        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        member = guild.get_member(payload.user_id)
        if member == guild.me or member.bot:
            return
        panel = "main"
        panels = await self.config.guild(guild).panels()
        if panel not in panels:
            return
        config = await self.get_config(guild, panel)
        if config["enable"]:
            if config["create_on_react"]:
                if str(payload.emoji) == str("🎟️"):
                    permissions = channel.permissions_for(member)
                    if not permissions.read_messages and not permissions.send_messages:
                        return
                    permissions = channel.permissions_for(guild.me)
                    if not permissions.read_messages and not permissions.read_message_history:
                        return
                    await self.cogsutils.invoke_command(
                        author=member, channel=channel, command="application create"
                    )
        return

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message) -> None:
        if message.guild is None:
            return
        config = await self.config.guild(message.guild).dropdowns.all()
        if f"{message.channel.id}-{message.id}" not in config:
            return
        del config[f"{message.channel.id}-{message.id}"]
        await self.config.guild(message.guild).dropdowns.set(config)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, old_channel: discord.abc.GuildChannel) -> None:
        data = await self.config.guild(old_channel.guild).applications.all()
        if str(old_channel.id) not in data:
            return
        try:
            del data[str(old_channel.id)]
        except KeyError:
            pass
        await self.config.guild(old_channel.guild).applications.set(data)
        return

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member) -> None:
        data = await self.config.guild(member.guild).applications.all()
        for channel in data:
            channel = member.guild.get_channel(int(channel))
            if channel is None:
                continue
            application: Application = await self.get_application(channel)
            config = await self.get_config(application.guild, application.panel)
            if config["close_on_leave"]:
                if (
                    getattr(application.owner, "id", application.owner) == member.id
                    and application.status == "open"
                ):
                    await application.close(application.guild.me)
        return
