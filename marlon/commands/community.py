import discord
from discord import app_commands
import datetime
from ..database import connect, check_user_exists
from ..runtime import bot
from ..helpers import emblema_autocomplete
from ..views import ProfilePaginationView, GenericListView, RankingView
from ..groups import grp_emblema, grp_destaque


@bot.tree.command(name="perfil", description="Exibe seu perfil completo")
async def perfil(interaction: discord.Interaction, usuario: discord.Member = None):
    target = usuario or interaction.user
    check_user_exists(target.id)
    conn = connect()
    c = conn.cursor()
    c.execute(
        "SELECT saldo, bio, destaques FROM usuarios WHERE user_id=?", (target.id,)
    )
    data = c.fetchone()
    saldo, bio, destaques = data[0], data[1] or "Sem bio. (Utilize /bio)", data[2]

    dest_viz = ""
    if destaques:
        lst = []
        for n in destaques.split(","):
            c.execute("SELECT emoji, nome FROM emblemas WHERE nome=?", (n,))
            r = c.fetchone()
            if r:
                lst.append(f"{r[0]} {r[1]}")
        if lst:
            dest_viz = "\n".join(lst)

    c.execute(
        """SELECT e.emoji, e.nome FROM inventario i JOIN emblemas e ON i.emblema_nome = e.nome WHERE i.user_id = ? ORDER BY e.rowid DESC""",
        (target.id,),
    )
    inv = [f"{r[0]} {r[1]}" for r in c.fetchall()]
    conn.close()
    view = ProfilePaginationView(inv, target, saldo, bio, dest_viz, interaction)
    await interaction.response.send_message(embed=view.create_embed(), view=view)


@bot.tree.command(name="bio", description="Muda bio")
async def bio(interaction: discord.Interaction, texto: str):
    check_user_exists(interaction.user.id)
    if len(texto) > 300:
        await interaction.response.send_message("Muito longo.", ephemeral=True)
        return
    conn = connect()
    c = conn.cursor()
    c.execute("UPDATE usuarios SET bio=? WHERE user_id=?", (texto, interaction.user.id))
    conn.commit()
    conn.close()
    await interaction.response.send_message("✅ Bio atualizada.")


@bot.tree.command(name="emblemas", description="Lista todos os emblemas")
async def emblemas(interaction: discord.Interaction):
    conn = connect()
    c = conn.cursor()
    c.execute(
        """SELECT e.emoji, e.nome, COUNT(i.user_id) FROM emblemas e LEFT JOIN inventario i ON e.nome = i.emblema_nome GROUP BY e.nome ORDER BY e.rowid DESC"""
    )
    items = c.fetchall()
    conn.close()
    if not items:
        await interaction.response.send_message("Vazio.", ephemeral=True)
        return
    data = [f"{i[0]} **{i[1]}** `({i[2]} membros)`" for i in items]
    view = GenericListView(data, "Emblemas Existentes", interaction)
    await interaction.response.send_message(embed=view.create_embed(), view=view)


@bot.tree.command(name="resgatar", description="Resgatar código")
async def resgatar(interaction: discord.Interaction, codigo: str):
    check_user_exists(interaction.user.id)
    conn = connect()
    c = conn.cursor()
    c.execute(
        "SELECT emblema_nome, limite, usos, validade, ativo FROM codigos WHERE codigo=?",
        (codigo,),
    )
    res = c.fetchone()

    if not res:
        await interaction.response.send_message(
            "❌ Código inexistente.", ephemeral=True
        )
        conn.close()
        return
    nome, limite, usos, validade, ativo = res

    if not ativo:
        await interaction.response.send_message("❌ Código encerrado.", ephemeral=True)
        conn.close()
        return
    if validade:
        try:
            if datetime.datetime.now() > datetime.datetime.strptime(
                validade, "%d/%m/%Y %H:%M"
            ):
                await interaction.response.send_message(
                    "❌ Código expirado.", ephemeral=True
                )
                conn.close()
                return
        except:
            pass
    if limite != -1 and usos >= limite:
        await interaction.response.send_message("❌ Limite atingido.", ephemeral=True)
        conn.close()
        return

    c.execute(
        "SELECT 1 FROM inventario WHERE user_id=? AND emblema_nome=?",
        (interaction.user.id, nome),
    )
    if c.fetchone():
        await interaction.response.send_message(f"⚠️ Já tem **{nome}**.", ephemeral=True)
        conn.close()
        return

    c.execute(
        "INSERT INTO inventario (user_id, emblema_nome) VALUES (?, ?)",
        (interaction.user.id, nome),
    )
    c.execute("UPDATE codigos SET usos = usos + 1 WHERE codigo=?", (codigo,))
    conn.commit()

    c.execute("SELECT emoji FROM emblemas WHERE nome=?", (nome,))
    emoji = c.fetchone()[0]
    conn.close()

    embed = discord.Embed(title=interaction.user.display_name, color=0x2B2D31)
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    embed.description = (
        f"Código resgatado com sucesso!\n\n**Emblema:**\n{emoji} ・{nome}"
    )
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="ranking", description="Veja o ranking do servidor")
async def ranking(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📊 Rankings do Servidor",
        description="Selecione o ranking que deseja visualizar usando o menu abaixo.",
        color=0x2B2D31,
    )
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    view = RankingView(interaction)
    await interaction.response.send_message(embed=embed, view=view)


