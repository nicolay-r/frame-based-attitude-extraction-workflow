# Frame-Based Attitude Extraction Workflow

A source code for a core of news processing workflow.
It provides scripts for sentiment attitude extraction using frame-based method.

![](logo.png)


## Dependencies

* python == 3.6
* tqdm >= 4.19.5
* sqlite3
* AREkit == [0.19.5](https://github.com/nicolay-r/AREkit/tree/0.19.5-bdr-elsevier-2020-py3)
    * Utilized as a core library for text parsing, frames reading, stemming application, etc.
* ner == 0.0.2 
    * Optional, for `deep-ner` NER model
* deep-pavlov == 1.11.0 
    * Optional, for `bert-mult-ontonotes` NER model
    
## Resources
* [RuWordNet](https://ruwordnet.ru/en/)
* [RuSentiFrames-2.0](https://github.com/nicolay-r/RuSentiFrames)
    
# Quick start

Please refer to the base class [API](texts/readers/base.py)

> TODO#1. Provide example and simple reader.
>
> TODO#2. Provide everything via Makefile.

## Optional: caching resources for processing speed enhancement 

1. NER cache [[readme]](scripts/cache/ner/README.md);
2. Frames cache [[readme]](scripts/cache/frames/README.md);
3. Synonyms collection [[readme]](scripts/synonyms/README.md).

## References
> TODO.
