from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from app.models import TicketCreate, Ticket
from app.db import fake_db, get_user_by_id

router = APIRouter(prefix="/tickets", tags=["tickets"])
agent_sessions = {}

@router.post("/")
def create_ticket(data: TicketCreate, user_id: int = Query(1)):
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="未登录")
    ticket = Ticket(
        id=fake_db["next_id"],
        title=data.title,
        description=data.description,
        system=data.system or "",
        environment=data.environment,
        attempts=data.attempts or "",
        category=data.category or "无法判断",
        priority=data.priority or "P3",
        created_at=datetime.now(),
        creator_id=user_id
    )
    fake_db["tickets"].append(ticket)
    fake_db["next_id"] += 1
    return {"id": ticket.id, "message": "Ticket created successfully"}

@router.get("/")
def list_tickets(user_id: int = Query(1)):
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="未登录")
    if user["role"] == "developer":
        return [t for t in fake_db["tickets"] if t.creator_id == user_id]
    return fake_db["tickets"]

@router.get("/{ticket_id}")
def get_ticket(ticket_id: int, user_id: int = Query(1)):
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="未登录")
    for t in fake_db["tickets"]:
        if t.id == ticket_id:
            if user["role"] == "developer" and t.creator_id != user_id:
                raise HTTPException(status_code=403, detail="无权查看")
            return t
    raise HTTPException(status_code=404, detail="工单不存在")


@router.post("/{ticket_id}/process")
def process_ticket(ticket_id: int, user_message: str = None, user_id: int = Query(1)):
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="未登录")
    agent = TicketAgent(ticket_id)
    result = agent.process(user_message)
    agent_sessions[ticket_id] = agent
    return result

@router.post("/{ticket_id}/approve")
def approve_action(ticket_id: int, user_id: int = Query(1)):
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="未登录")
    if user["role"] not in ["engineer", "admin"]:
        raise HTTPException(status_code=403, detail="权限不足")
    if ticket_id not in agent_sessions:
        return {"error": "没有正在进行的 Agent 会话"}
    agent = agent_sessions[ticket_id]
    result = agent.approve_action()
    if "执行" in result.get("message", ""):
        del agent_sessions[ticket_id]
    return result



@router.get("/{ticket_id}/audit")
def get_ticket_audit(ticket_id: int, user_id: int = Query(1)):
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="未登录")
    if user["role"] not in ["engineer", "admin"]:
        raise HTTPException(status_code=403, detail="权限不足")
    logs = get_audit_logs(ticket_id)
    return {"ticket_id": ticket_id, "logs": logs}
from app.agent import TicketAgent
from app.audit import get_audit_logs