# Comandos do Marlon

Os 30 comandos abaixo foram extraídos do registro local do bot, sem conectar ao Discord. A coluna de administração indica a intenção do comando original; a checagem na execução é uma proposta separada em `security/hardening`.

| Comando | O que faz | Acesso pretendido |
| --- | --- | --- |
| `/bio` | Muda bio | Membros |
| `/codigo desativar` | Desativar código | Administração |
| `/codigo excluir` | Excluir código permanentemente | Administração |
| `/codigo lista` | Listar códigos | Administração |
| `/criar anuncio_codigo` | Anuncia um código com template de emblema | Administração |
| `/criar cineminha` | Cria o anúncio do Cineminha | Administração |
| `/criar codigo` | Criar código | Administração |
| `/criar emblema` | Criar novo emblema | Administração |
| `/criar json` | Criar Embed usando JSON do Discohook | Administração |
| `/dar emblema` | Dar emblema (Deixe usuário vazio para TODOS) | Administração |
| `/dar moedas` | Adicionar moedas | Administração |
| `/destaque definir` | Define os destaques do seu perfil | Membros |
| `/destaque limpar` | Remove todos os destaques do seu perfil | Membros |
| `/economia apostar` | Aposte no Cara ou Coroa (2x) | Membros |
| `/economia slots` | Jogue no caça-níquel (Custo: aposta) | Membros |
| `/economia transferir` | Transfere moedas para outro usuário | Membros |
| `/emblema editar` | Editar emblema | Administração |
| `/emblema excluir` | Excluir emblema | Administração |
| `/emblema lista` | Lista todos os emblemas | Membros |
| `/emblema ver` | Ver detalhes de um emblema | Membros |
| `/emblemas` | Lista todos os emblemas | Membros |
| `/loja gerenciar` | Adicionar ou Remover emblema da loja | Administração |
| `/loja ver` | Ver a loja | Membros |
| `/perfil` | Exibe seu perfil completo | Membros |
| `/ranking` | Veja o ranking do servidor | Membros |
| `/recompensa diaria` | Resgate sua recompensa diária | Membros |
| `/recompensa trabalhar` | Trabalhe para ganhar moedas (1h cooldown) | Membros |
| `/remover emblema` | Remover emblema (Deixe usuário vazio para TODOS) | Administração |
| `/remover moedas` | Remover moedas | Administração |
| `/resgatar` | Resgatar código | Membros |

## Regras que vale conhecer

- `/recompensa diaria`: intervalo de 24 horas desde o último resgate, não uma virada fixa de calendário.
- `/recompensa trabalhar`: intervalo de uma hora.
- `/economia apostar`: acerto soma o valor apostado ao saldo; erro desconta esse valor.
- `/economia slots`: três símbolos iguais pagam 5 vezes a aposta; dois iguais, 2 vezes. A aposta é descontada do pagamento para calcular o resultado líquido.
- `/destaque definir`: usa no máximo três nomes separados por vírgula e aceita emblemas que o usuário possui.
- `/criar codigo`: limite `-1` significa ilimitado; validade usa `DD/MM/AAAA HH:MM` no fuso do processo.
- `/dar emblema` e `/remover emblema`: sem usuário-alvo, aplicam a operação aos usuários registrados; a opção `TODOS` também amplia o conjunto de emblemas. Confira os parâmetros antes de executar.
- `/criar cineminha`: monta o anúncio e o link informado; não cria automaticamente um evento agendado no Discord.
- `/criar json`: recebe o JSON em um modal e envia conteúdo/embeds. Não faz integração de conta com o Discohook.
- Rankings consultam o banco da instância, não filtram membros por servidor.
