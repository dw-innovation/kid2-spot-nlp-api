from typing import Dict
import json
import inflect
import pprint

num2word_engine = inflect.engine()

# TODO change it in the future
CONDITIONS = {
    'height': '["height"](if: t["height"] > VALUE)',
    'levels': '["building:levels"](if: t["building:levels"] > VALUE)',
    'level': '["building:levels"](if: t["building:levels"] > VALUE)',
    'name': '["name"~"VALUE",i]',
    'material': '["building:material"="VALUE"]'
}

# TODO change it in the future for the database, and remove this
CORRECTIONS = {
    'generator:source': '"generator:source"',
    'amentiy': 'amenity'
}


class Template:
    def template(self, area, nodes):
        pass

    def generate_op_query(self, intermediate_query: Dict):
        pass


class SearchWithinTemplate(Template):
    def template(self, area, nodes, edges):
        prefix = '[out:json][timeout:250];\n'

        # if 'bbox' not in area:
        #     area = f"geocodeArea:\"{area}\""
        #     prefix += f'{{{{{area}}}}}->.searchArea;\n'

        # todo fix it after frontend handling it
        area = '{{bbox}}'

        txt = prefix + "(\n"

        first_op = 'node' if len(edges) == 1 else 'nwr'

        # we create an edge dictionary where the key is the row we need to change in the query. Basically, it is 1.
        edge_dict = {}
        for idx, edge in enumerate(edges):
            edge_dict[edge['to']] = edge

        for idx, node in enumerate(nodes):
            if node['type'] == 'area':
                continue

            props = node['props']
            for incorrect_tag, correct_tag in CORRECTIONS.items():
                node['name'] = node['name'].replace(incorrect_tag, correct_tag)

            if len(props) > 0:
                prop_txt = ''
                for prop in props:
                    prop_txt += CONDITIONS[list(prop.keys())[0]].replace('VALUE', list(prop.values())[0])

                if idx in edge_dict:
                    around_txt = f"{first_op}(around.{num2word_engine.number_to_words(edge['from'])}:{edge['weight']})"
                    txt += f"{around_txt}{node['name']}{prop_txt}({area})->.{num2word_engine.number_to_words(idx)};\n"
                else:
                    txt += f"{first_op}{node['name']}{prop_txt}({area})->.{num2word_engine.number_to_words(idx)};\n"

            else:
                if idx in edge_dict:
                    around_txt = f"{first_op}(around.{num2word_engine.number_to_words(edge['from'])}:{edge['weight']})"
                    txt += f"{around_txt}{node['name']}({area})->.{num2word_engine.number_to_words(idx)};\n"
                else:
                    txt += f"{first_op}{node['name']}({area})->.{num2word_engine.number_to_words(idx)};\n"

        # for idx, edge in enumerate(edges):
        #
        #     print(idx)
        #
        #     loc_from = edge['from']
        #     loc_to = edge['to']
        #
        #     props_text = ''.join([prop for prop in nodes[int(loc_to)]['name']])
        #
        #     if loc_from == '0':
        #         if 'bbox' not in area:
        #             txt += f'{first_op}{props_text}(area.searchArea)->.{num2word_engine.number_to_words(loc_to)};\n'
        #         else:
        #             txt += f'{first_op}{props_text}({area})->.{num2word_engine.number_to_words(loc_to)};\n'
        #     else:
        #         dist = edge['weight']
        #         txt += f'nwr(around.{num2word_engine.number_to_words(loc_from)}:{dist}){props_text}->.{num2word_engine.number_to_words(loc_to)};\n'

        txt += ");\nout geom;"

        print(txt)

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

        # if 'bbox' not in area:
        #     area = f"geocodeArea:\"{area}\""
        #     prefix += f'{{{{{area}}}}}->.searchArea;\n'

        # todo fix it after frontend handling it
        area = '{{bbox}}'

        txt = prefix + "(\n"

        first_op = 'node' if len(edges) == 1 else 'nwr'

        # we create an edge dictionary where the key is the row we need to change in the query. Basically, it is 1.
        edge_dict = {}
        for idx, edge in enumerate(edges):
            edge_dict[edge['to']] = edge

        print(edge_dict)

        for idx, node in enumerate(nodes):
            if node['type'] == 'area':
                continue

            props = node['props']
            for incorrect_tag, correct_tag in CORRECTIONS.items():
                node['name'] = node['name'].replace(incorrect_tag, correct_tag)

            if len(props) > 0:
                prop_txt = ''
                for prop in props:
                    prop_name = list(prop.keys())[0]

                    if '%count%' == prop_name:
                        continue
                    prop_txt += CONDITIONS[list(prop.keys())[0]].replace('VALUE', list(prop.values())[0])

                if idx in edge_dict:
                    around_txt = f"{first_op}(around.{num2word_engine.number_to_words(edge_dict[idx]['from'])}:{edge_dict[idx]['weight']})"
                    txt += f"{around_txt}{node['name']}{prop_txt}({area})->.{num2word_engine.number_to_words(idx)};\n"
                else:
                    txt += f"{first_op}{node['name']}{prop_txt}({area})->.{num2word_engine.number_to_words(idx)};\n"

            else:
                if idx in edge_dict:
                    around_txt = f"{first_op}(around.{num2word_engine.number_to_words(edge_dict[idx]['from'])}:{edge_dict[idx]['weight']})"
                    txt += f"{around_txt}{node['name']}({area})->.{num2word_engine.number_to_words(idx)};\n"
                else:
                    txt += f"{first_op}{node['name']}({area})->.{num2word_engine.number_to_words(idx)};\n"

        # for node in nodes_with_count:
        #     count = node.split(':')
        #
        #     txt += f"foreach .one(\n  node.one(around:{edge['weight']});\n  node._(if:count(nodes)>={count[-1]});\n"

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
    0: SearchWithinTemplate(),
    1: ConditionalSearchWithin(),
    2: ComparisionSearchWithin()
}
