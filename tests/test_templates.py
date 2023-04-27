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

        expected_query = "[out:json][timeout:250];\n(\nnwr[shop=kiosk]({{bbox}})->.one;\nnwr(around.one:20)[amenity=pharmacy]->.two;\nnwr(around.two:40)[amenity=hospital][material=wooden]->.three;\n);\nout geom;"
        examples.append((generated_json, expected_query))

        # search within box
        # nodes of the sentence
        nodes = [{'name': 'bbox', 'type': 'area'}, {'name': 'kiosk', 'type': 'object', 'props': ['shop=kiosk']}]

        # edges for distance
        edges = [{'from': '0', 'to': '1', 'weight': 10}]

        generated_json = {
            'nodes': nodes,
            'relations': edges,
            'action': 'search_within'
        }

        expected_query = "[out:json][timeout:250];\n(\nnode[shop=kiosk]({{bbox}})->.one;\n);\nout geom;"

        examples.append((generated_json, expected_query))

        # search within LOCATION
        # nodes of the sentence
        nodes = [{'name': 'berlin', 'type': 'area'}, {'name': 'kiosk', 'type': 'object', 'props': ['shop=kiosk']}]

        # edges for distance
        edges = [{'from': '0', 'to': '1', 'weight': 10}]

        generated_json = {
            'nodes': nodes,
            'relations': edges,
            'action': 'search_within'
        }

        expected_query = "[out:json][timeout:250];\n{{geocodeArea:\"berlin\"}}->.searchArea;\n(\nnode[shop=kiosk](area.searchArea)->.one;\n);\nout geom;"

        examples.append((generated_json, expected_query))

        # looking for winds that minimum 8 of them within 1 km and they are still operated in Niedersachsen
        nodes = [{'name': 'niedersachsen', 'type': 'area'}, {'name': 'wind', 'type': 'object',
                                                             'props': ["\"generator:source\"=\"wind\"",
                                                                       "!\"removed:power\"", "count:8"]}]

        # edges for distance
        edges = [{'from': '0', 'to': '1', 'weight': 1000}]

        generated_json = {
            'nodes': nodes,
            'relations': edges,
            'action': 'conditional_search_within'
        }

        expected_query = "[out:json][timeout:250];\n{{geocodeArea:\"niedersachsen\"}}->.searchArea;\n" \
                         "node[\"generator:source\"=\"wind\"][!\"removed:power\"](area.searchArea)->.one;\n" \
                         "foreach .one(\n" \
                         "  node.one(around:1000);\n" \
                         "  node._(if:count(nodes)>=8);\nout geom;"

        examples.append((generated_json, expected_query))

        # find a cooling tower with a height larger than 80 meters
        nodes = [{'name': 'germany', 'type': 'area'},
                 {'name': 'wind', 'type': 'object',
                  'props': ['man_made=cooling_tower', "height larger 80"]}]

        edges = [{'from': '0', 'to': '1', 'weight': 1000}]

        generated_json = {
            'nodes': nodes,
            'relations': edges,
            'action': 'comparision_search_within'
        }

        expected_query = "[out:json][timeout:250];\n{{geocodeArea:\"germany\"}}->.searchArea;\n" \
                         "(\nnwr[man_made=cooling_tower](if:number(t[\"height\"])>=80)" \
                         "(area.searchArea)->.one;\n" \
                         ")\n" \
                         "->._;\n" \
                         "out geom;"

        print(generated_json)


        examples.append((generated_json, expected_query))

        return examples


    def test_search_within(self):
        examples = self.examples()

        for (example, expected_query) in examples:
            template = TEMPLATES[example['action']]
            op_query = template.generate_op_query(example)

            print('Generated Query')
            print(op_query)

            print('Expected Query')
            print(expected_query)

            assert expected_query == op_query


if __name__ == '__main__':
    unittest.main()
