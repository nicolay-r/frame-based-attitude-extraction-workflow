#!/usr/bin/python
# -*- coding: utf-8 -*-
import argparse

from core.helpers.frames import FramesHelper
from core.runtime.parser import TextParser
from scripts.args.rusentiframes import RuSentiFramesCacheArgs
from texts.extraction.default import Default


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Test obj parsing")

    text_sample = "В Конгрессе "

    # Reading frames filepath from cmd args.
    RuSentiFramesCacheArgs.add_argument(parser)
    args = parser.parse_args()
    frames_filepath = RuSentiFramesCacheArgs.read_argument(args)

    # Init stemmer.
    stemmer = Default.create_default_stemmer()
    s = TextParser.parse(text=text_sample, stemmer=stemmer)

    # Init frames helper.
    frames = Default.create_default_frames_collection(frames_filepath)
    frame_variants = Default.create_default_frame_variants_collection(frames=frames, stemmer=stemmer)
    frames_helper = FramesHelper(frame_variants)

    frame_variants = frames_helper.find_frames(s)

    if frame_variants is None:
        exit(0)

    for fv in frame_variants:
        bound = fv.get_bound()
        print(fv.Variant.get_value(), bound.TermIndex, bound.Length)
