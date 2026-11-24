import discord
from discord import app_commands
import sqlite3
import random
import string
import datetime
from ..config import ID_CARGO_MEMBRO
from ..database import connect, check_user_exists
from ..helpers import (
    numero_para_ordinal,
    emblema_autocomplete,
    emblema_autocomplete_admin,
)
from ..views import JSONModal, GenericListView
from ..groups import grp_criar, grp_dar, grp_remover, grp_emblema, grp_codigo


@grp_criar.command(name="emblema", description="[Admin] Criar novo emblema")
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    descricao="Descrição do emblema (Opcional)",
    data="Data criação (DD/MM/AAAA) (Opcional)",
)
async def criar_emblema(
    interaction: discord.Interaction,
    nome: str,
    url: str,
    emoji: str,
    descricao: str = None,
    data: str = None,
):
    conn = connect()
    c = conn.cursor()
    data_final = data if data else datetime.datetime.now().strftime("%d/%m/%Y")
    desc_final = descricao if descricao else "Sem descrição"

    try:
        c.execute(
            "INSERT INTO emblemas (nome, url_imagem, emoji, descricao, data_criacao) VALUES (?, ?, ?, ?, ?)",
            (nome, url, emoji, desc_final, data_final),
        )
        conn.commit()
        embed = discord.Embed(
            description=f"✅ Emblema criado: **{nome}**", color=0x00FF00
        )
        await interaction.response.send_message(embed=embed)
    except:
        embed = discord.Embed(
            description="❌ Erro ou emblema já existe.", color=0xFF0000
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    conn.close()


@grp_criar.command(name="codigo", description="[Admin] Criar código")
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    limite="-1 = infinito, 1 = único", validade="DD/MM/AAAA HH:MM (Vazio = Eterno)"
)
@app_commands.autocomplete(emblema_nome=emblema_autocomplete)
async def criar_codigo(
    interaction: discord.Interaction,
    emblema_nome: str,
    limite: int = -1,
    validade: str = None,
    codigo: str = None,
):
    conn = connect()
    c = conn.cursor()
    if validade:
        try:
            datetime.datetime.strptime(validade, "%d/%m/%Y %H:%M")
        except:
            embed = discord.Embed(
                description="❌ Data inválida (DD/MM/AAAA HH:MM)", color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            conn.close()
            return
    if not codigo:
        codigo = "".join(
            random.choice(string.ascii_uppercase + string.digits) for _ in range(8)
        )

    try:
        c.execute(
            "INSERT INTO codigos (codigo, emblema_nome, limite, validade, ativo) VALUES (?, ?, ?, ?, 1)",
            (codigo, emblema_nome, limite, validade),
        )
        conn.commit()
        embed = discord.Embed(
            description=f"🎟️ Código criado: `{codigo}`\nEmblema: **{emblema_nome}**",
            color=0x00FF00,
        )
        await interaction.response.send_message(embed=embed)
    except:
        embed = discord.Embed(description="❌ Erro ao criar código.", color=0xFF0000)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    conn.close()


@grp_criar.command(
    name="json", description="[Admin] Criar Embed usando JSON do Discohook"
)
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(canal="Canal para enviar (Opcional, padrão é o atual)")
async def criar_json(
    interaction: discord.Interaction, canal: discord.TextChannel = None
):
    await interaction.response.send_modal(JSONModal(canal))


@grp_criar.command(
    name="anuncio_codigo",
    description="[Admin] Anuncia um código com template de emblema",
)
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    titulo="Título do anúncio (Ex: Evento Especial)",
    mencionar_cargo="Mencionar o cargo? (Padrão: Não)",
)
@app_commands.autocomplete(emblema=emblema_autocomplete)
async def criar_anuncio_codigo(
    interaction: discord.Interaction,
    codigo: str,
    emblema: str,
    titulo: str = "Novo Emblema Disponível!",
    mencionar_cargo: bool = False,
):
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT url_imagem, emoji FROM emblemas WHERE nome=?", (emblema,))
    dados = c.fetchone()
    conn.close()

    if not dados:
        await interaction.response.send_message(
            "❌ Emblema não encontrado.", ephemeral=True
        )
        return

    url_img, emoji = dados

    embed = discord.Embed(
        title=titulo,
        description="Um novo código foi liberado! Resgate agora mesmo para garantir seu emblema exclusivo.",
        color=0xFFD700,
    )
    embed.add_field(name="🎟️ Código", value=f"`{codigo}`", inline=True)
    embed.add_field(name="🏆 Emblema", value=f"{emoji} {emblema}", inline=True)
    embed.set_thumbnail(url=url_img)
    embed.set_footer(text=f"Use /resgatar {codigo}")

    await interaction.response.send_message("✅ Anúncio gerado!", ephemeral=True)

    msg_content = f"||<@&{ID_CARGO_MEMBRO}>||" if mencionar_cargo else None
    await interaction.channel.send(content=msg_content, embed=embed)


