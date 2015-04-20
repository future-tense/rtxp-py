
from ecdsa import curves, SigningKey
from ecdsa.util import sigencode_der

from rtxp.core import hashes
from rtxp.core import utils


def sign(signing_hash, root_key):
	""" Signs hash with root_key. """

	number = utils.bytes_to_int(signing_hash)
	r, s = root_key.sign_number(number)
	r, s = _get_canonical_signature(r, s)
	return sigencode_der(r, s, None)


def get_root_key(seed):
	"""	Gets the root key from the seed. """

	# :TODO: add support for more than key #0
	# see https://github.com/ripple/ripple-lib/blob/develop/src/js/ripple/seed.js

	def generate_key(seed):

		i = 0
		res = 0
		while res < curves.SECP256k1.order:
			res = from_bytes(hashes.sha512half(seed + to_bytes(i, 4)))
			i += 1

		return res

	private_generator = generate_key(seed)
	public_generator = curves.SECP256k1.generator * private_generator

	# use public + private generators to generate a secret

	sequence = 0		#
	public_compressed = _get_compressed_point(public_generator)
	secret  = generate_key(public_compressed + to_bytes(sequence, 4))
	secret += private_generator
	secret %= curves.SECP256k1.order

	# use secret to generate a secp256k1 key

	return SigningKey.from_secret_exponent(secret, curves.SECP256k1)


def get_public_key_from_root(root_key):
	return _get_compressed_point(root_key.privkey.public_key.point, pad=True)


def get_public_key(seed):
	return get_public_key_from_root(get_root_key(seed))


#-------------------------------------------------------------------------------

def to_bytes(value, size):
	return utils.int_to_bytes(value, size=size)


def from_bytes(value):
	return utils.bytes_to_int(value)


def _get_compressed_point(point, pad=False):
	""" Returns the compressed ecc point. """

	header = '\x03' if point.y() & 1 else '\x02'
	bytes = to_bytes(
		point.x(),
		curves.SECP256k1.order.bit_length() // 8 if pad else None
	)
	return ''.join([header, bytes])


def _get_canonical_signature(r, s):
	""" returns a canonical signature. """

	N = curves.SECP256k1.order
	if not N / 2 >= s:
		s = N - s
	return r, s
