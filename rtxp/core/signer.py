
import os

from rtxp.core import dsa
from rtxp.core import hashes
from rtxp.core import utils


_HASH_TX_SIGN = 'STX\0'
_HASH_TX_SIGN_TESTNET = 'stx\0'


def _get_signing_hash(blob, test=False):
	prefix = _HASH_TX_SIGN_TESTNET if test else _HASH_TX_SIGN
	return hashes.sha512half(prefix + blob)


def _sign_blob(blob, root_key, test=False):
	signing_hash = _get_signing_hash(blob, test)
	return dsa.sign(signing_hash, root_key)


class Signer(object):

	def __init__(self, address, serializer):
		self.address = address
		self.serializer = serializer

	def generate_keypair(self):
		""" Generate an address and a secret key """

		seed = os.urandom(16)
		public_key = dsa.get_public_key(seed)
		account = hashes.hash160(public_key)
		account = self.address.account_to_human(account)
		seed = self.address.seed_to_human(seed)
		return account, seed

	def account_from_seed(self, secret):

		seed = self.address.seed_from_human(secret)
		public_key = dsa.get_public_key(seed)
		account = hashes.hash160(public_key)
		account = self.address.account_to_human(account)
		return account

	def sign(self, tx_json, secret, test=False):
		""" Signs a transaction with the secret and returns a tx_blob """

		seed = self.address.seed_from_human(secret)
		root_key = dsa.get_root_key(seed)
		public_key = dsa.get_public_key_from_root(root_key)
		tx_json['SigningPubKey'] = public_key

		tx_blob = self.serializer.serialize_json(tx_json)
		signature = _sign_blob(tx_blob, root_key, True)
		tx_json['TxnSignature'] = signature

		tx_blob = self.serializer.serialize_json(tx_json)
		return utils.to_hex(tx_blob)