@grp_criar.command(name="cineminha", description="[Admin] Cria o anúncio do Cineminha")
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    edicao="Número da edição",
    filme="Nome do filme",
    trailer_url="Link do trailer",
    genero_duracao="Ex: Terror ・ 1h 39m",
    data_horario="DD/MM/AAAA HH:MM",
    imagem_url="Link da imagem",
    link_evento="Link do evento Discord",
    cor_hex="Cor do embed (Ex: #FF0000). Vazio = Padrão.",
)
@app_commands.autocomplete(emblema=emblema_autocomplete)
async def criar_cineminha(
    interaction: discord.Interaction,
    edicao: int,
    filme: str,
    trailer_url: str,
    genero_duracao: str,
    data_horario: str,
    emblema: str,
    imagem_url: str,
    link_evento: str,
    cor_hex: str = None,
):
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT emoji, nome FROM emblemas WHERE nome=?", (emblema,))
    dados_emblema = c.fetchone()
    conn.close()

    if not dados_emblema:
        await interaction.response.send_message(
            "❌ Emblema não encontrado.", ephemeral=True
        )
        return

    emoji_emblema, nome_emblema_real = dados_emblema

    try:
        dt = datetime.datetime.strptime(data_horario, "%d/%m/%Y %H:%M")
        timestamp = int(dt.timestamp())
        tag_tempo = f"<t:{timestamp}:F>"
    except ValueError:
        await interaction.response.send_message(
            "❌ Data inválida! Use DD/MM/AAAA HH:MM", ephemeral=True
        )
        return

    texto_ordinal = numero_para_ordinal(edicao)

    cor_int = 0x2B2D31  # Padrão
    if cor_hex:
        try:
            cor_int = int(cor_hex.replace("#", ""), 16)
        except:
            pass

    embed = discord.Embed(
        title=f"{edicao}º Cineminha",
        description=f"Faça parte do nosso **{texto_ordinal}** cineminha de {dt.year} e receba um emblema exclusivo para colecionar.\n\n"
        f"Filme: **[{filme}]({trailer_url})** ({genero_duracao})\n\n"
        f"Data: **{tag_tempo}**\n\n"
        f"Emblema: **{emoji_emblema} • {nome_emblema_real}**",
        color=cor_int,
    )

    if imagem_url.startswith("http"):
        embed.set_thumbnail(url=imagem_url)

    await interaction.response.send_message("✅ Anúncio gerado!", ephemeral=True)
    await interaction.channel.send(embed=embed)
    await interaction.channel.send(content=f"||{link_evento} <@&{ID_CARGO_MEMBRO}>||")


