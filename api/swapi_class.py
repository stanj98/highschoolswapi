
from django.core.cache import cache
from rest_framework import status
from urllib.parse import urlparse
from django.conf import settings
import redis
import json
import requests

redis_instance = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

class Resource:

	'''
	Query the resource or perform additional features
	'''

	redis_instance = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)


	#returns the resource dataset or queried dataset if query params are specified
	def get_resource(self, resource, params = None):
		global redis_instance

		if params:
			url_path = urlparse(params.get_full_path())
			cached_url_path = json.loads(redis_instance.get("resources_list"))[resource]
			swapi_resource_api = cached_url_path.replace(f"{url_path.path}", f"{url_path.path}?{url_path.query}")
			
			if redis_instance.get(f"{url_path.path}?{url_path.query}"):
				key = f"{url_path.path}?{url_path.query}"
				print(f"{url_path.path}{url_path.query} - get results from cache")
				response = json.loads(redis_instance.get(key))
				return response
			else:
				response = None
				print(f"{url_path.path}{url_path.query} - get results from remote db")
				get_searched_data = requests.get(swapi_resource_api)
				if get_searched_data.json():
					# redis_instance.set(f"{url_path.path}?{url_path.query}", json.dumps(get_searched_data.json()), timeout= 1800)
					redis_instance.set(f"{url_path.path}?{url_path.query}", json.dumps(get_searched_data.json()))
					response = get_searched_data.json()
				else:
					response = {"message": "Error! No results found"}
				return response
		else:

			data = redis_instance.get(f"{resource}_data")
			if data is None:
				print(f"get {resource} data from remote DB")
				
				# swapi_resource_api = f"https://swapi.dev/api/{resource}/"
				swapi_resource_api = json.loads(redis_instance.get("resources_list"))[resource]
				# swapi_resource_api = f"https://anapioficeandfire.com/api/{resource}/"
				searched_resource_data = requests.get(swapi_resource_api)

				if not 'detail' in searched_resource_data.json().keys():
					# redis_instance.set(f"{resource}_data", json.dumps(searched_resource_data.json()), timeout= 3600)
					redis_instance.set(f"{resource}_data", json.dumps(searched_resource_data.json()))
					response = searched_resource_data.json()
					return response
				else:
					response = {"message" : "Error! Resource not available", "status": status.HTTP_404_NOT_FOUND}
					return response
			else:
				print(f"get {resource} data from cache")
				response = json.loads(redis_instance.get(f"{resource}_data"))
				return response

	#return the total count for each resource
	def get_resource_count(self):
		global redis_instance

		resource_report_list = []
		resource_report_dict = {}
		json_data = json.loads(redis_instance.get('resources_list')).keys()
		if redis_instance.get("results") and len(json_data) == 6:
			print('cached')
			response = {"results": json.loads(redis_instance.get("results"))}
			return response
		else:
			for resource in json_data:
				print('not cached')
				swapi_resource_api = json.loads(redis_instance.get("resources_list"))[resource]
				searched_resource_data = requests.get(swapi_resource_api)

				if not 'detail' in searched_resource_data.json().keys():
					resource_report_dict[f"total {resource}"] = searched_resource_data.json()['count']
				else:
					continue
			resource_report_list.append(resource_report_dict)
			redis_instance.set("results", json.dumps(resource_report_dict))
			response = {"results": resource_report_list}
			return response


	#get the specified resource dataset if the id is specifiec
	def get_specific_resource(self, resource, obj_id):
		global redis_instance
		data = redis_instance.get(f"{resource}_{obj_id}_data")
		if data is None:
			print(f"get {resource} {obj_id} data from remote DB")
			swapi_resource_api = f"{json.loads(redis_instance.get('resources_list'))[resource]}{obj_id}/"
			# swapi_resource_api = f"https://swapi.dev/api/{resource}/{obj_id}/"
			searched_resource_data = requests.get(swapi_resource_api)
			if not 'detail' in searched_resource_data.json().keys():
				# redis_instance.set(f"{resource}_{obj_id}_data", json.dumps(searched_resource_data.json()), timeout= 3600)
				redis_instance.set(f"{resource}_{obj_id}_data", json.dumps(searched_resource_data.json()))
				response = searched_resource_data.json()
				return response
			else:
				response = {"message" : f"Error! {response} with id {obj_id} not available", "status": status.HTTP_404_NOT_FOUND}
				return response
		else:
			print(f"get {resource} {obj_id} data from cache")
			response = json.loads(redis_instance.get(f"{resource}_{obj_id}_data"))
			return response


	#get the each resource id's bio data for an easy read
	def get_resource_object_summary(self, resource, obj_id):
		global redis_instance
		query_data = f"{resource}_{obj_id}_data"
		data = redis_instance.get(query_data)

		if not data:

			print(f"get {resource} {obj_id} data from remote dddDB")
			swapi_resource_api = f"{json.loads(redis_instance.get('resources_list'))[resource]}{obj_id}/"
			# swapi_resource_api = f"https://swapi.dev/api/{resource}/{obj_id}/"
			print(swapi_resource_api)
			searched_resource_data = requests.get(swapi_resource_api)
			if not 'detail' in searched_resource_data.json().keys():
				json_data = searched_resource_data.json()
				# redis_instance.set(f"{resource}_{obj_id}_data", json.dumps(searched_resource_data.json()), timeout= 3600)
				redis_instance.set(f"{resource}_{obj_id}_data", json.dumps(searched_resource_data.json()))
				response = self.initiate_summary(resource, obj_id, json_data)
				return response
			else:
				response = {"message" : f"Error! {response} with id {obj_id} not available", "status": status.HTTP_404_NOT_FOUND}
				return response
		else:
			print(f"get {resource} {obj_id} summarized data from cache")
			json_data = json.loads(redis_instance.get(query_data))
			response = self.initiate_summary(resource, obj_id, json_data)
			return response
			
	#Part 1: get_resource_object_summary()
	def initiate_summary(self, resource, obj_id, json_data):

		# if resource == "films":
		key = f"{json_data.get('title')}" if resource == "films" else f"{json_data.get('name')}"
		if redis_instance.get(key):
			response = self.get_summary(key)
			return response
		else:
			value = ""
			if resource == "films":
				value = f"Episode {json_data.get('episode_id')} was directed by {json_data.get('director')} and released at {json_data.get('release_date')}. Preamble: {json_data.get('opening_crawl')} - get more info at: {json.loads(redis_instance.get('resources_list'))['films']}{obj_id}/"
			elif resource == "people":
				value = f"Born in {json_data.get('birth_year')}. {json_data.get('gender')} individual with {json_data.get('hair_color')} hair, {json_data.get('skin_color')} skin, and weighs {json_data.get('mass')} kilograms. Also, this person is {json_data.get('height')}cm tall - get more info at: {json.loads(redis_instance.get('resources_list'))['people']}{obj_id}/"
			elif resource == "planets":
				value = f"{json_data.get('climate')} climate with a {json_data.get('terrain')} terrain. This planet stretches upto {json_data.get('diameter')}km and is inhabited by {json_data.get('population')} sentient beings. It has an orbital period of {json_data.get('orbital_period')} days with a rotation period of {json_data.get('rotation_period')} hours - get more info at: {json.loads(redis_instance.get('resources_list'))['planets']}{obj_id}/"
			elif resource == "species":
				value = f"{json_data.get('skin_color').capitalize()} {json_data.get('classification')} creature who is a {json_data.get('designation')} being. Speaks {json_data.get('language')} and lives upto {json_data.get('average_lifespan')} on average. With an average height of {json_data.get('average_height')}cm, this creature can inherit single eye colors ranging from {json_data.get('eye_colors')} and single hair colors ranging from {json_data.get('hair_colors')} - get more info at: {json.loads(redis_instance.get('resources_list'))['species']}{obj_id}/"
			elif resource == "starships":
				value = f"A {json_data.get('model')} manufactured by the {json_data.get('manufacturer')}. It is {json_data.get('length')}m long and belongs to the {json_data.get('starship_class')} class. It costs {json_data.get('cost_in_credits')} galactic credits. It requires {json_data.get('crew')} personnel to run or pilot and can carry {json_data.get('passengers')} non-essential passengers. It can transport objects upto {json_data.get('cargo_capacity')}kg. This baby can travel {json_data.get('MGLT')} within a standard hour - get more info at: {json.loads(redis_instance.get('resources_list'))['starships']}{obj_id}/"
			elif resource == "vehicles":
				value = f"{json_data.get('model')} manufactured by the {json_data.get('manufacturer')}. It is {json_data.get('length')}m long and belongs to the {json_data.get('vehicle_class')} class. It costs {json_data.get('cost_in_credits')} galactic credits. It requires {json_data.get('crew')} personnel to run or pilot and can carry {json_data.get('passengers')} non-essential passengers. It can transport objects upto {json_data.get('cargo_capacity')}kg - get more info at: {json.loads(redis_instance.get('resources_list'))['vehicles']}{obj_id}/"
			
			response = self.set_cache_get_summary(key, value)
			return response

	#Part 2: get_resource_object_summary()
	def get_summary(self, key):
		global redis_instance
		response = {key:json.loads(redis_instance.get(key))}
		return response


	#Part 2: get_resource_object_summary()
	def set_cache_get_summary(self, key, value):
		global redis_instance
		if value and value != "":
			# redis_instance.set(key, json.dumps(value), timeout= 3600)
			redis_instance.set(key, json.dumps(value))
			response = {key:value}
			return response
		else:
			response = {"message": "Error! No data available"}
			return response
