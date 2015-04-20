
import base58


_VER_SEED			= chr(33)
_VER_ACCOUNT_ID		= chr(0)
_VER_ACCOUNT_PUBLIC	= chr(67)


class Address(object):

	def __init__(self, alphabet):
		self.base58 = base58.Base58(alphabet)

	def to_human(self, version, data):
		return self.base58.encode_check(version + data)

	def from_human(self, version, h):
		seed = self.base58.decode_check(h)
		if seed[0] != version:
			raise TypeError

		return seed[1:]

	def account_to_human(self, account):
		return self.to_human(_VER_ACCOUNT_ID, account)

	def account_from_human(self, account):
		return self.from_human(_VER_ACCOUNT_ID, account)

	def seed_to_human(self, seed):
		return self.to_human(_VER_SEED, seed)

	def seed_from_human(self, seed):
		return self.from_human(_VER_SEED, seed)
