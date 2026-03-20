"""
动态规划算法模块
实现求解D{0-1}KP问题的动态规划算法
优化版本：内存优化、性能提升、代码清晰
"""

import time
from typing import List, Tuple
from data_structures import ItemSet, Item


class DynamicProgrammingSolver:
    """D{0-1}KP动态规划求解器（标准版）"""

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
        # 容量取整，支持浮点数容量
        self.capacity_int = int(capacity)

    def _preprocess_data(self) -> Tuple[List[List[int]], List[List[float]]]:
        """
        预处理数据，提取重量和价值矩阵

        Returns:
            (weights, values): 重量矩阵和价值矩阵，每个项集包含3个物品
        """
        weights = []
        values = []

        for item_set in self.item_sets:
            set_weights = []
            set_values = []
            for item in item_set.items:
                # 重量取整用于DP数组索引
                set_weights.append(int(item.weight))
                set_values.append(item.value)
            weights.append(set_weights)
            values.append(set_values)

        return weights, values

    def solve(self) -> Tuple[float, List[Item], float]:
        """
        使用标准动态规划求解D{0-1}KP问题
        时间复杂度: O(n * capacity * 3)
        空间复杂度: O(n * capacity)

        Returns:
            (optimal_value, selected_items, solve_time)
        """
        start_time = time.time()

        # 边界条件处理
        if self.n == 0 or self.capacity_int <= 0:
            return 0.0, [], 0.0

        # 预处理数据
        weights, values = self._preprocess_data()

        # 初始化DP表 - 使用列表推导式，比循环更快
        # dp[i][j] 表示考虑前i个项集，容量为j时的最大价值
        dp = [[0] * (self.capacity_int + 1) for _ in range(self.n + 1)]

        # 记录选择路径 - 只记录非零状态，节省内存
        # 使用字典存储选择信息，避免存储大量-1
        choice = {}  # key: (i, j), value: k (0,1,2) 或 -1

        # 动态规划主过程
        for i in range(1, self.n + 1):
            set_idx = i - 1
            w1, w2, w3 = weights[set_idx]
            v1, v2, v3 = values[set_idx]

            # 优化：预先获取上一行数据引用，减少索引开销
            prev_dp = dp[i-1]
            curr_dp = dp[i]

            for j in range(self.capacity_int + 1):
                # 初始化为不选当前项集
                best_value = prev_dp[j]
                best_k = -1

                # 检查物品1
                if j >= w1:
                    candidate = prev_dp[j - w1] + v1
                    if candidate > best_value:
                        best_value = candidate
                        best_k = 0

                # 检查物品2
                if j >= w2:
                    candidate = prev_dp[j - w2] + v2
                    if candidate > best_value:
                        best_value = candidate
                        best_k = 1

                # 检查物品3（折扣物品）
                if j >= w3:
                    candidate = prev_dp[j - w3] + v3
                    if candidate > best_value:
                        best_value = candidate
                        best_k = 2

                curr_dp[j] = best_value
                if best_k >= 0:
                    choice[(i, j)] = best_k

        # 回溯找到选中的物品
        selected_items = []
        remaining_capacity = self.capacity_int

        for i in range(self.n, 0, -1):
            k = choice.get((i, remaining_capacity), -1)

            if k >= 0:
                item = self.item_sets[i-1].items[k]
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
    """
    优化的动态规划求解器（使用一维数组优化空间）
    时间复杂度: O(n * capacity * 3)
    空间复杂度: O(capacity)
    相比标准版节省约 O(n * capacity) 的内存
    """

    def __init__(self, item_sets: List[ItemSet], capacity: float):
        """
        初始化优化求解器

        Args:
            item_sets: 项集列表
            capacity: 背包容量
        """
        super().__init__(item_sets, capacity)
        # 添加进度显示标志
        self.show_progress = False

    def solve(self, show_progress: bool = False) -> Tuple[float, List[Item], float]:
        """
        使用一维数组优化的动态规划
        通过逆序遍历容量，避免状态覆盖

        Args:
            show_progress: 是否显示求解进度

        Returns:
            (optimal_value, selected_items, solve_time)
        """
        start_time = time.time()

        # 边界条件处理
        if self.n == 0 or self.capacity_int <= 0:
            return 0.0, [], 0.0

        # 预处理数据
        weights, values = self._preprocess_data()

        # 一维DP数组 - 只保存当前容量状态
        dp = [0] * (self.capacity_int + 1)

        # 记录路径：使用列表存储每个状态的选择和来源
        # 采用更紧凑的存储方式
        choice = [(-1, -1)] * (self.capacity_int + 1)  # (selected_item_index, previous_capacity)

        # 记录每个项集的选择，用于回溯
        # 使用字典存储：capacity -> (item_k, prev_capacity)
        item_choices = {}

        # 进度显示相关
        progress_step = max(1, self.n // 20)  # 每5%显示一次进度

        # 动态规划主过程
        for i in range(1, self.n + 1):
            # 显示进度
            if show_progress and i % progress_step == 0:
                percent = (i * 100) // self.n
                print(f"  求解进度: {percent}% ({i}/{self.n})", end='\r')

            set_idx = i - 1
            w1, w2, w3 = weights[set_idx]
            v1, v2, v3 = values[set_idx]

            # 逆序遍历容量，确保每个物品只选一次
            # 从大到小遍历，避免重复选择同一项集中的多个物品
            for j in range(self.capacity_int, -1, -1):
                best_value = dp[j]
                best_k = -1
                best_prev_j = j

                # 优化：先检查更可能最优的物品（价值重量比高的）
                # 这里按物品3、物品2、物品1的顺序检查，因为物品3通常更有价值

                # 检查物品3（折扣物品，通常性价比更高）
                if j >= w3:
                    candidate = dp[j - w3] + v3
                    if candidate > best_value:
                        best_value = candidate
                        best_k = 2
                        best_prev_j = j - w3

                # 检查物品2
                if j >= w2:
                    candidate = dp[j - w2] + v2
                    if candidate > best_value:
                        best_value = candidate
                        best_k = 1
                        best_prev_j = j - w2

                # 检查物品1
                if j >= w1:
                    candidate = dp[j - w1] + v1
                    if candidate > best_value:
                        best_value = candidate
                        best_k = 0
                        best_prev_j = j - w1

                if best_k != -1:
                    dp[j] = best_value
                    # 存储选择信息
                    item_choices[(i, j)] = (best_k, best_prev_j)

        # 清除进度行
        if show_progress:
            print(" " * 50, end='\r')
            print("  求解完成!          ")

        # 回溯找到选中的物品
        selected_items = []
        remaining_capacity = self.capacity_int

        for i in range(self.n, 0, -1):
            k, prev_j = item_choices.get((i, remaining_capacity), (-1, -1))

            if k >= 0:
                item = self.item_sets[i-1].items[k]
                selected_items.append(item)
                remaining_capacity = prev_j

        # 反转列表，使其按项集顺序排列
        selected_items.reverse()

        optimal_value = dp[self.capacity_int]
        solve_time = time.time() - start_time

        return optimal_value, selected_items, solve_time

    def solve_with_sorting(self, sorted_item_sets: List[ItemSet] = None,
                          show_progress: bool = False) -> Tuple[float, List[Item], float]:
        """
        对排序后的项集进行求解

        Args:
            sorted_item_sets: 已排序的项集列表，如果为None则使用原始顺序
            show_progress: 是否显示求解进度

        Returns:
            (optimal_value, selected_items, solve_time)
        """
        if sorted_item_sets is not None:
            original_item_sets = self.item_sets
            self.item_sets = sorted_item_sets
            result = self.solve(show_progress)
            self.item_sets = original_item_sets
            return result
        else:
            return self.solve(show_progress)


# 添加一个便捷的函数接口，方便直接调用
def solve_knapsack(item_sets: List[ItemSet], capacity: float,
                   use_optimized: bool = True, show_progress: bool = False) -> Tuple[float, List[Item], float]:
    """
    求解D{0-1}KP问题的便捷函数

    Args:
        item_sets: 项集列表
        capacity: 背包容量
        use_optimized: 是否使用优化版本（一维数组）
        show_progress: 是否显示求解进度

    Returns:
        (optimal_value, selected_items, solve_time)
    """
    if use_optimized:
        solver = OptimizedDPSolver(item_sets, capacity)
        return solver.solve(show_progress)
    else:
        solver = DynamicProgrammingSolver(item_sets, capacity)
        return solver.solve()