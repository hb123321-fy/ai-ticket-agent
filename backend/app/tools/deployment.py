def get_deployment_history(service: str):
    """查询指定服务的最近发布记录"""
    if not service:
        return {"error": "缺少服务名称"}
    
    if "payment" in service.lower():
        return {
            "status": "success",
            "history": [
                {"version": "v2.4.1", "deployed_at": "2026-08-06 14:15:00", "status": "failed"},
                {"version": "v2.4.0", "deployed_at": "2026-08-05 10:00:00", "status": "success"},
                {"version": "v2.3.9", "deployed_at": "2026-08-04 09:00:00", "status": "success"}
            ]
        }
    return {
        "status": "success",
        "history": [
            {"version": "v1.0.1", "deployed_at": "2026-08-05 10:00:00", "status": "success"}
        ]
    }