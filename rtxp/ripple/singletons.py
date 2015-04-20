
import rtxp.core.address
import rtxp.core.amount
import rtxp.core.deserialize
import rtxp.core.serialize
import rtxp.core.signer
import traits

address = rtxp.core.address.Address(traits.ALPHABET)

Amount = rtxp.core.amount.create_amount(traits.NATIVE)

deserializer = rtxp.core.deserialize.Deserializer(
	traits.NATIVE,
	address.account_to_human
)

serializer = rtxp.core.serialize.Serializer(
	traits.NATIVE,
	address.account_from_human
)

signer = rtxp.core.signer.Signer(address, serializer)
