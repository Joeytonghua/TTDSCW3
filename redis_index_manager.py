import redis
import json
import msgpack
import zlib
import os
import time
from index_optimizer import IndexOptimizer


class RedisIndexManager:
    """管理Redis中的索引数据"""

    def __init__(self, host='localhost', port=6379, db=0,
                 index_key='inverted_index',
                 optimized_index_file="optimized_index.msgpack",
                 original_index_file="inverted_index.json"):
        """
        初始化Redis索引管理器

        参数:
        - host: Redis服务器主机
        - port: Redis服务器端口
        - db: Redis数据库编号
        - index_key: Redis中存储索引的键名
        - optimized_index_file: 优化索引文件路径
        - original_index_file: 原始索引文件路径
        """
        self.redis_client = redis.Redis(host=host, port=port, db=db, decode_responses=False)
        self.index_key = index_key
        self.optimized_index_file = optimized_index_file
        self.original_index_file = original_index_file

        # 内存中的缓存
        self._index_cache = None
        self._doc_id_map = None
        self._reverse_doc_id_map = None

    def is_index_in_redis(self):
        """检查Redis中是否已有索引"""
        return self.redis_client.exists(self.index_key)

    def load_index_to_redis(self):
        """将优化索引加载到Redis中"""
        # 首先检查优化索引是否存在
        if not os.path.exists(self.optimized_index_file):
            # 优化索引不存在，创建一个
            print(f"📌 优化索引文件不存在，开始创建: {self.optimized_index_file}")
            IndexOptimizer.compress_index(self.original_index_file, self.optimized_index_file)

        # 加载优化索引
        try:
            with open(self.optimized_index_file, "rb") as f:
                compressed_data = f.read()

            # 存储到Redis
            print(f"📤 正在将优化索引上传到Redis (大小: {len(compressed_data) / (1024 * 1024):.2f} MB)...")
            self.redis_client.set(self.index_key, compressed_data)
            print("✅ 索引已成功加载到Redis")
            return True
        except Exception as e:
            print(f"❌ 索引加载到Redis失败: {str(e)}")
            return False

    def get_index(self):
        """
        获取索引，优先从内存缓存中获取，其次从Redis获取
        返回元组: (索引字典, 文档ID映射)
        """
        # 如果内存中已有缓存，直接返回
        if self._index_cache is not None and self._doc_id_map is not None:
            return self._index_cache, self._doc_id_map

        # 尝试从Redis获取
        try:
            compressed_data = self.redis_client.get(self.index_key)
            if not compressed_data:
                # Redis中不存在索引，尝试加载
                if not self.load_index_to_redis():
                    raise Exception("无法加载索引到Redis")
                compressed_data = self.redis_client.get(self.index_key)

            # 解压缩和反序列化 - 添加strict_map_key=False参数
            decompressed_data = zlib.decompress(compressed_data)
            optimized_data = msgpack.unpackb(decompressed_data, raw=False, strict_map_key=False)

            # 缓存到内存
            self._doc_id_map = optimized_data["doc_id_map"]
            self._index_cache = optimized_data["index"]

            # 创建反向映射 (整数ID -> 原始ID)
            self._reverse_doc_id_map = {v: k for k, v in self._doc_id_map.items()}

            return self._index_cache, self._doc_id_map

        except Exception as e:
            print(f"❌ 从Redis加载索引失败: {str(e)}")
            # 如果Redis加载失败，直接从优化文件加载
            try:
                optimized_data = IndexOptimizer.decompress_index(self.optimized_index_file)
                if optimized_data:
                    self._doc_id_map = optimized_data["doc_id_map"]
                    self._index_cache = optimized_data["index"]
                    self._reverse_doc_id_map = {v: k for k, v in self._doc_id_map.items()}
                    return self._index_cache, self._doc_id_map
            except Exception as e2:
                print(f"❌ 从优化文件加载索引失败: {str(e2)}")

            # 如果优化文件也加载失败，尝试从原始JSON加载
            print(f"⚠️ 尝试从原始JSON加载索引 ({self.original_index_file})...")
            try:
                with open(self.original_index_file, "r", encoding="utf-8") as f:
                    original_index = json.load(f)

                # 使用原始索引，但没有ID优化
                self._index_cache = original_index
                self._doc_id_map = {}
                return self._index_cache, self._doc_id_map
            except Exception as e3:
                print(f"❌ 所有索引加载方法均失败: {str(e3)}")
                return {}, {}

    def get_original_doc_id(self, int_doc_id):
        """将整数文档ID转换回原始文档ID"""
        if self._reverse_doc_id_map is None:
            # 确保映射已加载
            self.get_index()

        return self._reverse_doc_id_map.get(int_doc_id, str(int_doc_id))

    def get_term_postings(self, term):
        """获取某个词的倒排记录，并转换回原始格式"""
        index, _ = self.get_index()

        # 确保查询词转换为小写以匹配索引
        term = term.lower()

        if term not in index:
            # 尝试查找大小写变体
            for indexed_term in index.keys():
                if indexed_term.lower() == term:
                    term = indexed_term
                    break
            else:
                return {}  # 如果没有找到任何匹配，返回空结果

        # 获取该词的倒排记录
        postings = index[term]

        # 转换为原始格式
        original_postings = {}
        for int_doc_id, diff_positions in postings.items():
            # 获取原始文档ID
            doc_id = self.get_original_doc_id(int_doc_id)

            # 还原差分编码的位置
            positions = []
            if diff_positions:
                current_pos = 0
                for diff in diff_positions:
                    current_pos += diff
                    positions.append(current_pos)

            # 使用原始格式存储
            original_postings[doc_id] = {
                "positions": positions
            }

        return original_postings

    def get_document_ids_for_term(self, term):
        """获取包含某个词的所有文档ID"""
        postings = self.get_term_postings(term)
        return list(postings.keys())


# 创建全局实例，用于应用中访问
index_manager = RedisIndexManager()

if __name__ == "__main__":
    # 测试索引加载和查询
    manager = RedisIndexManager()
    if not manager.is_index_in_redis():
        manager.load_index_to_redis()

    # 加载索引
    index, doc_id_map = manager.get_index()
    print(f"索引包含 {len(index)} 个词条")
    print(f"文档ID映射包含 {len(doc_id_map)} 个文档")

    # 测试查询某个词
    test_term = next(iter(index.keys()))
    print(f"测试查询词: {test_term}")
    postings = manager.get_term_postings(test_term)
    print(f"包含该词的文档数: {len(postings)}")