import redis
from flask import session
from flask_session import Session


def init_redis_session(app):
    """初始化 Redis 会话配置，并处理 Redis 连接错误"""
    app.config['SECRET_KEY'] = 'your_secret_key'

    try:
        # Redis 配置
        app.config['SESSION_TYPE'] = 'redis'
        app.config['SESSION_PERMANENT'] = False
        app.config['SESSION_USE_SIGNER'] = True  # 用于安全的 cookie
        app.config['SESSION_REDIS'] = redis.Redis(host='localhost', port=6379)

        # 测试 Redis 连接
        app.config['SESSION_REDIS'].ping()  # 尝试 ping Redis 服务器

        # 初始化会话
        Session(app)
        print("Redis session initialized successfully.")

    except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError) as e:
        print(f"Redis connection failed: {e}. Falling back to filesystem session storage.")

        # 使用文件系统存储会话作为回退机制
        app.config['SESSION_TYPE'] = 'filesystem'

        # 初始化会话
        Session(app)

    return app
