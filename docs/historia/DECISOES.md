# Decisões do João após o M0

1. **Caminho aprovado:** o `turtle` da biblioteca padrão, sem alteração, com um `tkinter` falso (canvas falso).
2. **Velocidade × fidelidade:** fidelidade por padrão (mesma duração do Tk). A página terá um botão "Mais rápido" que reduz o
   atraso sem mudar o desenho. A seção 7, item 5, do `SPEC.md` passa a ser: "tão rápido quanto o Tk, com opção de acelerar".
3. **`input()` dos programas é do app:** o canal NÃO usa o stdin do programa. Usa um socket local em 127.0.0.1, cuja porta chega
   por variável de ambiente (funciona em Linux, macOS e Windows).
4. **Entrada no programa:** `turtleweb.install()` injeta o `tkinter` falso em `sys.modules` antes de o `turtle` ser importado; o
   app chama essa função por um `sitecustomize`, ligado por variável de ambiente. Não se cria um `turtle.py` próprio, salvo motivo
   concreto registrado no relatório.
5. **Cores:** todo nome de cor vira hexadecimal com a tabela de cores do Tk (`green` = `#00ff00`).
   - **Ajuste registrado no M1 (precisa do João):** o Tk 8.6.14 real deste ambiente (o que o Python 3.12 usa) responde
     `green` = `#008000` (e `gray`, `maroon`, `purple` também têm o valor do CSS); `lime` = `#00ff00`. O `#00ff00` vinha do
     `rgb.txt` do X11, que o Tk atual não usa. A tabela embutida (`turtleweb/_colors.py`) foi gerada do Tk real por
     `tools/gen_colors.py`, para o navegador mostrar o que o Tk mostraria hoje. Se preferir o valor antigo, é só
     trocar 4 linhas dessa tabela.
6. **`experimentos/`** fica até o M6 e é removida no pacote final.
