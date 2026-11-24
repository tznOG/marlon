import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from marlon import database
from marlon.__main__ import register_handlers
from marlon.runtime import bot
from marlon.commands import economy, community

register_handlers()


def interaction(user_id=101):
    return SimpleNamespace(
        user=SimpleNamespace(
            id=user_id,
            mention=f"<@{user_id}>",
            display_name="Teste",
            display_avatar=SimpleNamespace(url="https://example.test/avatar.png"),
        ),
        response=SimpleNamespace(send_message=AsyncMock(), edit_message=AsyncMock()),
    )


class BotTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="marlon-test-")
        self.path = str(Path(self.temp.name) / "synthetic.db")
        self.setting = patch.object(database, "DATABASE_PATH", self.path)
        self.setting.start()
        database.init_db()
        self.addCleanup(self.setting.stop)
        self.addCleanup(self.temp.cleanup)

    def rows(self, sql, args=()):
        with closing(database.connect()) as db:
            return db.execute(sql, args).fetchall()

    def execute(self, sql, args=()):
        with closing(database.connect()) as db, db:
            db.execute(sql, args)

    def user(self, uid, balance=0):
        database.check_user_exists(uid)
        self.execute("UPDATE usuarios SET saldo=? WHERE user_id=?", (balance, uid))

    def badge(self):
        self.execute(
            "INSERT INTO emblemas(nome,emoji,url_imagem) VALUES (?,?,?)",
            ("Participante", "🏅", "https://example.test/badge.png"),
        )

    def test_command_contract(self):
        expected = {
            "perfil",
            "bio",
            "emblemas",
            "resgatar",
            "ranking",
            "recompensa diaria",
            "recompensa trabalhar",
            "criar emblema",
            "criar codigo",
            "criar json",
            "criar anuncio_codigo",
            "criar cineminha",
            "dar emblema",
            "dar moedas",
            "remover emblema",
            "remover moedas",
            "emblema lista",
            "emblema ver",
            "emblema editar",
            "emblema excluir",
            "codigo lista",
            "codigo desativar",
            "codigo excluir",
            "loja ver",
            "loja gerenciar",
            "destaque definir",
            "destaque limpar",
            "economia apostar",
            "economia slots",
            "economia transferir",
        }
        self.assertEqual(
            {
                c.qualified_name
                for c in bot.tree.walk_commands()
                if not hasattr(c, "commands")
            },
            expected,
        )

    def test_schema_is_idempotent(self):
        database.init_db()
        names = {
            r[0] for r in self.rows("SELECT name FROM sqlite_master WHERE type='table'")
        }
        self.assertEqual(names, {"usuarios", "emblemas", "inventario", "codigos"})

    async def test_daily_reward_and_cooldown(self):
        event = interaction()
        with patch.object(economy.random, "randint", return_value=125):
            await economy.diaria.callback(event)
            await economy.diaria.callback(event)
        self.assertEqual(
            self.rows("SELECT saldo FROM usuarios WHERE user_id=101"), [(125,)]
        )
        self.assertIn("Volte em", event.response.send_message.call_args.args[0])

    async def test_work_reward_and_cooldown(self):
        event = interaction()
        with patch.object(economy.random, "randint", return_value=30):
            await economy.trabalhar.callback(event)
            await economy.trabalhar.callback(event)
        self.assertEqual(
            self.rows("SELECT saldo FROM usuarios WHERE user_id=101"), [(30,)]
        )

    async def test_transfer_preserves_total(self):
        self.user(101, 100)
        self.user(202, 10)
        await economy.economia_transferir.callback(
            interaction(), interaction(202).user, 35
        )
        self.assertEqual(
            self.rows("SELECT saldo FROM usuarios ORDER BY user_id"), [(65,), (45,)]
        )

    async def test_invalid_transfers_do_not_change_balances(self):
        self.user(101, 100)
        self.user(202, 10)
        for value in [0, -1, 101]:
            await economy.economia_transferir.callback(
                interaction(), interaction(202).user, value
            )
        await economy.economia_transferir.callback(interaction(), interaction().user, 5)
        self.assertEqual(
            self.rows("SELECT saldo FROM usuarios ORDER BY user_id"), [(100,), (10,)]
        )

    async def test_redeem_once_and_respect_limit(self):
        self.badge()
        self.execute(
            "INSERT INTO codigos(codigo,emblema_nome,limite) VALUES (?,?,?)",
            ("EXEMPLO", "Participante", 1),
        )
        for uid in [101, 101, 202]:
            await community.resgatar.callback(interaction(uid), "EXEMPLO")
        self.assertEqual(
            self.rows("SELECT user_id,emblema_nome FROM inventario"),
            [(101, "Participante")],
        )
        self.assertEqual(self.rows("SELECT usos FROM codigos"), [(1,)])

    async def test_expired_or_inactive_code_is_rejected(self):
        self.badge()
        self.execute(
            "INSERT INTO codigos(codigo,emblema_nome,validade) VALUES (?,?,?)",
            ("EXPIRED", "Participante", "01/01/2000 00:00"),
        )
        self.execute(
            "INSERT INTO codigos(codigo,emblema_nome,ativo) VALUES (?,?,?)",
            ("INACTIVE", "Participante", 0),
        )
        for code in ["EXPIRED", "INACTIVE"]:
            await community.resgatar.callback(interaction(), code)
        self.assertEqual(self.rows("SELECT * FROM inventario"), [])

    async def test_coin_flip_net_gain_matches_rule(self):
        self.user(101, 100)
        with patch.object(economy.random, "choice", return_value="cara"):
            await economy.economia_apostar.callback(
                interaction(), 20, SimpleNamespace(value="cara")
            )
        self.assertEqual(self.rows("SELECT saldo FROM usuarios"), [(120,)])

    async def test_slots_three_matching_pay_five_times_stake(self):
        self.user(101, 100)
        with patch.object(economy.random, "choice", return_value="🍒"):
            await economy.economia_slots.callback(interaction(), 20)
        self.assertEqual(self.rows("SELECT saldo FROM usuarios"), [(180,)])


if __name__ == "__main__":
    unittest.main()
