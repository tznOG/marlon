import contextlib
import io
import unittest
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import discord
from discord import app_commands

import test_bot as fixtures
from marlon import database, chat, views
from marlon.runtime import bot
from marlon.commands import admin


class SecurityTests(unittest.IsolatedAsyncioTestCase):
    setUp = fixtures.BotTests.setUp
    rows = fixtures.BotTests.rows
    execute = fixtures.BotTests.execute
    user = fixtures.BotTests.user
    badge = fixtures.BotTests.badge

    async def test_every_admin_command_has_a_runtime_permission_check(self):
        commands = [
            c
            for c in bot.tree.walk_commands()
            if not hasattr(c, "commands") and c.description.startswith("[Admin]")
        ]
        self.assertEqual(len(commands), 15)
        for command in commands:
            with self.subTest(command=command.qualified_name):
                self.assertTrue(command.checks)
                denied = SimpleNamespace(permissions=discord.Permissions.none())
                allowed = SimpleNamespace(
                    permissions=discord.Permissions(administrator=True)
                )
                for check in command.checks:
                    with self.assertRaises(app_commands.MissingPermissions):
                        check(denied)
                    self.assertTrue(check(allowed))

    async def test_code_listing_is_ephemeral(self):
        self.badge()
        self.execute(
            "INSERT INTO codigos(codigo,emblema_nome) VALUES (?,?)",
            ("SYNTHETIC", "Participante"),
        )
        event = fixtures.interaction()
        with patch.object(bot._connection, "user", event.user):
            await admin.codigo_lista.callback(event)
        kwargs = event.response.send_message.call_args.kwargs
        self.assertTrue(kwargs["ephemeral"])
        self.assertTrue(kwargs["view"].require_admin)
        kwargs["view"].stop()

    async def test_view_rejects_other_user_and_revoked_admin_permission(self):
        owner = fixtures.interaction()
        view = views.GenericListView([], "Teste", owner)
        self.assertFalse(await view.interaction_check(fixtures.interaction(202)))
        self.assertTrue(await view.interaction_check(owner))
        view.require_admin = True
        owner.permissions = discord.Permissions.none()
        self.assertFalse(await view.interaction_check(owner))
        owner.permissions = discord.Permissions(administrator=True)
        self.assertTrue(await view.interaction_check(owner))
        view.stop()

    async def test_modal_rechecks_permission_before_sending(self):
        channel = SimpleNamespace(send=AsyncMock())
        modal = views.JSONModal(channel)
        event = fixtures.interaction()
        event.permissions = discord.Permissions.none()
        await modal.on_submit(event)
        channel.send.assert_not_awaited()
        self.assertTrue(event.response.send_message.call_args.kwargs["ephemeral"])
        modal.stop()

    def offer(self):
        self.badge()
        self.user(101, 100)
        self.execute("UPDATE emblemas SET preco=30,na_loja=1")

    def test_changed_price_does_not_charge(self):
        self.offer()
        with self.assertRaisesRegex(ValueError, "preço mudou"):
            database.purchase_badge(101, "Participante", 10)
        self.assertEqual(self.rows("SELECT saldo FROM usuarios"), [(100,)])
        self.assertEqual(self.rows("SELECT * FROM inventario"), [])

    def test_removed_offer_does_not_charge(self):
        self.offer()
        self.execute("UPDATE emblemas SET na_loja=0")
        with self.assertRaisesRegex(ValueError, "disponível"):
            database.purchase_badge(101, "Participante", 30)
        self.assertEqual(self.rows("SELECT saldo FROM usuarios"), [(100,)])

    def test_parallel_purchase_charges_once(self):
        self.offer()

        def purchase():
            try:
                database.purchase_badge(101, "Participante", 30)
                return True
            except ValueError:
                return False

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: purchase(), range(2)))
        self.assertEqual(results.count(True), 1)
        self.assertEqual(self.rows("SELECT saldo FROM usuarios"), [(70,)])
        self.assertEqual(self.rows("SELECT count(*) FROM inventario"), [(1,)])

    def test_insufficient_balance_rolls_back(self):
        self.offer()
        self.execute("UPDATE usuarios SET saldo=10")
        with self.assertRaisesRegex(ValueError, "Saldo insuficiente"):
            database.purchase_badge(101, "Participante", 30)
        self.assertEqual(self.rows("SELECT saldo FROM usuarios"), [(10,)])
        self.assertEqual(self.rows("SELECT * FROM inventario"), [])

    def test_chat_without_key_never_calls_provider(self):
        with (
            patch.object(chat, "GROQ_API_KEY", ""),
            patch.object(chat.requests, "post") as request,
        ):
            self.assertIn("não está configurado", chat.chamar_groq_manual("Teste"))
            request.assert_not_called()

    def test_chat_sets_timeout_and_hides_upstream_error_body(self):
        response = SimpleNamespace(status_code=500, text="synthetic private detail")
        with (
            patch.object(chat, "GROQ_API_KEY", "synthetic"),
            patch.object(chat.requests, "post", return_value=response) as request,
            contextlib.redirect_stdout(io.StringIO()) as log,
        ):
            result = chat.chamar_groq_manual("synthetic user content")
        self.assertEqual(request.call_args.kwargs["timeout"], (5, 20))
        self.assertFalse(request.call_args.kwargs["allow_redirects"])
        self.assertNotIn("private detail", result + log.getvalue())
        self.assertNotIn("user content", log.getvalue())

    def test_chat_success_preserves_provider_response(self):
        response = SimpleNamespace(
            status_code=200,
            json=lambda: {"choices": [{"message": {"content": "Olá!"}}]},
        )
        with (
            patch.object(chat, "GROQ_API_KEY", "synthetic"),
            patch.object(chat.requests, "post", return_value=response),
        ):
            self.assertEqual(chat.chamar_groq_manual("Oi"), "Olá!")


if __name__ == "__main__":
    unittest.main()
