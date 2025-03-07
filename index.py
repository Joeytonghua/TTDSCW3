# import sqlite3
# import re
# import nltk
# import json
# from nltk.corpus import stopwords
# from nltk.stem import PorterStemmer
# from collections import defaultdict
# from config import DB_PATH
# from tqdm import tqdm  # 导入 tqdm 库

# # 确保停用词库已下载
# # nltk.download("stopwords")

# class Indexer:
#     def __init__(self):
#         self.inverted_index = defaultdict(dict)  # 倒排索引结构
#         self.doc_lengths = {}  # 记录每个文档的长度
#         self.stop_words = set(stopwords.words("english"))  # 停用词表
#         self.stemmer = PorterStemmer()  # 词干提取器

#     def preprocess_text(self, text):
#         """清理文本：小写转换、去除标点、去停用词、词干化"""
#         text = text.lower()
#         text = re.sub(r"[^\w\s]", "", text)
#         words = text.split()
#         processed_tokens = [self.stemmer.stem(word) for word in words if word not in self.stop_words]
#         return processed_tokens

#     def fetch_news_data(self):
#         """从 SQLite 数据库提取新闻数据"""
#         conn = sqlite3.connect(DB_PATH)
#         cursor = conn.cursor()
#         cursor.execute("SELECT id, title, content FROM news")
#         documents = cursor.fetchall()
#         conn.close()
#         return documents

#     def build_inverted_index(self):
#         """构建倒排索引"""
#         documents = self.fetch_news_data()
#         total_docs = len(documents)
#         total_length = 0

#         for doc_id, title, content in tqdm(documents, desc="构建倒排索引"):
#             combined_text = f"{title} {content}"  # 合并 title + content
#             tokens = self.preprocess_text(combined_text)
#             self.doc_lengths[doc_id] = len(tokens)
#             total_length += len(tokens)

#             for pos, token in enumerate(tokens):
#                 if doc_id not in self.inverted_index[token]:
#                     self.inverted_index[token][doc_id] = []
#                 self.inverted_index[token][doc_id].append(pos)

#         self.avg_doc_length = total_length / total_docs if total_docs else 1
#         return total_docs

#     def save_index(self):
#         """存储索引到 JSON 文件"""
#         with open("inverted_index.json", "w", encoding="utf-8") as f:
#             json.dump(self.inverted_index, f, indent=4)
#         print("✅ 倒排索引已保存至 inverted_index.json")

#     def build_and_store_index(self):
#         """构建索引并存储"""
#         print("📌 开始构建倒排索引...")
#         self.build_inverted_index()
#         self.save_index()
#         print("🎉 索引构建完成！")


# if __name__ == "__main__":
#     indexer = Indexer()
#     indexer.build_and_store_index()


import sqlite3
import re
import nltk
import math
import json
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from collections import defaultdict
from config import DB_PATH


# 确保停用词库已下载
# nltk.download("stopwords")

class Indexer:
    def __init__(self):
        self.inverted_index = defaultdict(dict)  # 倒排索引结构
        self.doc_lengths = {}  # 记录每个文档的长度
        self.stop_words = set(stopwords.words("english"))  # 停用词表
        self.stemmer = PorterStemmer()  # 词干提取器

    def preprocess_text(self, text):
        """清理文本：小写转换、去除标点、去停用词、词干化"""
        text = text.lower()
        text = re.sub(r"[^\w\s]", "", text)
        words = text.split()
        processed_tokens = [self.stemmer.stem(word) for word in words if word not in self.stop_words]
        return processed_tokens

    def fetch_news_data(self):
        """从 SQLite 数据库提取新闻数据"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, content FROM news")
        documents = cursor.fetchall()
        conn.close()
        return documents

    def build_inverted_index(self):
        """构建倒排索引"""
        documents = self.fetch_news_data()
        total_docs = len(documents)
        total_length = 0

        for doc_id, title, content in documents:
            combined_text = f"{title} {content}"  # 合并 title + content
            tokens = self.preprocess_text(combined_text)
            self.doc_lengths[doc_id] = len(tokens)
            total_length += len(tokens)

            for pos, token in enumerate(tokens):
                if doc_id not in self.inverted_index[token]:
                    self.inverted_index[token][doc_id] = []
                self.inverted_index[token][doc_id].append(pos)

        self.avg_doc_length = total_length / total_docs if total_docs else 1
        return total_docs

    def compute_tf_idf_and_bm25(self, total_docs, k1=1.5, b=0.75):
        """计算 TF-IDF 和 BM25 评分"""
        index_data = {}
        for term, doc_dict in self.inverted_index.items():
            # df = len(doc_dict)
            # idf = math.log((total_docs + 1) / (df + 1)) + 1  # 计算 IDF

            for doc_id, positions in doc_dict.items():
                # tf = len(positions)
                # tf_idf_score = tf * idf

                # # 计算 BM25 评分
                # doc_length = self.doc_lengths.get(doc_id, 0)
                # bm25_score = idf * ((tf * (k1 + 1)) / (tf + k1 * (1 - b + b * (doc_length / self.avg_doc_length))))

                if term not in index_data:
                    index_data[term] = {}
                index_data[term][doc_id] = {
                    # "tf-idf": tf_idf_score,
                    # "bm25": bm25_score,
                    "positions": positions
                }
        return index_data

    def save_index(self, index_data):
        """存储索引到 JSON 文件"""
        with open("inverted_index.json", "w", encoding="utf-8") as f:
            json.dump(index_data, f, indent=4)
        print("✅ 倒排索引已保存至 inverted_index.json")

    def build_and_store_index(self):
        """构建索引并存储"""
        print("📌 开始构建倒排索引...")
        total_docs = self.build_inverted_index()
        print("📌 计算 TF-IDF 和 BM25 评分...")
        index_data = self.compute_tf_idf_and_bm25(total_docs)
        self.save_index(index_data)
        print("🎉 索引构建完成！")


if __name__ == "__main__":
    indexer = Indexer()
    indexer.build_and_store_index()
