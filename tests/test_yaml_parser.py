from app.yaml_parser import validate_and_fix_yaml

generated_yaml = 'area:\n   name: cologne\n   type: area\n entities:\n - id: 0\n   name: bar\n'
validated_data = validate_and_fix_yaml(generated_yaml)

assert validated_data

generated_yaml = '''area:
   name: ''
   type: bbox
 entities:
 - id: 0
   name: kiosk
 - id: 1
   name: park
 relations:
 - name: dist
   source: 0
   target: 1
   value: 100 m

'''
validated_data = validate_and_fix_yaml(generated_yaml)
assert validated_data

generated_yaml = '''area:
   name: Kopenhagen
   type: area
entities:
 - filters:
   - name: name
     operator: ''
     value: *rden
   - name: street name
     operator: '='
     value: Strget
   id: 0
   name: shop
'''
validated_data = validate_and_fix_yaml(generated_yaml)
assert validated_data
