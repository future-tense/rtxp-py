
import rtxp.core.remote
from singletons import signer


class Remote(rtxp.core.remote.Remote):

	def __init__(self, url, async=False, callback=None, signer=signer):
		super(Remote, self).__init__(
			url,
			async,
			callback,
			signer=signer
		)
