import discord
from discord import app_commands
import random
import datetime
from datetime import timedelta
from ..config import MOEDA_EMOJI
from ..database import connect, check_user_exists
from ..helpers import formatar_moeda
from ..groups import grp_recompensa, grp_economia


@grp_economia.command(name="apostar", description="Aposte no Cara ou Coroa (2x)")
@app_commands.describe(valor="Quantidade", escolha="Cara ou Coroa")
@app_commands.choices(
    escolha=[
        app_commands.Choice(name="Cara", value="cara"),
        app_commands.Choice(name="Coroa", value="coroa"),
    ]
)
async def economia_apostar(
    interaction: discord.Interaction, valor: int, escolha: app_commands.Choice[str]
):
    check_user_exists(interaction.user.id)
    if valor <= 0:
        await interaction.response.send_message("❌ Valor inválido.", ephemeral=True)
        return

    conn = connect()
    c = conn.cursor()
    c.execute("SELECT saldo FROM usuarios WHERE user_id=?", (interaction.user.id,))
    saldo = c.fetchone()[0]

    if saldo < valor:
        await interaction.response.send_message(
            f"❌ Você só tem {saldo} moedas.", ephemeral=True
        )
        conn.close()
        return

    resultado = random.choice(["cara", "coroa"])
    venceu = resultado == escolha.value

    if venceu:
        novo_saldo = saldo + valor
        c.execute(
            "UPDATE usuarios SET saldo = ? WHERE user_id=?",
            (novo_saldo, interaction.user.id),
        )
        embed = discord.Embed(
            title="🪙 Cara ou Coroa",
            description=f"Deu **{resultado.upper()}**!\nVocê ganhou **{valor}** {MOEDA_EMOJI}",
            color=0x00FF00,
        )
    else:
        novo_saldo = saldo - valor
        c.execute(
            "UPDATE usuarios SET saldo = ? WHERE user_id=?",
            (novo_saldo, interaction.user.id),
        )
        embed = discord.Embed(
            title="🪙 Cara ou Coroa",
            description=f"Deu **{resultado.upper()}**.\nVocê perdeu **{valor}** {MOEDA_EMOJI}",
            color=0xFF0000,
        )

    conn.commit()
    conn.close()
    await interaction.response.send_message(embed=embed)


@grp_economia.command(name="slots", description="Jogue no caça-níquel (Custo: aposta)")
async def economia_slots(interaction: discord.Interaction, aposta: int):
    check_user_exists(interaction.user.id)
    if aposta <= 0:
        await interaction.response.send_message("❌ Valor inválido.", ephemeral=True)
        return

    conn = connect()
    c = conn.cursor()
    c.execute("SELECT saldo FROM usuarios WHERE user_id=?", (interaction.user.id,))
    saldo = c.fetchone()[0]

    if saldo < aposta:
        await interaction.response.send_message(
            f"❌ Saldo insuficiente.", ephemeral=True
        )
        conn.close()
        return

    emojis = ["🍎", "🍒", "💎", "7️⃣", "🔔"]
    a, b, c_slot = random.choice(emojis), random.choice(emojis), random.choice(emojis)

    # Lógica de pagamento
    multiplicador = 0
    if a == b == c_slot:
        multiplicador = 5  # Jackpot
    elif a == b or b == c_slot or a == c_slot:
        multiplicador = 2  # Dois iguais

    ganho = aposta * multiplicador
    if ganho > 0:
        c.execute(
            "UPDATE usuarios SET saldo = saldo + ? WHERE user_id=?",
            (ganho - aposta, interaction.user.id),
        )  # Ganho liquido
        cor = 0x00FF00
        msg = f"Você ganhou **{ganho}** {MOEDA_EMOJI}!"
    else:
        c.execute(
            "UPDATE usuarios SET saldo = saldo - ? WHERE user_id=?",
            (aposta, interaction.user.id),
        )
        cor = 0xFF0000
        msg = "Você perdeu."

    conn.commit()
    conn.close()

    embed = discord.Embed(
        title="🎰 Slots", description=f"| {a} | {b} | {c_slot} |\n\n{msg}", color=cor
    )
    await interaction.response.send_message(embed=embed)


