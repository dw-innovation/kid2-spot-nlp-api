import unittest

from app.adopt_generation import adopt_generation


class TestAdoptFunction(unittest.TestCase):
    def setUp(self):
        self.test_data = [
            {
                "input": {'area': {'name': 'berlin', 'type': 'area'},
                          'entities': [{'id': 0, 'name': 'kiosk'}, {'id': 1, 'name': 'park'}],
                          'relations': [{'name': 'dist', 'source': 0, 'target': 1, 'value': '100 m'}]},
                "expected_output": {'area': {'value': 'berlin', 'type': 'area'},
                                    'nodes': [
                                        {
                                            'id': 0,
                                            'type': 'nwr',
                                            'name': 'kiosk',
                                            'display_name': 'kiosks',
                                            'filters': [
                                                {
                                                    'or': [{'key': 'building', 'operator': '=', 'value': 'kiosk'},
                                                           {'key': 'shop', 'operator': '=', 'value': 'kiosk'},
                                                           {'key': 'shop', 'operator': '=', 'value': 'convenience'}]}]
                                        },
                                        {
                                            'id': 1,
                                            'type': 'nwr',
                                            'name': 'park',
                                            'display_name': 'parks',
                                            'filters': [
                                                {'or': [
                                                    {'key': 'landuse', 'operator': '=', 'value': 'recreation_ground'},
                                                    {'key': 'landuse', 'operator': '=', 'value': 'village_green'},
                                                    {'key': 'leisure', 'operator': '=', 'value': 'park'},
                                                    {'key': 'leisure', 'operator': '=', 'value': 'garden'}]}
                                            ]
                                        }
                                    ],
                                    'edges': [{'type': 'dist', 'source': 0, 'target': 1, 'distance': '100 m'}]},
            },
            {
                "input": {
                    "area": {
                        "type": "area",
                        "name": "London"
                    },
                    "relations": [
                        {
                            "source": 0,
                            "target": 1,
                            "name": "dist",
                            "value": "200 m"
                        }
                    ],
                    "entities": [
                        {
                            "id": 0,
                            "name": "italian restaurant",
                        },
                        {
                            "id": 1,
                            "name": "fountain",
                        }
                    ]
                },
                "expected_output": {
                    "area": {
                        "type": "area",
                        "value": "London"
                    },
                    "edges": [
                        {
                            "source": 0,
                            "target": 1,
                            "type": "dist",
                            "distance": "200 m"
                        }
                    ],
                    "nodes": [
                        {
                            "id": 0,
                            "name": "italian restaurant",
                            "display_name": "italian restaurants",
                            "type": "nwr",
                            "filters": [
                                {
                                    "and": [

                                        {'or': [{'key': 'amenity', 'operator': '=', 'value': 'restaurant'},
                                                {'key': 'amenity', 'operator': '=', 'value': 'food_court'},
                                                {'key': 'amenity', 'operator': '=', 'value': 'fast_food'}]},
                                        {
                                            "key": "cuisine",
                                            "operator": "=",
                                            "value": "italian"
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "id": 1,
                            "name": "fountain",
                            "display_name": "fountains",
                            "type": "nwr",
                            "filters": [
                                {
                                    "or": [
                                        {
                                            "key": "amenity",
                                            "operator": "=",
                                            "value": "fountain"
                                        },
                                        {
                                            "key": "man_made",
                                            "operator": "=",
                                            "value": "water_well"
                                        },
                                        {
                                            "key": "man_made",
                                            "operator": "=",
                                            "value": "water_tap"
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }

            },
            {
                "input": {
                    'area': {'name': '', 'type': 'bbox'},
                    'entities': [{'id': 0, 'name': 'kiosk'}, {'id': 1, 'name': 'supermarket', 'filters': [
                        {'name': 'height', 'operator': '=', 'value': "10"}]}],

                },
                "expected_output": {
                    "area": {"type": "area", "value": "bbox"},
                    "nodes": [
                        {
                            'id': 0,
                            'type': 'nwr',
                            'filters': [
                                {
                                    'or': [{'key': 'building', 'operator': '=', 'value': 'kiosk'},
                                           {'key': 'shop', 'operator': '=', 'value': 'kiosk'},
                                           {'key': 'shop', 'operator': '=', 'value': 'convenience'}]}],
                            'name': 'kiosk',
                            'display_name': 'kiosks'
                        },
                        {
                            "id": 1,
                            "type": "nwr",
                            "filters": [
                                {
                                    "and": [
                                        {
                                            "or": [
                                                {"key": "shop", "operator": "=", "value": "supermarket"},
                                                {"key": "building", "operator": "=", "value": "supermarket"}
                                            ]
                                        },
                                        {'operator': '=', 'value': '10', 'key': 'height'}
                                    ]
                                }
                            ],
                            "name": "supermarket",
                            "display_name": "supermarkets"
                        }
                    ]
                }
            },
            {
                "input": {'area': {'name': 'berlin', 'type': 'area'},
                          'entities': [{'id': 0, 'name': 'bouldering'}, {'id': 1, 'name': 'river'}],
                          'relations': [{'name': 'dist', 'source': 0, 'target': 1, 'value': '127.8 cm'}]},
                "expected_output": {'area': {'type': 'area', 'value': 'berlin'}, 'nodes': [{'id': 0, 'type': 'nwr',
                                                                                     'filters': [{'and': [
                                                                                         {'key': 'sport',
                                                                                          'operator': '=',
                                                                                          'value': 'climbing'}]}],
                                                                                     'name': 'bouldering',
                                                                                     'display_name': 'boulderings'},
                                                                                    {'id': 1, 'type': 'nwr',
                                                                                     'filters': [{'or': [
                                                                                         {'key': 'water',
                                                                                          'operator': '=',
                                                                                          'value': 'river'},
                                                                                         {'key': 'water',
                                                                                          'operator': '=',
                                                                                          'value': 'stream'},
                                                                                         {'key': 'water',
                                                                                          'operator': '=',
                                                                                          'value': 'canal'},
                                                                                         {'key': 'waterway',
                                                                                          'operator': '=',
                                                                                          'value': 'river'},
                                                                                         {'key': 'waterway',
                                                                                          'operator': '=',
                                                                                          'value': 'stream'},
                                                                                         {'key': 'waterway',
                                                                                          'operator': '=',
                                                                                          'value': 'canal'},
                                                                                         {'key': 'water',
                                                                                          'operator': '=',
                                                                                          'value': 'oxbow'}]}],
                                                                                     'name': 'river',
                                                                                     'display_name': 'rivers'}],
                             'edges': [{'source': 0, 'target': 1, 'distance': '150 m', 'type': 'dist'}]}

            }
        ]

    def test_assign_combination(self):
        for sample in self.test_data:
            predicted_output = adopt_generation(sample['input'])
            assert predicted_output == sample['expected_output']

    if __name__ == '__main__':
        unittest.main()
