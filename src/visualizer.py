"""
数据可视化模块
绘制物品的重量-价值散点图
"""

import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import os
from typing import List
from data_structures import ItemSet, Item

# 设置中文字体
def setup_chinese_font():
    """设置matplotlib支持中文显示"""
    import platform

    system = platform.system()

    if system == "Windows":
        # Windows系统
        font_list = ['Microsoft YaHei', 'SimHei', 'KaiTi', 'FangSong']
        for font in font_list:
            try:
                matplotlib.rcParams['font.sans-serif'] = [font] + matplotlib.rcParams['font.sans-serif']
                matplotlib.rcParams['axes.unicode_minus'] = False
                # 测试字体是否可用
                plt.figure()
                plt.text(0.5, 0.5, '测试', fontproperties=font)
                plt.close()
                print(f"使用字体: {font}")
                return True
            except:
                continue
    elif system == "Darwin":  # macOS
        try:
            matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'Heiti TC', 'PingFang SC'] + matplotlib.rcParams['font.sans-serif']
            matplotlib.rcParams['axes.unicode_minus'] = False
        except:
            pass
    else:  # Linux
        try:
            matplotlib.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei', 'Noto Sans CJK SC'] + matplotlib.rcParams['font.sans-serif']
            matplotlib.rcParams['axes.unicode_minus'] = False
        except:
            pass

    # 如果上面的字体都不可用，尝试使用默认字体但添加回退
    matplotlib.rcParams['axes.unicode_minus'] = False
    return False


