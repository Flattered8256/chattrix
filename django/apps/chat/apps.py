from django.apps import AppConfig


class ChatConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.chat"
    def ready(self):
        """
        在应用启动时导入signals模块
        这是Django信号机制的要求，确保信号处理器被注册
        """
        import apps.messages.signals