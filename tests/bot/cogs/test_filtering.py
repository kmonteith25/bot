import asyncio
import textwrap
import unittest
import unittest.mock

import mock

import discord
from bot import constants

import discord.user as author


from bot.cogs import filtering

from datetime import datetime
from bot.decorators import InChannelCheckFailure
from tests import helpers


COG_PATH = "bot.cogs.filtering.Filtering"


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




        #self.ctx.author.roles.append(self.moderator_role)

    @unittest.mock.patch("bot.cogs.filtering.Filtering._filter_nicknames", new_callable=unittest.mock.AsyncMock)
    def test_filter_detect_only_ban_word_in_nickname(self, patch):
        self.ctx.message = helpers.MockMessage()
        self.ctx.message.author.name = "User"
        self.ctx.message.author.nick = "Suicide"
        self.ctx.message.author.display_name = "Suicide"
        coroutine = self.cog._filter_nicknames(self.ctx.message)
        results = asyncio.run(coroutine)
        self.assertTrue(results)

    @unittest.mock.patch("bot.cogs.filtering.Filtering._filter_nicknames", new_callable=unittest.mock.AsyncMock)
    def test_filter_detect_with_ban_word_in_nickname(self, patch):
        self.ctx.message = helpers.MockMessage()
        self.ctx.message.author.name = "User"
        self.ctx.message.author.nick = "SuicideMan"
        self.ctx.message.author.display_name = "SuicideMan"
        coroutine = self.cog._filter_nicknames(self.ctx.message)
        results = asyncio.run(coroutine)
        self.assertTrue(results)
    '''
    @unittest.mock.patch("bot.cogs.filtering.Filtering._filter_nicknames", new_callable=unittest.mock.AsyncMock)
    #@unittest.mock.patch("bot.cogs.filtering.discord.Member.edit")
    def test_filter_change_display_name(self, async_patch):
        username = "User123"
        inappropriate_name = "SuicideMan"
        user = helpers.MockMember()
        user.name = username
        user.nick = inappropriate_name
        user.display_name = inappropriate_name
        #user.edit.side_effect = lambda x: self.revert_username(x)
        # this side effect is needed because the function called will not change the nickname of an mock
        # however, it changes the nickname on a live program
        # this patch should happen if the function called a function to change the nickname
        #name_patch.side_effect = lambda x: self.revert_username(x)
        self.ctx = helpers.MockContext(author=user)
        self.ctx.message = helpers.MockMessage(author=self.ctx.author)
        coroutine = self.cog._filter_nicknames(self.ctx.message)
        #asyncio.run(coroutine)
        self.assertEqual(asyncio.run(coroutine)[1], username)
    '''
    @unittest.mock.patch("bot.cogs.filtering.Filtering._filter_nicknames", new_callable=unittest.mock.AsyncMock)
    def test_filter_change_display_name(self, async_patch):
        username = "User123"
        inappropriate_name = "SuicideMan"
        user = helpers.MockMember()
        user.name = username
        user.nick = inappropriate_name
        user.display_name = inappropriate_name
        # user.edit.side_effect = lambda x: self.revert_username(x)
        # this side effect is needed because the function called will not change the nickname of an mock
        # however, it changes the nickname on a live program
        # this patch should happen if the function called a function to change the nickname
        # name_patch.side_effect = lambda x: self.revert_username(x)
        self.ctx = helpers.MockContext(author=user)
        self.ctx.message = helpers.MockMessage(author=self.ctx.author)
        await coroutine = self.cog._filter_nicknames(self.ctx.message)
        output = coroutine
        self.assertEqual(output[1], username)


    def revert_username(self, username):
        self.ctx.author.nick = username
