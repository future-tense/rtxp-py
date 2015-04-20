
import rtxp.core.transaction as tx


class Transaction(tx.Transaction):

	tfDisallowSTR     = 0x00100000
	tfAllowSTR        = 0x00200000

	@staticmethod
	def account_merge(account, destination, sequence, fee):

		tx_json = {
			'TransactionType':	'AccountMerge',
			'Account':			account,
			'Destination':		destination,
			'Flags':			tx.Transaction.tfFullyCanonicalSig,
			'Sequence':			sequence,
			'Fee':				fee
		}

		return tx_json
