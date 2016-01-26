# -*- coding: utf-8 -*-
from django.conf import settings

from djunin.models import Node
from djunin.objects import MuninDataFile

class BaseViewMixin(object):
	page_title = None
	sidebar_item = None

	def __init__(self):
		self._datafile = None

	@property
	def data_file(self):
		if self._datafile is None:
			self._datafile = MuninDataFile()
		return self._datafile

	@property
	def all_node_groups(self):
		return Node.objects.values_list('group', flat=True).order_by('group').distinct()

	def get_context_data(self, **kwargs):
		d = kwargs
		d.setdefault('page_title', self.get_page_title())
		d.setdefault('sidebar_item', self.get_sidebar_item())
		d.setdefault('node_groups', self.all_node_groups)
		return super(BaseViewMixin, self).get_context_data(**d)

	def get_page_title(self):
		return self.page_title

	def get_sidebar_item(self):
		return self.sidebar_item
