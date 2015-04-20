
import hashlib


def sha512half(s):
	return hashlib.sha512(s).digest()[0:32]


def hash160(s):
	h = hashlib.sha256(s).digest()

	m = hashlib.new('ripemd160')
	m.update(h)
	t = m.digest()
	return t


def sha256hash(s):

	s = s if s else ' '
	hash1 = hashlib.sha256(s).digest()
	hash2 = hashlib.sha256(hash1).digest()
	return hash2
