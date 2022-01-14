from dependency_injector import containers, providers

from monitor.libs import redis_handler, services


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    redis_pool = providers.Resource(redis_handler.RedisHandler)
    service = providers.Factory(services.TaskService, redis=redis_pool)
