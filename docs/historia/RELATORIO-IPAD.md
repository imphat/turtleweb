# RELATÓRIO: correções do teste no iPad (iPad 7, iOS 18.7.4, Safari)

| Item | Causa | Correção | Teste |
|---|---|---|---|
| 5 e 6: "só a seta para cima funciona" | os programas só ligam `Up` (`referencia-controle-setas` liga `Up` e `Down`; os outros, só `Up`): **não é defeito**. ▼ funciona (testado) | só `TESTE-IPAD.md` | `test_seta_para_baixo_do_pad_funciona` |
| 5: segurar não repete | **defeito**: `onkey()` responde ao *soltar* a tecla e o botão repetia só *apertar* | segurar envia soltar+apertar a cada 120 ms (como o autorepeat do X11) | `test_segurar_o_botao_repete...`, `test_toque_curto_e_uma_acao_so` |
| 6: teclado do iPad não abre | **defeito**: o teclado só abre com um campo em foco | botão **⌨️ Teclado** (só em tela de toque, depois de `listen()`) + campo invisível que repassa as teclas; trata teclado com tecla "Unidentified" | `test_botao_teclado_abre...`, `..._so_com_listen_e_toque` |
| 7: `dot()` não aparece | **causa mais provável**: `dot()` é `forward(0)`, uma linha de comprimento zero com ponta redonda; o Safari não desenha traço de comprimento zero (o Chromium desenha). Não reproduzido no Safari (só há Chromium aqui) | a página desenha esse caso como círculo (ou quadrado, `projecting`) | `test_linha_de_comprimento_zero_vira_circulo` (simula o WebKit; falha sem a correção), `test_dot_colorido...` |
| 8: arraste trava | **defeito**: enquanto o tratador do arraste anima (`goto`), cada evento novo chamava o tratador *dentro* dele, cada vez mais fundo (pilha). Reproduzido: "aninhado" nos testes | tratadores não se aninham: entrada que chega durante um tratador espera ele acabar; só o último `mousemove` é mantido; a página também junta `mousemove` na fila de envio. Clique, soltar e teclas nunca são descartados | `test_arraste_com_animacao_lenta...` (falha sem a correção) |
| 8 (achado extra) | **defeito**: `turtle.onrelease()` liga `<Button1-ButtonRelease>`, forma que o canvas falso não entendia | normalizada | mesmo teste |
| 10: cancelar → pentágono | esperado (`except` do programa faz `lados = 5`) | — | — |
| 12: tela bloqueada | o programa segue rodando no servidor (esperado). No iOS o fluxo de eventos pode morrer sem aviso | ao voltar (`visibilitychange`, `pageshow`, `online`) a página reabre o fluxo com `?last=<último id>`, sem repetir nem perder | `test_pagina_volta_a_acompanhar_depois_de_dormir` |

Suíte inteira: 243 passou (inclui geometria × Tk real e corpus inteiro no navegador). Safari/iPad: ainda é preciso repetir os itens 5 a 8 e 12 no aparelho.
