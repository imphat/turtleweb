"""Roda todo o corpus pelo canvas falso, sem navegador e sem atrasos.
Uso: python rodar_corpus.py <python-do-filho>  (arquivos que o programa grava vão para um diretório temporário)"""
import json, os, subprocess, sys, tempfile, time
root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
idx = json.load(open(f"{root}/corpus/index.json"))
run = f"{root}/experimentos/m0_canvas_falso/run.py"
py = sys.argv[1]
ok = 0
for e in idx:
    prog = f"{root}/corpus/{e['programa']}"
    t0 = time.monotonic()
    try:
        r = subprocess.run([py, "-u", run, prog], stdin=subprocess.DEVNULL, capture_output=True, text=True,
                           timeout=20, cwd=tempfile.mkdtemp(), env=dict(os.environ, TW_NO_DELAY="1", PYTHONUTF8="1"))
    except subprocess.TimeoutExpired:
        print(f"TIMEOUT {e['programa']} ({e['tipo']})"); continue
    end = [l for l in r.stdout.splitlines() if l.startswith("@@TW@@ ") and '"end"' in l]
    info = json.loads(end[-1][7:])[-1] if end else None
    err = r.stderr.strip().splitlines()[-1] if r.stderr.strip() else ""
    status = "OK" if info and info[1] == 0 else "ERRO"
    ok += status == "OK"
    print(f"{status:5} {e['programa']:42} {e['tipo'][:13]:13} {time.monotonic()-t0:5.1f}s ops={info[2]['ops'] if info else '-':>6} bytes={info[2]['bytes'] if info else '-':>8} desconhecidos={info[3] if info else '-'} {err[:110]}")
print(f"{ok}/{len(idx)} OK")
