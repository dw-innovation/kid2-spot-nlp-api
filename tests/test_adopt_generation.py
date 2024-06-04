import unittest

from app.adopt_generation import adopt_generation

'''
Execute python -m unittest tests.test_adopt_generation
'''

class TestAdoptFunction(unittest.TestCase):

    def test_assign_combination(self):
        test_parsed_result = {'area': {'type': 'bbox', 'value': ''}, 'entities': [
            {'id': 0, 'is_area': True, 'name': 'supermarkets',
             'properties': [{'name': 'height', 'operator': '>', 'value': '10'}], 'type': 'nwr'}]}

        expected_result = {
            "area": {
                "type": "area",
                "value": "bbox"
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
                                            "key": "shop",
                                            "operator": "=",
                                            "value": "supermarket"
                                        },
                                        {
                                            "key": "building",
                                            "operator": "=",
                                            "value": "supermarket"
                                        },
                                        {
                                            "key": "shop",
                                            "operator": "=",
                                            "value": "discounter"
                                        },
                                        {
                                            "key": "shop",
                                            "operator": "=",
                                            "value": "wholesale"
                                        }
                                    ]
                                },
                                {
                                    "key": "height",
                                    "operator": ">",
                                    "value": "10"
                                }
                            ]
                        }
                    ],
                    "name": "supermarkets",
                    "display_name": "supermarkets"
                }
            ]
        }

        self.assertEqual(adopt_generation(test_parsed_result), expected_result)

    if __name__ == '__main__':
        unittest.main()