@grp_economia.command(
    name="transferir", description="Transfere moedas para outro usuário"
)
async def economia_transferir(
    interaction: discord.Interaction, usuario: discord.Member, valor: int
):
    check_user_exists(interaction.user.id)
    check_user_exists(usuario.id)

    if interaction.user.id == usuario.id:
        await interaction.response.send_message(
            "❌ Não pode transferir para si mesmo.", ephemeral=True
        )
        return
    if valor <= 0:
        await interaction.response.send_message("❌ Valor inválido.", ephemeral=True)
        return

    conn = connect()
    c = conn.cursor()
    c.execute("SELECT saldo FROM usuarios WHERE user_id=?", (interaction.user.id,))
    saldo_remetente = c.fetchone()[0]

    if saldo_remetente < valor:
        await interaction.response.send_message(
            "❌ Saldo insuficiente.", ephemeral=True
        )
        conn.close()
        return

    c.execute(
        "UPDATE usuarios SET saldo = saldo - ? WHERE user_id=?",
        (valor, interaction.user.id),
    )
    c.execute(
        "UPDATE usuarios SET saldo = saldo + ? WHERE user_id=?", (valor, usuario.id)
    )
    conn.commit()
    conn.close()

    embed = discord.Embed(
        description=f"💸 **{interaction.user.mention}** transferiu **{valor}** {MOEDA_EMOJI} para **{usuario.mention}**.",
        color=0x00FF00,
    )
    await interaction.response.send_message(embed=embed)


@grp_recompensa.command(name="diaria", description="Resgate sua recompensa diária")
async def diaria(interaction: discord.Interaction):
    check_user_exists(interaction.user.id)
    user_id = interaction.user.id
    agora = datetime.datetime.now()

    conn = connect()
    c = conn.cursor()
    c.execute("SELECT last_daily FROM usuarios WHERE user_id=?", (user_id,))
    res = c.fetchone()[0]

    if res:
        try:
            ultima_vez = datetime.datetime.fromisoformat(res)
            tempo_passado = agora - ultima_vez
            if tempo_passado < timedelta(hours=24):
                tempo_restante = timedelta(hours=24) - tempo_passado
                horas, resto = divmod(int(tempo_restante.total_seconds()), 3600)
                minutos, _ = divmod(resto, 60)
                await interaction.response.send_message(
                    f"⏳ Volte em **{horas}h {minutos}m**.", ephemeral=True
                )
                conn.close()
                return
        except ValueError:
            pass

    ganho = random.randint(50, 200)
    valor_fmt = formatar_moeda(ganho)
    c.execute(
        "UPDATE usuarios SET saldo = saldo + ?, last_daily = ? WHERE user_id=?",
        (ganho, agora.isoformat(), user_id),
    )
    conn.commit()
    conn.close()

    embed = discord.Embed(
        description=f"**{interaction.user.mention} ganhou {valor_fmt} {MOEDA_EMOJI}**\n\nVocê resgatou sua recompensa diária com sucesso!",
        color=0x00FF00,
    )
    await interaction.response.send_message(embed=embed)


@grp_recompensa.command(
    name="trabalhar", description="Trabalhe para ganhar moedas (1h cooldown)"
)
async def trabalhar(interaction: discord.Interaction):
    check_user_exists(interaction.user.id)
    user_id = interaction.user.id
    agora = datetime.datetime.now()

    conn = connect()
    c = conn.cursor()
    c.execute("SELECT last_work FROM usuarios WHERE user_id=?", (user_id,))
    res = c.fetchone()[0]

    if res:
        try:
            ultima_vez = datetime.datetime.fromisoformat(res)
            tempo_passado = agora - ultima_vez
            if tempo_passado < timedelta(hours=1):
                tempo_restante = timedelta(hours=1) - tempo_passado
                minutos = int(tempo_restante.total_seconds() / 60)
                await interaction.response.send_message(
                    f"⏳ Você está cansado. Descanse por **{minutos} minutos**.",
                    ephemeral=True,
                )
                conn.close()
                return
        except ValueError:
            pass

    ganho = random.randint(10, 50)
    c.execute(
        "UPDATE usuarios SET saldo = saldo + ?, last_work = ? WHERE user_id=?",
        (ganho, agora.isoformat(), user_id),
    )
    conn.commit()
    conn.close()

    frases = [
        "🧹 Você limpou o chão",
        "🍹 Você serviu mesas",
        "💻 Você programou um bot",
        "✂️ Você capinou um lote",
        "🪓 Você cortou uma árvore",
        "🚗 Você trabalhou de Uber",
    ]
    trabalho = random.choice(frases)

    embed = discord.Embed(
        description=f"**{trabalho}** e ganhou **{ganho}** {MOEDA_EMOJI}!",
        color=0x3498DB,
    )
    await interaction.response.send_message(embed=embed)
