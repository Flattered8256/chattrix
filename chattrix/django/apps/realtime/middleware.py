import jwt
from django.conf import settings
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from channels.sessions import CookieMiddleware, SessionMiddleware
from urllib.parse import parse_qs

@database_sync_to_async
def get_user_from_token(token):
    """
    从JWT令牌中获取用户对象
    """
    try:
        # 延迟导入，避免在Django设置加载前访问模型
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('user_id')
        if user_id:
            return User.objects.get(id=user_id)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
        return None
    return None

class JWTAuthMiddleware(BaseMiddleware):
    """
    自定义WebSocket JWT认证中间件
    从查询参数中提取JWT令牌并验证
    """
    def __init__(self, inner):
        super().__init__(inner)

    async def __call__(self, scope, receive, send):
        # 延迟导入，避免在Django设置加载前访问模型
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # 从查询参数中获取token
        query_string = scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string)
        token_list = query_params.get('token', [])
        
        if token_list:
            token = token_list[0]
            user = await get_user_from_token(token)
            if user:
                scope['user'] = user
            else:
                # 如果令牌无效，创建一个匿名用户
                scope['user'] = User()
        else:
            # 如果没有令牌，创建一个匿名用户
            scope['user'] = User()

        return await super().__call__(scope, receive, send)

# 创建中间件栈，将JWT中间件与其他必要的中间件组合
def JWTAuthMiddlewareStack(inner):
    return CookieMiddleware(SessionMiddleware(JWTAuthMiddleware(inner)))