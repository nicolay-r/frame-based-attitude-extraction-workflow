import importlib


if __name__ == "__main__":

    deepavlov = importlib.import_module("deeppavlov")
    build_model = deepavlov.build_model
    configs = deepavlov.configs

    ner_model = build_model(configs.ner.ner_ontonotes_bert_mult, download=True)

    ner_model(['Чемпионат мира по кёрлингу пройдёт в Антананариву'])
