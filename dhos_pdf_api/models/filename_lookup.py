from typing import Any, Dict

from flask_batteries_included.sqldb import ModelIdentifier, db


class FilenameLookup(ModelIdentifier, db.Model):

    lookup_uuid = db.Column(db.String, nullable=False, unique=True)
    file_name = db.Column(db.String, nullable=False)

    def __init__(self, **kwargs: Any) -> None:
        # Constructor to satisfy linters.
        super(FilenameLookup, self).__init__(**kwargs)

    @classmethod
    def schema(cls) -> Dict:
        raise NotImplementedError
