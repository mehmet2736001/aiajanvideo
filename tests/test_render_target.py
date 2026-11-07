import pytest

from core.orchestrator import GENERIC_COMPOSITION, GENERIC_ENTRY, ProductionError, resolve_render_target
from core.utils import InvalidSlugError


def test_existing_custom_projects_use_their_own_entry():
    t = resolve_render_target("hud-112")
    assert t["entry"] == "src/hud-112/index.ts" and t["composition"] == "Hud112" and not t["generic"]
    t = resolve_render_target("olum-son-mu")
    assert t["composition"] == "OlumSonMu"


def test_new_slug_uses_generic_template_never_another_project():
    t = resolve_render_target("yepyeni-konu")
    assert t["generic"] and t["entry"] == GENERIC_ENTRY and t["composition"] == GENERIC_COMPOSITION


@pytest.mark.parametrize("bad", ["", "..", "../src", "a/b"])
def test_bad_slug_rejected(bad):
    with pytest.raises(InvalidSlugError):
        resolve_render_target(bad)
