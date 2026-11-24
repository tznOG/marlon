import discord
from discord import app_commands
from .database import connect


def numero_para_ordinal(n):
    ordinais = {
        1: "primeiro",
        2: "segundo",
        3: "terceiro",
        4: "quarto",
        5: "quinto",
        6: "sexto",
        7: "sétimo",
        8: "oitavo",
        9: "nono",
        10: "décimo",
    }
    return ordinais.get(n, str(n) + "º")


async def emblema_autocomplete(interaction: discord.Interaction, current: str):
    conn = connect()
    c = conn.cursor()
    c.execute(
        "SELECT nome FROM emblemas WHERE nome LIKE ? ORDER BY rowid DESC",
        (f"%{current}%",),
    )
    emblemas = [row[0] for row in c.fetchall()]
    conn.close()
    return [app_commands.Choice(name=e, value=e) for e in emblemas[:25]]


async def emblema_autocomplete_admin(interaction: discord.Interaction, current: str):
    conn = connect()
    c = conn.cursor()
    c.execute(
        "SELECT nome FROM emblemas WHERE nome LIKE ? ORDER BY rowid DESC",
        (f"%{current}%",),
    )
    emblemas = [row[0] for row in c.fetchall()]
    conn.close()
    choices = [app_commands.Choice(name=e, value=e) for e in emblemas[:24]]
    if "todos".startswith(current.lower()):
        choices.insert(
            0, app_commands.Choice(name="TODOS (Todos os Emblemas)", value="TODOS")
        )
    return choices


def formatar_moeda(valor):
    return f"{valor:,}".replace(",", ".")
