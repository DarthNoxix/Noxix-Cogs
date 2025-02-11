from .AAA3A_utils import CogsUtils  # isort:skip
from redbot.core.bot import Red  # isort:skip
from redbot.core.utils import get_end_user_data_statement

if not CogsUtils().is_dpy2:
    from dislash import InteractionClient

from .applicationtool import ApplicationTool

__red_end_user_data_statement__ = get_end_user_data_statement(file=__file__)


async def setup(bot: Red) -> None:
    cog = ApplicationTool(bot)
    await cog.cogsutils.add_cog(bot)
    if not CogsUtils().is_dpy2:
        if not hasattr(bot, "slash"):
            bot.slash = InteractionClient(bot, sync_commands=False)
