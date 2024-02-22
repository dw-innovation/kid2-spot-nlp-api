from app.adopt_generation import adopt_generation

if __name__ == '__main__':
    input_imr = {'area': {'name': 'bonn', 'type': 'area'}, 'entities': [{'id': 0, 'name': 'mall'}]}

    expected_imr = {'area': {'type': 'area', 'value': 'bonn'}, 'nodes': [{'id': 0, 'type': 'nwr', 'filters': [
        {"and": [{'key': 'shop', 'operator': '=', 'value': 'mall'}]}], 'name': 'mall', 'display_name': 'malls'}]}

    assert adopt_generation(input_imr) == expected_imr
