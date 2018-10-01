from flask import Blueprint, request
import asyncio
import discord
from urllib.parse import urlencode
from urllib.request import Request, urlopen

auth = Blueprint("botauthentication", __name__)


class AuthApiMixin:
    @auth.route("/requestapikey", methods=['POST', 'GET'])
    def request_api_key(self):
        arguments = None
        if request.method == 'POST':
            arguments = request.form
        else:
            if request.method == 'GET':
                arguments = request.args

        if not arguments:
            return "invalid method call {.method}".format(request), 400

        keyrequest = {}
        keyrequest.state = arguments.get('state', '')
        try:
            keyrequest.userid = arguments['userid']
            keyrequest.callback = arguments['callback']
            keyrequest.name = arguments['name']
        except:
            return "missing parameters", 400

        self.bot.loop.create_task(self.ask_for_validation(keyrequest))
        return "OK", 200

    async def ask_for_validation(self, keyrequest):
        user = await self.bot.get_user_info(keyrequest.userid)

        def check(m):
            return m.author == user and isinstance(m.channel,
                                                   discord.abc.PrivateChannel)

        doc = await self.bot.database.get(user, self)
        ctx = {}
        ctx.author = user
        ctx.prefix = ''
        embed = await self.display_keys(
            ctx,
            doc,
            display_active=True,
            show_tokens=True,
            display_permissions=True)
        try:
            message = await user.send(
                """Authentication request from {.name}.
                Type the numbers of the keys you want to export. Seperate them with `,`.
                e.g.: `1, 2, 3` or simply `all`.
                If you did not initiate this, ignore this or contact the bot owner.
                To cancel the authentication, type anything invalid, e.g.: `cancel`."""
                .format(keyrequest),
                embed=embed)
        except discord.Forbidden:
            post_fields = {
                'userid': keyrequest.userid,
                'state': keyrequest.state,
                'error': 'user blocked verification dm'
            }

            request = Request(keyrequest.callback,
                              urlencode(post_fields).encode())
            urlopen(request)
            return
        answer = None
        try:
            answer = await self.bot.wait_for(
                "message", timeout=600, check=check)
        except asyncio.TimeoutError:
            await self.bot.edit_message(message, "Auth request timed out...")

            post_fields = {
                'userid': keyrequest.userid,
                'state': keyrequest.state,
                'error': 'timeout'
            }

            request = Request(keyrequest.callback,
                              urlencode(post_fields).encode())
            urlopen(request)
            return

        keys_to_export = []
        keys = doc.get("keys", [])
        if answer.content == 'all':
            keys_to_export = keys
        else:
            stripped_answer = answer.content.replace(" ", "")
            choices = stripped_answer.split(',')
            last_key = ""
            try:
                for _, number in choices:
                    last_key = number
                    num = int(number) - 1
                    keys_to_export.append(keys[num])
            except:
                user.send("You don't have a key with the ID {}. "
                          "Authentication process canceled.".format(last_key))

                post_fields = {
                    'userid': keyrequest.userid,
                    'state': keyrequest.state,
                    'error': 'user canceled'
                }

                request = Request(keyrequest.callback,
                                  urlencode(post_fields).encode())
                urlopen(request)
                return

        post_fields = {
            'userid': keyrequest.userid,
            'state': keyrequest.state,
            'api_keys': keys_to_export
        }

        request = Request(keyrequest.callback, urlencode(post_fields).encode())
        urlopen(request)