from typing import Dict

from dhos_pdf_api.models.api_spec import LocationSchema


class TestSchema:
    def test_location_schema(self) -> None:
        location: Dict = {
            "active": True,
            "address_line_1": None,
            "address_line_2": None,
            "address_line_3": None,
            "address_line_4": None,
            "country": None,
            "created": "2021-10-20T01:31:41.413Z",
            "created_by": "dhos-robot",
            "dh_products": [
                {
                    "closed_date": None,
                    "created": "2021-10-20T01:31:41.435",
                    "opened_date": "2017-10-19",
                    "product_name": "SEND",
                    "uuid": "9895fdb3-28f2-4b53-9148-e8c36d151525",
                }
            ],
            "display_name": "Bed 3",
            "locality": None,
            "location_type": "229772003",
            "modified": "2021-10-20T01:31:41.413Z",
            "modified_by": "dhos-robot",
            "ods_code": "CG19DIH",
            "parent": {
                "display_name": "Bay 3",
                "location_type": "225730009",
                "ods_code": "VU91YKS",
                "parent": {
                    "display_name": "A&E",
                    "location_type": "225746001",
                    "ods_code": "458EL",
                    "parent": {
                        "display_name": "Elm Hospital",
                        "location_type": "22232009",
                        "ods_code": "956HO",
                        "parent": None,
                        "uuid": "static_location_uuid_E1",
                    },
                    "uuid": "static_location_uuid_E1-1",
                },
                "uuid": "0f64a82c-d9b5-4679-9703-4910645a88b7",
            },
            "postcode": None,
            "region": None,
            "uuid": "37e4b6d9-bc82-49ed-b160-a3d1cb73a196",
        }

        expected: Dict = {
            "display_name": "Bed 3",
            "location_type": "229772003",
            "ods_code": "CG19DIH",
            "parent": {
                "display_name": "Bay 3",
                "location_type": "225730009",
                "ods_code": "VU91YKS",
                "parent": {
                    "display_name": "A&E",
                    "location_type": "225746001",
                    "ods_code": "458EL",
                    "parent": {
                        "display_name": "Elm Hospital",
                        "location_type": "22232009",
                        "ods_code": "956HO",
                        "parent": None,
                    },
                },
            },
        }

        data: Dict = LocationSchema().load(location)
        assert data == expected
