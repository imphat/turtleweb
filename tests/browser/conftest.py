import os
import shutil
import sys
import threading
from pathlib import Path

import pytest
from werkzeug.serving import make_server

TESTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TESTS))
sys.path.insert(0, str(TESTS.parent / "demo"))

from helpers import CHILD_PYTHON, CORPUS  # noqa: E402

playwright_sync = pytest.importorskip("playwright.sync_api")


def chromium_path():
    p = Path.home() / ".chromium-path"
    if p.exists():
        return p.read_text().strip()
    import glob
    hits = glob.glob("/opt/pw-browsers/*/chrome-linux/*")
    return hits[0] if hits else None


@pytest.fixture(scope="session")
def programs_dir(tmp_path_factory):
    d = tmp_path_factory.mktemp("programs")
    for src in list(CORPUS.glob("*.py")) + list((TESTS / "programs").glob("*.py")):
        shutil.copy(src, d / src.name)
    return d


def _serve(programs_dir, env):
    from app import create_app
    app = create_app(str(programs_dir), python=CHILD_PYTHON, env=env)
    srv = make_server("127.0.0.1", 0, app, threaded=True)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


@pytest.fixture(scope="session")
def server(programs_dir):
    """Demo server whose programs skip the animation delays (fast tests)."""
    srv = _serve(programs_dir, dict(os.environ, TURTLEWEB_NO_DELAY="1"))
    yield "http://127.0.0.1:%d" % srv.server_port
    srv.shutdown()


@pytest.fixture(scope="session")
def server_real_speed(programs_dir):
    """Demo server with the real Tk timing."""
    srv = _serve(programs_dir, None)
    yield "http://127.0.0.1:%d" % srv.server_port
    srv.shutdown()


@pytest.fixture(scope="session")
def browser():
    exe = chromium_path()
    if not exe or not os.path.exists(exe):
        pytest.skip("Chromium não encontrado")
    with playwright_sync.sync_playwright() as p:
        b = p.chromium.launch(executable_path=exe)
        yield b
        b.close()


class Run:
    """A page running one program, with helpers to look at the canvas."""

    def __init__(self, browser, server, prog, **ctx):
        self.context = browser.new_context(**ctx)
        self.page = self.context.new_page()
        self.errors = []
        self.page.on("pageerror", lambda e: self.errors.append(str(e)))
        self.page.goto("%s/?prog=%s" % (server, prog))

    def wait_state(self, *states, timeout=30000):
        sel = ",".join('.tw[data-state="%s"]' % s for s in states)
        self.page.wait_for_selector(sel, timeout=timeout)

    def state(self):
        return self.page.get_attribute(".tw", "data-state")

    def pixel(self, x, y):
        """RGB at turtle coordinates (x right, y up)."""
        return self.page.evaluate(
            """([x, y]) => { const c = document.querySelector('.tw canvas');
            const s = c.width / parseFloat(c.style.width);
            const d = c.getContext('2d').getImageData(Math.round((c.width/s/2 + x) * s),
                Math.round((c.height/s/2 - y) * s), 1, 1).data; return [d[0], d[1], d[2]]; }""", [x, y])

    def has_ink(self):
        """True if any pixel differs from the top-left one (the background)."""
        return self.page.evaluate("""() => { const c = document.querySelector('.tw canvas');
            const d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data;
            for (let i = 4; i < d.length; i += 4)
              if (d[i] !== d[0] || d[i+1] !== d[1] || d[i+2] !== d[2]) return true;
            return false; }""")

    def close(self):
        self.context.close()


@pytest.fixture
def run(browser, server):
    runs = []

    def start(prog, base=None, **ctx):
        r = Run(browser, base or server, prog, **ctx)
        runs.append(r)
        return r

    yield start
    for r in runs:
        r.close()


def near(a, b, tol=30):
    return all(abs(p - q) <= tol for p, q in zip(a, b))
