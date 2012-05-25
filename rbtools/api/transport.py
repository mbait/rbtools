class Transport(object):
	def __init__(self, builder, request):
		self._builder = builder
		self._request = request


class UrllibTransport(Transport):
	def __int__(self, *args):
		super(UrllibTransport, self).__init__(args)

	def __call__(self, **kwargs):
		pass


class AsyncTransport(Transport):
	"""Needs to be implemented."""
	def __int__(self, *args):
		super(AsyncTransport, self).__init__(args)

	def __call__(self, callback=None, **kwargs):
		"""Should send request asynchronously and
		call the 'callback' upon response.
		"""
		pass

# vim : set ts=4 :
# vim : set sw=4 :
# vim : set expandtab :
