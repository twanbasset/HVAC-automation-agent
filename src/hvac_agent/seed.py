"""Demo-data: één installateur, één monteur en een warmtepompklus in uitvoering.
Gebruik: python -m hvac_agent.seed"""

from sqlalchemy.orm import Session

from .models import Job, JobStatus, Technician, Tenant


def seed(session: Session) -> Job:
    tenant = Tenant(name="Demo Installatietechniek B.V.")
    session.add(tenant)
    session.flush()
    technician = Technician(tenant_id=tenant.id, name="Monteur Demo", phone="+31600000001", skills=["F-gassen", "warmtepomp"])
    session.add(technician)
    session.flush()
    job = Job(
        tenant_id=tenant.id,
        external_ref="P-2026-0042",
        job_type="warmtepomp_installatie",
        customer_name="Fam. Jansen",
        address="Voorbeeldstraat 1, Utrecht",
        technician_id=technician.id,
        status=JobStatus.IN_PROGRESS,
        invoice_lines=[
            {"omschrijving": "Hybride warmtepomp 4 kW", "aantal": 1, "prijs": 3950.0},
            {"omschrijving": "Installatie en inbedrijfstelling", "aantal": 1, "prijs": 1250.0},
        ],
    )
    session.add(job)
    session.flush()
    return job


if __name__ == "__main__":
    from .config import settings
    from .db import make_session_factory

    with make_session_factory(settings.database_url).begin() as session:
        job = seed(session)
        print(f"Demo-klus aangemaakt: job_id={job.id}, monteur +31600000001")
