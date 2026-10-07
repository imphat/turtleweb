"""O histórico de uma execução longa vira um retrato do desenho (memória limitada, página atrasada começa dele)."""
import json

from turtleweb import session as S


def _create(i):
    return ["create", i, "line", [0, 0, i, i], {"fill": "#000000"}]


def test_snapshot_reproduz_o_desenho():
    m = S._Model()
    for op in ([_create(1), _create(2), _create(3), ["coords", 1, [5, 5, 9, 9]], ["config", 2, {"width": 3}],
                ["raise", 1], ["delete", 3], ["bg", "#ffffe0"], ["geometry", 500, 400], ["listen"]]):
        m.apply(op)
    snap = m.snapshot()
    assert snap["reset"] is True
    ops = snap["ops"]
    assert ["create", 2, "line", [0, 0, 2, 2], {"fill": "#000000", "width": 3}] in ops
    assert ops.index(["create", 2, "line", [0, 0, 2, 2], {"fill": "#000000", "width": 3}]) < \
        ops.index(["create", 1, "line", [5, 5, 9, 9], {"fill": "#000000"}])      # item 1 was raised
    assert not any(o[:2] == ["create", 3] for o in ops)
    assert ["geometry", 500, 400] in ops and ["bg", "#ffffe0"] in ops and ops[-1] == ["listen"]


def test_historico_e_compactado_e_ids_continuam(monkeypatch):
    monkeypatch.setattr(S, "COMPACT_AT", 50)
    s = S.Session()
    for i in range(1, 201):
        s._model.apply(_create(i))
        s._push({"t": "ops", "ops": [_create(i)]})
        if len(s.events) > S.COMPACT_AT:
            s._compact()
    assert len(s.events) <= 52
    total = s._dropped + len(s.events)
    assert total == 200
    # a page that is far behind starts from the snapshot, with the right (absolute) ids
    first = next(iter(s.iter_events(0)))
    assert first[0] >= 0 and json.loads(first[1])["reset"] is True
    # a page that is up to date gets nothing old
    s._set_state("ended", 0)
    ids = [i for i, _ in (x for x in s.iter_events(total) if x)]
    assert ids == [total]
