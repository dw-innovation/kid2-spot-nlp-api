from app.templates.factory import TEMPLATES


# in area
# case_sentence = 'Find all wind turbines that have a height of 1201 meters or less, all pharmacies, all bars with the name Smith Lane and have more than 1098 levels, and all supermarkets with a building that has less than 2 levels.'
# case_intermediate_query = {'nodes': [{'name': 'bbox', 'type': 'area'},
#                                      {'name': '[generator:source=wind]', 'type': 'object',
#                                       'props': [{'height': '1201'}, {'levels': '1098'}]},
#                                      {'name': '[amentiy=pharmacy]', 'type': 'object', 'props': []},
#                                      {'name': '[amentiy=bar]', 'type': 'object',
#                                       'props': [{'name': 'Smith Lane'}, {'levels': '1098'}]}],
#                            'relations': [{'from': -1, 'to': -1, 'weight': -1}], 'action': 0}
#
# template = TEMPLATES[case_intermediate_query['action']]
# op_query = template.generate_op_query(case_intermediate_query)
#
# print("[out:json][timeout:250];\n(\nnode[shop=kiosk]({{bbox}})->.one;\n);\nout geom;")
#
# print(f'Sentence:\n{case_sentence}')
# print(f'Overpass Query:\n{op_query}')

# case_sentence = 'Find all towers in Dublin made of wood that are taller than 1639 feet. Additionally, locate all apartments in Dublin constructed with concrete, and all schools in Dublin built with cement blocks that have at least 1273 levels.'
#
# case_intermediate_query = {'nodes': [{'name': 'Dublin', 'type': 'area'}, {'name': '[man_made=tower]', 'type': 'object', 'props': [{'material': 'wood'}, {'height': '1639'}]}, {'name': '[building=apartments]', 'type': 'object', 'props': [{'material': 'concrete'}]}, {'name': '[amentiy=school]', 'type': 'object', 'props': [{'levels': '1273'}]}], 'relations': [{'from': -1, 'to': -1, 'weight': -1}], 'action': 0}
#
# template = TEMPLATES[case_intermediate_query['action']]
# op_query = template.generate_op_query(case_intermediate_query)
#
# print(f'Sentence:\n{case_sentence}')
# print(f'Overpass Query:\n{op_query}')

# TODO check the following query
# case_sentence = 'Find all buildings that have 1349 levels, as well as all restaurants, zoos, and kiosks in their vicinity.'
#
# case_intermediate_query = {'nodes': [{'name': 'bbox', 'type': 'area'}, {'name': '[man_made=tower]', 'type': 'object', 'props': [{'levels': '1349'}]}, {'name': '[amenity=restaurant]', 'type': 'object', 'props': []}, {'name': '[tourism=zoo]', 'type': 'object', 'props': []}], 'relations': [{'from': -1, 'to': -1, 'weight': -1}], 'action': 0}
#
#
# template = TEMPLATES[case_intermediate_query['action']]
# op_query = template.generate_op_query(case_intermediate_query)
#
# print(f'Sentence:\n{case_sentence}')
# print(f'Overpass Query:\n{op_query}')


# # individual distances
# # TODO challenging task
# case_sentence = 'Find me a school that is located less than 331 meters away from 16 wind turbines, which are situated within a radius of 1258 meters from a pharmacy, which in turn is located less than 370 meters away from a tower that has a height of less than 1171 and the number of levels in it is not more than 714.'
#
# case_intermediate_query = {'nodes': [{'name': 'bbox', 'type': 'area'}, {'name': '[amentiy=school]', 'type': 'object', 'props': []}, {'name': '[generator:source=wind]', 'type': 'object', 'props': [{'%count%': '16'}]}, {'name': '[amentiy=pharmacy]', 'type': 'object', 'props': []}], 'relations': [{'from': 0, 'to': 1, 'weight': 331}, {'from': 1, 'to': 2, 'weight': 1258}, {'from': 2, 'to': 3, 'weight': 370}], 'action': 1}
#
# template = TEMPLATES[case_intermediate_query['action']]
# op_query = template.generate_op_query(case_intermediate_query)
#
# print(f'Sentence:\n{case_sentence}')
# print(f'Overpass Query:\n{op_query}')


