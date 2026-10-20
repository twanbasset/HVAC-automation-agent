from hvac_agent.checklists import ItemKind, load_checklists
from hvac_agent.config import ROOT


def test_all_checklists_load_with_unique_keys():
    checklists = load_checklists(ROOT / "config" / "checklists")
    assert {"warmtepomp_installatie", "airco_installatie", "cv_onderhoud"} <= checklists.keys()
    for checklist in checklists.values():
        keys = [i.key for i in checklist.items]
        assert len(keys) == len(set(keys))
        assert checklist.items_of(ItemKind.PHOTO)
