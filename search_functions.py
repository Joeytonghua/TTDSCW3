import re
import time

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from redis_index_manager import index_manager

import fetch_news_db

# 全局常量
db_file = "news.db"
STOPWORDS = set(stopwords.words("english"))
STEMMER = PorterStemmer()  # 使用与索引构建时相同的词干提取器


def preprocess_query(text):
    """
    对查询文本进行与索引构建相同的预处理：
    1. 转换为小写
    2. 分词
    3. 去除停用词
    4. 词干提取
    """
    # 转换为小写
    text = text.lower()
    # 分词
    tokens = word_tokenize(text)
    # 去除停用词并进行词干提取
    processed_tokens = [STEMMER.stem(token) for token in tokens if token not in STOPWORDS]
    return processed_tokens


def proximity_search(query):
    """近邻搜索函数 - 使用Redis优化版本"""
    query = query.strip().lower()
    start_time = time.time()  # 记录开始时间

    # 解析近邻查询，格式如 "#3 apple banana"
    match = re.match(r"#(\d+)\s+(\w+)\s+(\w+)", query)
    if not match:
        return "Invalid proximity search format"

    max_distance = int(match.group(1))

    # 对两个关键词进行词干提取
    term1 = STEMMER.stem(match.group(2))
    term2 = STEMMER.stem(match.group(3))

    print(f"近邻搜索: 词干提取后的词条: '{term1}' 和 '{term2}'")

    # 获取词汇的倒排记录
    postings1 = index_manager.get_term_postings(term1)
    postings2 = index_manager.get_term_postings(term2)

    # 检查两个单词是否存在于索引中
    if not postings1:
        print(f"词条 '{term1}' 不在索引中")
    if not postings2:
        print(f"词条 '{term2}' 不在索引中")

    if not postings1 or not postings2:
        return []  # 直接返回空列表

    # 获取包含两个单词的文档ID集合
    docs_with_term1 = set(postings1.keys())
    docs_with_term2 = set(postings2.keys())

    # 找到两个单词都在的文档
    common_docs = docs_with_term1.intersection(docs_with_term2)

    # 结果存储
    valid_docs = []

    # 遍历共同文档，检查位置间距
    for doc_id in common_docs:
        positions1 = sorted(postings1[doc_id]["positions"])
        positions2 = sorted(postings2[doc_id]["positions"])

        # 双指针方法寻找最近距离
        i, j = 0, 0
        while i < len(positions1) and j < len(positions2):
            pos1, pos2 = positions1[i], positions2[j]
            if abs(pos1 - pos2) <= max_distance:
                valid_docs.append(doc_id)
                break  # 找到一个匹配的就可以跳出循环
            if pos1 < pos2:
                i += 1
            else:
                j += 1

    # 如果没有匹配的文档，直接返回空
    if not valid_docs:
        return []

    # 从数据库中查询完整新闻数据
    results = fetch_news_db.fetch_news_from_db(valid_docs, db_file)

    # 记录总搜索时间
    end_time = time.time()
    print(f"近邻搜索完成，耗时: {end_time - start_time:.4f} 秒，找到 {len(results)} 篇文章")

    return results


def phrase_search(query):
    """短语搜索函数 - 使用Redis优化版本"""
    query = query.strip().lower()
    start_time = time.time()  # 记录开始时间

    # 解析短语查询，格式如："apple banana"
    match = re.match(r'"(.+?)"', query)
    if not match:
        return "Invalid phrase search format"

    # 应用与索引构建相同的处理流程
    phrase_text = match.group(1)
    phrase_terms = preprocess_query(phrase_text)

    print(f"短语搜索: 词干提取后的词条: {phrase_terms}")

    # 确保短语中仍然有有效单词
    if not phrase_terms:
        return []

    # 获取各个词的倒排记录
    all_postings = {}
    for term in phrase_terms:
        postings = index_manager.get_term_postings(term)
        if not postings:  # 如果有任何一个词不在索引中，返回空结果
            print(f"词条 '{term}' 不在索引中")
            return []
        all_postings[term] = postings

    # 获取包含所有单词的文档集合
    doc_sets = [set(postings.keys()) for postings in all_postings.values()]
    common_docs = set.intersection(*doc_sets)  # 获取所有词共同出现的文档

    valid_docs = []  # 存储满足短语搜索的文档ID

    # 遍历共同文档，检查是否为短语
    for doc_id in common_docs:
        positions_list = [sorted(all_postings[term][doc_id]["positions"]) for term in phrase_terms]

        # 采用多指针方法检查是否构成连续短语
        if is_phrase_match(positions_list):
            valid_docs.append(doc_id)

    # 如果没有匹配的文档，直接返回空
    if not valid_docs:
        return []

    # 从数据库中查询完整新闻数据
    results = fetch_news_db.fetch_news_from_db(valid_docs, db_file)

    # 记录总搜索时间
    end_time = time.time()
    print(f"短语搜索完成，耗时: {end_time - start_time:.4f} 秒，找到 {len(results)} 篇文章")

    return results


