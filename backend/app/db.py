# 模拟数据库（内存存储）
fake_db = {
    "tickets": [],
    "next_id": 1
}

# 模拟用户数据
fake_users = [
    {"id": 1, "name": "张三", "role": "developer"},
    {"id": 2, "name": "李四", "role": "engineer"},
    {"id": 3, "name": "王五", "role": "admin"},
]

def get_user_by_id(user_id: int):
    for user in fake_users:
        if user["id"] == user_id:
            return user
    return None

def check_permission(user_id: int, required_role: str):
    user = get_user_by_id(user_id)
    if not user:
        return False
    role_hierarchy = {"developer": 1, "engineer": 2, "admin": 3}
    return role_hierarchy.get(user["role"], 0) >= role_hierarchy.get(required_role, 0)