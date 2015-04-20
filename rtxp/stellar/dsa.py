
import ed25519


def sign(message, seed):
	return ed25519.SigningKey(seed).sign(message)[0:64]


def get_public_key(seed):
	return ed25519.SigningKey(seed).get_verifying_key().vk_s