def is_phrase_match(positions_list):
    """检查多个单词的位置信息是否能构成一个连续短语"""
    if not all(positions_list):  # 如果任何一个单词没有位置信息
        return False

    pointers = [0] * len(positions_list)  # 初始化指针列表

    while all(ptr < len(positions) for ptr, positions in zip(pointers, positions_list)):
        # 获取每个单词当前指针指向的位置
        current_positions = [positions[i] for positions, i in zip(positions_list, pointers)]

        # 检查这些位置是否是连续的
        if all(current_positions[i] + 1 == current_positions[i + 1] for i in range(len(current_positions) - 1)):
            return True  # 找到匹配的短语

        # 找到最小的指针，尝试移动它
        min_val = min(current_positions)
        for i in range(len(pointers)):
            if current_positions[i] == min_val:
                pointers[i] += 1
                break

    return False


def boolean_search_and_not(query):
    """布尔搜索（AND NOT）- 使用Redis优化版本"""
    query = query.strip().lower()
    start_time = time.time()  # 记录开始时间

    # 解析 AND NOT 查询
    match = re.match(r"(.+?)\s+and\s+not\s+(.+)", query, re.IGNORECASE)
    if not match:
        return "Invalid AND NOT query format"

    # 对两部分查询应用词干提取
    term_a_text = match.group(1)
    term_b_text = match.group(2)

    term_a = preprocess_query(term_a_text)
    term_b = preprocess_query(term_b_text)

    print(f"布尔搜索(AND NOT): 词干提取后的词条: A={term_a}, B={term_b}")

    # 确保至少有一个有效单词
    if not term_a:
        return []

    # 获取 A 的文档集合
    doc_set_a = set()
    for term in term_a:
        postings = index_manager.get_term_postings(term)
        if not postings:
            print(f"词条 '{term}' 不在索引中")
            continue
        doc_set_a.update(postings.keys())

    # 获取 B 的文档集合
    doc_set_b = set()
    for term in term_b:
        postings = index_manager.get_term_postings(term)
        if not postings:
            print(f"词条 '{term}' 不在索引中")
            continue
        doc_set_b.update(postings.keys())

    # 计算 A - B
    valid_docs = list(doc_set_a - doc_set_b)

    # 从数据库中查询完整新闻数据
    results = fetch_news_db.fetch_news_from_db(valid_docs, db_file)

    # 记录总搜索时间
    end_time = time.time()
    print(f"布尔搜索(AND NOT)完成，耗时: {end_time - start_time:.4f} 秒，找到 {len(results)} 篇文章")

    return results


def boolean_search_and(query):
    """布尔搜索（AND）- 使用Redis优化版本"""
    query = query.strip().lower()
    start_time = time.time()  # 记录开始时间

    # 解析 AND 查询
    match = re.match(r"(.+?)\s+and\s+(.+)", query, re.IGNORECASE)
    if not match:
        return "Invalid AND query format"

    # 对两部分查询应用词干提取
    term_a_text = match.group(1)
    term_b_text = match.group(2)

    term_a = preprocess_query(term_a_text)
    term_b = preprocess_query(term_b_text)

    print(f"布尔搜索(AND): 词干提取后的词条: A={term_a}, B={term_b}")

    # 确保至少有一个有效单词
    if not term_a or not term_b:
        return []

    # 获取 A 的文档集合
    doc_set_a = set()
    for term in term_a:
        postings = index_manager.get_term_postings(term)
        if not postings:
            print(f"词条 '{term}' 不在索引中")
            continue
        doc_set_a.update(postings.keys())

    # 获取 B 的文档集合
    doc_set_b = set()
    for term in term_b:
        postings = index_manager.get_term_postings(term)
        if not postings:
            print(f"词条 '{term}' 不在索引中")
            continue
        doc_set_b.update(postings.keys())

    # 计算 A ∩ B
    valid_docs = list(doc_set_a & doc_set_b)

    # 从数据库中查询完整新闻数据
    results = fetch_news_db.fetch_news_from_db(valid_docs, db_file)

    # 记录总搜索时间
    end_time = time.time()
    print(f"布尔搜索(AND)完成，耗时: {end_time - start_time:.4f} 秒，找到 {len(results)} 篇文章")

    return results


