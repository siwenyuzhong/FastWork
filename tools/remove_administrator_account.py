"""
思路：
rbac 模块的权限初始化一次之后，不需要再去操作
("三级权限", "/rbac/user/", "用户管理：列表", '/rbac/user/list', "user-list"),
三级权限 url 以"/rbac"开头的，忽略
"""

if __name__ == '__main__':
    import os, django

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FastWork.settings')
    django.setup()
    from user.models import *

    UserProfile.objects.get(username="cwy", is_superuser=True).delete()
