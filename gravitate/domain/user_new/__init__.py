from flask_boiler.domain_model import DomainModel
from flask_boiler import attrs
from flask_boiler.utils import snapshot_to_obj


class User(DomainModel):

    class Meta:
        collection_name = "users"

    name = attrs.bproperty()
    email = attrs.bproperty()
    _id = attrs.bproperty(data_key="id", import_enabled=False)

    @classmethod
    def get(cls, *args, doc_id=None, transaction=None, **kwargs):
        doc_ref = cls.ref_from_id(doc_id=doc_id)
        if transaction is None:
            snapshot = doc_ref.get()
        else:
            snapshot = doc_ref.get(transaction=transaction)
        return cls.from_dict(
            d=snapshot.to_dict(),
            transaction=transaction,
            **kwargs,
            doc_id=snapshot.reference.id,
        )

    @_id.getter
    def _id(self):
        return self.doc_id


