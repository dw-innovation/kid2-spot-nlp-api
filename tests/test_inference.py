from app.tf_inference import generate
from app.yaml_parser import validate_and_fix_yaml
from app.adopt_generation import adopt_generation

if __name__ == '__main__':
    input_sentences = [
        "Find all italian restaurants that are no more than 200 meters from a fountain in London.",
        "Find supermarkets whose height is larger than 10 and with a red roof",
        "find me restaurants in berlin",
        "find me wind turbine in bonn"
    ]

    for idx, input_sentence in enumerate(input_sentences):
        print(f"===Sample {idx}")
        print(input_sentence)

        raw_output = generate(input_sentence)
        print("===raw_output===")
        print(raw_output)
        parsed_result = validate_and_fix_yaml(raw_output)

        assert parsed_result
        print("====parsed result====")
        print(parsed_result)

        result = adopt_generation(parsed_result)
        print("===adopted result====")
        print(result)
        assert result
