import yaml
from jsonschema import validate

SCHEMA = {
    'type': 'object',
    'properties': {
        'area': {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'type': {'type': 'string'},
            },
            'required': ['name', 'type']
        }
    },
    'required': ['area']
}


def validate_and_fix_yaml(yaml_text):
    try:
        result = yaml.safe_load(yaml_text)
    except yaml.parser.ParserError as e:
        line_num = e.problem_mark.line
        column_num = e.problem_mark.column
        lines = yaml_text.split('\n')

        misformatted_line = lines[line_num]
        if "entities" in lines[line_num]:
            corrected_line = misformatted_line.strip()
            yaml_text = yaml_text.replace(misformatted_line, corrected_line)
            result = validate_and_fix_yaml(yaml_text)

    validate(instance=result, schema=SCHEMA)
    return result
