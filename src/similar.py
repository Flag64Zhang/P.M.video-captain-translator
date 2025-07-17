#src/similar.py
#相似度计算、字幕合并、翻译字典构建等功能
import Levenshtein
import pysrt
from utils.translation_utils import translate

class SubtitleSimilarityHelper:
    @staticmethod
    def is_similar(text1, text2, threshold=0.9):
        import Levenshtein
        ratio = Levenshtein.ratio(text1, text2)
        return ratio >= threshold

    @staticmethod
    def build_translation_dict(subs, translate_func):
        unique_texts = set(text for _, _, text in subs)
        translation_dict = {}
        for text in unique_texts:
            translation_dict[text] = translate_func(text)
        return translation_dict

    @staticmethod
    def save_srt(subs, output_file, translation_dict):
        import pysrt
        subs_list = pysrt.SubRipFile()
        for idx, (start, end, text) in enumerate(subs, 1):
            translated = translation_dict.get(text, "")
            item = pysrt.SubRipItem(
                index=idx,
                start=pysrt.SubRipTime(seconds=start),
                end=pysrt.SubRipTime(seconds=end),
                text=translated
            )
            subs_list.append(item)
            print(f"[{start}-{end}] {text} -> {translated}")
        subs_list.save(output_file, encoding='utf-8')
        print(f"Subtitles saved to: {output_file}")

    @staticmethod
    def merge_duplicate_subtitles_fuzzy(subs, threshold=0.9):
        if not subs:
            return []
        merged = []
        last_start, last_end, last_text = subs[0]
        for start, end, text in subs[1:]:
            if SubtitleSimilarityHelper.is_similar(text, last_text, threshold):
                last_end = end
            else:
                merged.append((last_start, last_end, last_text))
                last_start, last_end, last_text = start, end, text
        merged.append((last_start, last_end, last_text))
        return merged

    @staticmethod
    def get_translation(text, translation_dict, translate_func, threshold=0.9):
        for zh, en in translation_dict.items():
            if SubtitleSimilarityHelper.is_similar(text, zh, threshold):
                return en
        return translate_func(text)  # 没有相似的就新翻译

