
from decimal import Decimal
import utils

FIELD_MAP = {

	(1, 1):		'LedgerEntryType',
	(1, 2):		'TransactionType',

	(2, 2):		'Flags',
	(2, 3):		'SourceTag',
	(2, 4):		'Sequence',
	(2, 5):		'PreviousTxnLgrSeq',
	(2, 10):	'Expiration',
	(2, 11):	'TransferRate',
	(2, 13):	'OwnerCount',
	(2, 14):	'DestinationTag',
	(2, 16):	'HighQualityIn',
	(2, 17):	'HighQualityOut',
	(2, 18):	'LowQualityIn',
	(2, 19):	'LowQualityOut',
	(2, 20):	'QualityIn',
	(2, 21):	'QualityOut',
	(2, 25):	'OfferSequence',
	(2, 27):	'LastLedgerSequence',
	(2, 28):	'TransactionIndex',
	(2, 33):	'SetFlag',
	(2, 34):	'ClearFlag',

	(3, 1):		'IndexNext',
	(3, 2):		'IndexPrevious',
	(3, 3):		'BookNode',
	(3, 4):		'OwnerNode',
	(3, 6):		'ExchangeRate',
	(3, 7):		'LowNode',
	(3, 8):		'HighNode',

	(4, 1):		'EmailHash',

	(5, 5):		'PreviousTxnID',
	(5, 6):		'LedgerIndex',
	(5, 8):		'RootIndex',
	(5, 9):		'AccountTxnID',
	(5, 16):	'BookDirectory',
	(5, 17):	'InvoiceID',

	(6, 1):		'Amount',
	(6, 2):		'Balance',
	(6, 3):		'LimitAmount',
	(6, 4):		'TakerPays',
	(6, 5):		'TakerGets',
	(6, 6):		'LowLimit',
	(6, 7):		'HighLimit',
	(6, 8):		'Fee',
	(6, 9):		'SendMax',
	(6, 18):	'DeliveredAmount',

	(7, 2):		'MessageKey',
	(7, 3):		'SigningPubKey',
	(7, 4):		'TxnSignature',
	(7, 7):		'Domain',
	(7, 12):	'MemoType',
	(7, 13):	'MemoData',
	(7, 14):	'MemoFormat',

	(8, 1):		'Account',
	(8, 2):		'Owner',
	(8, 3):		'Destination',
	(8, 9):		'InflationDest',		#stellar
	(8, 8):		'RegularKey',
	(8, 10):	'SetAuthKey',			#stellar

	(14, 1):	None,
	(14, 2):	'TransactionMetaData',
	(14, 3):	'CreatedNode',
	(14, 4):	'DeletedNode',
	(14, 5):	'ModifiedNode',
	(14, 6):	'PreviousFields',
	(14, 7):	'FinalFields',
	(14, 8):	'NewFields',
	(14, 9):	'TemplateEntry',
	(14, 10):	'Memo',

	(15, 1):	None,
	(15, 8):	'AffectedNodes',
	(15, 9):	'Memos',

	(16, 3):	'TransactionResult',

	(17, 1):	'TakerPaysCurrency',
	(17, 2):	'TakerPaysIssuer',
	(17, 3):	'TakerGetsCurrency',
	(17, 4):	'TakerGetsIssuer',

	(18, 1):	'Paths',
}

TRANSACTION_TYPES = {
	0:	'Payment',
	3:	'AccountSet',
	4:	'AccountMerge',					#stellar
	5:	'SetRegularKey',
	7:	'OfferCreate',
	8:	'OfferCancel',
	20:	'TrustSet',
}

LEDGER_ENTRY_TYPES = {
	97:		'AccountRoot',
	100:	'DirectoryNode',
	111:	'Offer',
	114:	'RippleState',
}

TRANSACTION_RESULTS = {
	0:		'tesSUCCESS',
}


ALL_ZEROES = 20*'\0'


def _clean_up(value):

	v = str(value)
	if '.' in v:
		v = v.rstrip('0')
		if v[-1] == '.':
			v = v[:-1]
	return v


def _is_iso(currency):
	return (
		currency[:12] == '\0\0\0\0\0\0\0\0\0\0\0\0' and
		currency[15:] == '\0\0\0\0\0'
	)


