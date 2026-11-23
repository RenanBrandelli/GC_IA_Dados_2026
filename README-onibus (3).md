# Não perca o ônibus (e leve o guarda-chuva) – Automação com n8n

**Autor:** Renan Brandelli Macedo

## 1. Problema
Todas as manhãs eu saio com pressa para pegar o ônibus e acabo esquecendo de
duas coisas: conferir a hora certa de sair de casa e olhar a previsão do tempo.
O resultado é perder o ônibus ou ser pego pela chuva sem guarda-chuva, e a rotina
do dia já começa atrasada ou desconfortável. Checar o clima manualmente toda
manhã é uma tarefa pequena, repetitiva e fácil de esquecer, ou seja, ideal para
automatizar.

## 2. Solução
Um fluxo no n8n que, de segunda a sexta às 6h, consulta a previsão do dia e me
envia uma mensagem no Telegram com:
- o horário do ônibus e o horário em que devo sair de casa;
- um aviso para levar guarda-chuva quando a chance de chuva é de 40% ou mais;
- a temperatura mínima e máxima do dia.

## 3. Como o fluxo funciona
| Etapa | Nó no n8n | O que faz |
|---|---|---|
| 1 | Dias úteis 6h (Schedule Trigger) | Dispara o fluxo de segunda a sexta às 6h |
| 2 | Previsão do tempo (HTTP Request) | Consulta a API Open-Meteo para Porto Alegre, com 3 tentativas em caso de falha |
| 3 | Tratar dados (Set) | Extrai chance de chuva, temperaturas e define os horários do ônibus |
| 4 | Vai chover? (IF) | Verifica se a chance de chuva é maior ou igual a 40% |
| 5a | Aviso com guarda-chuva (Telegram) | Mensagem pedindo para levar guarda-chuva |
| 5b | Aviso normal (Telegram) | Mensagem informando que não precisa de guarda-chuva |

Diagrama:
Dias úteis 6h → Previsão do tempo → Tratar dados → Vai chover? → Sim: aviso com guarda-chuva / Não: aviso normal

## 4. Tecnologias
- **n8n:** orquestração do fluxo
- **Open-Meteo API:** previsão do tempo, gratuita e sem chave
- **Telegram Bot API:** envio das notificações

## 5. Como usar
1. Importe `workflow-onibus.json` no n8n (Import from file).
2. Crie um bot no @BotFather e cadastre o token na credencial do Telegram.
3. Coloque o seu Chat ID nos dois nós do Telegram.
4. No nó "Tratar dados", ajuste `onibus` e `sair_as` para a sua rotina.
5. Salve e ative o workflow.

## 6. Validação da lógica
| Teste | Como foi feito | Resultado esperado | Resultado obtido |
|---|---|---|---|
| Dia com chuva | Limite da condição alterado de 40 para 0 | Mensagem com guarda-chuva | OK: ramo "verdadeiro" executado e mensagem "LEVE O GUARDA-CHUVA" recebida |
| Dia sem chuva | Execução manual com a previsão real do dia (chance de chuva 1%) | Mensagem normal | OK: mensagem "Pode sair sem guarda-chuva" recebida no Telegram |
| API fora do ar | URL inválida no nó de previsão | Nó com erro (e 3 tentativas configuradas) | OK: nó "Previsão do tempo" falhou com "recurso não encontrado" e o fluxo parou sem enviar mensagem |

## 7. Produção
O workflow foi salvo e ativado no n8n e roda sozinho nos dias úteis às 6h.
As execuções podem ser acompanhadas na aba Executions.

## 8. Resultado
Na execução de teste de 23/11/2026, o fluxo consultou a previsão (chance de chuva de 1%, temperatura de 19°C a 30°C) e enviou corretamente a mensagem do ônibus sem aviso de guarda-chuva.


Prints:
- [ok: print do canvas do workflow]
- [ok: print da aba Executions]
- [ok: print da mensagem no Telegram]

## 9. Melhorias futuras
- Usar a API da EPTC para mostrar o horário real do ônibus
- Avisar também em caso de frio forte ou calor extremo
- Enviar a mensagem no WhatsApp
- Mensagem diferente nos fins de semana
