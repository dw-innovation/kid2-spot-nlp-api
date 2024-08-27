# from app.tf_inference import generate
from app.llama_inference import generate
from app.yaml_parser import validate_and_fix_yaml
from app.adopt_generation import adopt_generation

if __name__ == '__main__':
    input_sentences = [
        "Find all italian restaurants that are no more than 200 meters from a fountain in London.",
        "Find supermarkets whose height is larger than 10 and with a red roof",
        "find me restaurants in berlin",
        "find me wind turbine in bonn",
        "find all kiosks within a park",
        "find all bars",
        "Find all book stores of brand thalia",
        "loking for discounter in lombrady. must be 100 metres way from a medical suppy store. there shuld be also hairdresser close to the discounter and the medical supply store.",
        "find mural, 300 yards form burger king restaurant with pakring spotts in laborde, cordoba, argentina",
        "i am looking for an italian restaurant with outdoor seating, the restaurant is within 300 meters from train tracks and a railway bridge."
    ]


    # mt5
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
