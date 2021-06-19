
from django.core.cache import cache
from django.conf import settings
import redis

redis_instance = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

#cron script to run after every hour -> delete the existing keys and get up-to-date information
def get_swapi():
	try:
		for key in redis_instance.keys('*'):
			if redis_instance.ttl(key) == -1:
				#kill keys after an hour
				redis_instance.expire(key, 60 * 60)
		swapi_api = "https://swapi.dev/api/"
		resources = requests.get(swapi_api)
		redis_instance.set("resources_list", json.dumps(resources.json()))
	except Exception as e:
		print(e)