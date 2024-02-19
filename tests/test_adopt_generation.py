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
            }
        ]

    def test_assign_combination(self):
        for sample in self.test_data:
            predicted_output = adopt_generation(sample['input'])
            assert predicted_output == sample['expected_output']

    if __name__ == '__main__':
        unittest.main()
