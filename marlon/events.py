import discord
from discord import app_commands
import traceback
import asyncio
from .config import ID_CANAL_LOGS
from .runtime import bot
from .chat import chamar_groq_manual


@bot.event
async def on_ready():
    print(f"Bot online: {bot.user}")
    await bot.tree.sync()


@bot.event
async def on_error(event, *args, **kwargs):
    canal_logs = bot.get_channel(ID_CANAL_LOGS)
    erro = traceback.format_exc()
    print(f"ERRO NO EVENTO {event}: {erro}")
    if canal_logs:
        try:
            if len(erro) > 1900:
                erro = erro[:1900] + "..."
            await canal_logs.send(
                f"⚠️ **ERRO CRÍTICO NO EVENTO: {event}**\n```py\n{erro}\n```"
            )
        except:
            pass


@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction, error: app_commands.AppCommandError
):
    canal_logs = bot.get_channel(ID_CANAL_LOGS)
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(
            "❌ Você não tem permissão para isso.", ephemeral=True
        )
        return

    erro_fmt = "".join(
        traceback.format_exception(type(error), error, error.__traceback__)
    )
    print(f"ERRO COMANDO: {erro_fmt}")

    if canal_logs:
        if len(erro_fmt) > 1900:
            erro_fmt = erro_fmt[:1900] + "..."
        await canal_logs.send(
            f"⚠️ **ERRO NO COMANDO: /{interaction.command.name if interaction.command else 'Desconhecido'}**\nUsuário: {interaction.user}\n```py\n{erro_fmt}\n```"
        )
    try:
        if not interaction.response.is_done():
            await interaction.response.send_message(
                "❌ Ocorreu um erro interno.", ephemeral=True
            )
    except:
        pass


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    is_dm = isinstance(message.channel, discord.DMChannel)
    is_mentioned = bot.user in message.mentions

    if is_dm or is_mentioned:
        async with message.channel.typing():
            try:
                # Remove a menção
                user_message = message.content.replace(f"<@{bot.user.id}>", "").strip()
                if not user_message:
                    user_message = "Olá!"

                # CHAMA A FUNÇÃO MANUAL (Roda em thread separada para não travar o bot)
                resposta_final = await asyncio.to_thread(
                    chamar_groq_manual, user_message
                )

                if len(resposta_final) > 2000:
                    resposta_final = resposta_final[:1997] + "..."

                await message.reply(resposta_final)

            except Exception as e:
                print(f"Erro na IA (Requests): {e}")

                # LOG NO CANAL DO DISCORD
                canal_logs = bot.get_channel(ID_CANAL_LOGS)
                if canal_logs:
                    try:
                        erro_fmt = "".join(
                            traceback.format_exception(type(e), e, e.__traceback__)
                        )
                        if len(erro_fmt) > 1900:
                            erro_fmt = erro_fmt[:1900] + "..."

                        await canal_logs.send(
                            f"⚠️ **ERRO NA IA (REQUESTS)**\n"
                            f"Usuário: {message.author}\n"
                            f"Mensagem: `{user_message}`\n"
                            f"```py\n{erro_fmt}\n```"
                        )
                    except:
                        pass

    await bot.process_commands(message)
