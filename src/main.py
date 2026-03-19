"""
D{0-1}背包问题求解程序主入口
提供友好的命令行用户界面
"""

import os
import sys
import time
from typing import List

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_structures import ItemSet, Item
from file_handler import FileHandler
from dynamic_programming import DynamicProgrammingSolver, OptimizedDPSolver
from visualizer import Visualizer
import utils


class D0_1KPSolver:
    """D{0-1}背包问题求解器主类"""

    def __init__(self):
        self.item_sets = []
        self.capacities = []  # 多个背包容量
        self.current_capacity = 0  # 当前使用的容量
        self.current_file = ""
        self.sorted_item_sets = []
        self.last_result = None
        self.last_solve_time = 0
        self.current_dataset_index = 0  # 当前使用的数据集索引

        # 创建必要的目录
        os.makedirs("data", exist_ok=True)
        os.makedirs("results", exist_ok=True)

    def clear_screen(self):
        """清屏"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self):
        """打印程序标题"""
        print("\n" + "=" * 60)
        print("          D{0-1}背包问题求解程序")
        print("=" * 60)

    def print_menu(self):
        """打印主菜单"""
        print("\n主菜单:")
        print("-" * 40)
        print("1. 加载数据文件")
        print("2. 显示当前数据信息")
        print("3. 绘制散点图")
        print("4. 按第三项价值重量比排序")
        print("5. 动态规划求解")
        print("6. 优化动态规划求解（一维数组）")
        print("7. 导出结果")
        print("8. 选择数据集")  # 新增：选择不同的数据集
        print("9. 关于")
        print("0. 退出")
        print("-" * 40)

    def load_data(self):
        """加载数据文件"""
        print("\n[加载数据文件]")
        print("-" * 40)

        # 显示data目录下的文件
        if os.path.exists("data"):
            files = [f for f in os.listdir("data") if f.endswith('.txt')]
            if files:
                print("可用的数据文件:")
                for i, f in enumerate(files):
                    print(f"  {i+1}. {f}")

        filename = input("\n请输入数据文件路径 (例如: data/idkp1-10.txt): ").strip()

        if not os.path.exists(filename):
            print(f"错误: 文件 '{filename}' 不存在")
            return

        self.item_sets, self.capacities = FileHandler.read_data_file(filename)

        if self.item_sets and self.capacities:
            self.current_file = filename
            self.sorted_item_sets = []  # 重置排序结果
            self.current_dataset_index = 0
            self.current_capacity = self.capacities[0] if self.capacities else 0

            print(f"\n成功加载数据!")
            print(f"总项集数量: {len(self.item_sets)}")
            print(f"包含 {len(self.capacities)} 个数据集")
            print(f"当前使用数据集 1，背包容量: {self.current_capacity}")

            # 显示所有数据集的容量
            print("\n所有数据集容量:")
            for i, cap in enumerate(self.capacities):
                print(f"  数据集 {i+1}: 容量 = {cap}")
        else:
            print("加载失败: 没有读取到有效数据")

    def select_dataset(self):
        """选择要使用的数据集"""
        if not self.item_sets or not self.capacities:
            print("\n请先加载数据文件")
            return

        print("\n[选择数据集]")
        print("-" * 40)

        # 显示所有可用的数据集
        print("可用的数据集:")
        for i, cap in enumerate(self.capacities):
            items_per_dataset = len(self.item_sets) // len(self.capacities)
            start_idx = i * items_per_dataset
            end_idx = (i + 1) * items_per_dataset
            print(f"  {i+1}. 数据集 {i+1}: 容量={cap}, 项集范围 {start_idx}-{end_idx-1}")

        try:
            choice = int(input(f"\n请选择数据集 [1-{len(self.capacities)}]: ").strip())
            if 1 <= choice <= len(self.capacities):
                self.current_dataset_index = choice - 1
                self.current_capacity = self.capacities[self.current_dataset_index]
                print(f"已选择数据集 {choice}, 背包容量: {self.current_capacity}")
            else:
                print("无效的选择")
        except ValueError:
            print("请输入有效的数字")

    def show_info(self):
        """显示当前数据信息"""
        if not self.item_sets:
            print("\n请先加载数据文件")
            return

        print("\n[当前数据信息]")
        print("-" * 40)
        print(f"数据文件: {self.current_file}")
        print(f"总项集数量: {len(self.item_sets)}")
        print(f"数据集数量: {len(self.capacities)}")
        print(f"当前使用: 数据集 {self.current_dataset_index + 1}")
        print(f"当前背包容量: {self.current_capacity:.2f}")

        # 计算当前数据集的项集范围
        items_per_dataset = len(self.item_sets) // len(self.capacities)
        start_idx = self.current_dataset_index * items_per_dataset
        end_idx = (self.current_dataset_index + 1) * items_per_dataset

        print(f"当前数据集项集范围: {start_idx} - {end_idx-1}")

        # 显示前几个项集的信息
        print("\n当前数据集前5个项集:")
        current_dataset = self.item_sets[start_idx:end_idx]
        utils.print_item_sets_info(current_dataset[:5])

    def plot_scatter(self):
        """绘制散点图"""
        if not self.item_sets:
            print("\n请先加载数据文件")
            return

        print("\n[绘制散点图]")
        print("-" * 40)

        # 计算当前数据集的项集范围
        items_per_dataset = len(self.item_sets) // len(self.capacities)
        start_idx = self.current_dataset_index * items_per_dataset
        end_idx = (self.current_dataset_index + 1) * items_per_dataset
        current_dataset = self.item_sets[start_idx:end_idx]

        # 生成保存路径
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        save_path = f"results/scatter_dataset{self.current_dataset_index+1}_{timestamp}.png"

        Visualizer.plot_scatter(
            current_dataset,
            title=f"D{{0-1}}KP散点图 - 数据集{self.current_dataset_index+1} (容量: {self.current_capacity:.2f})",
            show_plot=True,
            save_path=save_path
        )

    def sort_by_ratio(self):
        """按第三项价值重量比排序"""
        if not self.item_sets:
            print("\n请先加载数据文件")
            return

        print("\n[按第三项价值重量比排序]")
        print("-" * 40)

        # 计算当前数据集的项集范围
        items_per_dataset = len(self.item_sets) // len(self.capacities)
        start_idx = self.current_dataset_index * items_per_dataset
        end_idx = (self.current_dataset_index + 1) * items_per_dataset
        current_dataset = self.item_sets[start_idx:end_idx]

        # 选择排序方式
        print("排序方式:")
        print("1. 非递增排序 (从大到小，默认)")
        print("2. 递增排序 (从小到大)")

        choice = input("请选择 [1/2]: ").strip()
        reverse = (choice != "2")

        sorted_dataset = utils.sort_item_sets_by_ratio(current_dataset, reverse=reverse)

        # 保存排序结果（只保存当前数据集的排序结果）
        self.sorted_item_sets = sorted_dataset

        print(f"\n已按第三项价值重量比{'非递增' if reverse else '递增'}排序")

        # 显示排序结果
        utils.print_item_sets_info(sorted_dataset[:10])

    def solve_dp(self, use_optimized=False):
        """动态规划求解"""
        if not self.item_sets:
            print("\n请先加载数据文件")
            return

        solver_name = "优化动态规划" if use_optimized else "标准动态规划"
        print(f"\n[{solver_name}求解 - 数据集{self.current_dataset_index+1}]")
        print("-" * 40)

        # 计算当前数据集的项集范围
        items_per_dataset = len(self.item_sets) // len(self.capacities)
        start_idx = self.current_dataset_index * items_per_dataset
        end_idx = (self.current_dataset_index + 1) * items_per_dataset
        current_dataset = self.item_sets[start_idx:end_idx]

        # 选择使用排序后的数据
        use_sorted = False
        if self.sorted_item_sets:
            choice = input("使用排序后的数据? (y/n, 默认n): ").strip().lower()
            use_sorted = (choice == 'y')

        # 选择求解器
        if use_optimized:
            solver = OptimizedDPSolver(
                self.sorted_item_sets if use_sorted else current_dataset,
                self.current_capacity
            )
        else:
            solver = DynamicProgrammingSolver(
                self.sorted_item_sets if use_sorted else current_dataset,
                self.current_capacity
            )

        # 求解
        print(f"\n正在求解，请稍候...")
        optimal_value, selected_items, solve_time = solver.solve()

        # 保存结果
        self.last_result = (optimal_value, selected_items, solve_time)

        # 显示结果
        print(f"\n求解完成!")
        print(f"最优总价值: {optimal_value:.2f}")
        print(f"求解时间: {utils.format_time(solve_time)}")
        print(f"选中物品数量: {len(selected_items)}")

        # 显示选中的物品
        if selected_items:
            print("\n选中物品列表:")
            print(f"{'物品ID':<10}{'所属项集':<10}{'重量':<10}{'价值':<10}")
            print("-" * 40)
            total_weight = 0
            for item in selected_items:
                print(f"{item.id:<10}{item.set_id:<10}{item.weight:<10.2f}{item.value:<10.2f}")
                total_weight += item.weight
            print("-" * 40)
            print(f"总重量: {total_weight:.2f} / {self.current_capacity:.2f}")

    def export_results(self):
        """导出结果"""
        if not self.last_result:
            print("\n没有可导出的结果，请先进行求解")
            return

        optimal_value, selected_items, solve_time = self.last_result

        print("\n[导出结果]")
        print("-" * 40)

        # 生成文件名
        timestamp = time.strftime("%Y%m%d_%H%M%S")

        print("选择导出格式:")
        print("1. TXT文件")
        print("2. Excel文件")
        print("3. 两种格式都导出")

        choice = input("请选择 [1/2/3]: ").strip()

        if choice in ['1', '3']:
            txt_file = f"results/result_dataset{self.current_dataset_index+1}_{timestamp}.txt"
            FileHandler.export_to_txt(
                txt_file,
                optimal_value,
                selected_items,
                solve_time,
                self.current_capacity,
                "动态规划",
                self.current_dataset_index + 1
            )

        if choice in ['2', '3']:
            excel_file = f"results/result_dataset{self.current_dataset_index+1}_{timestamp}.xlsx"
            FileHandler.export_to_excel(
                excel_file,
                optimal_value,
                selected_items,
                solve_time,
                self.current_capacity,
                self.item_sets,
                self.current_dataset_index + 1
            )

    def show_about(self):
        """显示关于信息"""
        print("\n[关于本程序]")
        print("-" * 40)
        print("D{0-1}背包问题求解程序")
        print("版本: 1.0")
        print("\n功能:")
        print("  - 读取D{0-1}KP数据文件（支持多数据集）")
        print("  - 绘制重量-价值散点图")
        print("  - 按第三项价值重量比排序")
        print("  - 动态规划求解（标准版和优化版）")
        print("  - 导出结果为TXT或Excel")
        print("\n开发者: 个人项目")
        print("-" * 40)

    def run(self):
        """运行主程序"""
        while True:
            self.clear_screen()
            self.print_header()

            # 显示当前状态
            if self.item_sets:
                print(f"\n当前文件: {os.path.basename(self.current_file)}")
                print(f"当前数据集: {self.current_dataset_index + 1}/{len(self.capacities)}")
                print(f"背包容量: {self.current_capacity:.2f}")
                print(f"项集数量: {len(self.item_sets)}")

            self.print_menu()

            choice = input("\n请输入选择 [0-9]: ").strip()

            if choice == '1':
                self.load_data()
            elif choice == '2':
                self.show_info()
            elif choice == '3':
                self.plot_scatter()
            elif choice == '4':
                self.sort_by_ratio()
            elif choice == '5':
                self.solve_dp(use_optimized=False)
            elif choice == '6':
                self.solve_dp(use_optimized=True)
            elif choice == '7':
                self.export_results()
            elif choice == '8':
                self.select_dataset()
            elif choice == '9':
                self.show_about()
            elif choice == '0':
                print("\n感谢使用，再见！")
                break
            else:
                print("\n无效选择，请重新输入")

            if choice != '0':
                input("\n按Enter键继续...")


if __name__ == "__main__":
    app = D0_1KPSolver()
    app.run()