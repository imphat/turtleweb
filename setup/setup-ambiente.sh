#!/usr/bin/env bash
# Script de configuração do ambiente da nuvem (cole no campo "setup script" do ambiente).
# Precisa terminar em cerca de 5 minutos para o resultado ficar em cache. Cada etapa é tolerante a falha para o script
# não derrubar o ambiente: o que falhar fica registrado em /tmp/setup-turtleweb.log e a sessão de teste (prompts/ambiente.md)
# diz o que funcionou.
set +e
LOG=/tmp/setup-turtleweb.log
: > "$LOG"
step() { echo "== $*" | tee -a "$LOG"; }

step "tela virtual e Tkinter (para comparar com o turtle de verdade)"
(sudo -n true 2>/dev/null && SUDO=sudo || SUDO="")
$SUDO apt-get update -qq >>"$LOG" 2>&1
$SUDO apt-get install -y -qq xvfb python3-tk fonts-dejavu-core >>"$LOG" 2>&1 || echo "FALHOU: apt xvfb/python3-tk" | tee -a "$LOG"

step "dependências Python"
python3 -m pip install --quiet pytest flask playwright >>"$LOG" 2>&1 || echo "FALHOU: pip" | tee -a "$LOG"

step "Chromium sem janela (Playwright)"
python3 -m playwright install --with-deps chromium >>"$LOG" 2>&1 \
  || python3 -m playwright install chromium >>"$LOG" 2>&1 \
  || echo "FALHOU: playwright install (se for a rede, libere o domínio de download no acesso à rede do ambiente)" | tee -a "$LOG"

step "fim"
tail -n 20 "$LOG"
exit 0
