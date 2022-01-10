from dependency_injector import containers, providers

from source.libs import redis_handler, services


class Container(containers.DeclarativeContainer):

    config = providers.Configuration()

    redis_pool = providers.Resource(
        redis_handler.RedisHandler,
        # host=config.redis_host,
        # password=config.redis_password,
    )

    # redis_pool = providers.Resource(
    #     redis.init_redis_pool,
    #     host=config.redis_host,
    #     password=config.redis_password,
    # )


    service = providers.Singleton(
        services.TaskService,
        redis=redis_pool,
    )
