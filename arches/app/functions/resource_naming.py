import uuid
from django.core.exceptions import ValidationError
from arches.app.functions.base import BaseFunction
from arches.app.models import models
from arches.app.models.tile import Tile
import json

class ResourceNamingFunction(BaseFunction):

    def save(self):
        print 'calling save'

    def on_import(self):
        print 'calling on import'

    def get(self):
        print 'calling get'

    def delete(self):
        print 'calling delete'
