import json
import os
from tqdm import tqdm


def normalize_index_case(input_file="inverted_index.json", output_file="normalized_index.json"):
    """
    规范化倒排索引的大小写，将所有词条转换为小写并合并重复条目

    参数:
    - input_file: 输入索引文件
    - output_file: 输出规范化后的索引文件
    """
    print(f"📖 开始规范化索引文件大小写: {input_file}")

    # 加载原始索引
    with open(input_file, "r", encoding="utf-8") as f:
        original_index = json.load(f)

    # 创建新的规范化索引
    normalized_index = {}

    # 处理每个词条
    for term, postings in tqdm(original_index.items(), desc="规范化索引"):
        # 转换为小写
        lowercase_term = term.lower()

        # 如果小写词条已存在，合并倒排记录
        if lowercase_term in normalized_index:
            for doc_id, data in postings.items():
                # 如果文档已存在，合并位置信息
                if doc_id in normalized_index[lowercase_term]:
                    normalized_index[lowercase_term][doc_id]["positions"] = sorted(
                        list(set(normalized_index[lowercase_term][doc_id]["positions"] + data.get("positions", [])))
                    )
                else:
                    # 如果文档不存在，添加新文档
                    normalized_index[lowercase_term][doc_id] = data
        else:
            # 如果小写词条不存在，直接添加
            normalized_index[lowercase_term] = postings

    # 保存规范化后的索引
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(normalized_index, f, ensure_ascii=False, indent=2)

    # 输出结果统计
    original_terms = len(original_index)
    normalized_terms = len(normalized_index)
    print(f"✅ 索引规范化完成!")
    print(f"📊 原始索引词条数: {original_terms}")
    print(f"📊 规范化后词条数: {normalized_terms}")
    print(f"📊 减少了 {original_terms - normalized_terms} 个重复词条 (大小写变体)")
    print(f"📊 新索引已保存到: {output_file}")

    return {
        "original_terms": original_terms,
        "normalized_terms": normalized_terms,
        "reduction": original_terms - normalized_terms
    }


if __name__ == "__main__":
    # 执行索引规范化
    normalize_index_case()