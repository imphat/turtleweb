#!/usr/bin/env bash
# Script de configuração do ambiente da nuvem (cole no campo "setup script" do ambiente).
# Verificado na sessão de teste de 2026-10-06: o python3 padrão (3.13) NÃO tem Tkinter; o python3.12 tem. O Chromium já vem
# instalado em /opt/pw-browsers (o download do Playwright é bloqueado na rede Trusted, então não tentamos baixar).
# Precisa terminar em cerca de 5 minutos para o resultado ficar em cache. Tolerante a falha: o que falhar fica no log.
set +e
LOG=/tmp/setup-turtleweb.log
: > "$LOG"
step() { echo "== $*" | tee -a "$LOG"; }
(sudo -n true 2>/dev/null && SUDO=sudo || SUDO="")

step "tela virtual e Tkinter do Python 3.12 (para comparar com o turtle de verdade)"
$SUDO apt-get update -qq >>"$LOG" 2>&1
$SUDO apt-get install -y -qq xvfb python3.12-tk python3.12-venv fonts-dejavu-core >>"$LOG" 2>&1 \
  || echo "FALHOU: apt (xvfb, python3.12-tk, python3.12-venv)" | tee -a "$LOG"

step "ambiente Python 3.12 com Tkinter e as dependências (~/.venvs/turtleweb)"
python3.12 -m venv "$HOME/.venvs/turtleweb" >>"$LOG" 2>&1 || echo "FALHOU: venv" | tee -a "$LOG"
"$HOME/.venvs/turtleweb/bin/pip" install --quiet pytest flask playwright >>"$LOG" 2>&1 || echo "FALHOU: pip" | tee -a "$LOG"
"$HOME/.venvs/turtleweb/bin/python" -c "import tkinter" >>"$LOG" 2>&1 || echo "FALHOU: tkinter no python 3.12" | tee -a "$LOG"

step "Chromium que já existe (sem baixar nada)"
CHROME="$(find /opt/pw-browsers -type f \( -name chrome -o -name headless_shell \) 2>/dev/null | head -n 1)"
if [ -n "$CHROME" ]; then
  echo "$CHROME" > "$HOME/.chromium-path"
  echo "Chromium: $CHROME" | tee -a "$LOG"
else
  echo "FALHOU: não achei o Chromium em /opt/pw-browsers" | tee -a "$LOG"
fi

step "fim"
tail -n 20 "$LOG"
exit 0
