import base64

PHONE = "+31600000001"
IMG = base64.b64encode(b"fake-jpeg").decode()


def send(client, text="", photos=()):
    body = {
        "sender": PHONE,
        "text": text,
        "attachments": [{"filename": f, "media_type": "image/jpeg", "data_b64": IMG} for f in photos],
    }
    response = client.post("/tenants/1/channels/app/inbound", json=body)
    assert response.status_code == 200
    return response.json()


def test_unknown_sender_is_rejected(client, job):
    response = client.post("/tenants/1/channels/app/inbound", json={"sender": "+31699999999", "text": "hoi"})
    assert "niet bekend" in response.json()["reply"]


def test_photo_is_matched_and_typeplate_data_extracted(client, job):
    result = send(client, "typeplaatje buitenunit", ["IMG_001.jpg"])
    assert "✔ Foto typeplaatje buitenunit" in result["reply"]
    wo = client.get(f"/jobs/{job.id}/work-order").json()
    item = wo["items"]["foto_typeplaatje_buitenunit"]
    assert item["done"] and item["extracted"]["serienummer"]


def test_blurry_photo_is_refused(client, job):
    result = send(client, "typeplaatje wazig", ["IMG_002.jpg"])
    assert "❌" in result["reply"]
    wo = client.get(f"/jobs/{job.id}/work-order").json()
    assert not wo["items"]["foto_typeplaatje_buitenunit"]["done"]


def test_technician_warned_when_leaving_incomplete(client, job):
    result = send(client, "Vacuumtest 2 mbar 15 min. Ik ben klaar")
    assert "Nog niet vertrekken" in result["reply"]
    assert "Foto meterkast met aangesloten groep" in result["missing"]


def test_complete_work_order_submits_and_invoice_needs_approval(client, container, job):
    for caption in ["buitenunit", "typeplaatje", "binnenunit", "leidingwerk", "meterkast"]:
        send(client, caption, [f"{caption}.jpg"])
    send(client, "Vacuumtest 2 mbar. Druktest 30 bar. Koudemiddel 0 kg")
    result = send(client, "Klant heeft getekend, ik ben klaar")

    assert "Werkbon compleet" in result["reply"]
    assert result["missing"] == []
    assert container.field_service.work_orders[0].job_ref == "P-2026-0042"
    assert len(container.field_service.work_orders[0].attachments) == 5

    # Factuur gaat pas naar Exact na goedkeuring door kantoor.
    assert container.accounting.invoices == []
    approvals = client.get("/tenants/1/approvals").json()
    assert [a["kind"] for a in approvals] == ["factuur_concept"]
    decision = client.post(f"/approvals/{approvals[0]['id']}/decision", json={"approve": True, "user": "kantoor"})
    assert decision.json()["result"]["exact_ref"].startswith("EXACT-CONCEPT")
    assert container.accounting.invoices[0].lines[0].unit_price == 3950.0

    # Dubbel goedkeuren kan niet.
    again = client.post(f"/approvals/{approvals[0]['id']}/decision", json={"approve": True, "user": "kantoor"})
    assert again.status_code == 409
