def search_similar_tickets(description: str):
    """检索相似历史工单及处理结果"""
    historical_tickets = [
        {
            "id": "T-1001",
            "title": "测试环境发布后出现502",
            "description": "测试环境 order-service 发布后出现502",
            "resolution": "回滚到上一版本后恢复"
        },
        {
            "id": "T-1002",
            "title": "用户误把403当作服务异常",
            "description": "用户访问数据库返回403",
            "resolution": "通过权限申请解决"
        }
    ]
    
    results = []
    for ticket in historical_tickets:
        if "502" in description and "502" in ticket["description"]:
            results.append(ticket)
            break
        elif "403" in description and "403" in ticket["description"]:
            results.append(ticket)
            break
    
    return results if results else [{"message": "未找到相似工单"}]