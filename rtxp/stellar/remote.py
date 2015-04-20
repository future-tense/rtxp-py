
import rtxp.core.remote

from server import Server
from transaction import Transaction
from singletons import signer

#-------------------------------------------------------------------------------


class Remote(rtxp.core.remote.Remote):

	def __init__(self,
			url,
			async=False,
			callback=None,
			server=Server,
			transaction=Transaction,
			signer=signer
	):
		super(Remote, self).__init__(
			url,
			async,
			callback,
			server,
			transaction,
			signer
		)

	def create_find_path(
			self,
			source_account,
			destination_account,
			destination_amount,
			callback,
			async=None,
			**kwargs
	):
		""" Creates a find_path_session """

		local = locals()
		local['subcommand'] = 'create'
		callback = local.pop('callback')
		self.server.set_path_callback(callback)

		return self.__command('find_path', local)

	def close_find_path(self, async=None):
		""" Closes a find_path session """

		subcommand = 'close'
		return self.__command('find_path', locals())

	def get_static_path(
			self,
			source_account,
			destination_account,
			destination_amount,
			async=None
	):
		""" Finds a path for a transfer """

		return self.__command('static_path_find', locals())

	def merge_accounts(self, secret, account, destination, async=None):
		""" Merges an account into a destination account. """

		if not account:
			account = signer.account_from_seed(secret)

		def on_success(res):
			seq, fee = res
			tx_json = Transaction.account_merge(
				account,
				destination,
				seq,
				fee
			)
			tx_blob = signer.sign(tx_json, secret)
			return self.submit_transaction(tx_blob, async=True)

		return self.__hl_command(account, on_success, async)
