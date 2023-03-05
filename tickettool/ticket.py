from .AAA3A_utils import CogsUtils  # isort:skip
from redbot.core import commands  # isort:skip
from redbot.core.i18n import Translator  # isort:skip
from redbot.core.bot import Red  # isort:skip
import discord  # isort:skip
import typing  # isort:skip

# import typing_extensions  # isort:skip

if CogsUtils().is_dpy2:
    from .AAA3A_utils import Buttons  # isort:skip
else:
    from dislash import (
        ActionRow,
        Button,
        ButtonStyle,
    )  # isort:skip

import datetime
import io

import chat_exporter

from .utils import utils

_ = Translator("ApplicationTool", __file__)


class Application:
    """Representation of an application"""

    def __init__(
        self,
        bot,
        cog,
        id,
        owner,
        guild,
        channel,
        claim,
        created_by,
        opened_by,
        closed_by,
        deleted_by,
        renamed_by,
        members,
        created_at,
        opened_at,
        closed_at,
        deleted_at,
        renamed_at,
        status,
        reason,
        logs_messages,
        save_data,
        first_message,
        panel,
    ):
        self.bot: Red = bot
        self.cog: commands.Cog = cog
        self.id: int = id
        self.owner: discord.Member = owner
        self.guild: discord.Guild = guild
        self.channel: discord.TextChannel = channel
        self.claim: discord.Member = claim
        self.created_by: discord.Member = created_by
        self.opened_by: discord.Member = opened_by
        self.closed_by: discord.Member = closed_by
        self.deleted_by: discord.Member = deleted_by
        self.renamed_by: discord.Member = renamed_by
        self.members: typing.List[discord.Member] = members
        self.created_at: datetime.datetime = created_at
        self.opened_at: datetime.datetime = opened_at
        self.closed_at: datetime.datetime = closed_at
        self.deleted_at: datetime.datetime = deleted_at
        self.renamed_at: datetime.datetime = renamed_at
        self.status: str = status
        self.reason: str = reason
        self.logs_messages: bool = logs_messages
        self.save_data: bool = save_data
        self.first_message: discord.Message = first_message
        self.panel: str = panel

    @staticmethod
    def instance(
        ctx: commands.Context,
        panel: str,
        reason: typing.Optional[str] = _("Applicationm to join Rome."),
    ) -> typing.Any:  # typing_extensions.Self
        application: Application = Application(
            bot=ctx.bot,
            cog=ctx.cog,
            id=None,
            owner=ctx.author,
            guild=ctx.guild,
            channel=None,
            claim=None,
            created_by=ctx.author,
            opened_by=ctx.author,
            closed_by=None,
            deleted_by=None,
            renamed_by=None,
            members=[],
            created_at=datetime.datetime.now(),
            opened_at=None,
            closed_at=None,
            deleted_at=None,
            renamed_at=None,
            status="open",
            reason=reason,
            logs_messages=True,
            save_data=True,
            first_message=None,
            panel=panel,
        )
        return application

    @staticmethod
    def from_json(json: dict, bot: Red, cog: commands.Cog) -> typing.Any:  # typing_extensions.Self
        application: Application = Application(
            bot=bot,
            cog=cog,
            id=json["id"],
            owner=json["owner"],
            guild=json["guild"],
            channel=json["channel"],
            claim=json["claim"],
            created_by=json["created_by"],
            opened_by=json["opened_by"],
            closed_by=json["closed_by"],
            deleted_by=json["deleted_by"],
            renamed_by=json["renamed_by"],
            members=json["members"],
            created_at=json["created_at"],
            opened_at=json["opened_at"],
            closed_at=json["closed_at"],
            deleted_at=json["deleted_at"],
            renamed_at=json["renamed_at"],
            status=json["status"],
            reason=json["reason"],
            logs_messages=json["logs_messages"],
            save_data=json["save_data"],
            first_message=json["first_message"],
            panel=json["panel"],
        )
        return application

    async def save(application) -> typing.Dict[str, typing.Any]:
        if not application.save_data:
            return
        cog = application.cog
        guild = application.guild
        channel = application.channel
        application.bot = None
        application.cog = None
        if application.owner is not None:
            application.owner = int(getattr(application.owner, "id", application.owner))
        if application.guild is not None:
            application.guild = int(application.guild.id)
        if application.channel is not None:
            application.channel = int(application.channel.id)
        if application.claim is not None:
            application.claim = application.claim.id
        if application.created_by is not None:
            application.created_by = (
                int(application.created_by.id)
                if not isinstance(application.created_by, int)
                else int(application.created_by)
            )
        if application.opened_by is not None:
            application.opened_by = (
                int(application.opened_by.id)
                if not isinstance(application.opened_by, int)
                else int(application.opened_by)
            )
        if application.closed_by is not None:
            application.closed_by = (
                int(application.closed_by.id)
                if not isinstance(application.closed_by, int)
                else int(application.closed_by)
            )
        if application.deleted_by is not None:
            application.deleted_by = (
                int(application.deleted_by.id)
                if not isinstance(application.deleted_by, int)
                else int(application.deleted_by)
            )
        if application.renamed_by is not None:
            application.renamed_by = (
                int(application.renamed_by.id)
                if not isinstance(application.renamed_by, int)
                else int(application.renamed_by)
            )
        members = application.members
        application.members = []
        for m in members:
            application.members.append(int(m.id))
        if application.created_at is not None:
            application.created_at = float(datetime.datetime.timestamp(application.created_at))
        if application.opened_at is not None:
            application.opened_at = float(datetime.datetime.timestamp(application.opened_at))
        if application.closed_at is not None:
            application.closed_at = float(datetime.datetime.timestamp(application.closed_at))
        if application.deleted_at is not None:
            application.deleted_at = float(datetime.datetime.timestamp(application.deleted_at))
        if application.renamed_at is not None:
            application.renamed_at = float(datetime.datetime.timestamp(application.renamed_at))
        if application.first_message is not None:
            application.first_message = int(application.first_message.id)
        json = application.__dict__
        data = await cog.config.guild(guild).applications.all()
        data[str(channel.id)] = json
        await cog.config.guild(guild).applications.set(data)
        return data

    async def create(application) -> typing.Any:  # typing_extensions.Self
        config = await application.cog.get_config(application.guild, application.panel)
        logschannel = config["logschannel"]
        overwrites = await utils().get_overwrites(application)
        emoji_open = config["emoji_open"]
        ping_role = config["ping_role"]
        application.id = config["last_nb"] + 1
        reason = await application.cog.get_audit_reason(
            guild=application.guild,
            panel=application.panel,
            author=application.created_by,
            reason=_("Creating the application {application.id}.").format(application=application),
        )
        try:
            to_replace = {
                "application_id": str(application.id),
                "owner_display_name": application.owner.display_name,
                "owner_name": application.owner.name,
                "owner_id": str(application.owner.id),
                "guild_name": application.guild.name,
                "guild_id": application.guild.id,
                "bot_display_name": application.guild.me.display_name,
                "bot_name": application.bot.user.name,
                "bot_id": str(application.bot.user.id),
                "shortdate": application.created_at.strftime("%m-%d"),
                "longdate": application.created_at.strftime("%m-%d-%Y"),
                "time": application.created_at.strftime("%I-%M-%p"),
            }
            name = config["dynamic_channel_name"].format(**to_replace).replace(" ", "-")
            application.channel = await application.guild.create_text_channel(
                name,
                overwrites=overwrites,
                category=config["category_open"],
                topic=application.reason,
                reason=reason,
            )
        except (KeyError, AttributeError, discord.HTTPException):
            name = f"{emoji_open}-application-{application.id}"
            application.channel = await application.guild.create_text_channel(
                name,
                overwrites=overwrites,
                category=config["category_open"],
                topic=application.reason,
                reason=reason,
            )
        topic = _(
            "🎟️ Application ID: {application.id}\n"
            "🔥 Channel ID: {application.channel.id}\n"
            "🕵️ Application created by: @{application.created_by.display_name} ({application.created_by.id})\n"
            "☢️ Application reason: {application.reason}\n"
            "👥 Application claimed by: Nobody."
        ).format(application=application)
        await application.channel.edit(topic=topic)
        if config["create_modlog"]:
            await application.cog.create_modlog(application, "application_created", reason)
        if CogsUtils().is_dpy2:
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
                function=application.cog.on_button_interaction,
                infinity=True,
            )
        else:
            buttons = ActionRow(
                Button(
                    style=ButtonStyle.grey,
                    label=_("Close"),
                    emoji="🔒",
                    custom_id="close_application_button",
                    disabled=False,
                ),
                Button(
                    style=ButtonStyle.grey,
                    label=_("Claim"),
                    emoji="🙋‍♂️",
                    custom_id="claim_application_button",
                    disabled=False,
                ),
            )
        if ping_role is not None:
            optionnal_ping = f" ||{ping_role.mention}||"
        else:
            optionnal_ping = ""
        embed = await application.cog.get_embed_important(
            application,
            False,
            author=application.created_by,
            title=_("Welcome to Rome!"),
            description=_("Hello <@!{UserID}> and welcome to Rome! Please answer the following questions and an emplyee of <@&998658518758477954> will be with you shortly. \n1. Are you new to PnW? \n2. What was your previous alliance if you answered no to the first question? \n3. Do you owe money/resources to your previous alliance or any banks? \n4. Have you ever been kicked or asked to leave an alliance before? \n5. Do you agree to the membership agreement? \n6. Do you have any questions about Rome? \nLastly, please do the following things: `!verify [nation id]` `/verify nation_id: [nation id]` `/link nation: [nation link]`."),
        )
        if CogsUtils().is_dpy2:
            application.first_message = await application.channel.send(
                f"{application.created_by.mention}{optionnal_ping}",
                embed=embed,
                view=view,
                allowed_mentions=discord.AllowedMentions(users=True, roles=True),
            )
            application.cog.cogsutils.views.append(view)
        else:
            application.first_message = await application.channel.send(
                f"{application.created_by.mention}{optionnal_ping}",
                embed=embed,
                components=[buttons],
                allowed_mentions=discord.AllowedMentions(users=True, roles=True),
            )
        if config["custom_message"] is not None:
            try:
                embed: discord.Embed = discord.Embed()
                embed.title = "Custom Message"
                to_replace = {
                    "application_id": str(application.id),
                    "owner_display_name": application.owner.display_name,
                    "owner_name": application.owner.name,
                    "owner_id": str(application.owner.id),
                    "guild_name": application.guild.name,
                    "guild_id": application.guild.id,
                    "bot_display_name": application.guild.me.display_name,
                    "bot_name": application.bot.user.name,
                    "bot_id": str(application.bot.user.id),
                    "shortdate": application.created_at.strftime("%m-%d"),
                    "longdate": application.created_at.strftime("%m-%d-%Y"),
                    "time": application.created_at.strftime("%I-%M-%p"),
                }
                embed.description = config["custom_message"].format(**to_replace)
                await application.channel.send(embed=embed)
            except (KeyError, AttributeError, discord.HTTPException):
                pass
        if logschannel is not None:
            embed = await application.cog.get_embed_important(
                application,
                True,
                author=application.created_by,
                title=_("Application Created"),
                description=_("The application was created by {application.created_by}.").format(
                    application=application
                ),
            )
            await logschannel.send(
                _("Report on the creation of the application {application.id}.").format(application=application),
                embed=embed,
            )
        if config["application_role"] is not None:
            if application.owner:
                try:
                    await application.owner.add_roles(config["application_role"], reason=reason)
                except discord.HTTPException:
                    pass
        await application.cog.config.guild(application.guild).panels.set_raw(
            application.panel, "last_nb", value=application.id
        )
        await application.save()
        return application

    async def export(application) -> typing.Optional[discord.File]:
        if application.channel:
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
                transcript_file = discord.File(
                    io.BytesIO(transcript.encode()),
                    filename=f"transcript-application-{application.panel}-{application.id}.html",
                )
                return transcript_file
        return None

    async def open(
        application, author: typing.Optional[discord.Member] = None
    ) -> typing.Any:  # typing_extensions.Self
        config = await application.cog.get_config(application.guild, application.panel)
        reason = await application.cog.get_audit_reason(
            guild=application.guild,
            panel=application.panel,
            author=author,
            reason=_("Opening the application {application.id}.").format(application=application),
        )
        logschannel = config["logschannel"]
        emoji_open = config["emoji_open"]
        emoji_close = config["emoji_close"]
        application.status = "open"
        application.opened_by = author
        application.opened_at = datetime.datetime.now()
        application.closed_by = None
        application.closed_at = None
        new_name = f"{application.channel.name}"
        new_name = new_name.replace(f"{emoji_close}-", "", 1)
        new_name = f"{emoji_open}-{new_name}"
        await application.channel.edit(name=new_name, category=config["category_open"], reason=reason)
        if application.logs_messages:
            embed = await application.cog.get_embed_action(
                application, author=application.opened_by, action=_("Application Opened")
            )
            await application.channel.send(embed=embed)
            if logschannel is not None:
                embed = await application.cog.get_embed_important(
                    application,
                    True,
                    author=application.opened_by,
                    title=_("Application Opened"),
                    description=_("The application was opened by {application.opened_by}.").format(
                        application=application
                    ),
                )
                await logschannel.send(
                    _("Report on the close of the application {application.id}.").format(application=application),
                    embed=embed,
                )
        if application.first_message is not None:
            try:
                if CogsUtils().is_dpy2:
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
                        function=application.cog.on_button_interaction,
                        infinity=True,
                    )
                    application.first_message = await application.channel.fetch_message(
                        int(application.first_message.id)
                    )
                    await application.first_message.edit(view=view)
                else:
                    buttons = ActionRow(
                        Button(
                            style=ButtonStyle.grey,
                            label=_("Close"),
                            emoji="🔒",
                            custom_id="close_application_button",
                            disabled=False,
                        ),
                        Button(
                            style=ButtonStyle.grey,
                            label=_("Claim"),
                            emoji="🙋‍♂️",
                            custom_id="claim_application_button",
                            disabled=False,
                        ),
                    )
                    application.first_message = await application.channel.fetch_message(
                        int(application.first_message.id)
                    )
                    await application.first_message.edit(components=[buttons])
            except discord.HTTPException:
                pass
        await application.save()
        return application

    async def close(
        application, author: typing.Optional[discord.Member] = None
    ) -> typing.Any:  # typing_extensions.Self
        config = await application.cog.get_config(application.guild, application.panel)
        reason = await application.cog.get_audit_reason(
            guild=application.guild,
            panel=application.panel,
            author=author,
            reason=f"Closing the application {application.id}.",
        )
        logschannel = config["logschannel"]
        emoji_open = config["emoji_open"]
        emoji_close = config["emoji_close"]
        application.status = "close"
        application.closed_by = author
        application.closed_at = datetime.datetime.now()
        new_name = f"{application.channel.name}"
        new_name = new_name.replace(f"{emoji_open}-", "", 1)
        new_name = f"{emoji_close}-{new_name}"
        await application.channel.edit(name=new_name, category=config["category_close"], reason=reason)
        if application.logs_messages:
            embed = await application.cog.get_embed_action(
                application, author=application.closed_by, action="Application Closed"
            )
            await application.channel.send(embed=embed)
            if logschannel is not None:
                embed = await application.cog.get_embed_important(
                    application,
                    True,
                    author=application.closed_by,
                    title="Application Closed",
                    description=f"The application was closed by {application.closed_by}.",
                )
                await logschannel.send(
                    _("Report on the close of the application {application.id}."),
                    embed=embed,
                )
        if application.first_message is not None:
            try:
                if CogsUtils().is_dpy2:
                    view = Buttons(
                        timeout=None,
                        buttons=[
                            {
                                "style": 2,
                                "label": _("Close"),
                                "emoji": "🔒",
                                "custom_id": "close_application_button",
                                "disabled": True,
                            },
                            {
                                "style": 2,
                                "label": _("Claim"),
                                "emoji": "🙋‍♂️",
                                "custom_id": "claim_application_button",
                                "disabled": True,
                            },
                        ],
                        function=application.cog.on_button_interaction,
                        infinity=True,
                    )
                    application.first_message = await application.channel.fetch_message(
                        int(application.first_message.id)
                    )
                    await application.first_message.edit(view=view)
                else:
                    buttons = ActionRow(
                        Button(
                            style=ButtonStyle.grey,
                            label=_("Close"),
                            emoji="🔒",
                            custom_id="close_application_button",
                            disabled=True,
                        ),
                        Button(
                            style=ButtonStyle.grey,
                            label=_("Claim"),
                            emoji="🙋‍♂️",
                            custom_id="claim_application_button",
                            disabled=True,
                        ),
                    )
                    application.first_message = await application.channel.fetch_message(
                        int(application.first_message.id)
                    )
                    await application.first_message.edit(components=[buttons])
            except discord.HTTPException:
                pass
        await application.save()
        return application

    async def rename(
        application, new_name: str, author: typing.Optional[discord.Member] = None
    ) -> typing.Any:  # typing_extensions.Self
        reason = await application.cog.get_audit_reason(
            guild=application.guild,
            panel=application.panel,
            author=author,
            reason=_(
                "Renaming the application {application.id}. (`{application.channel.name}` to `{new_name}`)"
            ).format(application=application, new_name=new_name),
        )
        await application.channel.edit(name=new_name, reason=reason)
        if author is not None:
            application.renamed_by = author
            application.renamed_at = datetime.datetime.now()
            if application.logs_messages:
                embed = await application.cog.get_embed_action(
                    application,
                    author=application.renamed_by,
                    action=_("Application Renamed."),
                )
                await application.channel.send(embed=embed)
            await application.save()
        return application

    async def delete(
        application, author: typing.Optional[discord.Member] = None
    ) -> typing.Any:  # typing_extensions.Self
        config = await application.cog.get_config(application.guild, application.panel)
        logschannel = config["logschannel"]
        reason = await application.cog.get_audit_reason(
            guild=application.guild,
            panel=application.panel,
            author=author,
            reason=_("Deleting the application {application.id}.").format(application=application),
        )
        application.deleted_by = author
        application.deleted_at = datetime.datetime.now()
        if application.logs_messages:
            if logschannel is not None:
                embed = await application.cog.get_embed_important(
                    application,
                    True,
                    author=application.deleted_by,
                    title=_("Application Deleted"),
                    description=_("The application was deleted by {application.deleted_by}.").format(
                        application=application
                    ),
                )
                try:
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
                except AttributeError:
                    transcript = None
                if transcript is not None:
                    file = discord.File(
                        io.BytesIO(transcript.encode()),
                        filename=f"transcript-application-{application.id}.html",
                    )
                else:
                    file = None
                message = await logschannel.send(
                    _("Report on the deletion of the application {application.id}.").format(application=application),
                    embed=embed,
                    file=file,
                )
                embed = discord.Embed(
                    title="Transcript Link",
                    description=(
                        f"[Click here to view the transcript.](https://mahto.id/chat-exporter?url={message.attachments[0].url})"
                    ),
                    colour=discord.Colour.green(),
                )
                await logschannel.send(embed=embed)
        await application.channel.delete(reason=reason)
        data = await application.cog.config.guild(application.guild).applications.all()
        try:
            del data[str(application.channel.id)]
        except KeyError:
            pass
        await application.cog.config.guild(application.guild).applications.set(data)
        return application

    async def claim_application(
        application, member: discord.Member, author: typing.Optional[discord.Member] = None
    ) -> typing.Any:  # typing_extensions.Self
        config = await application.cog.get_config(application.guild, application.panel)
        reason = await application.cog.get_audit_reason(
            guild=application.guild,
            panel=application.panel,
            author=author,
            reason=_("Claiming the application {application.id}.").format(application=application),
        )
        if member.bot:
            raise commands.UserFeedbackCheckFailure(_("A bot cannot claim an application."))
        application.claim = member
        topic = _(
            "🎟️ Application ID: {application.id}\n"
            "🔥 Channel ID: {application.channel.id}\n"
            "🕵️ Application created by: @{application.created_by.display_name} ({application.created_by.id})\n"
            "☢️ Application reason: {application.reason}\n"
            "👥 Application claimed by: @{application.claim.display_name} (@{application.claim.id})."
        ).format(application=application)
        overwrites = application.channel.overwrites
        overwrites[member] = discord.PermissionOverwrite(
            attach_files=True,
            read_message_history=True,
            read_messages=True,
            send_messages=True,
            view_channel=True,
        )
        if config["ia_role"] is not None:
            overwrites[config["ia_role"]] = discord.PermissionOverwrite(
                attach_files=False,
                read_message_history=True,
                read_messages=True,
                send_messages=False,
                view_channel=True,
            )
        await application.channel.edit(topic=topic, overwrites=overwrites, reason=reason)
        if application.first_message is not None:
            try:
                if CogsUtils().is_dpy2:
                    view = Buttons(
                        timeout=None,
                        buttons=[
                            {
                                "style": 2,
                                "label": _("Close"),
                                "emoji": "🔒",
                                "custom_id": "close_application_button",
                                "disabled": False if application.status == "open" else True,
                            },
                            {
                                "style": 2,
                                "label": _("Claim"),
                                "emoji": "🙋‍♂️",
                                "custom_id": "claim_application_button",
                                "disabled": True,
                            },
                        ],
                        function=application.cog.on_button_interaction,
                        infinity=True,
                    )
                    application.first_message = await application.channel.fetch_message(
                        int(application.first_message.id)
                    )
                    await application.first_message.edit(view=view)
                else:
                    buttons = ActionRow(
                        Button(
                            style=ButtonStyle.grey,
                            label=_("Close"),
                            emoji="🔒",
                            custom_id="close_application_button",
                            disabled=False if application.status == "open" else True,
                        ),
                        Button(
                            style=ButtonStyle.grey,
                            label=_("Claim"),
                            emoji="🙋‍♂️",
                            custom_id="claim_application_button",
                            disabled=True,
                        ),
                    )
                    application.first_message = await application.channel.fetch_message(
                        int(application.first_message.id)
                    )
                    await application.first_message.edit(components=[buttons])
            except discord.HTTPException:
                pass
        await application.save()
        return application

    async def unclaim_application(
        application, member: discord.Member, author: typing.Optional[discord.Member] = None
    ) -> typing.Any:  # typing_extensions.Self
        config = await application.cog.get_config(application.guild, application.panel)
        reason = await application.cog.get_audit_reason(
            guild=application.guild,
            panel=application.panel,
            author=author,
            reason=_("Claiming the application {application.id}.").format(application=application),
        )
        application.claim = None
        topic = _(
            "🎟️ Application ID: {application.id}\n"
            "🔥 Channel ID: {application.channel.id}\n"
            "🕵️ Application created by: @{application.created_by.display_name} ({application.created_by.id})\n"
            "☢️ Application reason: {application.reason}\n"
            "👥 Application claimed by: Nobody."
        ).format(application=application)
        await application.channel.edit(topic=topic)
        if config["ia_role"] is not None:
            overwrites = application.channel.overwrites
            overwrites[config["ia_role"]] = discord.PermissionOverwrite(
                attach_files=True,
                read_message_history=True,
                read_messages=True,
                send_messages=True,
                view_channel=True,
            )
            await application.channel.edit(overwrites=overwrites, reason=reason)
        await application.channel.set_permissions(member, overwrite=None, reason=reason)
        if application.first_message is not None:
            try:
                if CogsUtils().is_dpy2:
                    view = Buttons(
                        timeout=None,
                        buttons=[
                            {
                                "style": 2,
                                "label": _("Close"),
                                "emoji": "🔒",
                                "custom_id": "close_application_button",
                                "disabled": False if application.status == "open" else True,
                            },
                            {
                                "style": 2,
                                "label": _("Claim"),
                                "emoji": "🙋‍♂️",
                                "custom_id": "claim_application_button",
                                "disabled": True,
                            },
                        ],
                        function=application.cog.on_button_interaction,
                        infinity=True,
                    )
                    application.first_message = await application.channel.fetch_message(
                        int(application.first_message.id)
                    )
                    await application.first_message.edit(view=view)
                else:
                    buttons = ActionRow(
                        Button(
                            style=ButtonStyle.grey,
                            label=_("Close"),
                            emoji="🔒",
                            custom_id="close_application_button",
                            disabled=False if application.status == "open" else True,
                        ),
                        Button(
                            style=ButtonStyle.grey,
                            label=_("Claim"),
                            emoji="🙋‍♂️",
                            custom_id="claim_application_button",
                            disabled=False,
                        ),
                    )
                    application.first_message = await application.channel.fetch_message(
                        int(application.first_message.id)
                    )
                    await application.first_message.edit(components=[buttons])
            except discord.HTTPException:
                pass
        await application.save()
        return application

    async def change_owner(
        application, member: discord.Member, author: typing.Optional[discord.Member] = None
    ) -> typing.Any:  # typing_extensions.Self
        config = await application.cog.get_config(application.guild, application.panel)
        reason = await application.cog.get_audit_reason(
            guild=application.guild,
            panel=application.panel,
            author=author,
            reason=_("Changing owner of the application {application.id}.").format(application=application),
        )
        if member.bot:
            raise commands.UserFeedbackCheckFailure(
                _("You cannot transfer ownership of an application to a bot.")
            )
        if not isinstance(application.owner, int):
            if config["application_role"] is not None:
                try:
                    application.owner.remove_roles(config["application_role"], reason=reason)
                except discord.HTTPException:
                    pass
            application.remove_member(application.owner, author=None)
            application.add_member(application.owner, author=None)
        application.owner = member
        application.remove_member(application.owner, author=None)
        overwrites = application.channel.overwrites
        overwrites[member] = discord.PermissionOverwrite(
            attach_files=True,
            read_message_history=True,
            read_messages=True,
            send_messages=True,
            view_channel=True,
        )
        await application.channel.edit(overwrites=overwrites, reason=reason)
        if config["application_role"] is not None:
            try:
                application.owner.add_roles(config["application_role"], reason=reason)
            except discord.HTTPException:
                pass
        if application.logs_messages:
            embed = await application.cog.get_embed_action(
                application, author=author, action=_("Owner Modified.")
            )
            await application.channel.send(embed=embed)
        await application.save()
        return application

    async def add_member(
        application,
        members: typing.List[discord.Member],
        author: typing.Optional[discord.Member] = None,
    ) -> typing.Any:  # typing_extensions.Self
        config = await application.cog.get_config(application.guild, application.panel)
        reason = await application.cog.get_audit_reason(
            guild=application.guild,
            panel=application.panel,
            author=author,
            reason=_("Adding a member to the application {application.id}.").format(application=application),
        )
        if config["gov_role"] is not None:
            gov_role_members = config["gov_role"].members
        else:
            gov_role_members = []
        overwrites = application.channel.overwrites
        for member in members:
            if author is not None:
                if member.bot:
                    raise commands.UserFeedbackCheckFailure(
                        _("You cannot add a bot to an application. ({member})").format(member=member)
                    )
                if not isinstance(application.owner, int):
                    if member == application.owner:
                        raise commands.UserFeedbackCheckFailure(
                            _(
                                "This member is already the owner of this application. ({member})"
                            ).format(member=member)
                        )
                if member in gov_role_members:
                    raise commands.UserFeedbackCheckFailure(
                        _(
                            "This member is an administrator for the application system. They will always have access to the application anyway. ({member})"
                        ).format(member=member)
                    )
                if member in application.members:
                    raise commands.UserFeedbackCheckFailure(
                        _("This member already has access to this application. ({member})").format(
                            member=member
                        )
                    )
            if member not in application.members:
                application.members.append(member)
            overwrites[member] = discord.PermissionOverwrite(
                attach_files=True,
                read_message_history=True,
                read_messages=True,
                send_messages=True,
                view_channel=True,
            )
        await application.channel.edit(overwrites=overwrites, reason=reason)
        await application.save()
        return application

    async def remove_member(
        application,
        members: typing.List[discord.Member],
        author: typing.Optional[discord.Member] = None,
    ) -> typing.Any:  # typing_extensions.Self
        config = await application.cog.get_config(application.guild, application.panel)
        reason = await application.cog.get_audit_reason(
            guild=application.guild,
            panel=application.panel,
            author=author,
            reason=_("Removing a member to the application {application.id}.").format(application=application),
        )
        if config["gov_role"] is not None:
            gov_role_members = config["gov_role"].members
        else:
            gov_role_members = []
        if config["ia_role"] is not None:
            ia_role_members = config["ia_role"].members
        else:
            ia_role_members = []
        for member in members:
            if author is not None:
                if member.bot:
                    raise commands.UserFeedbackCheckFailure(
                        _("You cannot remove a bot to an application ({member}).").format(member=member)
                    )
                if not isinstance(application.owner, int):
                    if member == application.owner:
                        raise commands.UserFeedbackCheckFailure(
                            _("You cannot remove the owner of this application. ({member})").format(
                                member=member
                            )
                        )
                if member in gov_role_members:
                    raise commands.UserFeedbackCheckFailure(
                        _(
                            "This member is an administrator for the application system. They will always have access to the application. ({member})"
                        ).format(member=member)
                    )
                if member not in application.members and member not in ia_role_members:
                    raise commands.UserFeedbackCheckFailure(
                        _(
                            "This member is not in the list of those authorised to access the application. ({member})"
                        ).format(member=member)
                    )
            if member in application.members:
                application.members.remove(member)
            if member in ia_role_members:
                overwrites = application.channel.overwrites
                overwrites[member] = discord.PermissionOverwrite(
                    attach_files=False,
                    read_message_history=False,
                    read_messages=False,
                    send_messages=False,
                    view_channel=False,
                )
                await application.channel.edit(overwrites=overwrites, reason=reason)
            else:
                await application.channel.set_permissions(member, overwrite=None, reason=reason)
        await application.save()
        return application
