from typing import Dict
import json
import inflect
import pprint

num2word_engine = inflect.engine()


class Template:
    def template(self, area, nodes):
        pass

    def generate_op_query(self, intermediate_query: Dict):
        pass


class SearchWithinTemplate(Template):
    def template(self, area, nodes, edges):
        prefix = '[out:json][timeout:250];\n'
        if 'bbox' not in area:
            area = f"geocodeArea:\"{area}\""
            prefix += f'{{{{{area}}}}}->.searchArea;\n'

        txt = prefix + "(\n"

        first_op = 'node' if len(edges) == 1 else 'nwr'

        for idx, edge in enumerate(edges):

            loc_from = edge['from']
            loc_to = edge['to']

            props_text = ''.join([f'[{prop}]' for prop in nodes[int(loc_to)]['props']])

            if loc_from == '0':
                if 'bbox' not in area:
                    txt += f'{first_op}{props_text}(area.searchArea)->.{num2word_engine.number_to_words(loc_to)};\n'
                else:
                    txt += f'{first_op}{props_text}({area})->.{num2word_engine.number_to_words(loc_to)};\n'
            else:
                dist = edge['weight']
                txt += f'nwr(around.{num2word_engine.number_to_words(loc_from)}:{dist}){props_text}->.{num2word_engine.number_to_words(loc_to)};\n'

        txt += ");\nout geom;"
        return txt.strip()

    def generate_op_query(self, intermediate_query: Dict):
        nodes = intermediate_query['nodes']
        objects = []
        for node in nodes:
            if node['type'] == 'area':
                area = node['name']

                if area == 'bbox':
                    area = f'{{{{{area}}}}}'
            else:
                objects.append(node)

        edges = intermediate_query['relations']
        txt = self.template(area, nodes, edges)

        return txt


class ConditionalSearchWithin(SearchWithinTemplate):
    def template(self, area, nodes, edges):
        prefix = '[out:json][timeout:250];\n'
        if 'bbox' not in area:
            area = f"geocodeArea:\"{area}\""
            prefix += f'{{{{{area}}}}}->.searchArea;\n'

        txt = prefix

        first_op = 'node' if len(edges) == 1 else 'nwr'

        for idx, edge in enumerate(edges):

            loc_from = edge['from']
            loc_to = edge['to']

            filtered_nodes = filter(lambda prop: 'count' not in prop, nodes[int(loc_to)]['props'])
            props_text = ''.join([f'[{prop}]' for prop in filtered_nodes])

            if loc_from == '0':
                if 'bbox' not in area:
                    txt += f'{first_op}{props_text}(area.searchArea)->.{num2word_engine.number_to_words(loc_to)};\n'
                else:
                    txt += f'{first_op}{props_text}({area})->.{num2word_engine.number_to_words(loc_to)};\n'
            else:
                dist = edge['weight']
                txt += f'nwr(around.{num2word_engine.number_to_words(loc_from)}:{dist}){props_text}->.{num2word_engine.number_to_words(loc_to)};\n'

            nodes_with_count = list(filter(lambda prop: 'count' in prop, nodes[int(loc_to)]['props']))

            for node in nodes_with_count:
                count = node.split(':')

                txt += f"foreach .one(\n  node.one(around:{edge['weight']});\n  node._(if:count(nodes)>={count[-1]});\n"

        txt += "out geom;"
        return txt.strip()


class ComparisionSearchWithin(SearchWithinTemplate):
    def __init__(self):
        super(SearchWithinTemplate, self).__init__()

        self.comparision_tags = {
            "smaller": "<=",
            "larger": ">="
        }

    def template(self, area, nodes, edges):
        prefix = '[out:json][timeout:250];\n'
        if 'bbox' not in area:
            area = f"geocodeArea:\"{area}\""
            prefix += f'{{{{{area}}}}}->.searchArea;\n'

        txt = prefix + "(\n"

        first_op = 'nwr'

        for idx, edge in enumerate(edges):

            loc_from = edge['from']
            loc_to = edge['to']

            props_text = ''
            for idx, node in enumerate(nodes[int(loc_to)]['props']):
                for tag in self.comparision_tags:
                    if tag in node:
                        comp_operator = self.comparision_tags[tag]
                        node = node.replace(tag, comp_operator)
                        splits = node.split(comp_operator)
                        prop = splits[0].strip()
                        number = splits[1].strip()
                        changed_prop = f'(if:number(t[\"{prop}\"]){comp_operator}{number})'
                    else:
                        changed_prop = f'[{node}]'
                props_text += changed_prop

            if loc_from == '0':
                if 'bbox' not in area:
                    txt += f'{first_op}{props_text}(area.searchArea)->.{num2word_engine.number_to_words(loc_to)};\n'
                else:
                    txt += f'{first_op}{props_text}({area})->.{num2word_engine.number_to_words(loc_to)};\n'
            else:
                dist = edge['weight']
                txt += f'nwr(around.{num2word_engine.number_to_words(loc_from)}:{dist}){props_text}->.{num2word_engine.number_to_words(loc_to)};'

        txt += ")\n->._;\nout geom;"
        return txt.strip()


TEMPLATES = {
    'search_within': SearchWithinTemplate(),
    'conditional_search_within': ConditionalSearchWithin(),
    'comparision_search_within': ComparisionSearchWithin()
}
