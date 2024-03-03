import unittest

from app.adopt_generation import adopt_generation


class TestAdoptFunction(unittest.TestCase):
    def setUp(self):
        self.test_data = [
            {
                "input": {'area': {'name': 'berlin', 'type': 'area'},
                          'entities': [{'id': 0, 'name': 'kiosk'}, {'id': 1, 'name': 'park'}],
                          'relations': [{'name': 'dist', 'source': 0, 'target': 1, 'value': '100 m'}]},
                "expected_output": {'area': {'type': 'area', 'value': 'berlin'}, 'nodes': [{'id': 0, 'type': 'nwr',
                                                                                            'filters': [{'or': [
                                                                                                {'key': 'building',
                                                                                                 'operator': '=',
                                                                                                 'value': 'kiosk'},
                                                                                                {'key': 'shop',
                                                                                                 'operator': '=',
                                                                                                 'value': 'kiosk'},
                                                                                                {'key': 'shop',
                                                                                                 'operator': '=',
                                                                                                 'value': 'convenience'},
                                                                                                {'key': 'shop',
                                                                                                 'operator': '=',
                                                                                                 'value': 'cigarette'}]}],
                                                                                            'name': 'kiosk',
                                                                                            'display_name': 'kiosks'},
                                                                                           {'id': 1, 'type': 'nwr',
                                                                                            'filters': [{'or': [
                                                                                                {'key': 'landuse',
                                                                                                 'operator': '=',
                                                                                                 'value': 'recreation_ground'},
                                                                                                {'key': 'landuse',
                                                                                                 'operator': '=',
                                                                                                 'value': 'village_green'},
                                                                                                {'key': 'leisure',
                                                                                                 'operator': '=',
                                                                                                 'value': 'park'},
                                                                                                {'key': 'leisure',
                                                                                                 'operator': '=',
                                                                                                 'value': 'garden'}]}],
                                                                                            'name': 'park',
                                                                                            'display_name': 'parks'}],
                                    'edges': [{'source': 0, 'target': 1, 'distance': '100 m', 'type': 'dist'}]}
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

            }
        ]

    def test_assign_combination(self):
        for sample in self.test_data:
            predicted_output = adopt_generation(sample['input'])
            print("predicted output")
            print(predicted_output)
            assert predicted_output == sample['expected_output']

    def test_return_partial_matches(self):
        test_input = {'area': {'name': 'augsburg', 'type': 'area'},
                      'entities': [{'id': 0, 'name': 'kfc'}, {'id': 1, 'name': 'pizza hut'},
                                   {'filters': [{'name': 'name', 'operator': '=', 'value': 'al sultan'}], 'id': 2,
                                    'name': 'restaurant'}],
                      'relations': [{'name': 'dist', 'source': 0, 'target': 1, 'value': '10 m'},
                                    {'name': 'dist', 'source': 1, 'target': 2, 'value': '10 m'}]}

        assert adopt_generation(test_input)

    def test_invalid_filter(self):
        test_input = {'area': {'name': 'perugia', 'type': 'area'}, 'entities': [
            {'filters': [{'name': 'viewpoint', 'operator': '=', 'value': 'viewpoint'}], 'id': 0, 'name': 'park'},
            {'id': 1, 'name': 'drinking fountain'},
            {'filters': [{'name': 'name', 'operator': '', 'value': 'b'}], 'id': 2, 'name': 'hotel bar'}],
                      'relations': [{'name': 'dist', 'source': 0, 'target': 1, 'value': '200 m'},
                                    {'name': 'dist', 'source': 1, 'target': 2, 'value': '100 m'}]}

        expected_output = {
            "area": {
                "type": "area",
                "value": "perugia"
            },
            "nodes": [
                {
                    "id": 0,
                    "type": "nwr",
                    "filters": [
                        {
                            "and": [
                                {
                                    "or": [
                                        {
                                            "key": "landuse",
                                            "operator": "=",
                                            "value": "recreation_ground"
                                        },
                                        {
                                            "key": "landuse",
                                            "operator": "=",
                                            "value": "village_green"
                                        },
                                        {
                                            "key": "leisure",
                                            "operator": "=",
                                            "value": "park"
                                        },
                                        {
                                            "key": "leisure",
                                            "operator": "=",
                                            "value": "garden"
                                        }
                                    ]
                                }
                            ]
                        }
                    ],
                    "name": "park",
                    "display_name": "parks"
                },
                {
                    "id": 1,
                    "type": "nwr",
                    "filters": [
                        {
                            "and": [
                                {
                                    "key": "amenity",
                                    "operator": "=",
                                    "value": "drinking_water"
                                }
                            ]
                        }
                    ],
                    "name": "drinking fountain",
                    "display_name": "drinking fountains"
                },
                {
                    "id": 2,
                    "type": "nwr",
                    "filters": [
                        {
                            "and": [
                                {
                                    "or": [
                                        {
                                            "key": "tourism",
                                            "operator": "=",
                                            "value": "hotel"
                                        },
                                        {
                                            "key": "building",
                                            "operator": "=",
                                            "value": "hotel"
                                        }
                                    ]
                                },
                                {
                                    "operator": "=",
                                    "value": "b",
                                    "key": "name"
                                }
                            ]
                        }
                    ],
                    "name": "hotel bar",
                    "display_name": "hotel bars"
                }
            ],
            "edges": [
                {
                    "source": 0,
                    "target": 1,
                    "distance": "200 m",
                    "type": "dist"
                },
                {
                    "source": 1,
                    "target": 2,
                    "distance": "100 m",
                    "type": "dist"
                }
            ]
        }

        assert adopt_generation(test_input) == expected_output

    if __name__ == '__main__':
        unittest.main()
