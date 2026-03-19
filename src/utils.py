"""
工具函数模块
提供排序、格式化等辅助功能
"""

from typing import List
from data_structures import ItemSet


def sort_item_sets_by_ratio(item_sets: List[ItemSet], reverse: bool = True) -> List[ItemSet]:
    """
    按项集第三项的价值重量比对项集进行排序

    Args:
        item_sets: 原始项集列表
        reverse: True表示非递增排序（从大到小），False表示递增

    Returns:
        排序后的项集列表
    """
    return sorted(item_sets,
                  key=lambda x: x.get_third_item_ratio(),
                  reverse=reverse)


def format_time(seconds: float) -> str:
    """格式化时间显示"""
    if seconds < 1e-6:
        return f"{seconds * 1e9:.2f} ns"
    elif seconds < 1e-3:
        return f"{seconds * 1e6:.2f} µs"
    elif seconds < 1:
        return f"{seconds * 1e3:.2f} ms"
    else:
        return f"{seconds:.4f} s"


def print_item_sets_info(item_sets: List[ItemSet]):
    """打印项集信息"""
    print("\n" + "=" * 60)
    print("项集信息")
    print("=" * 60)
    print(f"{'项集ID':<10}{'物品1(v/w)':<15}{'物品2(v/w)':<15}{'物品3(v/w)':<15}{'第三项比率':<10}")
    print("-" * 60)

    for item_set in item_sets:
        items = item_set.items
        ratio3 = item_set.get_third_item_ratio()
        print(f"{item_set.id:<10}"
              f"{items[0].value}/{items[0].weight}={items[0].ratio:.2f}  "
              f"{items[1].value}/{items[1].weight}={items[1].ratio:.2f}  "
              f"{items[2].value}/{items[2].weight}={items[2].ratio:.2f}  "
              f"{ratio3:<10.2f}")

    print("=" * 60)