class Deserializer(object):

	def __init__(self, native_currency, account_to_human):
		self.native_currency = native_currency
		self.account_to_human = account_to_human
		self.blob = None

	def deserialize_blob(self, blob):

		self.blob = blob

		json = {}
		while self.blob:
			key, value = self.get_kv_pair()
			json[key] = value
			print key, value

		return json

	def peek_byte(self):
		return ord(self.blob[0])

	def get_byte(self):
		char = ord(self.blob[0])
		self.blob = self.blob[1:]
		return char

	def get_bytes(self, n):
		res, self.blob = self.blob[:n], self.blob[n:]
		return res

	def get_kv_pair(self):
		char = self.get_byte()
		type_id  = char >> 4
		field_id = char & 15

		if type_id == 0:
			type_id = self.get_byte()

		if field_id == 0:
			field_id = self.get_byte()

		key = FIELD_MAP[(type_id, field_id)]
		value = self.deserializer_dict[type_id](self) if key else None

		if key == 'TransactionType':
			value = TRANSACTION_TYPES[value]

		elif key == 'LedgerEntryType':
			value = LEDGER_ENTRY_TYPES[value]

		elif key == 'TransactionResult':
			value = TRANSACTION_RESULTS[value]

		return key, value

	def deserialize_int8(self):
		return utils.bytes_to_int(self.get_bytes(1))

	def deserialize_int16(self):
		return utils.bytes_to_int(self.get_bytes(2))

	def deserialize_int32(self):
		return utils.bytes_to_int(self.get_bytes(4))

	def deserialize_int64(self):
		return utils.to_hex(self.get_bytes(8))

	def deserialize_hash128(self):
		return utils.to_hex(self.get_bytes(16))

	def deserialize_hash256(self):
		return utils.to_hex(self.get_bytes(32))

	def deserialize_hash160(self):
		return utils.to_hex(self.get_bytes(20))

	def deserialize_currency(self):
		currency = self.get_bytes(20)

		if currency == ALL_ZEROES:
			currency = self.native_currency
		elif _is_iso(currency):
			currency = currency[12:15]
		else:
			currency = utils.to_hex(currency)
		return currency

	def deserialize_amount(self):

		t = utils.bytes_to_int(self.get_bytes(8))
		if (t >> 63) == 1:

			positive = (t >> 62) & 1
			exponent = ((t >> 54) & 255) - 97
			value = str(t & ((1 << 54) - 1))
			if value != '0':
				decimal = Decimal((positive ^ 1, tuple(map(int, value)), exponent))
				value = _clean_up(str(decimal))

			currency = self.deserialize_currency()
			issuer = self.deserialize_account_id()

			return {
				'value': value,
				'currency': currency,
				'issuer': issuer
			}
		else:
			positive = t >> 62
			value = t & ((1 << 62) - 1)
			value = value if positive else -value
			return str(value)

	def deserialize_vl_length(self):

		"""
			Variable Length Data Encoding

			A variable-length type contains a length indicator followed by the data.
			The length of the data is determined based on the value of the first byte as follows:

			0 - 192
				The length is 0 to 192, occupies 1-byte, and is the value of the first byte
			193 - 240
				The length 193 to 12,480, occupies 2-bytes, and is computed:
					193 + (b1-193)*256 + b2
			241 - 254
				The length is 12,481 to 918,744, occupies 3-bytes, and is computed:
						12481 + (b1-241)*65536 + b2*256 + b3
			255
				Reserved
		"""

		l1 = self.get_byte()
		if l1 <= 192:
			return l1
		elif l1 <= 240:
			l2 = self.get_byte()
			return 193 + (l1 - 193) * 256 + l2
		else:
			l2 = self.get_byte()
			l3 = self.get_byte()
			return 12481 + (l1 - 241) * 65536 + l2 * 256 + l3

	def deserialize_vl(self):
		length = self.deserialize_vl_length()
		bytes  = self.get_bytes(length)
		return utils.to_hex(bytes).upper()

	def deserialize_account_id(self):
		bytes = self.get_bytes(20)
		return self.account_to_human(bytes)

	def deserialize_account(self):
		length = self.get_byte()
		return self.deserialize_account_id()

	def deserialize_object(self):

		json = {}
		while True:
			key, value = self.get_kv_pair()
			if key is None:
				break

			json[key] = value

		return json

	def deserialize_array(self):

		array = []
		while True:
			key, value = self.get_kv_pair()
			if key is None:
				break
			array.append({key: value})

		return array

	def deserialize_path(self):

		FLAG_ACCOUNT	= 0x01
		FLAG_CURRENCY	= 0x10
		FLAG_ISSUER		= 0x20

		path = []
		while True:
			flags = self.peek_byte()

			if flags == 255:
				skip = self.get_byte()
				break
			elif flags == 0:
				break

			flags = self.get_byte()

			entry = {}
			if flags & FLAG_ACCOUNT:
				entry['account'] = self.deserialize_account_id()
			if flags & FLAG_CURRENCY:
				entry['currency'] = self.deserialize_currency()
			if flags & FLAG_ISSUER:
				entry['issuer'] = self.deserialize_account_id()
			path.append(entry)

		return path

	def deserialize_pathset(self):

		pathset = []

		while self.peek_byte() != 0:
			path = self.deserialize_path()
			pathset.append(path)

		skip = self.get_byte()
		return pathset

	deserializer_dict = {
		1:	deserialize_int16,
		2:	deserialize_int32,
		3:	deserialize_int64,
		4:	deserialize_hash128,
		5:	deserialize_hash256,
		6:	deserialize_amount,
		7:	deserialize_vl,
		8:  deserialize_account,
		14:	deserialize_object,
		15:	deserialize_array,
		16:	deserialize_int8,
		17:	deserialize_hash160,
		18:	deserialize_pathset,
	}
