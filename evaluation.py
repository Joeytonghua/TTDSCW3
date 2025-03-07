import math
import re
from collections import defaultdict


def preprocess_text(text):
    """预处理文本:小写转换,简单分词"""
    if not text:
        return []
    # 转换为小写
    text = text.lower()
    # 简单分词
    tokens = text.split()
    return tokens


def calculate_term_frequency(term, tokens):
    """计算词频"""
    if not tokens:
        return 0
    term_count = sum(1 for token in tokens if token.lower() == term.lower())
    return term_count / len(tokens)


def tfidf(results, query):
    """
    使用TF-IDF对结果进行排序
    参数:
    - results: 搜索结果列表
    - query: 搜索关键词(假设已经去除停用词)
    返回:
    - 排序后的搜索结果列表
    """
    if not results:
        return []

    print(f"TF-IDF排序: 输入结果数量 {len(results)}")

    # 直接使用查询词，假设search_functions已经去除了停用词
    query_terms = query.lower().split()
    if not query_terms:
        return results  # 如果查询为空,直接返回原结果

    # 预处理文档内容
    doc_tokens = {}
    for result in results:
        # 合并标题和内容以提高匹配质量
        title = result.get("title", "")
        content = result.get("content", "")
        combined_text = f"{title} {content}"
        doc_tokens[result["id"]] = preprocess_text(combined_text)

    # 计算文档评分
    doc_scores = defaultdict(float)

    for term in query_terms:
        # 计算含有该词的文档数
        term_docs = sum(1 for doc_id, tokens in doc_tokens.items()
                        if any(token.lower() == term.lower() for token in tokens))
        if term_docs == 0:
            continue  # 如果没有文档包含该词,跳过

        # 计算IDF (平滑处理避免除零错误)
        idf = math.log((len(results) + 1) / (term_docs + 1)) + 1

        # 为每个文档计算TF-IDF分数
        for result in results:
            doc_id = result["id"]
            tokens = doc_tokens[doc_id]

            # 计算词频 (TF)
            tf = calculate_term_frequency(term, tokens)

            # 累加TF-IDF评分
            doc_scores[doc_id] += tf * idf

    # 如果没有任何文档获得分数,返回原始结果
    if not doc_scores:
        return results

    # 按评分排序
    sorted_results = sorted(results, key=lambda x: doc_scores.get(x["id"], 0), reverse=True)

    print(f"TF-IDF排序: 输出结果数量 {len(sorted_results)}")
    if sorted_results:
        top_score = doc_scores.get(sorted_results[0]["id"], 0)
        print(f"最高分数: {top_score:.4f}, 最低分数: {doc_scores.get(sorted_results[-1]['id'], 0):.4f}")

    return sorted_results


def bm25(results, query, k1=1.5, b=0.75):
    """
    使用BM25对结果进行排序
    参数:
    - results: 搜索结果列表
    - query: 搜索关键词(假设已经去除停用词)
    - k1: BM25参数,控制词频缩放(默认1.5)
    - b: BM25参数,控制文档长度归一化(默认0.75)
    返回:
    - 排序后的搜索结果列表
    """
    if not results:
        return []

    print(f"BM25排序: 输入结果数量 {len(results)}")

    # 直接使用查询词，假设search_functions已经去除了停用词
    query_terms = query.lower().split()
    if not query_terms:
        return results  # 如果查询为空,直接返回原结果

    # 预处理文档内容
    doc_tokens = {}
    for result in results:
        # 合并标题和内容以提高匹配质量
        title = result.get("title", "")
        content = result.get("content", "")
        combined_text = f"{title} {content}"
        doc_tokens[result["id"]] = preprocess_text(combined_text)

    # 计算平均文档长度
    doc_lengths = {doc_id: len(tokens) for doc_id, tokens in doc_tokens.items()}
    avg_doc_length = sum(doc_lengths.values()) / len(doc_lengths) if doc_lengths else 1

    # 计算文档评分
    doc_scores = defaultdict(float)

    for term in query_terms:
        # 计算含有该词的文档数
        term_docs = sum(1 for doc_id, tokens in doc_tokens.items()
                        if any(token.lower() == term.lower() for token in tokens))
        if term_docs == 0:
            continue  # 如果没有文档包含该词,跳过

        # 计算IDF (BM25公式)
        idf = math.log((len(results) - term_docs + 0.5) / (term_docs + 0.5) + 1)

        # 为每个文档计算BM25分数
        for result in results:
            doc_id = result["id"]
            tokens = doc_tokens[doc_id]

            # 计算词频(考虑大小写不敏感)
            tf = sum(1 for token in tokens if token.lower() == term.lower())

            # 文档长度归一化
            doc_length = doc_lengths[doc_id]
            normalized_length = doc_length / avg_doc_length

            # BM25评分公式
            score_part = (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * normalized_length))
            doc_scores[doc_id] += idf * score_part

    # 如果没有任何文档获得分数,返回原始结果
    if not doc_scores:
        return results

    # 按评分排序
    sorted_results = sorted(results, key=lambda x: doc_scores.get(x["id"], 0), reverse=True)

    print(f"BM25排序: 输出结果数量 {len(sorted_results)}")
    if sorted_results:
        top_score = doc_scores.get(sorted_results[0]["id"], 0)
        print(f"最高分数: {top_score:.4f}, 最低分数: {doc_scores.get(sorted_results[-1]['id'], 0):.4f}")

    return sorted_results