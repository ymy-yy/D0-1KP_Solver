"""
测试修正后的文件读取功能
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.file_handler import FileHandler

def test_read_file():
    """测试读取数据文件"""

    # 获取data目录下的所有txt文件
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    if not os.path.exists(data_dir):
        print(f"目录 {data_dir} 不存在")
        print("请创建data目录并放入数据文件")
        return

    files = [f for f in os.listdir(data_dir) if f.endswith('.txt')]

    if not files:
        print("data目录下没有找到txt文件")
        print("请将数据文件放入data目录")
        return

    print("找到以下数据文件:")
    for i, f in enumerate(files):
        print(f"  {i+1}. {f}")

    # 测试每个文件
    for file in files:
        filepath = os.path.join(data_dir, file)
        print(f"\n{'='*60}")
        print(f"测试文件: {file}")
        print('='*60)

        item_sets, capacities = FileHandler.read_data_file(filepath)

        if item_sets and capacities:
            print(f"\n✅ 成功读取 {len(item_sets)} 个项集")
            print(f"✅ 找到 {len(capacities)} 个背包容量: {capacities}")

            # 验证每个数据集的项集数量
            items_per_dataset = len(item_sets) // len(capacities)
            print(f"每个数据集约有 {items_per_dataset} 个项集")

            # 显示第一个数据集的第一个项集信息
            if item_sets:
                print("\n第一个项集信息:")
                first_set = item_sets[0]
                print(f"  项集ID: {first_set.id}")
                for j, item in enumerate(first_set.items):
                    print(f"    物品{j+1}: 重量={item.weight}, 价值={item.value}, 比={item.ratio:.2f}")
        else:
            print(f"❌ 文件 {file} 读取失败")

        input("\n按Enter键继续...")

if __name__ == "__main__":
    test_read_file()