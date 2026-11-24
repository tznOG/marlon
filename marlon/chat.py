from .config import MOEDA_EMOJI, GROQ_API_KEY
import requests

SYSTEM_INSTRUCTION = f"""
Você é o Marlon, um bot de economia e emblemas colecionaveis para Discord.
Sua moeda é: {MOEDA_EMOJI} (Moedas).
Você foi baseado no personagem Loc Dog do filme "Don't Be a Menace" (Vizinhança do Barulho).
Seja engraçado, use gírias, seja maluco, seja porra louca, divertido e prestativo.
Sem ser muito cringe e vergonhoso, não fique repetindo tantas coisas sobre você.
Responda dúvidas sobre seus comandos de forma descontraída.

SEUS COMANDOS DISPONÍVEIS:
- /perfil, /bio, /emblemas, /emblema ver, /resgatar, /ranking, /loja ver.
- /recompensa diaria, /recompensa trabalhar.
- /economia apostar, /economia slots, /economia transferir.
- /destaque definir, /destaque limpar.
"""


def chamar_groq_manual(user_message):
    if not GROQ_API_KEY:
        return "O chat ainda não está configurado. Os comandos do bot continuam disponíveis."
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "messages": [
            {"role": "system", "content": SYSTEM_INSTRUCTION},
            {"role": "user", "content": user_message},
        ],
        # Usando o modelo versátil e atualizado
        "model": "llama-3.3-70b-versatile",
        "temperature": 0.7,
        "max_tokens": 1024,
    }

    try:
        response = requests.post(
            url, headers=headers, json=data, timeout=(5, 20), allow_redirects=False
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            print(f"Falha na Groq: HTTP {response.status_code}")
            return "O chat está indisponível no momento. Tente novamente mais tarde."
    except Exception as e:
        print(f"Falha na Groq: {type(e).__name__}")
        return "O chat está indisponível no momento. Tente novamente mais tarde."
