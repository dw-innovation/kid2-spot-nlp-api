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
                "input": {'area': {'name': '', 'type': 'bbox'}, 'entities': [{'filters': [
                    {'name': 'height', 'operator': '=', 'value': '1201 m'},
                    {'name': 'height', 'operator': None, 'value': '1201 m'},
                    {'name': 'pharmacie', 'operator': '=', 'value': 'pharmacy'},
                    {'name': 'bar', 'operator': '=', 'value': 'bar'},
                    {'name': 'name', 'operator': '=', 'value': 'smith lane'}], 'id': 0, 'name': 'wind turbine'}, {
                    'filters': [{'name': 'building levels',
                                 'operator': None,
                                 'value': '1098'}],
                    'id': 1, 'name': 'supermarket'}]},
                "expected_output": {'area': {'name': '', 'type': 'bbox'}, 'entities': [{'filters': [
                    {'name': 'height', 'operator': '=', 'value': '1201 m'},
                    {'name': 'pharmacie', 'operator': '=', 'value': 'pharmacy'},
                    {'name': 'bar', 'operator': '=', 'value': 'bar'},
                    {'name': 'name', 'operator': '=', 'value': 'smith lane'}], 'id': 0, 'name': 'wind turbine'}, {
                    'filters': [{'name': 'building levels',
                                 'operator': '=',
                                 'value': '1098'}],
                    'id': 1, 'name': 'supermarket'}]},

            }
        ]

    def test_assign_combination(self):
        for sample in self.test_data:
            predicted_output = adopt_generation(sample['input'])

            print("predicted_output")
            print(predicted_output)

            assert predicted_output == sample['expected_output']

    if __name__ == '__main__':
        unittest.main()
