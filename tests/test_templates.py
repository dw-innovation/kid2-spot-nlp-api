import unittest
from app.templates.factory import TEMPLATES


class TestTemplates(unittest.TestCase):
    def examples(self):
        examples = []
        # 'Search kiosk within 10 meters. There is a pharmacy within 20 meters and next to pharmacy, there is a wooden hospital.'

        # nodes of the sentence
        nodes = [{'name': 'bbox', 'type': 'area'}, {'name': 'kiosk', 'type': 'object', 'props': ['shop=kiosk']},
                 {'name': 'pharmacy', 'type': 'object', 'props': ['amenity=pharmacy']},
                 {'name': 'hospital', 'type': 'object', 'props': ['amenity=hospital', 'material=wooden']}]

        # edges for distance
        edges = [{'from': '0', 'to': '1', 'weight': 10}, {
            'from': '1', 'to': '2', 'weight': 20,
        }, {'from': '2', 'to': '3', 'weight': 40}]

        generated_json = {
            'nodes': nodes,
            'relations': edges,
            'action': 'search_within'
        }

        expected_query = "(\nway[shop=kiosk]({{bbox}})->.one;\nway(around.one:20)[amenity=pharmacy]->.two;\nway(around.two:40)[amenity=hospital][material=wooden]->.three;\n);\nout geom;"

        #

        '''
        // search in …
        {{geocodeArea:Deutschland}}->.searchArea;
        // search for …
        way[man_made=cooling_tower](if:number(t["height"])>=80)(area.searchArea)->.one;
        way[man_made=tower]["tower:type"="cooling"](if:number(t["height"])>=80)(area.searchArea)->.two;
        node(around.one:2000)["generator:source"="wind"][!"removed:power"]->.three;
        node(around.two:2000)["generator:source"="wind"][!"removed:power"]->.four;
        '''

        examples.append((generated_json, expected_query))

        return examples

    def test_search_within(self):
        examples = self.examples()

        for (example, expected_query) in examples:
            template = TEMPLATES[example['action']]
            op_query = template.generate_op_query(example)
            assert expected_query == op_query


if __name__ == '__main__':
    unittest.main()
