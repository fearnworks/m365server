import redis

def create_redis():
    return redis.ConnectionPool(
        host='redis',
        port=6379,
        db=0,
        decode_responses=True
    )

default_pool: redis.ConnectionPool = create_redis()

def get_cache(pool: redis.ConnectionPool = default_pool):
    return redis.Redis(connection_pool=pool)