class Visualizer:
    """数据可视化器"""

    def __init__(self):
        """初始化可视化器，设置中文字体"""
        self.font_supported = setup_chinese_font()
        if not self.font_supported:
            print("警告: 系统可能不支持中文显示，图表中的中文将显示为方框")

    @staticmethod
    def plot_scatter(item_sets: List[ItemSet],
                     title: str = "D{0-1}KP物品散点图",
                     show_plot: bool = True,
                     save_path: str = None):
        """
        绘制所有物品的重量-价值散点图

        Args:
            item_sets: 项集列表
            title: 图表标题
            show_plot: 是否显示图表
            save_path: 保存路径（如果为None则不保存）
        """
        # 创建图形，设置dpi提高清晰度
        plt.figure(figsize=(12, 8), dpi=100)

        # 收集所有物品
        all_items = []
        for item_set in item_sets:
            all_items.extend(item_set.items)

        # 提取重量和价值
        weights = [item.weight for item in all_items]
        values = [item.value for item in all_items]

        # 计算统计信息用于图例
        total_items = len(all_items)
        total_sets = len(item_sets)

        # 按项集分组着色，使用更鲜明的颜色
        colors = plt.cm.tab20(np.linspace(0, 1, min(len(item_sets), 20)))

        # 创建散点图
        for idx, item_set in enumerate(item_sets[:20]):  # 最多显示20个项集，避免颜色过多
            set_weights = [item.weight for item in item_set.items]
            set_values = [item.value for item in item_set.items]

            # 为每个项集的三个物品使用不同标记
            markers = ['o', 's', '^']  # 物品1:圆圈, 物品2:方块, 物品3:三角形
            marker_sizes = [60, 60, 80]  # 物品3稍微大一点突出显示
            alpha_values = [0.6, 0.6, 0.8]  # 物品3更不透明

            for i in range(3):
                plt.scatter(set_weights[i], set_values[i],
                          c=[colors[idx % len(colors)]],
                          marker=markers[i],
                          s=marker_sizes[i],
                          alpha=alpha_values[i],
                          edgecolors='black' if i == 2 else None,
                          linewidth=0.5 if i == 2 else 0)

        # 添加其他未显示的项集（灰色小点）
        if len(item_sets) > 20:
            other_weights = []
            other_values = []
            for item_set in item_sets[20:]:
                for item in item_set.items:
                    other_weights.append(item.weight)
                    other_values.append(item.value)
            plt.scatter(other_weights, other_values,
                      c='lightgray', marker='.', s=20, alpha=0.3, label='其他项集')

        # 设置标签和标题
        plt.xlabel('重量', fontsize=14, fontweight='bold')
        plt.ylabel('价值', fontsize=14, fontweight='bold')

        # 处理标题中的中文
        if not setup_chinese_font():
            # 如果中文不支持，使用英文标题
            title = title.replace('散点图', 'Scatter Plot')
            title = title.replace('数据集', 'Dataset')
            title = title.replace('容量', 'Capacity')

        plt.title(title, fontsize=16, fontweight='bold', pad=20)

        # 添加网格
        plt.grid(True, alpha=0.3, linestyle='--')

        # 添加统计信息
        stats_text = f'总物品数: {total_items} | 项集数: {total_sets}'
        plt.text(0.02, 0.98, stats_text, transform=plt.gca().transAxes,
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        # 创建图例
        legend_elements = []
        # 添加物品类型图例
        from matplotlib.lines import Line2D
        legend_elements.extend([
            Line2D([0], [0], marker='o', color='w', markerfacecolor='gray',
                   markersize=8, label='物品1'),
            Line2D([0], [0], marker='s', color='w', markerfacecolor='gray',
                   markersize=8, label='物品2'),
            Line2D([0], [0], marker='^', color='w', markerfacecolor='gray',
                   markersize=8, markeredgecolor='black', label='物品3 (折扣)')
        ])

        plt.legend(handles=legend_elements, loc='upper right',
                  framealpha=0.9, fontsize=10)

        # 调整布局
        plt.tight_layout()

        # 保存图片
        if save_path:
            # 确保目录存在
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            print(f"图表已保存到: {save_path}")

        # 显示图片
        if show_plot:
            plt.show()
        else:
            plt.close()

    @staticmethod
    def plot_item_sets_comparison(item_sets: List[ItemSet],
                                   title: str = "项集内物品对比",
                                   show_plot: bool = True,
                                   max_sets: int = 5):
        """
        绘制每个项集内三个物品的对比图

        Args:
            item_sets: 项集列表
            title: 图表标题
            show_plot: 是否显示图表
            max_sets: 最多显示多少个项集
        """
        n_sets = min(len(item_sets), max_sets)
        fig, axes = plt.subplots(1, n_sets, figsize=(5*n_sets, 4))

        if n_sets == 1:
            axes = [axes]

        for idx in range(n_sets):
            item_set = item_sets[idx]
            ax = axes[idx]

            items = item_set.items
            x = range(3)
            weights = [item.weight for item in items]
            values = [item.value for item in items]

            width = 0.35
            bars1 = ax.bar([i - width/2 for i in x], weights, width,
                          label='重量', color='skyblue', alpha=0.7)
            bars2 = ax.bar([i + width/2 for i in x], values, width,
                          label='价值', color='lightcoral', alpha=0.7)

            # 在柱子上添加数值标签
            for bar in bars1:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}', ha='center', va='bottom', fontsize=8)
            for bar in bars2:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}', ha='center', va='bottom', fontsize=8)

            # 设置标签
            ax.set_xlabel('物品索引', fontsize=10)
            ax.set_ylabel('数值', fontsize=10)

            # 处理标题中的中文
            title_text = f'项集 {item_set.id}'
            if not setup_chinese_font():
                title_text = f'Set {item_set.id}'
            ax.set_title(title_text, fontsize=11, fontweight='bold')

            ax.set_xticks(x)
            ax.set_xticklabels(['物品1', '物品2', '物品3'] if setup_chinese_font() else ['Item1', 'Item2', 'Item3'])
            ax.legend(fontsize=8)
            ax.grid(True, alpha=0.3, axis='y')

        # 设置总标题
        if setup_chinese_font():
            fig.suptitle(title, fontsize=14, fontweight='bold', y=1.05)
        else:
            fig.suptitle('Item Set Comparison', fontsize=14, fontweight='bold', y=1.05)

        plt.tight_layout()

        if show_plot:
            plt.show()
        else:
            plt.close()

    @staticmethod
    def plot_value_weight_ratio(item_sets: List[ItemSet],
                               title: str = "价值重量比分布",
                               show_plot: bool = True):
        """
        绘制每个项集的价值重量比分布

        Args:
            item_sets: 项集列表
            title: 图表标题
            show_plot: 是否显示图表
        """
        plt.figure(figsize=(12, 6))

        # 收集每个项集的三个物品的比率
        set_ids = []
        ratios_item1 = []
        ratios_item2 = []
        ratios_item3 = []

        for item_set in item_sets[:50]:  # 最多显示50个项集
            set_ids.append(item_set.id)
            ratios_item1.append(item_set.items[0].ratio)
            ratios_item2.append(item_set.items[1].ratio)
            ratios_item3.append(item_set.items[2].ratio)

        x = range(len(set_ids))
        width = 0.25

        plt.bar([i - width for i in x], ratios_item1, width,
               label='物品1', alpha=0.7, color='skyblue')
        plt.bar(x, ratios_item2, width,
               label='物品2', alpha=0.7, color='lightcoral')
        plt.bar([i + width for i in x], ratios_item3, width,
               label='物品3 (折扣)', alpha=0.8, color='gold', edgecolor='black')

        plt.xlabel('项集ID' if setup_chinese_font() else 'Item Set ID', fontsize=12)
        plt.ylabel('价值/重量比' if setup_chinese_font() else 'Value/Weight Ratio', fontsize=12)

        if setup_chinese_font():
            plt.title(title, fontsize=14, fontweight='bold')
        else:
            plt.title('Value/Weight Ratio Distribution', fontsize=14, fontweight='bold')

        plt.legend()
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()

        if show_plot:
            plt.show()
        else:
            plt.close()


# 为了兼容性，保留原来的函数调用方式
def setup_plot_for_chinese():
    """设置绘图支持中文的辅助函数"""
    success = setup_chinese_font()
    if not success:
        print("提示: 如果中文显示为方框，请安装中文字体或使用英文标题")
    return success