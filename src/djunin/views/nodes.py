# -*- coding: utf-8 -*-
import json

from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.views.generic import View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from djunin.graphs import FlotGraphOptsGenerator, FlotGraphDataGenerator
from djunin.models.muninobj import Node, Graph
from djunin.views.base import BaseViewMixin
import logging

logger = logging.getLogger(__file__)

class NodesListView(BaseViewMixin, ListView):
	model = Node
	context_object_name = 'nodes'
	sidebar_item = 'nodes'
	page_title = _('Nodes')

	def get_page_title(self):
		return self.kwargs.get('group', self.page_title)

	def get_queryset(self):
		nodes = Node.objects.all()

		if 'group' in self.kwargs:
			nodes = nodes.filter(group=self.kwargs['group'])

		return nodes

	def get_context_data(self, **kwargs):
		kwargs.setdefault('selected_group', self.kwargs.get('group', None))
		return super(NodesListView, self).get_context_data(**kwargs)

class GraphsListView(NodesListView):
	model = Graph
	context_object_name = 'graphs'
	sidebar_item = 'nodes'

	def __init__(self, *args, **kwargs):
		super(GraphsListView, self).__init__(*args, **kwargs)
		self._node = None

	def get_page_title(self):
		return self.node.name

	@property
	def node(self):
		if self._node is None:
			self._node = get_object_or_404(Node.objects.filter(group=self.kwargs['group'], name=self.kwargs['node']))
		return self._node

	def get_context_data(self, **kwargs):
		kwargs.setdefault('node', self.node)
		kwargs.setdefault('selected_group', self.node.group)
		return super(GraphsListView, self).get_context_data(nodes=super(GraphsListView, self).get_queryset(), **kwargs)

	def get_queryset(self):
		return super(ListView, self).get_queryset().\
			filter(node=self.node, parent=None).\
			select_related('node').\
			order_by('graph_category', 'name')


class GraphDataView(BaseViewMixin, DetailView):
	model = Graph
	slug_url_kwarg = 'name'
	slug_field = 'name'

	def __init__(self, *args, **kwargs):
		super(GraphDataView, self).__init__(*args, **kwargs)
		self._node = None

	@property
	def node(self):
		if self._node is None:
			self._node = get_object_or_404(Node.objects.filter(group=self.kwargs['group'], name=self.kwargs['node']))
		return self._node

	def get_queryset(self):
		return Graph.objects.filter(node=self.node, name=self.kwargs['name'])

	def render_to_response(self, context, **response_kwargs):
		return JsonResponse({
			'graph_name': self.kwargs['name'],
			'options': FlotGraphOptsGenerator().generate(self.node, self.get_queryset().get()),
			'datarows': FlotGraphDataGenerator().generate(self.node, self.object),
		})
