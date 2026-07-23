"""Seed demo data for Residencial MVP."""

from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.database import SessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models.announcement import Announcement, AnnouncementPriority
from app.models.payment import ChargeStatus, FeePeriod, Payment, PaymentStatus, UnitCharge
from app.models.report import Report, ReportStatus
from app.models.unit import MemberRelation, Unit, UnitMember, UnitStatus
from app.models.user import User, UserRole


def seed(db: Session) -> None:
    if db.query(User).filter(User.email == "admin@example.com").first():
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
        ("ana@example.com", "Ana Pérez", "A-101"),
        ("luis@example.com", "Luis Gómez", "A-102"),
        ("maria@example.com", "María López", "B-201"),
        ("jose@example.com", "José Ruiz", "B-202"),
        ("sofia@example.com", "Sofía Díaz", "C-301"),
        ("pedro@example.com", "Pedro Santana", "C-302"),
    ]
    residents: list[User] = []
    for email, name, _ in residents_data:
        residents.append(
            User(
                email=email,
                password_hash=get_password_hash("vecino123"),
                name=name,
                role=UserRole.resident,
            )
        )

    db.add_all([admin, staff, *residents])
    db.flush()

    units: list[Unit] = []
    for _, _, code in residents_data:
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
    print("Seed OK")
    print("  admin@example.com / admin123")
    print("  staff@example.com / staff123")
    print("  ana@example.com / vecino123 (y otros vecinos)")


if __name__ == "__main__":
    # Ensure tables exist if migrations not run
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        seed(session)
    finally:
        session.close()
