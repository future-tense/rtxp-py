
import rtxp.core.server


class Server(rtxp.core.server.Server):

	def __init__(self, url, callback):
		super(Server, self).__init__(url, callback)

	def clear_subscriptions(self):

		self.subscriptions = {
			'streams':		[],
			'accounts':		[],
			'accounts_rt':	[],
			'books':		[]
		}
