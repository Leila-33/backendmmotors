from datetime import datetime, timedelta, timezone

from sqlalchemy import asc, case, desc, func, or_
from sqlalchemy.orm import Session
from typing import Literal

from modules.auth.domain.enums import UserRole
from modules.auth.infrastructure.db.user_model import UserModel

from modules.sav.application.results.support_ticket_list_item import (
    SupportTicketListItem,
)

from modules.sav.domain.enums import (
    TicketCategory,
    TicketPriority,
    TicketStatus,
)

from modules.sav.domain.repositories.support_ticket_repository import (
    SupportTicketRepository,
)

from modules.sav.infrastructure.db.support_ticket_model import (
    SupportTicketModel,
)

from modules.sav.infrastructure.db.ticket_message_model import (
    TicketMessageModel,
)

from modules.sav.infrastructure.db.ticket_read_state_model import (
    TicketReadStateModel,
)
from modules.sav.infrastructure.mappers.support_ticket_mapper import SupportTicketMapper

class SupportTicketSQLRepository(SupportTicketRepository):

    def __init__(self, db: Session):
        self.db = db

    def create(self, ticket):

        model = SupportTicketMapper.to_model(ticket)

        self.db.add(model)

        return ticket

    def get_by_id(self, ticket_id: str):

        model = (
            self.db.query(SupportTicketModel)
            .filter(SupportTicketModel.id == ticket_id)
            .first()
        )

        if not model:
            return None

        return SupportTicketMapper.to_domain(model)

    def update(
            self,
            ticket
        ):

            model = (
                self.db.query(SupportTicketModel)
                .filter(
                    SupportTicketModel.id == ticket.id
                )
                .first()
            )

            if model is None:
                return None

            SupportTicketMapper.update_model(
                model,
                ticket
            )

            return SupportTicketMapper.to_domain(model)
    
    def find_all(
        self,
        page: int,
        limit: int,
        search: str | None,
        status: TicketStatus | list[TicketStatus] | Literal["ALL"],
        category: TicketCategory | Literal["ALL"],
        priority: TicketPriority | Literal["ALL"],
        sort: str,
        archive: bool,
        user_id: str,
        user_role: UserRole,
    ) -> tuple[list[SupportTicketListItem], int]:

        # =====================================================
        # BASE QUERY
        # =====================================================

        query = self.db.query(
            SupportTicketModel
        )

        # =====================================================
        # ARCHIVE
        # =====================================================

        if archive:

            query = query.filter(
                SupportTicketModel.archived_at.is_not(None)
            )

        else:

            query = query.filter(
                SupportTicketModel.archived_at.is_(None)
            )

        # =====================================================
        # SECURITY
        # =====================================================

        if user_role == UserRole.CLIENT:

            query = query.filter(
                SupportTicketModel.user_id == user_id
            )

        elif user_role == UserRole.SAV_AGENT:

            query = query.filter(
                SupportTicketModel.assigned_to == user_id
            )

        elif user_role == UserRole.ADMIN:

            pass

        else:

            return [], 0

        # =====================================================
        # SEARCH
        # =====================================================

        if search:

            query = query.join(
                UserModel,
                UserModel.id
                == SupportTicketModel.user_id,
            ).filter(
                or_(
                    SupportTicketModel.subject.ilike(
                        f"%{search}%"
                    ),
                    UserModel.first_name.ilike(
                        f"%{search}%"
                    ),
                    UserModel.last_name.ilike(
                        f"%{search}%"
                    ),
                )
            )

        # =====================================================
        # STATUS
        # =====================================================

        if status and status != "ALL":

            if isinstance(status, list):

                query = query.filter(
                    SupportTicketModel.status.in_(status)
                )

            else:

                query = query.filter(
                    SupportTicketModel.status == status
                )

        # =====================================================
        # CATEGORY
        # =====================================================

        if category and category != "ALL":

            query = query.filter(
                SupportTicketModel.category == category
            )

        # =====================================================
        # PRIORITY
        # =====================================================

        if priority and priority != "ALL":

            query = query.filter(
                SupportTicketModel.priority == priority
            )

        # =====================================================
        # TOTAL
        #
        # IMPORTANT :
        # Calculé avant les joins d'enrichissement.
        # =====================================================

        total = query.count()

        # =====================================================
        # LAST MESSAGE
        #
        # ROW_NUMBER permet de garantir un seul message
        # par ticket même si deux messages ont le même
        # created_at.
        # =====================================================

        message_ranked_sq = (
            self.db.query(
                TicketMessageModel.ticket_id,
                TicketMessageModel.message,
                TicketMessageModel.sender_id,
                TicketMessageModel.created_at,

                func.row_number()
                .over(
                    partition_by=(
                        TicketMessageModel.ticket_id
                    ),
                    order_by=(
                        TicketMessageModel.created_at.desc(),
                        TicketMessageModel.id.desc(),
                    ),
                )
                .label("message_rank"),
            )
            .subquery()
        )

        last_message_sq = (
            self.db.query(
                message_ranked_sq.c.ticket_id,
                message_ranked_sq.c.message,
                message_ranked_sq.c.sender_id,
                message_ranked_sq.c.created_at,
            )
            .filter(
                message_ranked_sq.c.message_rank == 1
            )
            .subquery()
        )

        # =====================================================
        # READ STATE
        # =====================================================

        read_sq = (
            self.db.query(
                TicketReadStateModel.ticket_id,
                TicketReadStateModel.last_read_at,
            )
            .filter(
                TicketReadStateModel.user_id == user_id
            )
            .subquery()
        )

        # =====================================================
        # USER
        # =====================================================

        query = query.outerjoin(
            UserModel,
            UserModel.id
            == SupportTicketModel.user_id,
        )

        # =====================================================
        # SELECT
        # =====================================================

        query = query.with_entities(

            SupportTicketModel,

            func.concat(
                UserModel.first_name,
                " ",
                UserModel.last_name,
            ).label(
                "user_name"
            ),

            last_message_sq.c.message.label(
                "last_message_preview"
            ),

            last_message_sq.c.sender_id.label(
                "last_actor"
            ),

            last_message_sq.c.created_at.label(
                "last_activity_at"
            ),

            read_sq.c.last_read_at,
        )

        # =====================================================
        # LAST MESSAGE JOIN
        # =====================================================

        query = query.outerjoin(
            last_message_sq,
            last_message_sq.c.ticket_id
            == SupportTicketModel.id,
        )

        # =====================================================
        # READ STATE JOIN
        # =====================================================

        query = query.outerjoin(
            read_sq,
            read_sq.c.ticket_id
            == SupportTicketModel.id,
        )

        # =====================================================
        # PRIORITY ORDER
        # =====================================================

        priority_order = case(

            (
                SupportTicketModel.priority
                == TicketPriority.URGENT,
                4,
            ),

            (
                SupportTicketModel.priority
                == TicketPriority.HIGH,
                3,
            ),

            (
                SupportTicketModel.priority
                == TicketPriority.MEDIUM,
                2,
            ),

            (
                SupportTicketModel.priority
                == TicketPriority.LOW,
                1,
            ),

            else_=0,
        )

        # =====================================================
        # SORT
        # =====================================================

        if sort == "activity_desc":

            query = query.order_by(
                desc(
                    last_message_sq.c.created_at
                )
            )

        elif sort == "activity_asc":

            query = query.order_by(
                asc(
                    last_message_sq.c.created_at
                )
            )

        elif sort == "priority":

            query = query.order_by(
                desc(priority_order),
                desc(
                    SupportTicketModel.created_at
                ),
            )

        elif sort == "created_at_asc":

            query = query.order_by(
                asc(
                    SupportTicketModel.created_at
                )
            )

        else:

            query = query.order_by(
                desc(
                    SupportTicketModel.created_at
                )
            )

        # =====================================================
        # PAGINATION
        # =====================================================

        results = (
            query
            .offset(
                (page - 1) * limit
            )
            .limit(limit)
            .all()
        )
        items = []

        for row in results:

            ticket = row.SupportTicketModel

            unread = (
                row.last_read_at is None
                or (
                    row.last_activity_at is not None
                    and row.last_read_at < row.last_activity_at
                )
            )

            items.append(
                SupportTicketListItem(
                    id=ticket.id,
                    subject=ticket.subject,
                    category=ticket.category,
                    status=ticket.status,
                    priority=ticket.priority,
                    user_id=ticket.user_id,
                    user_name=row.user_name,
                    last_message_preview=row.last_message_preview,
                    last_actor=row.last_actor,
                    last_activity_at=row.last_activity_at,
                    unread=unread,
                    created_at=ticket.created_at,
                    updated_at=ticket.updated_at,
                    archived_at=ticket.archived_at,
                )
            )

        return items, total

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
            SupportTicketModel.priority == TicketPriority.URGENT
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
    

    def get_sav_statistics(
        self,
        user_id: str,
    ):

        # =========================
        # BASE QUERY
        # =========================

        query = (
            self.db
            .query(SupportTicketModel)
            .filter(
                SupportTicketModel.assigned_to == user_id
            )
        )


        # =========================
        # TOTAL
        # =========================

        total = query.count()


        # =========================
        # CLOSED
        # =========================

        closed = (
            query
            .filter(
                SupportTicketModel.status
                == TicketStatus.CLOSED
            )
            .count()
        )


        # =========================
        # DATES
        # =========================

        now = datetime.now(timezone.utc)

        last_7_days = (
            query
            .filter(
                SupportTicketModel.created_at
                >= now - timedelta(days=7)
            )
            .count()
        )

        last_30_days = (
            query
            .filter(
                SupportTicketModel.created_at
                >= now - timedelta(days=30)
            )
            .count()
        )


        # =========================
        # CATEGORY DISTRIBUTION
        # =========================

        category_distribution = (
            self.db
            .query(
                SupportTicketModel.category,
                func.count(
                    SupportTicketModel.id
                ).label("count"),
            )
            .filter(
                SupportTicketModel.assigned_to == user_id
            )
            .group_by(
                SupportTicketModel.category
            )
            .all()
        )


        # =========================
        # RESOLUTION RATE
        # =========================

        resolved = (
            query
            .filter(
                SupportTicketModel.status.in_(
                    [
                        TicketStatus.RESOLVED,
                        TicketStatus.CLOSED,
                    ]
                )
            )
            .count()
        )


        resolution_rate = (
            round(
                (resolved / total) * 100,
                2,
            )
            if total > 0
            else 0
        )


        # =========================
        # RESULT
        # =========================

        return {
            "total": total,
            "closed": closed,
            "last_7_days": last_7_days,
            "last_30_days": last_30_days,
            "category_distribution": category_distribution,
            "resolution_rate": resolution_rate,
        }

    def count_open_tickets_by_agent(self, agent_id: str):

        return (
            self.db.query(SupportTicketModel)
            .filter(
                SupportTicketModel.assigned_to == agent_id,
                SupportTicketModel.status != TicketStatus.CLOSED
            )
            .count()
        )

    def count_unread(
        self,
        user_id: str,
        user_role: UserRole,
    ) -> int:

        # =====================================
        # DERNIER MESSAGE DE CHAQUE TICKET
        # =====================================

        last_message_subquery = (
            self.db.query(
                TicketMessageModel.ticket_id,
                func.max(
                    TicketMessageModel.created_at
                ).label("last_message_at"),
            )
            .group_by(
                TicketMessageModel.ticket_id
            )
            .subquery()
        )

        # =====================================
        # DERNIÈRE LECTURE DE L'UTILISATEUR
        # =====================================

        read_state_subquery = (
            self.db.query(
                TicketReadStateModel.ticket_id,
                TicketReadStateModel.last_read_at,
            )
            .filter(
                TicketReadStateModel.user_id == user_id
            )
            .subquery()
        )

        # =====================================
        # BASE QUERY
        # =====================================

        query = (
            self.db.query(
                func.count(
                    SupportTicketModel.id
                )
            )
            .join(
                last_message_subquery,
                last_message_subquery.c.ticket_id
                == SupportTicketModel.id,
            )
            .outerjoin(
                read_state_subquery,
                read_state_subquery.c.ticket_id
                == SupportTicketModel.id,
            )
        )

        # =====================================
        # VISIBILITÉ
        # =====================================

        if user_role == UserRole.CLIENT:

            query = query.filter(
                SupportTicketModel.user_id == user_id
            )

        elif user_role == UserRole.SAV_AGENT:

            query = query.filter(
                SupportTicketModel.assigned_to == user_id
            )

        elif user_role == UserRole.ADMIN:

            # ADMIN voit tous les tickets
            pass

        else:

            # Aucun accès
            return 0

        # =====================================
        # UNREAD
        # =====================================

        query = query.filter(
            or_(
                read_state_subquery.c.last_read_at.is_(None),

                read_state_subquery.c.last_read_at
                < last_message_subquery.c.last_message_at,
            )
        )

        return query.scalar() or 0