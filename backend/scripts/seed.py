"""Seed demo data for Residencial MVP."""

from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.database import SessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models.announcement import Announcement, AnnouncementPriority
from app.models.payment import ChargeStatus, FeePeriod, Payment, PaymentStatus, UnitCharge
from app.models.report import Report, ReportStatus
from app.models.service import ServiceCategory, ServiceProvider
from app.models.unit import MemberRelation, Unit, UnitMember, UnitStatus
from app.models.user import User, UserRole
from app.services.schema import ensure_schema


def seed_service_directory(db: Session, admin_id: int | None = None) -> None:
    if db.query(ServiceProvider).count() > 0:
        return
    providers = [
        ("Plomería Rápida RD", ServiceCategory.plomeria, "809-555-1001", "Emergencias 24h, fugas y destapes"),
        ("ElectroHogar López", ServiceCategory.electricidad, "809-555-1002", "Instalaciones y fallas eléctricas"),
        ("Taller Mecánico del Este", ServiceCategory.mecanica, "809-555-1003", "Mecánica ligera y baterías"),
        ("Cerrajería Express", ServiceCategory.cerrajeria, "809-555-1004", "Apertura de puertas y cambios de bombín"),
        ("FrioTotal Aires", ServiceCategory.aires, "809-555-1005", "Mantenimiento e instalación de AC"),
        ("Limpieza Brillante", ServiceCategory.limpieza, "809-555-1006", "Limpieza profunda de apartamentos"),
        ("Pinturas del Caribe", ServiceCategory.pintura, "809-555-1007", "Pintura interior y exterior"),
        ("Jardines Verde Vivo", ServiceCategory.jardineria, "809-555-1008", "Poda y mantenimiento de áreas verdes"),
    ]
    for name, category, phone, description in providers:
        db.add(
            ServiceProvider(
                name=name,
                category=category,
                phone=phone,
                whatsapp=phone,
                description=description,
                active=True,
                created_by=admin_id,
            )
        )
    db.commit()
    print("Service directory seeded.")


