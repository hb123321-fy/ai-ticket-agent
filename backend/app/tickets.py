from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from app.models import TicketCreate, Ticket
from app.db import fake_db, get_user_by_id, check_permission

router = APIRouter(prefix="/tickets", tags=["tickets"])

agent_sessions = {}

# 创建工单
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
        created_at=datetime.now(),
        creator_id=user_id
    )
    fake_db["tickets"].append(ticket)
    fake_db["next_id"] += 1
    return {"id": ticket.id, "message": "Ticket created successfully"}

# 查询工单列表
@router.get("/")
def list_tickets(user_id: int = Query(1)):
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="未登录")
    
    if user["role"] == "developer":
        # 普通用户只能看到自己的工单
        return [t for t in fake_db["tickets"] if t.creator_id == user_id]
    
    # 工程师和管理员可以看到所有工单
    return fake_db["tickets"]

# 查询单个工单
@router.get("/{ticket_id}")
def get_ticket(ticket_id: int, user_id: int = Query(1)):
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="未登录")
    
    ticket = None
    for t in fake_db["tickets"]:
        if t.id == ticket_id:
            ticket = t
            break
    
    if not ticket:
        raise HTTPException(status_code=404, detail="工单不存在")
    
    # 普通用户只能看自己的工单
    if user["role"] == "developer" and ticket.creator_id != user_id:
        raise HTTPException(status_code=403, detail="无权查看此工单")
    
    return ticket


from app.agent import TicketAgent

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
    
    # 只有工程师和管理员可以批准
    if user["role"] not in ["engineer", "admin"]:
        raise HTTPException(status_code=403, detail="权限不足，需要工程师或管理员角色")
    
    if ticket_id not in agent_sessions:
        return {"error": "没有正在进行的 Agent 会话，请先执行 /process"}
    
    agent = agent_sessions[ticket_id]
    result = agent.approve_action()
    if "执行" in result.get("message", ""):
        del agent_sessions[ticket_id]
    return result


from app.audit import get_audit_logs

@router.get("/{ticket_id}/audit")
def get_ticket_audit(ticket_id: int, user_id: int = Query(1)):
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="未登录")
    
    # 只有工程师和管理员可以查看审计记录
    if user["role"] not in ["engineer", "admin"]:
        raise HTTPException(status_code=403, detail="权限不足，需要工程师或管理员角色")
    
    logs = get_audit_logs(ticket_id)
    if not logs:
        return {"message": "暂无审计记录", "logs": []}
    return {"ticket_id": ticket_id, "logs": logs}