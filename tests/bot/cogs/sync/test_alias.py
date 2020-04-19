import asyncio
import unittest
import warnings

from bot.cogs import bot
from tests.helpers import MockBot, MockContext
from bot.cogs.alias import Alias
from bot.cogs.watchchannels.bigbrother import BigBrother


class BotAliasTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.bot_inst = MockBot()
        self.bot_cog = bot.Bot(self.bot_inst)
        self.alias_inst = Alias(self.bot_cog)
        self.big_bro_inst = BigBrother(self.bot_cog)
        self.bot_cog.add_cog(self.alias_inst)
        self.bot_cog.add_cog(self.big_bro_inst)
        self.ctx = MockContext()
        warnings.simplefilter("ignore", (ResourceWarning, DeprecationWarning))

    def test_check_permission_of_alias_command_false(self):
        """Test if permitted alias command returns False"""
        cmd_name = "bigbrother watch"
        coroutine = self.alias_inst.check_permission_of_alias_command(self.ctx, cmd_name)
        self.assertFalse(asyncio.run(coroutine))

    def test_check_permission_of_alias_command_true(self):
        """Test if permitted alias command returns True"""
        cmd_name = "nominees"
        coroutine = self.alias_inst.check_permission_of_alias_command(self.ctx, cmd_name)
        self.assertTrue(asyncio.run(coroutine))

    def test_check_permission_of_alias_command_special(self):
        """Test if 'get group' returns True"""
        cmd_name = "get group"
        coroutine = self.alias_inst.check_permission_of_alias_command(self.ctx, cmd_name)
        self.assertTrue(asyncio.run(coroutine))
