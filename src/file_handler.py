"""
文件处理模块
负责读取D{0-1}KP数据文件和导出结果
"""

import os
import re
from typing import List, Tuple
import pandas as pd
from data_structures import Item, ItemSet


class FileHandler:
    """文件处理器类"""

    @staticmethod
    def read_data_file(filename: str) -> Tuple[List[ItemSet], List[float]]:
        """
        读取D{0-1}KP数据文件（处理多数据集格式）

        Args:
            filename: 文件路径

        Returns:
            (all_item_sets, capacities): 所有项集列表和对应的背包容量列表
        """
        all_item_sets = []
        capacities = []

        try:
            with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # 按IDKP标记分割数据集
            datasets = []
            current_dataset = []
            current_id = None

            for line in lines:
                if line.startswith('IDKP'):
                    # 遇到新的IDKP标记，保存前一个数据集
                    if current_dataset:
                        datasets.append((current_id, current_dataset))
                    current_id = line.strip()
                    current_dataset = [line]
                elif current_id is not None:
                    current_dataset.append(line)

            # 保存最后一个数据集
            if current_dataset:
                datasets.append((current_id, current_dataset))

            print(f"找到 {len(datasets)} 个数据集")

            for idx, (dataset_id, dataset_lines) in enumerate(datasets):
                print(f"\n解析数据集 {idx + 1} (ID: {dataset_id})...")

                # 提取背包容量
                capacity = None
                for line in dataset_lines:
                    if 'cubage of knapsack is' in line:
                        match = re.search(r'cubage of knapsack is (\d+)', line)
                        if match:
                            capacity = float(match.group(1))
                            capacities.append(capacity)
                            print(f"  背包容量: {capacity}")
                            break

                if capacity is None:
                    print(f"  警告: 未找到背包容量信息")
                    continue

                # 提取利润数据
                profits = []
                profit_section = False
                for line in dataset_lines:
                    if 'The profit of' in line and ('itmes' in line or 'items' in line):
                        profit_section = True
                        continue
                    elif profit_section and ('The weight of' in line):
                        profit_section = False
                        break
                    elif profit_section:
                        # 解析这一行的数字
                        numbers = FileHandler._parse_line_numbers(line)
                        profits.extend(numbers)

                # 提取重量数据
                weights = []
                weight_section = False
                for line in dataset_lines:
                    if 'The weight of' in line and ('itmes' in line or 'items' in line):
                        weight_section = True
                        continue
                    elif weight_section and (line.startswith('\n') or line.startswith('IDKP')):
                        weight_section = False
                        break
                    elif weight_section:
                        # 解析这一行的数字
                        numbers = FileHandler._parse_line_numbers(line)
                        weights.extend(numbers)

                print(f"  解析到利润数据: {len(profits)} 个")
                print(f"  解析到重量数据: {len(weights)} 个")

                if len(profits) == 0 or len(weights) == 0:
                    print(f"  警告: 未找到利润或重量数据")
                    continue

                # 确保数据数量一致
                min_len = min(len(profits), len(weights))
                if min_len % 3 != 0:
                    print(f"  警告: 数据数量({min_len})不是3的倍数，将截断到3的倍数")
                    min_len = (min_len // 3) * 3

                profits = profits[:min_len]
                weights = weights[:min_len]

                # 创建项集
                set_count = min_len // 3
                dataset_item_sets = []

                for set_id in range(set_count):
                    base_idx = set_id * 3

                    # 创建三个物品
                    items = []
                    for i in range(3):
                        idx = base_idx + i
                        # 使用全局唯一的物品ID
                        item_id = len(all_item_sets) * 3 + i
                        item = Item(
                            item_id=item_id,
                            weight=weights[idx],
                            value=profits[idx],
                            set_id=len(all_item_sets) + set_id
                        )
                        items.append(item)

                    # 创建项集
                    item_set = ItemSet(len(all_item_sets) + set_id, items)
                    dataset_item_sets.append(item_set)

                print(f"  创建了 {set_count} 个项集")
                all_item_sets.extend(dataset_item_sets)

            print(f"\n总共读取 {len(all_item_sets)} 个项集")
            print(f"找到 {len(capacities)} 个背包容量: {capacities}")

            return all_item_sets, capacities

        except FileNotFoundError:
            print(f"错误: 文件 {filename} 不存在")
            return [], []
        except Exception as e:
            print(f"读取文件时发生错误: {e}")
            import traceback
            traceback.print_exc()
            return [], []

    @staticmethod
    def _parse_line_numbers(line: str) -> List[float]:
        """
        解析一行中的数字

        Args:
            line: 文本行

        Returns:
            数字列表
        """
        line = line.strip()
        if not line:
            return []

        # 按逗号分割
        parts = line.split(',')
        numbers = []

        for part in parts:
            part = part.strip()
            if part:
                try:
                    # 移除可能的末尾点号
                    if part.endswith('.'):
                        part = part[:-1]
                    num = float(part)
                    numbers.append(num)
                except ValueError:
                    continue

        return numbers

    @staticmethod
    def export_to_txt(filename: str,
                      optimal_value: float,
                      selected_items: List[Item],
                      solve_time: float,
                      capacity: float,
                      algorithm_name: str = "动态规划",
                      dataset_index: int = None):
        """
        将结果导出到TXT文件
        """
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("D{0-1}背包问题求解结果\n")
            f.write("=" * 60 + "\n\n")

            if dataset_index is not None:
                f.write(f"数据集索引: {dataset_index}\n")
            f.write(f"求解算法: {algorithm_name}\n")
            f.write(f"背包容量: {capacity:.2f}\n")
            f.write(f"最优总价值: {optimal_value:.2f}\n")
            f.write(f"求解时间: {solve_time:.6f} 秒\n\n")

            f.write("选中物品详情:\n")
            f.write("-" * 40 + "\n")
            f.write(f"{'物品ID':<10}{'所属项集':<10}{'重量':<10}{'价值':<10}\n")
            f.write("-" * 40 + "\n")

            total_weight = 0
            for item in selected_items:
                f.write(f"{item.id:<10}{item.set_id:<10}{item.weight:<10.2f}{item.value:<10.2f}\n")
                total_weight += item.weight

            f.write("-" * 40 + "\n")
            f.write(f"总计重量: {total_weight:.2f} / {capacity:.2f}\n")
            f.write("=" * 60 + "\n")

        print(f"结果已保存到: {filename}")

    @staticmethod
    def export_to_excel(filename: str,
                        optimal_value: float,
                        selected_items: List[Item],
                        solve_time: float,
                        capacity: float,
                        item_sets: List[ItemSet] = None,
                        dataset_index: int = None):
        """
        将结果导出到Excel文件
        """
        # 创建Excel写入器
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # 1. 概要信息
            summary_data = {
                '项目': ['数据集索引', '背包容量', '最优总价值', '求解时间(秒)', '选中物品数'],
                '数值': [dataset_index if dataset_index is not None else '全部',
                        capacity, optimal_value, solve_time, len(selected_items)]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='概要', index=False)

            # 2. 选中物品详情
            if selected_items:
                items_data = []
                for item in selected_items:
                    items_data.append({
                        '物品ID': item.id,
                        '所属项集': item.set_id,
                        '重量': item.weight,
                        '价值': item.value,
                        '价值重量比': item.ratio
                    })
                items_df = pd.DataFrame(items_data)
                items_df.to_excel(writer, sheet_name='选中物品', index=False)

            # 3. 所有项集数据（可选）
            if item_sets:
                all_items_data = []
                for item_set in item_sets:
                    for i, item in enumerate(item_set.items):
                        all_items_data.append({
                            '项集ID': item_set.id,
                            '物品索引': i,
                            '物品ID': item.id,
                            '重量': item.weight,
                            '价值': item.value,
                            '价值重量比': item.ratio
                        })
                all_df = pd.DataFrame(all_items_data)
                all_df.to_excel(writer, sheet_name='所有物品', index=False)

        print(f"Excel文件已保存到: {filename}")