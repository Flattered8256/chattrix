from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts"
    
    def ready(self):
        # 导入signals模块以注册信号处理器
        import apps.accounts.signals
