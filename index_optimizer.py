import json
import os
import time
import zlib

import msgpack


class IndexOptimizer:
    """用于优化倒排索引的工具类，减少内存占用并提高访问速度"""

    @staticmethod
    def compress_index(input_file="inverted_index.json", output_file="optimized_index.msgpack"):
        """
        将原始JSON索引转换为优化的压缩格式

        优化策略：
        1. 使用msgpack替代JSON提高序列化/反序列化速度
        2. 使用差分编码存储位置信息
        3. 使用zlib压缩整体数据
        4. 对文档ID使用整数编码
        """
        print(f"📊 开始优化索引文件: {input_file}")
        start_time = time.time()

        # 加载原始索引
        with open(input_file, "r", encoding="utf-8") as f:
            original_index = json.load(f)

        print(f"📝 原始索引大小: {os.path.getsize(input_file) / (1024 * 1024):.2f} MB")
        print(f"📝 原始索引包含 {len(original_index)} 个词条")

        # 创建文档ID映射表（字符串ID -> 整数ID）
        doc_id_map = {}
        next_doc_id = 0

        # 优化后的索引
        optimized_index = {}

        # 处理每个词条
        for term, postings in original_index.items():
            term_data = {}

            for doc_id, data in postings.items():
                # 为字符串文档ID分配整数ID
                if doc_id not in doc_id_map:
                    doc_id_map[doc_id] = next_doc_id
                    next_doc_id += 1

                int_doc_id = doc_id_map[doc_id]

                # 处理位置信息 - 使用差分编码
                positions = data.get("positions", [])
                if positions:
                    # 差分编码 - 存储相邻位置的差值而不是绝对位置
                    diff_positions = []
                    prev_pos = 0
                    for pos in sorted(positions):
                        diff_positions.append(pos - prev_pos)
                        prev_pos = pos

                    term_data[int_doc_id] = diff_positions
                else:
                    term_data[int_doc_id] = []

            optimized_index[term] = term_data

        # 创建完整优化索引数据
        optimized_data = {
            "doc_id_map": doc_id_map,
            "index": optimized_index
        }

        # 使用msgpack序列化并压缩
        serialized_data = msgpack.packb(optimized_data, use_bin_type=True)
        compressed_data = zlib.compress(serialized_data, level=9)  # 最高压缩级别

        # 保存优化后的索引
        with open(output_file, "wb") as f:
            f.write(compressed_data)

        # 输出优化结果
        end_time = time.time()
        optimized_size = os.path.getsize(output_file) / (1024 * 1024)
        original_size = os.path.getsize(input_file) / (1024 * 1024)

        print(f"✅ 索引优化完成!")
        print(f"📊 优化后大小: {optimized_size:.2f} MB")
        print(f"📊 压缩比: {original_size / optimized_size:.2f}x")
        print(f"⏱️ 处理时间: {end_time - start_time:.2f} 秒")

        return {
            "original_size_mb": original_size,
            "optimized_size_mb": optimized_size,
            "compression_ratio": original_size / optimized_size,
            "processing_time_sec": end_time - start_time
        }

    @staticmethod
    def decompress_index(file_path="optimized_index.msgpack"):
        """从优化格式加载索引并解压"""
        try:
            with open(file_path, "rb") as f:
                compressed_data = f.read()

            # 解压数据
            decompressed_data = zlib.decompress(compressed_data)

            # 反序列化 - 添加strict_map_key=False参数
            optimized_data = msgpack.unpackb(decompressed_data, raw=False, strict_map_key=False)

            return optimized_data
        except Exception as e:
            print(f"❌ 加载优化索引失败: {str(e)}")
            return None


if __name__ == "__main__":
    # 执行索引优化
    IndexOptimizer.compress_index()