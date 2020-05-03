import asyncio
import unittest.mock
from bot import constants
from bot.cogs import filtering
from tests import helpers


class FilteringCogTests(unittest.TestCase):
    """Tests the filtering cog."""

    @classmethod
    def setUpClass(cls):
        cls.moderator_role = helpers.MockRole(name="Moderator", id=constants.Roles.moderators)

    def setUp(self):
        """Sets up fresh objects for each test."""
        self.bot = helpers.MockBot()
        self.cog = filtering.Filtering(self.bot)
        self.ctx = helpers.MockContext()
        self.ctx.channel = helpers.MockTextChannel()

    @unittest.mock.patch("bot.cogs.filtering.Filtering.nickname_filter", new_callable=unittest.mock.AsyncMock)
    def test_filter_detect_only_ban_word_in_nickname(self, patch):
        self.ctx.message = helpers.MockMessage()
        self.ctx.message.author.name = "User"
        self.ctx.message.author.nick = "Suicide"
        self.ctx.message.author.display_name = "Suicide"
        output = asyncio.run(self.cog.nickname_filter.callback(self.cog, self.ctx.message))
        success = output[0]
        self.assertTrue(success)

    @unittest.mock.patch("bot.cogs.filtering.Filtering.nickname_filter", new_callable=unittest.mock.AsyncMock)
    def test_filter_detect_with_ban_word_in_nickname(self, patch):
        self.ctx.message = helpers.MockMessage()
        self.ctx.message.author.name = "User"
        self.ctx.message.author.nick = "SuicideMan"
        self.ctx.message.author.display_name = "SuicideMan"
        output = asyncio.run(self.cog.nickname_filter.callback(self.cog, self.ctx.message))
        success = output[0]
        self.assertTrue(success)

    @unittest.mock.patch("bot.cogs.filtering.Filtering.nickname_filter", new_callable=unittest.mock.AsyncMock)
    @unittest.mock.patch("bot.cogs.moderation.modlog.ModLog", new_callable=unittest.mock.AsyncMock)
    def test_filter_change_display_name(self, c, s):
        username = "syntaxaire"
        author = helpers.MockMember(name=username, nick="Suicide", display_name="Suicide")
        self.ctx.message = helpers.MockMessage(author=author)
        return_values = asyncio.run(self.cog.nickname_filter.callback(self.cog, self.ctx.message))
        new_nickname = return_values[1]
        self.assertEqual(username, new_nickname)