def boolean_search_or(query):
    """布尔搜索（OR）- 使用Redis优化版本"""
    query = query.strip().lower()
    start_time = time.time()  # 记录开始时间

    # 解析 OR 查询
    match = re.match(r"(.+?)\s+or\s+(.+)", query, re.IGNORECASE)
    if not match:
        return "Invalid OR query format"

    # 对两部分查询应用词干提取
    term_a_text = match.group(1)
    term_b_text = match.group(2)

    term_a = preprocess_query(term_a_text)
    term_b = preprocess_query(term_b_text)

    print(f"布尔搜索(OR): 词干提取后的词条: A={term_a}, B={term_b}")

    # 确保至少有一个有效单词
    if not term_a and not term_b:
        return []

    # 获取 A 的文档集合
    doc_set_a = set()
    for term in term_a:
        postings = index_manager.get_term_postings(term)
        if not postings:
            print(f"词条 '{term}' 不在索引中")
            continue
        doc_set_a.update(postings.keys())

    # 获取 B 的文档集合
    doc_set_b = set()
    for term in term_b:
        postings = index_manager.get_term_postings(term)
        if not postings:
            print(f"词条 '{term}' 不在索引中")
            continue
        doc_set_b.update(postings.keys())

    # 计算 A ∪ B
    valid_docs = list(doc_set_a | doc_set_b)

    # 从数据库中查询完整新闻数据
    results = fetch_news_db.fetch_news_from_db(valid_docs, db_file)

    # 记录总搜索时间
    end_time = time.time()
    print(f"布尔搜索(OR)完成，耗时: {end_time - start_time:.4f} 秒，找到 {len(results)} 篇文章")

    return results


def keyword_search(query):
    """关键词搜索 - 使用Redis优化版本"""
    original_query = query.strip()
    query = original_query.lower()
    start_time = time.time()  # 记录开始时间

    print(f"关键词搜索: 原始查询 '{original_query}'")

    # 使用与索引构建相同的预处理
    keywords = preprocess_query(query)

    print(f"关键词搜索: 词干提取后的词条: {keywords}")

    # 确保至少有一个有效的关键词
    if not keywords:
        print("查询中没有有效关键词(可能全为停用词)")
        return "No valid keywords in the query."

    # 获取包含关键词的文档集合
    doc_sets = set()
    for term in keywords:
        postings = index_manager.get_term_postings(term)
        if not postings:
            print(f"词条 '{term}' 不在索引中")
            continue
        doc_count = len(postings)
        print(f"词条 '{term}' 在 {doc_count} 篇文档中出现")
        doc_sets.update(postings.keys())

    # 如果没有包含关键词的文档，返回空列表
    if not doc_sets:
        print("没有找到包含这些关键词的文档")
        return []

    # 获取有效文档ID
    valid_docs = list(doc_sets)

    # 从数据库中查询完整新闻数据
    results = fetch_news_db.fetch_news_from_db(valid_docs, db_file)

    # 记录总搜索时间
    end_time = time.time()
    print(f"关键词搜索完成，耗时: {end_time - start_time:.4f} 秒，找到 {len(results)} 篇文章")

    return results


# 初始化索引 - 在导入模块时不会立即执行，只有在首次使用时才会加载
def initialize_index():
    """初始化索引，只在首次调用时执行"""
    # 检查Redis中是否有索引
    if not index_manager.is_index_in_redis():
        print("⚠️ Redis中未找到索引，正在加载...")
        index_manager.load_index_to_redis()
    else:
        print("✅ Redis中已有索引，无需重新加载")

    # 预热索引 - 将索引加载到内存
    index, doc_id_map = index_manager.get_index()
    print(f"✅ 索引预热完成，共有 {len(index)} 个词条和 {len(doc_id_map)} 个文档")

    # 测试一些常见词的索引情况
    test_terms = ["appl", "googl", "china", "technolog", "presid"]
    for term in test_terms:
        if term in index:
            doc_count = len(index[term])
            print(f"测试词条 '{term}' 在索引中，包含于 {doc_count} 篇文档")
        else:
            print(f"测试词条 '{term}' 不在索引中")