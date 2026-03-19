"""
动态规划算法模块
实现求解D{0-1}KP问题的动态规划算法
"""

import time
from typing import List, Tuple
from data_structures import ItemSet, Item


class DynamicProgrammingSolver:
    """D{0-1}KP动态规划求解器"""

    def __init__(self, item_sets: List[ItemSet], capacity: float):
        """
        初始化求解器

        Args:
            item_sets: 项集列表
            capacity: 背包容量
        """
        self.item_sets = item_sets
        self.capacity = capacity
        self.n = len(item_sets)

        # 对于整数数据，不需要缩放
        self.capacity_int = int(capacity)

    def solve(self) -> Tuple[float, List[Item], float]:
        """
        使用动态规划求解D{0-1}KP问题

        Returns:
            (optimal_value, selected_items, solve_time)
        """
        start_time = time.time()

        if self.n == 0 or self.capacity_int <= 0:
            return 0.0, [], 0.0

        # 预处理物品重量（整数）
        weights = []
        values = []
        for item_set in self.item_sets:
            set_weights = []
            set_values = []
            for item in item_set.items:
                set_weights.append(int(item.weight))
                set_values.append(item.value)
            weights.append(set_weights)
            values.append(set_values)

        # 动态规划表：dp[i][j] 表示考虑前i个项集，容量为j时的最大价值
        dp = [[0] * (self.capacity_int + 1) for _ in range(self.n + 1)]

        # 记录选择的路径
        choice = [[-1] * (self.capacity_int + 1) for _ in range(self.n + 1)]

        # 动态规划主过程
        for i in range(1, self.n + 1):
            set_idx = i - 1
            for j in range(self.capacity_int + 1):
                # 初始化为不选当前项集
                dp[i][j] = dp[i-1][j]
                choice[i][j] = -1

                # 尝试选择三个物品中的每一个
                for k in range(3):
                    w = weights[set_idx][k]
                    v = values[set_idx][k]

                    if j >= w:
                        candidate = dp[i-1][j-w] + v
                        if candidate > dp[i][j]:
                            dp[i][j] = candidate
                            choice[i][j] = k

        # 回溯找到选中的物品
        selected_items = []
        remaining_capacity = self.capacity_int

        for i in range(self.n, 0, -1):
            set_idx = i - 1
            k = choice[i][remaining_capacity]

            if k >= 0:
                item = self.item_sets[set_idx].items[k]
                selected_items.append(item)
                remaining_capacity -= int(item.weight)

        # 反转列表，使其按项集顺序排列
        selected_items.reverse()

        optimal_value = dp[self.n][self.capacity_int]
        solve_time = time.time() - start_time

        return optimal_value, selected_items, solve_time

    def solve_with_sorting(self, sorted_item_sets: List[ItemSet] = None) -> Tuple[float, List[Item], float]:
        """
        对排序后的项集进行求解

        Args:
            sorted_item_sets: 已排序的项集列表，如果为None则使用原始顺序

        Returns:
            (optimal_value, selected_items, solve_time)
        """
        if sorted_item_sets is not None:
            original_item_sets = self.item_sets
            self.item_sets = sorted_item_sets
            result = self.solve()
            self.item_sets = original_item_sets
            return result
        else:
            return self.solve()


class OptimizedDPSolver(DynamicProgrammingSolver):
    """优化的动态规划求解器（使用一维数组优化空间）"""

    def solve(self) -> Tuple[float, List[Item], float]:
        """
        使用一维数组优化的动态规划

        Returns:
            (optimal_value, selected_items, solve_time)
        """
        start_time = time.time()

        if self.n == 0 or self.capacity_int <= 0:
            return 0.0, [], 0.0

        # 预处理
        weights = []
        values = []
        for item_set in self.item_sets:
            set_weights = []
            set_values = []
            for item in item_set.items:
                set_weights.append(int(item.weight))
                set_values.append(item.value)
            weights.append(set_weights)
            values.append(set_values)

        # 一维DP数组
        dp = [0] * (self.capacity_int + 1)

        # 记录路径：对于每个状态，记录选择的物品
        choice = [{} for _ in range(self.capacity_int + 1)]

        for i in range(1, self.n + 1):
            set_idx = i - 1
            # 逆序遍历容量，确保每个物品只选一次
            for j in range(self.capacity_int, -1, -1):
                best_value = dp[j]
                best_k = -1
                best_prev_j = j

                for k in range(3):
                    w = weights[set_idx][k]
                    if j >= w:
                        candidate = dp[j - w] + values[set_idx][k]
                        if candidate > best_value:
                            best_value = candidate
                            best_k = k
                            best_prev_j = j - w

                if best_k != -1:
                    dp[j] = best_value
                    choice[j][i] = (best_k, best_prev_j)

        # 回溯
        selected_items = []
        current_capacity = self.capacity_int
        current_choice = choice[current_capacity]

        # 由于是逆序，需要先收集再反转
        temp_items = []
        for i in range(self.n, 0, -1):
            if i in current_choice:
                k, prev_j = current_choice[i]
                item = self.item_sets[i-1].items[k]
                temp_items.append(item)
                current_capacity = prev_j
                current_choice = choice[current_capacity]

        selected_items = list(reversed(temp_items))

        optimal_value = dp[self.capacity_int]
        solve_time = time.time() - start_time

        return optimal_value, selected_items, solve_time