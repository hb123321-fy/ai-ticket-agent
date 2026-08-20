from app.db import fake_db
from app.models import Ticket
from app.audit import log_audit_event
class TicketAgent:
    def __init__(self, ticket_id: int):
        self.ticket_id = ticket_id
        self.ticket = self._get_ticket()
        self.state = "COLLECTING_INFORMATION"
        self.messages = []
        self.evidence = []
        self.proposed_action = None
        self.approval_id = None

    def _get_ticket(self):
        for t in fake_db["tickets"]:
            if t.id == self.ticket_id:
                return t
        return None

    def process(self, user_message: str = None):
        if not self.ticket:
            return {"error": "工单不存在"}

        # 恶意检测
        desc = self.ticket.description or ""
        title = self.ticket.title or ""
        combined = (desc + title).lower()
        malicious = ["忽略", "绕过", "跳过", "不要请求", "显示系统提示词", "管理员", "所有限制", "安全规则", "注入", "攻击"]
        for pattern in malicious:
            if pattern in combined:
                self.state = "BLOCKED"
                return {
                    "state": self.state,
                    "message": "检测到可能的恶意指令，已拒绝处理。",
                    "reason": f"包含敏感关键词: {pattern}",
                    "suggest": "已转人工处理"
                }

        if self.state == "COLLECTING_INFORMATION":
            return self._collect_info()
        if self.state == "INVESTIGATING":
            return self._investigate()
        if self.state == "PROPOSING_PLAN":
            return self._propose_plan()
        if self.state == "WAITING_FOR_APPROVAL":
            return {
                "state": self.state,
                "message": "等待人工确认中...",
                "proposed_action": self.proposed_action
            }
        if self.state == "EXECUTING":
            return self._execute()
        if self.state == "VERIFYING":
            return self._verify()
        if self.state == "RESOLVED":
            return {"state": self.state, "message": "工单已解决"}
        if self.state == "ESCALATED":
            return {"state": self.state, "message": "已转人工处理"}
        if self.state == "FAILED":
            return {"state": self.state, "message": "Agent 无法继续处理"}
        return {"state": self.state, "message": "处理中..."}

    def _collect_info(self):
        desc = self.ticket.description or ""
        if len(desc) < 10:
            self.state = "COLLECTING_INFORMATION"
            return {
                "state": self.state,
                "message": "请提供更详细的问题描述，例如：哪个接口？什么错误码？发生在什么环境？",
                "need_more_info": True
            }
        missing = []
        if "接口" not in desc and "服务" not in desc:
            missing.append("具体是哪个接口或服务？")
        if "环境" not in desc and self.ticket.environment == "测试":
            missing.append("确认是测试环境吗？")
        if "状态码" not in desc and "报错" in desc:
            missing.append("返回的状态码是什么？")
        if missing:
            self.state = "COLLECTING_INFORMATION"
            return {
                "state": self.state,
                "message": "还需要一些信息：\n" + "\n".join(missing),
                "need_more_info": True
            }
        self.state = "INVESTIGATING"
        return self._investigate()

    def _investigate(self):
        self.state = "INVESTIGATING"
        knowledge = self._search_knowledge()
        self.evidence.append({"type": "knowledge", "data": knowledge})
        status = self._get_service_status()
        self.evidence.append({"type": "service_status", "data": status})
        try:
            from app.tools.deployment import get_deployment_history
            deploy = get_deployment_history(self.ticket.system or "")
            self.evidence.append({"type": "deployment_history", "data": deploy})
        except:
            self.evidence.append({"type": "deployment_history", "data": {"error": "加载失败"}})
        try:
            from app.tools.similar_tickets import search_similar_tickets
            similar = search_similar_tickets(self.ticket.description or "")
            self.evidence.append({"type": "similar_tickets", "data": similar})
        except:
            self.evidence.append({"type": "similar_tickets", "data": {"error": "加载失败"}})
        self.state = "PROPOSING_PLAN"
        return self._propose_plan()

    def _search_knowledge(self):
        desc = self.ticket.description or ""
        if "502" in desc:
            return [{"title": "测试环境 API 返回 502 的排查方法", "content": "1. 查询服务健康状态\n2. 根据 request id 查询网关日志\n3. 查看最近30分钟是否存在发布\n4. 如果新版本发布后健康检查持续失败，可以申请回滚测试环境发布"}]
        elif "权限" in desc or "403" in desc:
            return [{"title": "权限不足问题处理规范", "content": "1. 确认用户、资源和环境\n2. 区分401与403\n3. 不得通过共享管理员账号绕过权限"}]
        return [{"title": "未找到相关文章", "content": "请尝试更具体的关键词"}]

    def _get_service_status(self):
        system = self.ticket.system or ""
        if "payment" in system.lower():
            return {"status": "unhealthy", "message": "服务健康检查失败"}
        return {"status": "healthy", "message": "服务运行正常"}

    def _propose_plan(self):
        self.state = "PROPOSING_PLAN"
        desc = self.ticket.description or ""
        system = self.ticket.system or ""
        if "502" in desc:
            self.proposed_action = {
                "tool": "rollback_test_deployment",
                "params": {"service": system},
                "need_approval": True,
                "risk": "回滚可能导致新功能不可用",
                "reason": "根据知识库，502通常由新版本发布导致"
            }
            self.state = "WAITING_FOR_APPROVAL"
            log_audit_event(
                ticket_id=self.ticket_id,
                event_type="PROCESS",
                actor="system",
                details={"state": self.state, "action": self.proposed_action}
            )
            return {
                "state": self.state,
                "message": "根据分析，建议回滚测试环境发布。\n依据：知识库文章《测试环境 API 返回 502 的排查方法》\n风险：回滚可能导致新功能不可用\n需要人工确认：是",
                "evidence": self.evidence,
                "proposed_action": self.proposed_action,
                "need_approval": True,
                "category": "服务不可用",
                "priority": "P1"
            }
        if "权限" in desc or "403" in desc:
            self.proposed_action = {
                "tool": "create_human_escalation",
                "params": {"reason": "权限问题需要人工处理"},
                "need_approval": False,
                "risk": "低",
                "reason": "权限问题需要资源负责人审核"
            }
            self.state = "ESCALATED"
            return {
                "state": self.state,
                "message": "这是权限问题，建议转人工处理。\n依据：知识库文章《权限不足问题处理规范》\n风险：低\n需要人工确认：否",
                "evidence": self.evidence,
                "proposed_action": self.proposed_action,
                "need_approval": False,
                "category": "权限问题",
                "priority": "P2"
            }
        self.state = "FAILED"
        return {
            "state": self.state,
            "message": "无法判断问题原因，建议转人工处理。",
            "evidence": self.evidence,
            "category": "无法判断",
            "priority": "P3"
        }

    def approve_action(self):
        if self.proposed_action and self.proposed_action.get("need_approval"):
            self.state = "EXECUTING"
            return self._execute()
        log_audit_event(
            ticket_id=self.ticket_id,
            event_type="APPROVE",
            actor="engineer",
            details={"action": self.proposed_action}
        )
        return {"error": "没有待批准的操作"}

    def _execute(self):
        # 模拟执行
        self.state = "EXECUTING"
        result = {
            "state": self.state,
            "message": "操作已批准，正在执行回滚...",
            "action": self.proposed_action
        }
        # 执行后进入复核
        self.state = "VERIFYING"
        return self._verify()

    def _verify(self):
        # 模拟复核
        status = self._get_service_status()
        if status.get("status") == "healthy":
            self.state = "RESOLVED"
            return {
                "state": self.state,
                "message": "服务已恢复，工单解决。",
                "evidence": self.evidence
            }
        else:
            self.state = "ESCALATED"
            return {
                "state": self.state,
                "message": "服务未恢复，已转人工处理。",
                "evidence": self.evidence
            }