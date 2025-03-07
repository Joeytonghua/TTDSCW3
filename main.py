#!/usr/bin/env python3
"""
新闻搜索引擎入口点
使用说明:
    - 运行 python main.py --help 查看所有选项
    - 运行 python main.py run 启动搜索服务
    - 运行 python main.py optimize 优化索引
    - 运行 python main.py normalize 规范化索引大小写
    - 运行 python main.py reset 重置Redis索引缓存
"""
import download_data  # 确保数据库和索引文件已下载

import argparse
import os
import sys
import subprocess
import time

from index_optimizer import IndexOptimizer
from redis_index_manager import RedisIndexManager
from search_utils_fix import normalize_index_case


def run_server():
    """启动搜索服务器"""
    print("🚀 启动搜索服务器...")

    # 使用子进程启动Flask应用
    try:
        subprocess.run([sys.executable, "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 搜索服务已停止")
    except subprocess.CalledProcessError as e:
        print(f"❌ 启动服务器时出错: {str(e)}")
        sys.exit(1)


def optimize_index():
    """优化索引"""
    print("🔧 开始优化索引...")

    try:
        # 运行索引优化
        results = IndexOptimizer.compress_index()

        # 打印结果统计
        print("\n📊 优化结果摘要:")
        print(f"原始索引大小: {results['original_size_mb']:.2f} MB")
        print(f"优化后大小: {results['optimized_size_mb']:.2f} MB")
        print(f"压缩比: {results['compression_ratio']:.2f}x")
        print(f"处理耗时: {results['processing_time_sec']:.2f} 秒")

        print("\n✅ 索引优化完成！")
    except Exception as e:
        print(f"❌ 索引优化失败: {str(e)}")
        sys.exit(1)


def normalize_index():
    """规范化索引大小写"""
    print("🔤 开始规范化索引大小写...")

    try:
        # 规范化原始索引
        results = normalize_index_case()

        print("\n📊 规范化结果摘要:")
        print(f"原始词条数: {results['original_terms']}")
        print(f"规范化后词条数: {results['normalized_terms']}")
        print(f"减少了 {results['reduction']} 个重复词条 (大小写变体)")

        # 提示用户进行下一步操作
        print("\n✅ 索引规范化完成！")
        print("⚠️ 请注意，要使修改生效，您需要重新优化索引并重置Redis缓存:")
        print("1. python main.py optimize")
        print("2. python main.py reset")

    except Exception as e:
        print(f"❌ 索引规范化失败: {str(e)}")
        sys.exit(1)


def reset_redis():
    """重置Redis索引缓存"""
    print("🗑️ 重置Redis索引缓存...")

    try:
        # 创建Redis管理器实例
        manager = RedisIndexManager()

        # 检查Redis中是否有索引
        if manager.is_index_in_redis():
            # 删除现有索引
            manager.redis_client.delete(manager.index_key)
            print("✅ 索引已从Redis中删除")
        else:
            print("⚠️ Redis中没有索引，无需重置")

        # 重新加载索引
        print("📥 重新加载索引到Redis...")
        manager.load_index_to_redis()
        print("✅ 索引已重新加载到Redis")

    except Exception as e:
        print(f"❌ 重置Redis索引失败: {str(e)}")
        sys.exit(1)


def setup_argparse():
    """设置命令行参数解析"""
    parser = argparse.ArgumentParser(description="新闻搜索引擎管理工具")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # 运行服务器
    run_parser = subparsers.add_parser("run", help="启动搜索服务器")

    # 优化索引
    optimize_parser = subparsers.add_parser("optimize", help="优化索引")

    # 规范化索引
    normalize_parser = subparsers.add_parser("normalize", help="规范化索引大小写")

    # 重置Redis
    reset_parser = subparsers.add_parser("reset", help="重置Redis索引缓存")

    return parser


def main():
    """主入口点"""
    parser = setup_argparse()
    args = parser.parse_args()

    if args.command == "run":
        run_server()
    elif args.command == "optimize":
        optimize_index()
    elif args.command == "normalize":
        normalize_index()
    elif args.command == "reset":
        reset_redis()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()