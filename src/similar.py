#src/similar.py
#相似度计算、字幕合并、翻译字典构建等功能
import Levenshtein

# 计算归一化相似度
def is_similar(text1, text2, threshold=0.9):
    ratio = Levenshtein.ratio(text1, text2)
    return ratio >= threshold

#统计所有合并后的中文字幕，去重，统一翻译一次
def build_translation_dict(subs):
    unique_texts = set(text for _, _, text in subs)
    translation_dict = {}
    for text in unique_texts:
        translation_dict[text] = translate(text)
    return translation_dict

#生成SRT时查表
def save_srt(subs, output_file, translation_dict):
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

#合并字幕时用相似度
def merge_duplicate_subtitles_fuzzy(subs, threshold=0.9):
    if not subs:
        return []
    merged = []
    last_start, last_end, last_text = subs[0]
    for start, end, text in subs[1:]:
        if is_similar(text, last_text, threshold):
            last_end = end
        else:
            merged.append((last_start, last_end, last_text))
            last_start, last_end, last_text = start, end, text
    merged.append((last_start, last_end, last_text))
    return merged

#翻译查表时用相似度
def get_translation(text, translation_dict, threshold=0.9):
    for zh, en in translation_dict.items():
        if is_similar(text, zh, threshold):
            return en
    return translate(text)  # 没有相似的就新翻译