


from arches.app.views.base import BaseManagerView
from django.http import HttpResponse, HttpResponseNotFound
from arches.app.models.resource import Resource
from arches.app.utils.data_management.resources.formats.rdffile import RdfWriter

from pyld import jsonld
from pyld.jsonld import compact, expand, frame
import json

class LdpView(BaseManagerView):

	# This should be per model, by reference not value
	# But this is useful for testing :)
	context = {"@context": {"id": "@id", 
		"type": "@type",
		"rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
		"rdfs": "http://www.w3.org/2000/01/rdf-schema#",
		"crm": "http://www.cidoc-crm.org/cidoc-crm/",
		"la": "https://linked.art/ns/terms/",

		"Right": "crm:E30_Right",
		"LinguisticObject": "crm:E33_Linguistic_Object",
		"Name": "la:Name",
		"Identifier": "crm:E42_Identifier",
		"Language": "crm:E56_Language",
		"Type": "crm:E55_Type",
		"ManMadeObject": "crm:E22_Man-Made_Object",

		"label": "rdfs:label",
		"value": "rdf:value",
		"classified_as": "crm:P2_has_type",
		"referred_to_by": "crm:P67i_is_referred_to_by",
		"language": "crm:P72_has_language",
		"includes": "crm:P106_is_composed_of",
		"identified_by": "crm:P1_is_identified_by"
		}}

	def get(self, *args, **kw):
		modelid = kw['modelid']
		resourceid = kw['resourceid']
		context = self.get_context_data()
		models = context['graph_models']
		model = None
		for m in models:
			# This shouldn't be the name, but a separate slug
			if m.name == modelid:
				model = m
				break
		if model == None:
			return HttpResponseNotFound('<h1>Model not found</h1>')
		if resourceid is not None:
			resource_instance = Resource.objects.get(pk=resourceid)
			if resource_instance:
				ri_graph = resource_instance.graph
				if ri_graph != model:
					return HttpResponseNotFound('<h1>Instance not found</h1>')
			else:
				return HttpResponseNotFound('<h1>Instance not found</h1>')				

			writer = RdfWriter()
			writer.get_tiles(resourceinstanceids=[resourceid])
			graph = writer.get_rdf_graph()
			value = graph.serialize(format='json-ld', indent=2, context=self.context)
			js = json.loads(value)

			# Now pass to pyld to frame it so it's nested properly
			myframe = {
				"@omitDefault": True,
				# This needs to be fixed to use configurable URL pattern
				"@id": "http://localhost/resource/%s" % resourceid
			}

			framed = frame(js, myframe)
			out = compact(framed, self.context)
			out['@context'] = "https://linked.art/ns/v1/linked-art.json"
			value = json.dumps(out, indent=2, sort_keys=True)

		else:
			# GET on the container
			out = {
				"@context": "https://www.w3.org/ns/ldp/",
				"id": "http://localhost:8000/ldp/%s/" % modelid,
				"type": "BasicContainer",
				# Here we actually mean the name
				"label": str(model.name),
				"contains": []
			}

			out['contains'] = ["http://localhost:8000/ldp/%s/%s" % ( modelid, str(x.pk)) for x in Resource.objects.filter(graph=model)]
			value = json.dumps(out, indent=2, sort_keys=True)

		return HttpResponse(value)


	def post(self, *args, **kw):
		# Here we accept data in the body of the post
		# and reverse the process of resources/formats/rdffile.py to get from
		# RDF to the internal model

		# And then return the new representation as per get() above
		# (this gives the client back the UUIDs we just generated)
		pass

	def put(self, *args, **kw):
		# Here we accept data in the body of the PUT
		# and reverse the process of resources/formats/rdffile.py to get from
		# RDF to the internal model. Then we replace the instance with the given
		# resourceid

		# Then we return the new representation as per get() above
		pass

	def delete(self, *args, **kw):
		# Here we just delete the resource identified
		pass