@grp_dar.command(
    name="emblema", description="[Admin] Dar emblema (Deixe usuário vazio para TODOS)"
)
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.autocomplete(emblema=emblema_autocomplete_admin)
async def dar_emblema(
    interaction: discord.Interaction, emblema: str, usuario: discord.Member = None
):
    conn = connect()
    c = conn.cursor()

    if emblema != "TODOS":
        c.execute("SELECT 1 FROM emblemas WHERE nome=?", (emblema,))
        if not c.fetchone():
            embed = discord.Embed(description="❌ Emblema não existe.", color=0xFF0000)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            conn.close()
            return

    afetados = 0
    msg = ""

    try:
        if usuario:
            check_user_exists(usuario.id)
            if emblema == "TODOS":
                c.execute(
                    """
                    INSERT INTO inventario (user_id, emblema_nome)
                    SELECT ?, nome FROM emblemas
                    WHERE NOT EXISTS (SELECT 1 FROM inventario WHERE user_id=? AND emblema_nome=emblemas.nome)
                """,
                    (usuario.id, usuario.id),
                )
                afetados = c.rowcount
                msg = f"✅ Adicionado **TODOS** os emblemas para {usuario.mention} ({afetados} novos)."
            else:
                c.execute(
                    "INSERT INTO inventario (user_id, emblema_nome) VALUES (?, ?)",
                    (usuario.id, emblema),
                )
                msg = f"✅ Emblema **{emblema}** adicionado para {usuario.mention}."
                afetados = 1
        else:
            if emblema == "TODOS":
                c.execute("""
                    INSERT INTO inventario (user_id, emblema_nome)
                    SELECT u.user_id, e.nome FROM usuarios u CROSS JOIN emblemas e
                    WHERE NOT EXISTS (SELECT 1 FROM inventario WHERE user_id=u.user_id AND emblema_nome=e.nome)
                """)
                afetados = c.rowcount
                msg = f"✅ Adicionado **TODOS** os emblemas para **TODOS** os usuários ({afetados} inserções)."
            else:
                c.execute(
                    """
                    INSERT INTO inventario (user_id, emblema_nome)
                    SELECT user_id, ? FROM usuarios
                    WHERE NOT EXISTS (SELECT 1 FROM inventario WHERE user_id=usuarios.user_id AND emblema_nome=?)
                """,
                    (emblema, emblema),
                )
                afetados = c.rowcount
                msg = f"✅ Emblema **{emblema}** adicionado para **TODOS** os usuários ({afetados} afetados)."

        conn.commit()
        embed = discord.Embed(description=msg, color=0x00FF00)
        await interaction.response.send_message(embed=embed)

    except sqlite3.IntegrityError:
        embed = discord.Embed(
            description="⚠️ Usuário já possui ou erro de banco.", color=0xFF0000
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        embed = discord.Embed(description=f"❌ Erro: {e}", color=0xFF0000)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    conn.close()


@grp_dar.command(name="moedas", description="[Admin] Adicionar moedas")
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def dar_moedas(
    interaction: discord.Interaction, usuario: discord.Member, qtd: int
):
    check_user_exists(usuario.id)
    conn = connect()
    c = conn.cursor()
    c.execute(
        "UPDATE usuarios SET saldo = saldo + ? WHERE user_id=?", (qtd, usuario.id)
    )
    conn.commit()
    conn.close()
    embed = discord.Embed(
        description=f"✅ Adicionado **{qtd}** moedas para {usuario.display_name}.",
        color=0x00FF00,
    )
    await interaction.response.send_message(embed=embed)


@grp_remover.command(
    name="emblema",
    description="[Admin] Remover emblema (Deixe usuário vazio para TODOS)",
)
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.autocomplete(emblema=emblema_autocomplete_admin)
async def remover_emblema(
    interaction: discord.Interaction, emblema: str, usuario: discord.Member = None
):
    conn = connect()
    c = conn.cursor()

    afetados = 0
    msg = ""

    if usuario:
        if emblema == "TODOS":
            c.execute("DELETE FROM inventario WHERE user_id=?", (usuario.id,))
            afetados = c.rowcount
            msg = f"🗑️ Removido **TODOS** os emblemas de {usuario.mention}."
        else:
            c.execute(
                "DELETE FROM inventario WHERE user_id=? AND emblema_nome=?",
                (usuario.id, emblema),
            )
            afetados = c.rowcount
            msg = f"🗑️ Emblema **{emblema}** removido de {usuario.mention}."
    else:
        if emblema == "TODOS":
            c.execute("DELETE FROM inventario")
            afetados = c.rowcount
            msg = f"🗑️ Removido **TODOS** os emblemas de **TODOS** os usuários ({afetados} registros)."
        else:
            c.execute("DELETE FROM inventario WHERE emblema_nome=?", (emblema,))
            afetados = c.rowcount
            msg = f"🗑️ Emblema **{emblema}** removido de **TODOS** os usuários."

    conn.commit()
    conn.close()

    if afetados > 0:
        embed = discord.Embed(description=msg, color=0x00FF00)
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(
            description="⚠️ Nada foi removido (ninguém possuía).", color=0xFF0000
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


@grp_remover.command(name="moedas", description="[Admin] Remover moedas")
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def remover_moedas(
    interaction: discord.Interaction, usuario: discord.Member, qtd: int
):
    check_user_exists(usuario.id)
    conn = connect()
    c = conn.cursor()
    c.execute(
        "UPDATE usuarios SET saldo = MAX(0, saldo - ?) WHERE user_id=?",
        (qtd, usuario.id),
    )
    conn.commit()
    conn.close()
    embed = discord.Embed(
        description=f"✅ Removido **{qtd}** moedas de {usuario.display_name}.",
        color=0x00FF00,
    )
    await interaction.response.send_message(embed=embed)


@grp_emblema.command(name="editar", description="[Admin] Editar emblema")
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(nova_data="Formato: 23 de junho de 2023")
@app_commands.autocomplete(emblema_atual=emblema_autocomplete)
async def emblema_editar(
    interaction: discord.Interaction,
    emblema_atual: str,
    novo_nome: str = None,
    novo_emoji: str = None,
    nova_url: str = None,
    nova_descricao: str = None,
    nova_data: str = None,
):
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT 1 FROM emblemas WHERE nome=?", (emblema_atual,))
    if not c.fetchone():
        embed = discord.Embed(description="❌ Emblema não encontrado.", color=0xFF0000)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        conn.close()
        return

    updates = []
    params = []
    emblema_alvo = emblema_atual

    if novo_nome:
        try:
            c.execute("PRAGMA foreign_keys = OFF")
            c.execute(
                "UPDATE emblemas SET nome=? WHERE nome=?", (novo_nome, emblema_atual)
            )
            c.execute(
                "UPDATE inventario SET emblema_nome=? WHERE emblema_nome=?",
                (novo_nome, emblema_atual),
            )
            c.execute(
                "UPDATE codigos SET emblema_nome=? WHERE emblema_nome=?",
                (novo_nome, emblema_atual),
            )
            c.execute("PRAGMA foreign_keys = ON")
            emblema_alvo = novo_nome
        except:
            embed = discord.Embed(description="❌ Erro ao renomear.", color=0xFF0000)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            conn.close()
            return

    if novo_emoji:
        updates.append("emoji=?")
        params.append(novo_emoji)
    if nova_url:
        updates.append("url_imagem=?")
        params.append(nova_url)
    if nova_descricao:
        updates.append("descricao=?")
        params.append(nova_descricao)
    if nova_data:
        updates.append("data_criacao=?")
        params.append(nova_data)

    if updates:
        sql = f"UPDATE emblemas SET {', '.join(updates)} WHERE nome=?"
        params.append(emblema_alvo)
        c.execute(sql, tuple(params))

    c.execute(
        "UPDATE inventario SET data_resgate = CURRENT_TIMESTAMP WHERE emblema_nome=?",
        (emblema_alvo,),
    )
    conn.commit()
    conn.close()
    embed = discord.Embed(
        description=f"✅ Emblema **{emblema_alvo}** editado com sucesso!",
        color=0x00FF00,
    )
    await interaction.response.send_message(embed=embed)


@grp_emblema.command(name="excluir", description="[Admin] Excluir emblema")
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.autocomplete(emblema=emblema_autocomplete)
async def emblema_excluir(interaction: discord.Interaction, emblema: str):
    conn = connect()
    c = conn.cursor()
    c.execute("DELETE FROM inventario WHERE emblema_nome=?", (emblema,))
    c.execute("DELETE FROM codigos WHERE emblema_nome=?", (emblema,))
    c.execute("DELETE FROM emblemas WHERE nome=?", (emblema,))
    conn.commit()
    conn.close()
    embed = discord.Embed(
        description=f"🗑️ Emblema **{emblema}** deletado.", color=0x00FF00
    )
    await interaction.response.send_message(embed=embed)


@grp_codigo.command(name="lista", description="[Admin] Listar códigos")
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def codigo_lista(interaction: discord.Interaction):
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT codigo, emblema_nome, limite, usos, validade, ativo FROM codigos")
    codigos = c.fetchall()
    conn.close()
    if not codigos:
        await interaction.response.send_message("Nenhum código.", ephemeral=True)
        return

    lista_fmt = []
    agora = datetime.datetime.now()
    for cod in codigos:
        c_str, nome, lim, usos, val, ativo = cod
        status = "🟢 Ativo"
        if not ativo:
            status = "🔴 Encerrado"
        elif lim != -1 and usos >= lim:
            status = "🚫 Esgotado"
        elif val:
            try:
                if agora > datetime.datetime.strptime(val, "%d/%m/%Y %H:%M"):
                    status = "⏰ Expirado"
            except:
                pass
        validade_str = val if val else "Eterno"
        limite_str = f"{usos}/{lim}" if lim != -1 else f"{usos}/∞"
        lista_fmt.append(
            f"`{c_str}` | **{nome}**\nStatus: {status} | Usos: {limite_str} | Vence: {validade_str}\n"
        )

    view = GenericListView(
        lista_fmt, "Gerenciamento de Códigos", interaction, items_per_page=5
    )
    view.require_admin = True
    await interaction.response.send_message(
        embed=view.create_embed(), view=view, ephemeral=True
    )


@grp_codigo.command(name="desativar", description="[Admin] Desativar código")
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def codigo_desativar(interaction: discord.Interaction, codigo: str):
    conn = connect()
    c = conn.cursor()
    c.execute("UPDATE codigos SET ativo=0 WHERE codigo=?", (codigo,))
    if c.rowcount:
        embed = discord.Embed(
            description=f"🛑 Código `{codigo}` desativado.", color=0x00FF00
        )
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(description="❌ Não encontrado.", color=0xFF0000)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    conn.commit()
    conn.close()


@grp_codigo.command(
    name="excluir", description="[Admin] Excluir código permanentemente"
)
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def codigo_excluir(interaction: discord.Interaction, codigo: str):
    conn = connect()
    c = conn.cursor()
    c.execute("DELETE FROM codigos WHERE codigo=?", (codigo,))
    if c.rowcount > 0:
        embed = discord.Embed(
            description=f"🗑️ Código `{codigo}` excluído.", color=0x00FF00
        )
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(description="❌ Não encontrado.", color=0xFF0000)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    conn.commit()
    conn.close()
