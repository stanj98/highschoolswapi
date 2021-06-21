from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.cache import cache
from api.swapi_class import Resource
from django.conf import settings
import datetime
import requests
import json
import redis


redis_instance = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

@api_view(['GET'])
def swapi_research(request, resource = None, obj_id = None, summarize = None, get_count = None):
	
	'''
	Use this API and:
	1) Search for the whole or specific resource dataset(s)
	2) Obtain a bio data for each specific resource queried
	3) Get a summarized report on the total count for each available resource
	'''

	if request.method == 'GET':
		
		#delete after and use cron
		swapi_api = "https://swapi.dev/api/"
		# swapi_api = "https://anapioficeandfire.com/api/"
		resources = requests.get(swapi_api)
		# redis_instance.set("resources_list", json.dumps(resources.json()), timeout= 3600)
		redis_instance.set("resources_list", json.dumps(resources.json()))

		available_resources = json.loads(redis_instance.get("resources_list")).keys()
		# print(available_resources)
		error_flag = None

		try:
			#validations

			#True if the total count parameter is accepted as the first path parameter, returns the specific total resource count
			if resource == 'total_count' and (obj_id is None or summarize is None):
				serve_resource = Resource()
				response = serve_resource.get_resource_count()
				return Response(response)

			#True if none of the path parameters are inputted
			elif not resource and not obj_id and not summarize:
				response = {
					"message" : "Apart from SWAPI's regular endpoints (https://swapi.dev/api/), use the following features to get a more qualitative and quantiative experience",
					"films info": f"Films - {request.build_absolute_uri()}films/",
					"people info": f"People - {request.build_absolute_uri()}people/",
					"planets info": f"Planets - {request.build_absolute_uri()}planets/",
					"species info": f"Species - {request.build_absolute_uri()}species/",
					"starships info": f"Starships - {request.build_absolute_uri()}starships/",
					"vehicles info": f"Vehicles - {request.build_absolute_uri()}vehicles/",
					"feature 1": "search - search a specified resource by name, title or model (if available)",
					"feature 2": "summarize - get a summarized bio for a specific resource object",
					"feature 3": "get total resource count - get a summarized report on the aggregate total for each resource"
				}
				return Response(response)
			
			#True if the resource parameter is not within the list of available resources or if the parameter is not a string instance
			elif resource not in available_resources or not isinstance(resource, str):
				error_flag = 1
				raise
			
			#True if random text or data is inputted as the summary path parameter
			elif summarize and summarize != "summarize":
				error_flag = 2
				raise

			else:
				serve_resource = Resource()
				#if the resource and id are only available, get the specific resource data
				if resource and obj_id and (not summarize):
					response = serve_resource.get_specific_resource(resource, obj_id)
					return Response(response)

				#if the resource is available with/without query params, get the queried/whole resource dataset
				elif resource and (obj_id is None or summarize is None):
					#functionality to search the whole resource dataset
					response = None
					if request.query_params:
						response = serve_resource.get_resource(resource, request)
					else:
						response = serve_resource.get_resource(resource)
					return Response(response)

				#if the resource and id and summarize path variables are specified, return the summarized bio data
				elif resource and obj_id and summarize:
					response = serve_resource.get_resource_object_summary(resource, obj_id)
					return Response(response)

		except Exception as e:

			response = None
			if error_flag == 2:
				# response = {"error_message" : "Error! Please query a resource by an integer id", "status": status.HTTP_404_NOT_FOUND}
				response = {"error_message" : "Error! Please use the 'summarize' keyword for a summarized bio data", "status": status.HTTP_404_NOT_FOUND}
			# elif error_flag == 3:
			# 	response = {"error_message" : "Error! Please use the 'summarize' keyword for a summarized bio data", "status": status.HTTP_404_NOT_FOUND}
			else:
				response = {"error_message" : "Error! Resource not available", "status": status.HTTP_404_NOT_FOUND}
			return Response(response)