from flask_boiler.domain_model import DomainModel
from flask_boiler import attrs


class User(DomainModel):

    class Meta:
        collection_name = "users"

    name = attrs.bproperty()
    email = attrs.bproperty()
    _id = attrs.bproperty(data_key="id", import_enabled=False)

    @_id.getter
    def _id(self):
        return self.doc_id
