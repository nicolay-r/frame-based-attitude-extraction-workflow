import io

from core.common.bound import Bound
from core.runtime.parser import ParsedText
from core.runtime.ref_opinon import RefOpinion
from core.source.frames.complete import FramesCollection
from core.source.frames.variants import FrameVariantInText
from texts.frames import TextFrameVariantsCollection
from texts.objects.authorized.object import AuthTextObject
from texts.objects.collection import TextObjectsCollection
from texts.readers.utils import NewsInfo
from texts.utils import optional_invert_label

AttitudeKey = 'Attitude'
ObjectKey = 'Object'
FrameVariantKey = 'FrameVariant'
AttitudeDescriptionTemplate = "{template}: '{source_value}'->'{target_value}' b:({sentiment}) oi:[{s_ind}, {t_ind}] si:{{{ss_ind},{st_ind}}}\n"


def print_objects(f, objects_collection):
    assert(isinstance(f, io.TextIOWrapper))
    assert(isinstance(objects_collection, TextObjectsCollection))

    for obj_ind, obj in enumerate(objects_collection):
        assert(isinstance(obj, AuthTextObject))
        bound = obj.get_bound()
        assert(isinstance(bound, Bound))
        position = "{},{}".format(bound.TermIndex, bound.Length)

        s = "{template}: '{value}' b:({pos}) oi:[{obj_ind}] si:{{{tag}}} d:{descr} t:[{obj_type}] {is_auth}\n".format(
            template=ObjectKey,
            value=obj.get_value(),
            pos=position,
            obj_ind=obj_ind,
            tag=str(obj.Tag),
            obj_type=obj.Type,
            descr=obj.Description,
            is_auth='<AUTH>' if obj.IsAuthorized else '')

        f.writelines(s)


def print_opinions(f, opinion_refs, objects_collection):
    assert(isinstance(f, io.TextIOWrapper))
    assert(isinstance(opinion_refs, list))
    assert(isinstance(objects_collection, TextObjectsCollection))

    for opinion_ref in opinion_refs:
        assert(isinstance(opinion_ref, RefOpinion))

        l_obj = objects_collection.get_object(opinion_ref.LeftIndex)
        r_obj = objects_collection.get_object(opinion_ref.RightIndex)

        s = AttitudeDescriptionTemplate.format(
            template=AttitudeKey,
            source_value=l_obj.get_value(),
            target_value=r_obj.get_value(),
            sentiment=str(opinion_ref.Sentiment.to_int()),
            s_ind=opinion_ref.LeftIndex,
            t_ind=opinion_ref.RightIndex,
            ss_ind=str(l_obj.Tag),
            st_ind=str(r_obj.Tag))

        f.writelines(s)


def print_frame_variants(f, text_frames, frames):
    assert(isinstance(f, io.TextIOWrapper))
    assert(isinstance(text_frames, TextFrameVariantsCollection))
    assert(isinstance(frames, FramesCollection))

    for text_frame_variant in text_frames:
        assert(isinstance(text_frame_variant, FrameVariantInText))
        bound = text_frame_variant.get_bound()
        frame_id = text_frame_variant.Variant.FrameID
        p = frames.try_get_frame_polarity(frame_id, role_src="a0", role_dest="a1")

        p_info = ""
        if p is not None:
            p_info = "{}->{}[{}]".format(
                p.Source,
                p.Destination,
                optional_invert_label(p.Label, text_frame_variant.IsInverted).to_str())

        s = "{template}: {value} ({bound}) b:[{p_info}] id:({frame_id}) {is_inv}\n".format(
            template=FrameVariantKey,
            value=text_frame_variant.Variant.get_value(),
            bound="{}, {}".format(bound.TermIndex, bound.Length),
            p_info=p_info,
            frame_id=frame_id,
            is_inv="<INV>" if text_frame_variant.IsInverted else "")

        f.writelines(s)


class TitleDescriptor:

    def __init__(self, news_info, parsed_title, text_index, title_frames, objects_collection, opinion_refs, frames):
        assert(isinstance(news_info, NewsInfo))
        assert(isinstance(title_frames, TextFrameVariantsCollection))
        assert(isinstance(parsed_title, ParsedText))
        assert(isinstance(opinion_refs, list))
        assert(isinstance(objects_collection, TextObjectsCollection))
        assert(isinstance(frames, FramesCollection))
        self.opinion_refs = opinion_refs
        self.parsed_title = parsed_title
        self.news_info = news_info
        self.text_index = text_index
        self.title_frames = title_frames
        self.objects_collection = objects_collection
        self.frames = frames


class ContextDescriptor:

    def __init__(self, sentence_index, parsed_text, opinion_refs, objects_collection, text_frames, frames):
        assert(isinstance(sentence_index, int))
        assert(isinstance(objects_collection, TextObjectsCollection))
        assert(isinstance(parsed_text, ParsedText))
        assert(isinstance(opinion_refs, list))
        assert(isinstance(text_frames, TextFrameVariantsCollection))
        assert(isinstance(frames, FramesCollection))
        self.opinion_refs = opinion_refs
        self.parsed_text = parsed_text
        self.sentence_index = sentence_index
        self.objects_collection = objects_collection
        self.text_frames = text_frames
        self.frames = frames
