from django.conf.urls import url
from rbac import views_role, views_menu
from user import views_user, views_structure

app_name = "rbac"

urlpatterns = [
    # 组织架构的改删查操作
    url(r'^structure/$', views_structure.StructureView.as_view(), name="structure"),
    url(r'^structure/list$', views_structure.StructureListView.as_view(), name="structure-list"),
    url(r'^structure/detail$', views_structure.StructureDetailView.as_view(), name="structure-detail"),
    url(r'^structure/delete$', views_structure.StructureDeleteView.as_view(), name="structure-delete"),
    url(r'^structure/add_user$', views_structure.Structure2UserView.as_view(), name="structure-add_user"),

    # 角色管理
    url(r'^role/$', views_role.RoleView.as_view(), name="role"),
    url(r'^role/list$', views_role.RoleListView.as_view(), name="role-list"),
    url(r'^role/detail$', views_role.RoleDetailView.as_view(), name="role-detail"),
    url(r'^role/delete$', views_role.RoleDeleteView.as_view(), name="role-delete"),
    url(r'^role/role_menu$', views_role.Role2MenuView.as_view(), name="role-role_menu"),
    url(r'^role/role_menu_list$', views_role.Role2MenuListView.as_view(), name="role-role_menu_list"),
    url(r'^role/role_user$', views_role.Role2UserView.as_view(), name="role-role_user"),

    # 菜单管理
    url(r'^menu/$', views_menu.MenuView.as_view(), name="menu"),
    url(r'^menu/list$', views_menu.MenuListView.as_view(), name="menu-list"),
    url(r'^menu/detail$', views_menu.MenuListDetailView.as_view(), name="menu-detail"),
    url(r'^menu/delete$', views_menu.MenuListDeleteView.as_view(), name="menu-delete"),

    # 用户管理
    url(r'^user/$', views_user.UserView.as_view(), name="user"),
    url(r'^user/list$', views_user.UserListView.as_view(), name="user-list"),
    url(r'^user/detail$', views_user.UserDetailView.as_view(), name="user-detail"),
    url(r'^user/update$', views_user.UserUpdataView.as_view(), name="user-update"),
    url(r'^user/create$', views_user.UserCreateView.as_view(), name="user-create"),
    url(r'^user/delete$', views_user.UserDeleteView.as_view(), name="user-delete"),
    url(r'^user/enable$', views_user.UserEnableView.as_view(), name="user-enable"),
    url(r'^user/disable$', views_user.UserDisableView.as_view(), name="user-disable"),
    url(r'^user/adminpasswdchange$', views_user.AdminPasswdChangeView.as_view(), name="user-adminpasswdchange"),

    #首次登录分配权限页面
    url(r'^admin/page/$', views_role.AdminPageView.as_view(), name="admin-page"),
    url(r'^admin/page/bind/$', views_role.AdminPageBindView.as_view(), name="admin-page-bind"),

]
