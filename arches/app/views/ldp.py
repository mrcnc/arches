


from arches.app.views.base import BaseManagerView
from django.http import HttpResponse, HttpResponseNotFound
from arches.app.models.resource import Resource
from arches.app.utils.data_management.resources.formats.rdffile import RdfWriter

from pyld import jsonld
from pyld.jsonld import compact, expand, frame
import json

class LdpView(BaseManagerView):

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
				# This needs to be fixed
				"@id": "http://localhost/resource/%s" % resourceid
			}

			framed = frame(js, myframe)
			out = compact(framed, self.context)
			out['@context'] = "https://linked.art/ns/v1/linked-art.json"
			value = json.dumps(out, indent=2, sort_keys=True)

		else:
			# GET on the container
			pass

		return HttpResponse(value)


	def post(self, *args, **kw):
		pass

	def delete(self, *args, **kw):
		pass
