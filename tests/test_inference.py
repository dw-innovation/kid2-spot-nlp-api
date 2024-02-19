from app.tf_inference import generate
from app.yaml_parser import validate_and_fix_yaml
from app.adopt_generation import adopt_generation

if __name__ == '__main__':
    input_sentence = "Find all wind turbines that have a height of 1201 meters or less, all pharmacies, all bars with the name Smith Lane and have more than 1098 levels, and all supermarkets with a building that has less than 1208 levels."
    raw_output = generate(input_sentence)

    print("===raw_output===")
    print(raw_output)

    parsed_result = validate_and_fix_yaml(raw_output)

    print("====parsed result====")
    print(parsed_result)

    result = adopt_generation(parsed_result)

    print("===adopted result====")
    print(result)