@grp_destaque.command(name="definir", description="Define os destaques do seu perfil")
@app_commands.describe(emblemas="Nomes separados por vírgula")
async def destaque_definir(interaction: discord.Interaction, emblemas: str):
    check_user_exists(interaction.user.id)
    nomes = [n.strip() for n in emblemas.split(",")][:3]
    conn = connect()
    c = conn.cursor()
    validos = []
    for nome in nomes:
        c.execute(
            "SELECT 1 FROM inventario WHERE user_id=? AND emblema_nome=?",
            (interaction.user.id, nome),
        )
        if c.fetchone():
            validos.append(nome)
    if not validos:
        await interaction.response.send_message("❌ Nenhum válido.", ephemeral=True)
        conn.close()
        return
    c.execute(
        "UPDATE usuarios SET destaques=? WHERE user_id=?",
        (",".join(validos), interaction.user.id),
    )
    conn.commit()
    conn.close()
    await interaction.response.send_message("⭐ Destaques atualizados.")


@grp_destaque.command(
    name="limpar", description="Remove todos os destaques do seu perfil"
)
async def destaque_limpar(interaction: discord.Interaction):
    check_user_exists(interaction.user.id)
    conn = connect()
    c = conn.cursor()
    c.execute(
        "UPDATE usuarios SET destaques='' WHERE user_id=?", (interaction.user.id,)
    )
    conn.commit()
    conn.close()
    await interaction.response.send_message("🧹 Destaques limpos com sucesso!")


@grp_emblema.command(name="lista", description="Lista todos os emblemas")
async def emblema_lista(interaction: discord.Interaction):
    conn = connect()
    c = conn.cursor()
    c.execute(
        """SELECT e.emoji, e.nome, COUNT(i.user_id) FROM emblemas e LEFT JOIN inventario i ON e.nome = i.emblema_nome GROUP BY e.nome ORDER BY e.rowid DESC"""
    )
    items = c.fetchall()
    conn.close()
    if not items:
        await interaction.response.send_message("Vazio.", ephemeral=True)
        return
    data = [f"{i[0]} **{i[1]}** `({i[2]} membros)`" for i in items]
    view = GenericListView(data, "Emblemas Existentes", interaction)
    await interaction.response.send_message(embed=view.create_embed(), view=view)


@grp_emblema.command(name="ver", description="Ver detalhes de um emblema")
@app_commands.autocomplete(emblema=emblema_autocomplete)
async def emblema_ver(interaction: discord.Interaction, emblema: str):
    conn = connect()
    c = conn.cursor()
    c.execute(
        "SELECT url_imagem, emoji, descricao, data_criacao FROM emblemas WHERE nome=?",
        (emblema,),
    )
    d = c.fetchone()
    conn.close()
    if not d:
        await interaction.response.send_message("❌ 404.", ephemeral=True)
        return

    desc_str = d[2] or "-"
    data_str = d[3] or "Desconhecida"
    nova_descricao = f"{desc_str}\n\n📅 **Data:** `{data_str}`"

    embed = discord.Embed(
        title=f"{d[1]} {emblema}", description=nova_descricao, color=0x3498DB
    )
    embed.set_thumbnail(url=d[0])
    await interaction.response.send_message(embed=embed)
