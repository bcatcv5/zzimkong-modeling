import redis
import env


class QueueDataSource:
    """redis 커넥션 데이터 소스"""

    def __init__(self) -> None:
        self.conn = redis.Redis(
            host=env.REDIS_SERVER_IP,
            port=env.REDIS_SERVER_PORT,
            db=env.REDIS_SERVER_INDEX,
            password=env.REDIS_SERVER_PASSWORD,
        )

    def getConnection(self):
        return self.conn
