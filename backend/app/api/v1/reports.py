from fastapi import APIRouter, File, HTTPException, UploadFile, status
from sqlalchemy.orm import joinedload

from app.core.deps import AdminUser, CurrentUser, DbSession, StaffOrAdmin
from app.models.report import Report, ReportStatus, ReportUpdate
from app.models.user import User, UserRole
from app.models.unit import Unit
from app.schemas.report import ReportAssign, ReportCreate, ReportOut, ReportUpdateCreate, ReportUpdateOut
from app.services.uploads import save_upload

router = APIRouter(prefix="/reports", tags=["reports"])


def serialize_report(report: Report, users: dict[int, User], units: dict[int, Unit]) -> ReportOut:
    creator = users.get(report.created_by)
    assignee = users.get(report.assigned_to) if report.assigned_to else None
    unit = units.get(report.unit_id) if report.unit_id else None
    return ReportOut(
        id=report.id,
        unit_id=report.unit_id,
        unit_code=unit.code if unit else None,
        created_by=report.created_by,
        creator_name=creator.name if creator else None,
        assigned_to=report.assigned_to,
        assignee_name=assignee.name if assignee else None,
        category=report.category,
        title=report.title,
        description=report.description,
        location=report.location,
        photo_url=report.photo_url,
        status=report.status,
        created_at=report.created_at,
        updated_at=report.updated_at,
        updates=[ReportUpdateOut.model_validate(u) for u in report.updates],
    )


def load_maps(db, reports: list[Report]):
    user_ids = set()
    unit_ids = set()
    for r in reports:
        user_ids.add(r.created_by)
        if r.assigned_to:
            user_ids.add(r.assigned_to)
        if r.unit_id:
            unit_ids.add(r.unit_id)
        for u in r.updates:
            user_ids.add(u.author_id)
    users = {u.id: u for u in db.query(User).filter(User.id.in_(user_ids or [-1])).all()}
    units = {u.id: u for u in db.query(Unit).filter(Unit.id.in_(unit_ids or [-1])).all()}
    return users, units


@router.get("", response_model=list[ReportOut])
def list_reports(db: DbSession, user: CurrentUser, status_filter: ReportStatus | None = None):
    q = db.query(Report).options(joinedload(Report.updates))
    if user.role == UserRole.resident:
        q = q.filter(Report.created_by == user.id)
    elif user.role == UserRole.staff:
        q = q.filter(Report.assigned_to == user.id)
    if status_filter:
        q = q.filter(Report.status == status_filter)
    reports = q.order_by(Report.created_at.desc()).all()
    users, units = load_maps(db, reports)
    return [serialize_report(r, users, units) for r in reports]


@router.post("", response_model=ReportOut, status_code=status.HTTP_201_CREATED)
async def create_report(
    db: DbSession,
    user: CurrentUser,
    category: str,
    title: str,
    description: str,
    unit_id: int | None = None,
    location: str | None = None,
    photo: UploadFile | None = File(None),
):
    if user.role == UserRole.resident:
        unit_ids = [m.unit_id for m in user.memberships]
        if unit_id and unit_id not in unit_ids:
            raise HTTPException(status_code=403, detail="Sin permiso sobre esa vivienda")
        if not unit_id and unit_ids:
            unit_id = unit_ids[0]
    photo_url = None
    if photo and photo.filename:
        photo_url = await save_upload(photo, "reports")
    report = Report(
        unit_id=unit_id,
        created_by=user.id,
        category=category,
        title=title,
        description=description,
        location=location,
        photo_url=photo_url,
        status=ReportStatus.open,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    report = db.query(Report).options(joinedload(Report.updates)).filter(Report.id == report.id).one()
    users, units = load_maps(db, [report])
    return serialize_report(report, users, units)


@router.post("/json", response_model=ReportOut, status_code=status.HTTP_201_CREATED)
def create_report_json(payload: ReportCreate, db: DbSession, user: CurrentUser):
    unit_id = payload.unit_id
    if user.role == UserRole.resident:
        unit_ids = [m.unit_id for m in user.memberships]
        if unit_id and unit_id not in unit_ids:
            raise HTTPException(status_code=403, detail="Sin permiso")
        if not unit_id and unit_ids:
            unit_id = unit_ids[0]
    report = Report(
        unit_id=unit_id,
        created_by=user.id,
        category=payload.category,
        title=payload.title,
        description=payload.description,
        location=payload.location,
        status=ReportStatus.open,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    report = db.query(Report).options(joinedload(Report.updates)).filter(Report.id == report.id).one()
    users, units = load_maps(db, [report])
    return serialize_report(report, users, units)


@router.get("/{report_id}", response_model=ReportOut)
def get_report(report_id: int, db: DbSession, user: CurrentUser):
    report = db.query(Report).options(joinedload(Report.updates)).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    if user.role == UserRole.resident and report.created_by != user.id:
        raise HTTPException(status_code=403, detail="Sin permiso")
    if user.role == UserRole.staff and report.assigned_to != user.id:
        raise HTTPException(status_code=403, detail="Sin permiso")
    users, units = load_maps(db, [report])
    return serialize_report(report, users, units)


@router.patch("/{report_id}/assign", response_model=ReportOut)
def assign_report(report_id: int, payload: ReportAssign, db: DbSession, _: AdminUser):
    report = db.query(Report).options(joinedload(Report.updates)).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    assignee = db.get(User, payload.assigned_to)
    if not assignee or assignee.role != UserRole.staff:
        raise HTTPException(status_code=400, detail="Asignar solo a personal staff")
    report.assigned_to = payload.assigned_to
    report.status = ReportStatus.assigned
    db.add(
        ReportUpdate(
            report_id=report.id,
            author_id=_.id,
            note=f"Asignado a {assignee.name}",
            status_to=ReportStatus.assigned,
        )
    )
    db.commit()
    report = db.query(Report).options(joinedload(Report.updates)).filter(Report.id == report_id).one()
    users, units = load_maps(db, [report])
    return serialize_report(report, users, units)


@router.post("/{report_id}/updates", response_model=ReportOut)
def add_update(report_id: int, payload: ReportUpdateCreate, db: DbSession, user: StaffOrAdmin):
    report = db.query(Report).options(joinedload(Report.updates)).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    if user.role == UserRole.staff and report.assigned_to != user.id:
        raise HTTPException(status_code=403, detail="Sin permiso")
    if payload.status_to:
        report.status = payload.status_to
    db.add(
        ReportUpdate(
            report_id=report.id,
            author_id=user.id,
            note=payload.note,
            status_to=payload.status_to,
        )
    )
    db.commit()
    report = db.query(Report).options(joinedload(Report.updates)).filter(Report.id == report_id).one()
    users, units = load_maps(db, [report])
    return serialize_report(report, users, units)
