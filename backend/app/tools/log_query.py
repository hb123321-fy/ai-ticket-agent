def query_log_by_request_id(request_id: str):
    """根据 request id 查询脱敏日志"""
    if not request_id:
        return {"error": "缺少 request id"}
    
    if "8899" in request_id:
        return {
            "status": "success",
            "logs": [
                {"timestamp": "2026-08-06 14:20:15", "level": "ERROR", "message": "Connection timeout"},
                {"timestamp": "2026-08-06 14:20:20", "level": "WARN", "message": "Retry attempt 1 failed"},
                {"timestamp": "2026-08-06 14:20:25", "level": "ERROR", "message": "All retry attempts exhausted"}
            ]
        }
    return {
        "status": "success",
        "logs": [
            {"timestamp": "2026-08-06 14:20:15", "level": "INFO", "message": "Request received"},
            {"timestamp": "2026-08-06 14:20:16", "level": "INFO", "message": "Response sent"}
        ]
    }