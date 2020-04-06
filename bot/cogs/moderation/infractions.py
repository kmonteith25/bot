import logging
import typing as t

import discord
from discord import Member
from discord.ext import commands
from discord.ext.commands import Context, command

from bot import constants
from bot.bot import Bot
from bot.constants import Event
from bot.converters import Expiry, FetchedMember
from bot.decorators import respect_role_hierarchy
from bot.utils.checks import with_role_check
from . import utils
from .scheduler import InfractionScheduler
from .utils import UserSnowflake

log = logging.getLogger(__name__)


class Infractions(InfractionScheduler, commands.Cog):
    """Apply and pardon infractions on users for moderation purposes."""

    category = "Moderation"
    category_description = "Server moderation tools."

    def __init__(self, bot: Bot):
        super().__init__(bot, supported_infractions={"ban", "kick", "mute", "note", "warning"})

        self.category = "Moderation"
        self._muted_role = discord.Object(constants.Roles.muted)

    @commands.Cog.listener()
    async def on_member_join(self, member: Member) -> None:
        """Reapply active mute infractions for returning members."""
        active_mutes = await self.bot.api_client.get(
            "bot/infractions",
            params={
                "active": "true",
                "type": "mute",
                "user__id": member.id
            }
        )

        if active_mutes:
            reason = f"Re-applying active mute: {active_mutes[0]['id']}"
            action = member.add_roles(self._muted_role, reason=reason)

            await self.reapply_infraction(active_mutes[0], action)

    # region: Permanent infractions

    @command()
    async def warn(self, ctx: Context, user: Member, *, reason: str = None) -> None:
        """Warn a user for the given reason."""
        infraction = await utils.post_infraction(ctx, user, "warning", reason, active=False)
        if infraction is None:
            return

        await self.apply_infraction(ctx, infraction, user)

    @command()
    async def kick(self, ctx: Context, user: Member, *, reason: str = None) -> None:
        """Kick a user for the given reason."""
        await self.apply_kick(ctx, user, reason, active=False)

    @command()
    async def ban(self, ctx: Context, user: FetchedMember, *, reason: str = None) -> None:
        """Permanently ban a user for the given reason and stop watching them with Big Brother."""
        await self.apply_ban(ctx, user, reason)

    # endregion
    # region: Temporary infractions

    @command(aliases=["mute"])
    async def tempmute(self, ctx: Context, user: Member, duration: Expiry, *, reason: str = None) -> None:
        """
        Temporarily mute a user for the given reason and duration.

        A unit of time should be appended to the duration.
        Units (∗case-sensitive):
        \u2003`y` - years
        \u2003`m` - months∗
        \u2003`w` - weeks
        \u2003`d` - days
        \u2003`h` - hours
        \u2003`M` - minutes∗
        \u2003`s` - seconds

        Alternatively, an ISO 8601 timestamp can be provided for the duration.
        """
        await self.apply_mute(ctx, user, reason, expires_at=duration)

    @command()
    async def tempban(self, ctx: Context, user: FetchedMember, duration: Expiry, *, reason: str = None) -> None:
        """
        Temporarily ban a user for the given reason and duration.

        A unit of time should be appended to the duration.
        Units (∗case-sensitive):
        \u2003`y` - years
        \u2003`m` - months∗
        \u2003`w` - weeks
        \u2003`d` - days
        \u2003`h` - hours
        \u2003`M` - minutes∗
        \u2003`s` - seconds

        Alternatively, an ISO 8601 timestamp can be provided for the duration.
        """
        await self.apply_ban(ctx, user, reason, expires_at=duration)

    # endregion
    # region: Permanent shadow infractions

    @command(hidden=True)
    async def note(self, ctx: Context, user: FetchedMember, *, reason: str = None) -> None:
        """Create a private note for a user with the given reason without notifying the user."""
        infraction = await utils.post_infraction(ctx, user, "note", reason, hidden=True, active=False)
        if infraction is None:
            return

        await self.apply_infraction(ctx, infraction, user)

    @command(hidden=True, aliases=['shadowkick', 'skick'])
    async def shadow_kick(self, ctx: Context, user: Member, *, reason: str = None) -> None:
        """Kick a user for the given reason without notifying the user."""
        await self.apply_kick(ctx, user, reason, hidden=True, active=False)

    @command(hidden=True, aliases=['shadowban', 'sban'])
    async def shadow_ban(self, ctx: Context, user: FetchedMember, *, reason: str = None) -> None:
        """Permanently ban a user for the given reason without notifying the user."""
        await self.apply_ban(ctx, user, reason, hidden=True)

    # endregion
    # region: Temporary shadow infractions

    @command(hidden=True, aliases=["shadowtempmute, stempmute", "shadowmute", "smute"])
    async def shadow_tempmute(self, ctx: Context, user: Member, duration: Expiry, *, reason: str = None) -> None:
        """
        Temporarily mute a user for the given reason and duration without notifying the user.

        A unit of time should be appended to the duration.
        Units (∗case-sensitive):
        \u2003`y` - years
        \u2003`m` - months∗
        \u2003`w` - weeks
        \u2003`d` - days
        \u2003`h` - hours
        \u2003`M` - minutes∗
        \u2003`s` - seconds

        Alternatively, an ISO 8601 timestamp can be provided for the duration.
        """
        await self.apply_mute(ctx, user, reason, expires_at=duration, hidden=True)

    @command(hidden=True, aliases=["shadowtempban, stempban"])
    async def shadow_tempban(
        self,
        ctx: Context,
        user: FetchedMember,
        duration: Expiry,
        *,
        reason: str = None
    ) -> None:
        """
        Temporarily ban a user for the given reason and duration without notifying the user.

        A unit of time should be appended to the duration.
        Units (∗case-sensitive):
        \u2003`y` - years
        \u2003`m` - months∗
        \u2003`w` - weeks
        \u2003`d` - days
        \u2003`h` - hours
        \u2003`M` - minutes∗
        \u2003`s` - seconds

        Alternatively, an ISO 8601 timestamp can be provided for the duration.
        """
        await self.apply_ban(ctx, user, reason, expires_at=duration, hidden=True)

    # endregion
    # region: Remove infractions (un- commands)

    @command()
    async def unmute(self, ctx: Context, user: FetchedMember) -> None:
        """Prematurely end the active mute infraction for the user."""
        await self.pardon_infraction(ctx, "mute", user)

    # add reason here to this function as argument, maybe method overload may be better
    @command()
    async def unban(self, ctx: Context, user: FetchedMember) -> None:
        """Prematurely end the active ban infraction for the user."""
        await self.pardon_infraction(ctx, "ban", user)

    # this is version I made to pass reason, if we remove this remove this comment also
    @command()
    async def unban(self, ctx: Context, user: FetchedMember, reason: str) -> None:
        """Prematurely end the active ban infraction for the user."""
        await self.pardon_infraction(ctx, "ban", user, reason)

    # endregion
    # region: Base apply functions

    async def apply_mute(self, ctx: Context, user: Member, reason: str, **kwargs) -> None:
        """Apply a mute infraction with kwargs passed to `post_infraction`."""
        if await utils.has_active_infraction(ctx, user, "mute"):
            return

        infraction = await utils.post_infraction(ctx, user, "mute", reason, active=True, **kwargs)
        if infraction is None:
            return

        self.mod_log.ignore(Event.member_update, user.id)

        async def action() -> None:
            await user.add_roles(self._muted_role, reason=reason)

            log.trace(f"Attempting to kick {user} from voice because they've been muted.")
            await user.move_to(None, reason=reason)

        await self.apply_infraction(ctx, infraction, user, action())

    @respect_role_hierarchy()
    async def apply_kick(self, ctx: Context, user: Member, reason: str, **kwargs) -> None:
        """Apply a kick infraction with kwargs passed to `post_infraction`."""
        infraction = await utils.post_infraction(ctx, user, "kick", reason, active=False, **kwargs)
        if infraction is None:
            return

        self.mod_log.ignore(Event.member_remove, user.id)

        action = user.kick(reason=reason)
        await self.apply_infraction(ctx, infraction, user, action)

    @respect_role_hierarchy()
    async def apply_ban(self, ctx: Context, user: UserSnowflake, reason: str, **kwargs) -> None:
        """
        Apply a ban infraction with kwargs passed to `post_infraction`.

        Will also remove the banned user from the Big Brother watch list if applicable.
        """
        if await utils.has_active_infraction(ctx, user, "ban"):
            return

        infraction = await utils.post_infraction(ctx, user, "ban", reason, active=True, **kwargs)
        if infraction is None:
            return

        self.mod_log.ignore(Event.member_remove, user.id)

        action = ctx.guild.ban(user, reason=reason, delete_message_days=0)
        await self.apply_infraction(ctx, infraction, user, action)

        if infraction.get('expires_at') is not None:
            log.trace(f"Ban isn't permanent; user {user} won't be unwatched by Big Brother.")
            return

        bb_cog = self.bot.get_cog("Big Brother")
        if not bb_cog:
            log.error(f"Big Brother cog not loaded; perma-banned user {user} won't be unwatched.")
            return

        log.trace(f"Big Brother cog loaded; attempting to unwatch perma-banned user {user}.")

        bb_reason = "User has been permanently banned from the server. Automatically removed."
        await bb_cog.apply_unwatch(ctx, user, bb_reason, send_message=False)

    # endregion
    # region: Base pardon functions

    async def pardon_mute(self, user_id: int, guild: discord.Guild, reason: str) -> t.Dict[str, str]:
        """Remove a user's muted role, DM them a notification, and return a log dict."""
        user = guild.get_member(user_id)
        log_text = {}

        if user:
            # Remove the muted role.
            self.mod_log.ignore(Event.member_update, user.id)
            await user.remove_roles(self._muted_role, reason=reason)

            # DM the user about the expiration.
            notified = await utils.notify_pardon(
                user=user,
                title="You have been unmuted",
                content="You may now send messages in the server.",
                icon_url=utils.INFRACTION_ICONS["mute"][1]
            )

            log_text["Member"] = f"{user.mention}(`{user.id}`)"
            log_text["DM"] = "Sent" if notified else "**Failed**"
        else:
            log.info(f"Failed to unmute user {user_id}: user not found")
            log_text["Failure"] = "User was not found in the guild."

        return log_text

    async def pardon_ban(self, user_id: int, guild: discord.Guild, reason: str) -> t.Dict[str, str]:
        """Remove a user's ban on the Discord guild and return a log dict."""
        user = discord.Object(user_id)
        log_text = {}

        self.mod_log.ignore(Event.member_unban, user_id)

        try:
            await guild.unban(user, reason=reason)
        except discord.NotFound:
            log.info(f"Failed to unban user {user_id}: no active ban found on Discord")
            log_text["Note"] = "No active ban found on Discord."
        return log_text

    async def _pardon_action(self, infraction: utils.Infraction) -> t.Optional[t.Dict[str, str]]:
        """
        Execute deactivation steps specific to the infraction's type and return a log dict.

        If an infraction type is unsupported, return None instead.
        """
        guild = self.bot.get_guild(constants.Guild.id)
        user_id = infraction["user"]
        reason = f"Infraction #{infraction['id']} expired or was pardoned."
        if infraction["type"] == "mute":
            return await self.pardon_mute(user_id, guild, reason)
        elif infraction["type"] == "ban":
            return await self.pardon_ban(user_id, guild, reason)

    # endregion

    # This cannot be static (must have a __func__ attribute).
    def cog_check(self, ctx: Context) -> bool:
        """Only allow moderators to invoke the commands in this cog."""
        return with_role_check(ctx, *constants.MODERATION_ROLES)

    # This cannot be static (must have a __func__ attribute).
    async def cog_command_error(self, ctx: Context, error: Exception) -> None:
        """Send a notification to the invoking context on a Union failure."""
        if isinstance(error, commands.BadUnionArgument):
            if discord.User in error.converters or discord.Member in error.converters:
                await ctx.send(str(error.errors[0]))
                error.handled = True