def seed(db: Session) -> None:
    if db.query(User).filter(User.email == "admin@example.com").first():
        admin = db.query(User).filter(User.email == "admin@example.com").first()
        seed_service_directory(db, admin.id if admin else None)
        print("Seed already applied.")
        return

    admin = User(
        email="admin@example.com",
        password_hash=get_password_hash("admin123"),
        name="Admin Junta",
        phone="809-000-0001",
        role=UserRole.admin,
    )
    staff = User(
        email="staff@example.com",
        password_hash=get_password_hash("staff123"),
        name="Carlos Portería",
        phone="809-000-0002",
        role=UserRole.staff,
    )
    residents_data = [
        ("ana@example.com", "Ana Pérez", "A-101", "809-111-0101", "809-111-0102"),
        ("luis@example.com", "Luis Gómez", "A-102", "809-111-0201", None),
        ("maria@example.com", "María López", "B-201", "809-111-0301", "809-111-0302"),
        ("jose@example.com", "José Ruiz", "B-202", "809-111-0401", None),
        ("sofia@example.com", "Sofía Díaz", "C-301", "809-111-0501", None),
        ("pedro@example.com", "Pedro Santana", "C-302", "809-111-0601", "809-111-0602"),
    ]
    residents: list[User] = []
    for email, name, _, phone, phone2 in residents_data:
        residents.append(
            User(
                email=email,
                password_hash=get_password_hash("vecino123"),
                name=name,
                phone=phone,
                phone_secondary=phone2,
                whatsapp=phone,
                show_in_directory=True,
                role=UserRole.resident,
            )
        )

    db.add_all([admin, staff, *residents])
    db.flush()

    units: list[Unit] = []
    for _, _, code, _, _ in residents_data:
        block, number = code.split("-")
        units.append(Unit(code=code, block=block, number=number, floor=number[0], status=UnitStatus.active))
    db.add_all(units)
    db.flush()

    for user, unit in zip(residents, units):
        db.add(UnitMember(user_id=user.id, unit_id=unit.id, relation=MemberRelation.owner))

    today = date.today()
    periods = []
    for i in range(2, -1, -1):
        d = today.replace(day=1) - timedelta(days=30 * i)
        periods.append(
            FeePeriod(
                year=d.year,
                month=d.month,
                amount_default=Decimal("3500.00"),
                due_date=d.replace(day=10) if d.day >= 10 else d,
                label=f"Cuota {d.month:02d}/{d.year}",
            )
        )
    db.add_all(periods)
    db.flush()

    # Latest period: mix of paid / pending / overdue / submitted
    latest = periods[-1]
    statuses = [
        ChargeStatus.paid,
        ChargeStatus.paid,
        ChargeStatus.pending,
        ChargeStatus.overdue,
        ChargeStatus.submitted,
        ChargeStatus.pending,
    ]
    for unit, st in zip(units, statuses):
        charge = UnitCharge(unit_id=unit.id, period_id=latest.id, amount=latest.amount_default, status=st)
        db.add(charge)
        db.flush()
        if st == ChargeStatus.paid:
            db.add(
                Payment(
                    charge_id=charge.id,
                    amount=charge.amount,
                    method="transferencia",
                    submitted_by=residents[units.index(unit)].id,
                    status=PaymentStatus.approved,
                    reviewed_by=admin.id,
                )
            )
        elif st == ChargeStatus.submitted:
            db.add(
                Payment(
                    charge_id=charge.id,
                    amount=charge.amount,
                    method="transferencia",
                    submitted_by=residents[units.index(unit)].id,
                    status=PaymentStatus.submitted,
                )
            )

    # Previous periods mostly paid
    for period in periods[:-1]:
        for i, unit in enumerate(units):
            st = ChargeStatus.paid if i < 5 else ChargeStatus.overdue
            charge = UnitCharge(unit_id=unit.id, period_id=period.id, amount=period.amount_default, status=st)
            db.add(charge)
            db.flush()
            if st == ChargeStatus.paid:
                db.add(
                    Payment(
                        charge_id=charge.id,
                        amount=charge.amount,
                        method="efectivo",
                        submitted_by=residents[i].id,
                        status=PaymentStatus.approved,
                        reviewed_by=admin.id,
                    )
                )

    db.add(
        Report(
            unit_id=units[0].id,
            created_by=residents[0].id,
            assigned_to=staff.id,
            category="Mantenimiento",
            title="Fuga en área común",
            description="Hay una fuga de agua cerca del lobby A.",
            location="Lobby Torre A",
            status=ReportStatus.assigned,
        )
    )
    db.add(
        Report(
            unit_id=units[2].id,
            created_by=residents[2].id,
            category="Ruido",
            title="Ruido excesivo en horario nocturno",
            description="Se escucha música alta después de las 11pm.",
            location="Torre B",
            status=ReportStatus.open,
        )
    )
    db.add(
        Announcement(
            title="Reunión de junta de vecinos",
            body="La próxima asamblea será el sábado a las 10:00 AM en el salón comunal.",
            priority=AnnouncementPriority.high,
            created_by=admin.id,
        )
    )
    db.add(
        Announcement(
            title="Mantenimiento de ascensores",
            body="El martes se realizará mantenimiento preventivo de 9:00 a 12:00.",
            priority=AnnouncementPriority.normal,
            created_by=admin.id,
        )
    )

    db.commit()
    seed_service_directory(db, admin.id)
    print("Seed OK")
    print("  admin@example.com / admin123")
    print("  staff@example.com / staff123")
    print("  ana@example.com / vecino123 (y otros vecinos)")


if __name__ == "__main__":
    ensure_schema()
    session = SessionLocal()
    try:
        seed(session)
    finally:
        session.close()
