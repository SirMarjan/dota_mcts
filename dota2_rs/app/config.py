from huey import RedisHuey
from huey.serializer import Serializer

from dota2_rs.utils import load_key

__REDIS_KEY = load_key('private/redis_key.txt')
__REDIS_HOST = load_key('private/redis_host.txt')

__SERIALIZER = Serializer(pickle_protocol=4)

huey_match_history_scheduler = RedisHuey(name='huey_match_history_scheduler',
                                         host=__REDIS_HOST,
                                         password=__REDIS_KEY,
                                         serializer=__SERIALIZER)
huey_match_details_scheduler = RedisHuey(name='huey_match_details_scheduler',
                                         host=__REDIS_HOST,
                                         password=__REDIS_KEY,
                                         serializer=__SERIALIZER)
huey_sqlite = RedisHuey(name='huey_sqlite',
                        host=__REDIS_HOST,
                        password=__REDIS_KEY,
                        serializer=__SERIALIZER)
huey_match_details = RedisHuey(name='huey_match_details',
                               host=__REDIS_HOST,
                               password=__REDIS_KEY,
                               serializer=__SERIALIZER)
