
from decimal import Decimal

import utils

#-------------------------------------------------------------------------------

FIELD_MAP = {
	'Account':			(8, 1),
	'Amount':			(6, 1),
	'ClearFlag':		(2, 34),
	'Destination':		(8, 3),
	'DestinationTag':	(2, 14),
	'Fee':				(6, 8),
	'Flags':			(2, 2),
	'InflationDest':	(8, 9),				#stellar
	'LimitAmount':		(6, 3),
	'OfferSequence':	(2, 25),
	'Paths':			(18, 1),
	'RegularKey':		(8, 8),
	'SendMax':			(6, 9),
	'Sequence':			(2, 4),
	'SetAuthKey':		(8, 10),			#stellar
	'SetFlag':			(2, 33),
	'SigningPubKey':	(7, 3),
	'SourceTag':		(2, 3),
	'TakerGets':		(6, 5),
	'TakerPays':		(6, 4),
	'TransactionType':	(1, 2),
	'TransferRate':		(2, 11),
	'TxnSignature':		(7, 4),
}

TRANSACTION_TYPES = {
	'AccountMerge':		4,					#stellar
	'AccountSet':		3,
	'OfferCancel':		8,
	'OfferCreate':		7,
	'Payment': 			0,
	'SetRegularKey':	5,
	'TrustSet':			20
}

#-------------------------------------------------------------------------------


class Serializer(object):

	def __init__(self, native_currency, account_from_human):
		self.native_currency = native_currency
		self.account_from_human = account_from_human

	def serialize_json(self, tx_json):

		def comparator(a, b):
			return 1 if FIELD_MAP[a] > FIELD_MAP[b] else -1

		blob = ''
		keys = sorted(tx_json.keys(), cmp=comparator)
		for k in keys:
			value = tx_json[k]
			if k == 'TransactionType':
				value = TRANSACTION_TYPES[value]

			type_id, field_id = FIELD_MAP[k]
			tag = ((type_id << 4 if type_id  < 16 else 0) |
				   (field_id     if field_id < 16 else 0))
			blob += chr(tag)

			if type_id >= 16:
				blob += chr(type_id)
			if field_id >= 16:
				blob += chr(field_id)

			if type_id in self.serializer_dict:
				blob += self.serializer_dict[type_id](self, value)

		return blob

	def parse_non_native_amount(self, string):

		amount	 = Decimal(string).normalize()
		parts	 = amount.as_tuple()
		exponent = parts.exponent

		value = ''.join(map(str, parts.digits))
		exponent += len(value)

		value = value.ljust(16, '0')
		exponent -= 16

		value = int(value)
		if value == 0:
			exponent = -99

		return parts.sign, value, exponent

	def serialize_non_native_amount(self, amount):

		negative, value, exponent = self.parse_non_native_amount(amount)

		hi = 1 << 31
		if value:
			if not negative:
				hi |= 1 << 30
			hi |= ((97 + exponent) & 0xff) << 22

		value |= hi << 32
		return self.serialize_int64(value)

	def serialize_currency(self, currency):

		if currency == self.native_currency:
			data = 20 * chr(0)
		else:
			data = 12 * chr(0) + currency + 5 * chr(0)
		return data

	def serialize_native_amount(self, amount):

		amount = int(amount)
		pos = True if amount > 0 else False
		amount &= (1 << 62) - 1
		if pos:
			amount |= 1 << 62

		return self.serialize_int64(amount)

	def serialize_account_id(self, human):
		return self.account_from_human(human)

	def serialize_amount(self, value):

		if type(value) == int:
			amount = value				#	tx fee in provided as an int
		else:
			amount = value.to_json()

		if type(amount) == dict:
			blob  = self.serialize_non_native_amount(amount['value'])
			blob += self.serialize_currency(amount['currency'])
			blob += self.serialize_account_id(amount['issuer'])
		else:
			blob  = self.serialize_native_amount(amount)
		return blob

	def serialize_account(self, value):
		data = self.serialize_account_id(value)
		return self.serialize_vl(data)

	def serialize_path(self, path):

		FLAG_ACCOUNT	= 0x01
		FLAG_CURRENCY	= 0x10
		FLAG_ISSUER		= 0x20

		blob = ''
		for entry in path:
			flags = 0
			if 'account' in entry:
				flags |= FLAG_ACCOUNT
			if 'currency' in entry:
				flags |= FLAG_CURRENCY
			if 'issuer' in entry:
				flags |= FLAG_ISSUER
			if entry['type'] != flags:
				#raise hell
				pass

			flags = entry['type']
			blob += chr(flags)
			if flags & FLAG_ACCOUNT:
				blob += self.serialize_account_id(entry['account'])
			if flags & FLAG_CURRENCY:
				blob += self.serialize_currency(entry['currency'])
			if flags & FLAG_ISSUER:
				blob += self.serialize_account_id(entry['issuer'])

		return blob

	def serialize_pathset(self, pathset):

		PATH_BOUNDARY = chr(0xff)
		PATH_END      = chr(0x00)

		blobs = [
			self.serialize_path(path)
			for path in pathset
		]

		return PATH_BOUNDARY.join(blobs) + PATH_END

	def serialize_int16(self, value):
		return utils.int_to_bytes(value, size=2)

	def serialize_int32(self, value):
		return utils.int_to_bytes(value, size=4)

	def serialize_int64(self, value):
		return utils.int_to_bytes(value, size=8)

	def serialize_vl(self, value):
		return chr(len(value)) + value

	serializer_dict = {
		1: serialize_int16,
		2: serialize_int32,
		6: serialize_amount,
		7: serialize_vl,
		8: serialize_account,
		18: serialize_pathset,
	}

#-------------------------------------------------------------------------------
