import discord
from discord import app_commands
from ..config import MOEDA_EMOJI
from ..database import connect
from ..runtime import bot
from ..helpers import formatar_moeda, emblema_autocomplete
from ..views import ShopView
from ..groups import grp_loja


@grp_loja.command(name="ver", description="Ver a loja")
async def loja_ver(interaction: discord.Interaction):
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT emoji, nome, preco FROM emblemas WHERE na_loja=1")
    items = c.fetchall()
    conn.close()

    embed = discord.Embed(title="🏪 Loja", description="Compre abaixo:", color=0xFFA500)
    embed.set_thumbnail(url=bot.user.display_avatar.url)

    if not items:
        embed.description = "Nenhum emblema disponível no momento."
        await interaction.response.send_message(embed=embed)
        return

    # Listagem visual no Embed
    lines = []
    for item in items:
        # item[0]=emoji, item[1]=nome, item[2]=preco
        lines.append(
            f"{item[0]} **{item[1]}** — {formatar_moeda(item[2])} {MOEDA_EMOJI}"
        )

    embed.description = "\n".join(lines)
    await interaction.response.send_message(embed=embed, view=ShopView(items))


@grp_loja.command(
    name="gerenciar", description="[Admin] Adicionar ou Remover emblema da loja"
)
@app_commands.default_permissions(administrator=True)
@app_commands.describe(acao="O que fazer?", preco="Preço (Necessário para adicionar)")
@app_commands.choices(
    acao=[
        app_commands.Choice(name="✅ Adicionar à Loja / Atualizar Preço", value="add"),
        app_commands.Choice(name="❌ Remover da Loja", value="remove"),
    ]
)
@app_commands.autocomplete(emblema=emblema_autocomplete)
async def loja_gerenciar(
    interaction: discord.Interaction,
    emblema: str,
    acao: app_commands.Choice[str],
    preco: int = None,
):
    conn = connect()
    c = conn.cursor()

    if acao.value == "add":
        if preco is None:
            embed = discord.Embed(
                description="❌ Você precisa definir um **preço** para adicionar.",
                color=0xFF0000,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            conn.close()
            return
        c.execute(
            "UPDATE emblemas SET preco=?, na_loja=1 WHERE nome=?", (preco, emblema)
        )
        msg = f"✅ Loja atualizada: **{emblema}** | Preço: {formatar_moeda(preco)}"
        cor = 0x00FF00
    else:  # remove
        c.execute("UPDATE emblemas SET na_loja=0 WHERE nome=?", (emblema,))
        msg = f"🗑️ **{emblema}** removido da loja."
        cor = 0xFF0000

    conn.commit()
    conn.close()
    embed = discord.Embed(description=msg, color=cor)
    await interaction.response.send_message(embed=embed)
