# Demonstração do Marlon

O README apresenta o uso do bot com comandos reais. As capturas devem mostrar o resultado no Discord, em um servidor de teste, com conta e dados de demonstração. Não simule uma conversa como se fosse uma captura real.

## Imagens para a apresentação

| Captura | Conteúdo |
| --- | --- |
| Avatar | Imagem usada pelo Marlon no Discord, caso possa ser reutilizada no repositório. |
| Perfil | Resultado de `/perfil`, com bio fictícia e emblemas de demonstração. |
| Loja | Resultado de `/loja ver`, mostrando os botões e preços. |
| Coleção | Resultado de `/emblemas`, com emblemas e paginação quando houver. |
| Recompensa | Resultado de `/recompensa diaria`, mostrando a resposta ao comando. |

Prefira PNG legível, com a mensagem do bot e pouco espaço vazio. Recorte nomes de canais, mensagens de outras pessoas, convites e dados que não façam parte da demonstração. Não inclua tokens, códigos administrativos ativos, configurações de contas ou painéis de credenciais.

Guarde as imagens aprovadas em `docs/images/` e referencie-as no README por caminho relativo. A galeria só deve entrar quando os arquivos existirem; não deixe imagens quebradas nem capturas de outra versão identificadas como atuais.

## Percurso de cerca de dois minutos

1. Explique que o bot reúne economia virtual e emblemas de uma comunidade.
2. Mostre `/perfil` e os destaques.
3. Abra `/loja ver` e explique que saldo e inventário ficam no SQLite. Compra de demonstração deve usar apenas a conta de teste.
4. Mostre `/emblemas` e a navegação da coleção.
5. No repositório, abra `commands/`, `database.py` e os testes para explicar a organização.

As respostas de chat via Groq são opcionais. Não é necessário consumir a integração para apresentar os comandos, a interface e o armazenamento. A proposta de mudanças de segurança permanece separada na revisão de código.
