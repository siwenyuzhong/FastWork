import os
from configFiles import config_files

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = '*we-&4v_xifb2hnfg7j5^9+6&swytxeeluj9hx#67&uuz=u7tb'
DEBUG = True

# 允许主机访问
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "django_apscheduler",
    "channels",
    "rbac",
    "user",
    "project",
    "issue",
    "wiki",
    "sitemap",
    "scripts",
    "tools_execution",
    "task_scheduler",
    "deploy",
    "agent",
    "cmdb",
    "batchTasks",
    "file_depository",
    "notifications",
    "journal",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'middleware.auth.AuthMiddleware',
    # 权限开关
    # 'user.middleware.MenuMiddleware',
    # 'rbac.middleware.RbacMiddleware',
]

# 解决前段同源策略
X_FRAME_OPTIONS = 'SAMEORIGIN'

ROOT_URLCONF = 'FastWork.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR, 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'FastWork.wsgi.application'

# 生产环境
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'fastwork',
        'USER': 'yizhi',
        'PASSWORD': '123456',
        'HOST': '103.116.78.204',
        'PORT': '3306',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'zh-hans'

# TIME_ZONE = 'UTC'
TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

# 影响自动生成数据库时间字段
# USE_TZ = True
USE_TZ = False

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

AUTH_USER_MODEL = 'user.UserProfile'

# URL white list
SAFE_URL = [
    '/user/login/',
    '/user/register/',
    '/user/logout/',
    '/media/',
    '/admin/',
    "/rbac/admin/page/",
    "/user/image_code/",
    "/rbac/admin/page/bind/",
    '/file_depository/media/$'
    '/index/',
]

WHITE_URL_LISTS = [
    "/admin/",
    "/user/register/",
    "/user/login/",
    "/user/image_code/",
    "/agent/v1/client",
    "/wiki/invite/join/wiki/",
    "/script/invite/join/script",
    "/file_depository/media/",
    "/file_depository/invite/join/file/depository/",
    "/rbac/admin/page/",
    "/index/",
]

# 配置日志
BASE_LOG_DIR = os.path.join(BASE_DIR, "logs")

DEPLOY_CODE_PATH = os.path.join(BASE_DIR, 'deploy/codes')

# 本地项目打包文件存放路径
PACKAGE_PATH = os.path.join(BASE_DIR, 'deploy/packages')

# 服务器端接收本地上传的文件存放地址
SERVER_PACKAGE_PATH = "/root/chen/"

# 配置channels
ASGI_APPLICATION = "FastWork.routing.application"
# 开辟群聊的模式
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    }
}

# 文件下载路径
DOWNLOADFILE_DIR = "%s/download/downloads/" % BASE_DIR
