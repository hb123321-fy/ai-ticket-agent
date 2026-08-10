from datetime import datetime

audit_logs = []

def log_audit_event(ticket_id, event_type, actor, details):
    log = {
        "ticket_id": ticket_id,
        "event_type": event_type,
        "actor": actor,
        "details": details,
        "timestamp": datetime.now().isoformat()
    }
    audit_logs.append(log)
    return log

def get_audit_logs(ticket_id=None):
    if ticket_id:
        return [log for log in audit_logs if log["ticket_id"] == ticket_id]
    return audit_logs