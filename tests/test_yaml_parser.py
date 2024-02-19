from app.yaml_parser import validate_and_fix_yaml

generated_yaml = 'area:\n   name: cologne\n   type: area\n entities:\n - id: 0\n   name: bar\n'
validated_data = validate_and_fix_yaml(generated_yaml)
assert validated_data
