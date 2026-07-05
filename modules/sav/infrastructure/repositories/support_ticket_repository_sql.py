from modules.sav.infrastructure.db.support_ticket_model import SupportTicketModel
from modules.sav.infrastructure.db.ticket_message_model import TicketMessageModel
from modules.sav.infrastructure.db.ticket_read_state_model import TicketReadStateModel
from modules.sav.domain.repositories.support_ticket_repository import SupportTicketRepository
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import or_, desc, asc, func
from modules.core.enums import UserRole, TicketStatus, TicketPriority
from modules.sav.infrastructure.mappers.support_ticket_mapper import SupportTicketMapper
from datetime import datetime, timedelta

class SupportTicketSQLRepository(SupportTicketRepository):

    def __init__(self, db: Session):
        self.db = db

    def create(self, ticket):

        model = SupportTicketMapper.to_model(ticket)

        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)

        return SupportTicketMapper.to_domain(model)

    def get_by_id(self, ticket_id: str):

        model = (
            self.db.query(SupportTicketModel)
            .filter(SupportTicketModel.id == ticket_id)
            .first()
        )

        if not model:
            return None

        return SupportTicketMapper.to_domain(model)

    def find_all(
        self,
        page,
        limit,
        search,
        status,
        category,
        priority,
        sort,
        user,
    ):
        query = self.db.query(SupportTicketModel)

        # =======================
        # SECURITY
        # =======================

        if user.role == UserRole.CLIENT:
            query = query.filter(
                SupportTicketModel.user_id == user.id
            )

        elif user.role == UserRole.SAV_AGENT:
            query = query.filter(
                SupportTicketModel.assigned_to == user.id
            )

        # =======================
        # SEARCH
        # =======================

        if search:
            query = query.filter(
                SupportTicketModel.subject.ilike(f"%{search}%")
            )

        # =======================
        # STATUS
        # =======================

        if status != "ALL":
            query = query.filter(
                SupportTicketModel.status == status
            )

        # =======================
        # CATEGORY
        # =======================

        if category != "ALL":
            query = query.filter(
                SupportTicketModel.category == category
            )

        # =======================
        # PRIORITY
        # =======================

        if priority != "ALL":
            query = query.filter(
                SupportTicketModel.priority == priority
            )

        # =======================
        # SORT
        # =======================

        if sort == "created_at_desc":
            query = query.order_by(
                desc(SupportTicketModel.created_at)
            )

        elif sort == "created_at_asc":
            query = query.order_by(
                asc(SupportTicketModel.created_at)
            )

        elif sort == "priority":
            query = query.order_by(
                desc(SupportTicketModel.priority)
            )

        # =======================
        # PAGINATION
        # =======================

        total = query.count()

        tickets = (
            query
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        return tickets, total


    def get_dashboard_stats(self, user):

        query = self.db.query(SupportTicketModel)

        # =======================
        # SECURITY
        # =======================

        query = query.filter(
            SupportTicketModel.assigned_to == user.id
        )

        # =======================
        # COUNTS
        # =======================

        total = query.count()

        open_count = query.filter(
            SupportTicketModel.status == TicketStatus.OPEN
        ).count()

        urgent_count = query.filter(
            SupportTicketModel.priority == TicketPriority.HIGH
        ).count()

        # =======================
        # RECENT TICKETS
        # =======================

        recent_tickets = (
            query
            .order_by(desc(SupportTicketModel.created_at))
            .limit(5)
            .all()
        )

        return {
            "total": total,
            "open": open_count,
            "urgent": urgent_count,
            "recent_tickets": recent_tickets,
        }
    def update(self, ticket):

        model = (
            self.db.query(SupportTicketModel)
            .filter(SupportTicketModel.id == ticket.id)
            .first()
        )

        if not model:
            return None

        SupportTicketMapper.update_model(model, ticket)

        self.db.commit()
        self.db.refresh(model)

        return SupportTicketMapper.to_domain(model)
    
    def count_open_tickets_by_agent(self, agent_id: str):

        return (
            self.db.query(SupportTicketModel)
            .filter(
                SupportTicketModel.assigned_to == agent_id,
                SupportTicketModel.status != TicketStatus.CLOSED
            )
            .count()
        )
    
    def count_open(self) -> int:
        return (
            self.db.query(func.count(SupportTicketModel.id))
            .filter(SupportTicketModel.status == TicketStatus.OPEN)
            .scalar()
        )
    


    def get_sav_statistics(self, user):

        query = self.db.query(SupportTicketModel)

        # =====================
        # SCOPE
        # =====================
        query = query.filter(
                SupportTicketModel.assigned_to == user.id
            )

        # =====================
        # TOTAL
        # =====================
        total = query.count()

        # =====================
        # CLOSED TICKETS
        # =====================
        closed = query.filter(
            SupportTicketModel.status == TicketStatus.CLOSED
        ).count()

        # =====================
        # TREND
        # =====================
        last_7_days = query.filter(
            SupportTicketModel.created_at >= datetime.utcnow() - timedelta(days=7)
        ).count()

        last_30_days = query.filter(
            SupportTicketModel.created_at >= datetime.utcnow() - timedelta(days=30)
        ).count()

        # =====================
        # DISTRIBUTION PAR CATEGORIE
        # =====================
        category_distribution = (
            self.db.query(
                SupportTicketModel.category,
                func.count(SupportTicketModel.id)
            )
            .group_by(SupportTicketModel.category)
            .all()
        )

        # =====================
        # PERFORMANCE GLOBALE
        # =====================

        closed_tickets = closed

        resolution_rate = 0
        if total > 0:
            resolution_rate = round((closed_tickets / total) * 100, 2)

        return {
            "total": total,
            "closed": closed,
            "last_7_days": last_7_days,
            "last_30_days": last_30_days,
            "category_distribution": category_distribution,
            "resolution_rate": resolution_rate,
        }
    
    def get_unread_ticket_ids(self, user) -> list[str]:

        subquery_last_message = (
            self.db.query(
                TicketMessageModel.ticket_id,
                func.max(TicketMessageModel.created_at).label("last_message_at"),
            )
            .group_by(TicketMessageModel.ticket_id)
            .subquery()
        )

        subquery_read = (
            self.db.query(TicketReadStateModel)
            .filter(TicketReadStateModel.user_id == user.id)
            .subquery()
        )

        query = (
            self.db.query(SupportTicketModel.id)
            .join(
                subquery_last_message,
                subquery_last_message.c.ticket_id == SupportTicketModel.id,
            )
            .outerjoin(
                subquery_read,
                subquery_read.c.ticket_id == SupportTicketModel.id,
            )
        )

        # =====================
        # VISIBILITÉ (IMPORTANT)
        # =====================
        if user.role == UserRole.CLIENT:
            query = query.filter(
                SupportTicketModel.user_id == user.id
            )

        elif user.role == UserRole.SAV_AGENT:
            query = query.filter(
                SupportTicketModel.assigned_to == user.id
            )

        # =====================
        # UNREAD LOGIC
        # =====================
        query = query.filter(
            (subquery_read.c.last_read_at.is_(None))
            |
            (subquery_read.c.last_read_at < subquery_last_message.c.last_message_at)
        )

        return [row[0] for row in query.all()]
    
    def count_unread(self, user) -> int:

        subquery_last_message = (
            self.db.query(
                TicketMessageModel.ticket_id,
                func.max(TicketMessageModel.created_at).label("last_message_at"),
            )
            .group_by(TicketMessageModel.ticket_id)
            .subquery()
        )

        subquery_read = (
            self.db.query(
                TicketReadStateModel.ticket_id,
                TicketReadStateModel.last_read_at,
            )
            .filter(TicketReadStateModel.user_id == user.id)
            .subquery()
        )

        query = (
            self.db.query(func.count())
            .select_from(SupportTicketModel)
            .join(
                subquery_last_message,
                subquery_last_message.c.ticket_id == SupportTicketModel.id,
            )
            .outerjoin(
                subquery_read,
                subquery_read.c.ticket_id == SupportTicketModel.id,
            )
        )

        # =====================
        # VISIBILITÉ
        # =====================
        if user.role == UserRole.CLIENT:
            query = query.filter(
                SupportTicketModel.user_id == user.id
            )

        elif user.role == UserRole.SAV_AGENT:
            query = query.filter(
                SupportTicketModel.assigned_to == user.id
            )

        # =====================
        # UNREAD LOGIC
        # =====================
        query = query.filter(
            (subquery_read.c.last_read_at.is_(None))
            |
            (
                subquery_read.c.last_read_at
                < subquery_last_message.c.last_message_at
            )
        )

        return query.scalar() or 0