# # TODO challenging task
# case_sentence = 'Find a pharmacy that is located within a 219m radius of 13 buildings made of cement blocks, which are themselves located within 1907m of 8 schools. These schools are within 1376m of an apartment.'
#
# case_intermediate_query = {'nodes': [{'name': 'bbox', 'type': 'area'}, {'name': '[amentiy=pharmacy]', 'type': 'object', 'props': []}, {'name': '[amentiy=school]', 'type': 'object', 'props': [{'%count%': '13'}, {'material': 'cement_block'}]}, {'name': '[amentiy=school]', 'type': 'object', 'props': [{'%count%': '8'}]}], 'relations': [{'from': 0, 'to': 1, 'weight': 219}, {'from': 1, 'to': 2, 'weight': 1907}, {'from': 2, 'to': 3, 'weight': 1376}], 'action': 1}

# # TODO challenging task
# case_sentence = 'Find a tower made of plaster material that is located within a distance of 1561m from a school with an unlimited number of levels and a height less than 635m, and also located within a distance of 1413m from a wind generator with a maximum height of 152m.'
#
#
# case_intermediate_query ={'nodes': [{'name': 'bbox', 'type': 'area'}, {'name': '[man_made=tower]', 'type': 'object', 'props': [{'material': 'plaster'}]}, {'name': '[amentiy=school]', 'type': 'object', 'props': [{'levels': '635'}]}, {'name': '[generator:source=wind]', 'type': 'object', 'props': [{'height': '152'}]}], 'relations': [{'from': 0, 'to': 1, 'weight': 1561}, {'from': 1, 'to': 2, 'weight': 1413}], 'action': 1}
#
# # within radius
# case_sentence = 'Find one wind turbine, thirteen buildings located on levels higher than 1243 with a name ending with "ise Road" tags, and one school with a name containing the letters "ount Pleasant", which are all within a distance of 1048 meters.'
#
# case_intermediate_query = {'nodes': [{'name': 'bbox', 'type': 'area'}, {'name': '[generator:source=wind]', 'type': 'object', 'props': []}, {'name': '[man_made=tower]', 'type': 'object', 'props': [{'%count%': '13'}, {'levels': '1243'}]}, {'name': '[amentiy=school]', 'type': 'object', 'props': [{'name': 'ount Pleasant'}]}], 'relations': [{'from': -1, 'to': -1, 'weight': 1048}], 'action': 2}
#
#
# case_sentence = 'Find me a wind turbine, a supermarket that has a name starting with "Ru", and an apartment that is no more than 1644 meters away from each other.'
#
# case_intermediate_query = {'nodes': [{'name': 'bbox', 'type': 'area'}, {'name': '[generator:source=wind]', 'type': 'object', 'props': []}, {'name': '[shop=supermarket]', 'type': 'object', 'props': [{'name': 'Ru'}]}], 'relations': [{'from': -1, 'to': -1, 'weight': 1644}], 'action': 2}
#
#
case_sentence = 'Find me a wind turbine that is at least 83 meters tall and a restaurant that is located within a 1313 meter radius of the turbine.'

case_intermediate_query = {'nodes': [{'name': 'bbox', 'type': 'area'}, {'name': '[generator:source=wind]', 'type': 'object', 'props': [{'height': '83'}]}, {'name': '[amenity=restaurant]', 'type': 'object', 'props': []}], 'relations': [{'from': -1, 'to': -1, 'weight': 1313}], 'action': 2}
template = TEMPLATES[case_intermediate_query['action']]
op_query = template.generate_op_query(case_intermediate_query)

print(f'Sentence:\n{case_sentence}')
print(f'Overpass Query:\n{op_query}')
