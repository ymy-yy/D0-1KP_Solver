"""
数据可视化模块
绘制物品的重量-价值散点图
"""

import os
import platform
from typing import List, Optional, Union
from dataclasses import dataclass

# 尝试导入必需的库
try:
    import matplotlib.pyplot as plt
    import matplotlib
    import numpy as np
    from matplotlib.lines import Line2D
    MATPLOTLIB_AVAILABLE = True
except ImportError as e:
    MATPLOTLIB_AVAILABLE = False
    print(f"警告: 无法导入可视化库: {e}")
    print("请安装 matplotlib 和 numpy: pip install matplotlib numpy")

from data_structures import ItemSet, Item


# ==================== 字体配置 ====================

class FontConfig:
    """中文字体配置管理器"""

    # 各系统的字体候选列表
    FONT_CANDIDATES = {
        "Windows": ['Microsoft YaHei', 'SimHei', 'KaiTi', 'FangSong'],
        "Darwin": ['Arial Unicode MS', 'Heiti TC', 'PingFang SC'],
        "Linux": ['WenQuanYi Zen Hei', 'Noto Sans CJK SC']
    }

    _supported = None

    @classmethod
    def setup(cls) -> bool:
        """设置matplotlib支持中文显示"""
        if not MATPLOTLIB_AVAILABLE:
            return False

        if cls._supported is not None:
            return cls._supported

        system = platform.system()
        candidates = cls.FONT_CANDIDATES.get(system, [])

        # 设置通用配置
        matplotlib.rcParams['axes.unicode_minus'] = False

        # 尝试每个候选字体
        for font in candidates:
            try:
                matplotlib.rcParams['font.sans-serif'] = [font] + matplotlib.rcParams.get('font.sans-serif', [])
                # 测试字体是否可用
                fig = plt.figure()
                fig.text(0.5, 0.5, '测试', fontproperties=font)
                plt.close(fig)
                print(f"使用字体: {font}")
                cls._supported = True
                return True
            except:
                continue

        cls._supported = False
        print("警告: 系统可能不支持中文显示，图表中的中文将显示为方框")
        return False

    @classmethod
    def is_supported(cls) -> bool:
        """检查中文是否支持"""
        if cls._supported is None:
            cls.setup()
        return cls._supported


# ==================== 图表样式配置 ====================

@dataclass
class PlotStyle:
    """图表样式配置"""
    # 图形尺寸
    figsize_scatter: tuple = (12, 8)
    figsize_comparison: tuple = (5, 4)
    figsize_ratio: tuple = (12, 6)

    # 颜色
    color_palette: str = 'tab20'

    # 标记样式 [物品1, 物品2, 物品3]
    markers: List[str] = None
    marker_sizes: List[int] = None
    alpha_values: List[float] = None

    # 网格
    grid_alpha: float = 0.3
    grid_linestyle: str = '--'

    # 文本
    label_fontsize: int = 14
    label_fontweight: str = 'bold'
    title_fontsize: int = 16
    title_fontweight: str = 'bold'

    def __post_init__(self):
        if self.markers is None:
            self.markers = ['o', 's', '^']
        if self.marker_sizes is None:
            self.marker_sizes = [60, 60, 80]
        if self.alpha_values is None:
            self.alpha_values = [0.6, 0.6, 0.8]


# ==================== 文本处理 ====================

class TextHelper:
    """文本辅助类，处理中英文切换"""

    TRANSLATIONS = {
        'scatter_title': ('D{0-1}KP物品散点图', 'D{0-1}KP Scatter Plot'),
        'comparison_title': ('项集内物品对比', 'Item Set Comparison'),
        'ratio_title': ('价值重量比分布', 'Value/Weight Ratio Distribution'),
        'weight': ('重量', 'Weight'),
        'value': ('价值', 'Value'),
        'item_index': ('物品索引', 'Item Index'),
        'value_weight_ratio': ('价值/重量比', 'Value/Weight Ratio'),
        'set_id': ('项集ID', 'Item Set ID'),
        'item1': ('物品1', 'Item 1'),
        'item2': ('物品2', 'Item 2'),
        'item3': ('物品3 (折扣)', 'Item 3 (Discounted)'),
        'other_sets': ('其他项集', 'Other Sets'),
        'total_items': ('总物品数', 'Total Items'),
        'total_sets': ('项集数', 'Sets'),
    }

    @classmethod
    def get_text(cls, key: str, *args) -> str:
        """获取本地化文本"""
        cn_text, en_text = cls.TRANSLATIONS.get(key, (key, key))
        text = cn_text if FontConfig.is_supported() else en_text
        return text.format(*args) if args else text


# ==================== 可视化器 ====================

class Visualizer:
    """数据可视化器"""

    def __init__(self, style: Optional[PlotStyle] = None):
        """
        初始化可视化器

        Args:
            style: 图表样式配置，为None时使用默认配置
        """
        if not MATPLOTLIB_AVAILABLE:
            print("错误: matplotlib 未安装，无法使用可视化功能")
            print("请运行: pip install matplotlib numpy")
            return

        FontConfig.setup()
        self.style = style or PlotStyle()

    def plot_scatter(
        self,
        item_sets: List[ItemSet],
        title: Optional[str] = None,
        show_plot: bool = True,
        save_path: Optional[str] = None,
        max_sets_display: int = 20
    ) -> None:
        """
        绘制所有物品的重量-价值散点图

        Args:
            item_sets: 项集列表
            title: 图表标题，为None时使用默认标题
            show_plot: 是否显示图表
            save_path: 保存路径（如果为None则不保存）
            max_sets_display: 最多显示多少个项集的不同颜色
        """
        if not MATPLOTLIB_AVAILABLE:
            print("错误: matplotlib 未安装，无法绘制图表")
            return

        if not item_sets:
            print("警告: 没有数据可绘制")
            return

        # 创建图形
        plt.figure(figsize=self.style.figsize_scatter, dpi=100)

        # 收集统计信息
        all_items = [item for item_set in item_sets for item in item_set.items]
        total_items = len(all_items)
        total_sets = len(item_sets)

        # 按项集分组着色
        colors = plt.cm.get_cmap(self.style.color_palette)(
            np.linspace(0, 1, min(total_sets, max_sets_display))
        )

        # 绘制每个项集的物品
        for idx, item_set in enumerate(item_sets[:max_sets_display]):
            weights = [item.weight for item in item_set.items]
            values = [item.value for item in item_set.items]

            for i, (w, v) in enumerate(zip(weights, values)):
                plt.scatter(
                    w, v,
                    c=[colors[idx % len(colors)]],
                    marker=self.style.markers[i],
                    s=self.style.marker_sizes[i],
                    alpha=self.style.alpha_values[i],
                    edgecolors='black' if i == 2 else None,
                    linewidth=0.5 if i == 2 else 0
                )

        # 绘制其他项集（灰色小点）
        if total_sets > max_sets_display:
            other_weights = []
            other_values = []
            for item_set in item_sets[max_sets_display:]:
                for item in item_set.items:
                    other_weights.append(item.weight)
                    other_values.append(item.value)
            plt.scatter(
                other_weights, other_values,
                c='lightgray', marker='.', s=20, alpha=0.3,
                label=TextHelper.get_text('other_sets')
            )

        # 设置标签
        plt.xlabel(TextHelper.get_text('weight'), fontsize=self.style.label_fontsize, fontweight=self.style.label_fontweight)
        plt.ylabel(TextHelper.get_text('value'), fontsize=self.style.label_fontsize, fontweight=self.style.label_fontweight)

        # 设置标题
        if title is None:
            title = TextHelper.get_text('scatter_title')
        plt.title(title, fontsize=self.style.title_fontsize, fontweight=self.style.title_fontweight, pad=20)

        # 添加网格
        plt.grid(True, alpha=self.style.grid_alpha, linestyle=self.style.grid_linestyle)

        # 添加统计信息
        stats_text = f'{TextHelper.get_text("total_items")}: {total_items} | {TextHelper.get_text("total_sets")}: {total_sets}'
        plt.text(
            0.02, 0.98, stats_text,
            transform=plt.gca().transAxes,
            fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        )

        # 创建图例
        legend_elements = [
            Line2D([0], [0], marker='o', color='w', markerfacecolor='gray',
                   markersize=8, label=TextHelper.get_text('item1')),
            Line2D([0], [0], marker='s', color='w', markerfacecolor='gray',
                   markersize=8, label=TextHelper.get_text('item2')),
            Line2D([0], [0], marker='^', color='w', markerfacecolor='gray',
                   markersize=8, markeredgecolor='black', label=TextHelper.get_text('item3'))
        ]
        plt.legend(handles=legend_elements, loc='upper right',
                   framealpha=0.9, fontsize=10)

        self._save_and_show(plt.gcf(), save_path, show_plot)

    def plot_item_sets_comparison(
        self,
        item_sets: List[ItemSet],
        title: Optional[str] = None,
        show_plot: bool = True,
        max_sets: int = 5,
        save_path: Optional[str] = None
    ) -> None:
        """绘制每个项集内三个物品的对比图"""
        if not MATPLOTLIB_AVAILABLE:
            print("错误: matplotlib 未安装，无法绘制图表")
            return

        if not item_sets:
            print("警告: 没有数据可绘制")
            return

        n_sets = min(len(item_sets), max_sets)
        fig, axes = plt.subplots(1, n_sets, figsize=(self.style.figsize_comparison[0] * n_sets, self.style.figsize_comparison[1]))

        if n_sets == 1:
            axes = [axes]

        width = 0.35
        x = range(3)

        for idx, ax in enumerate(axes):
            item_set = item_sets[idx]
            items = item_set.items

            weights = [item.weight for item in items]
            values = [item.value for item in items]

            # 绘制柱状图
            bars1 = ax.bar([i - width/2 for i in x], weights, width,
                          label=TextHelper.get_text('weight'), color='skyblue', alpha=0.7)
            bars2 = ax.bar([i + width/2 for i in x], values, width,
                          label=TextHelper.get_text('value'), color='lightcoral', alpha=0.7)

            # 添加数值标签
            self._add_bar_labels(bars1, ax)
            self._add_bar_labels(bars2, ax)

            # 设置标签
            ax.set_xlabel(TextHelper.get_text('item_index'), fontsize=10)
            ax.set_ylabel(TextHelper.get_text('value'), fontsize=10)

            # 设置标题
            title_text = f'Set {item_set.id}' if not FontConfig.is_supported() else f'项集 {item_set.id}'
            ax.set_title(title_text, fontsize=11, fontweight='bold')

            ax.set_xticks(x)
            ax.set_xticklabels([TextHelper.get_text('item1'), TextHelper.get_text('item2'), TextHelper.get_text('item3')])
            ax.legend(fontsize=8)
            ax.grid(True, alpha=self.style.grid_alpha, axis='y')

        # 设置总标题
        if title is None:
            title = TextHelper.get_text('comparison_title')
        fig.suptitle(title, fontsize=self.style.title_fontsize, fontweight=self.style.title_fontweight, y=1.05)

        self._save_and_show(fig, save_path, show_plot)

    def plot_value_weight_ratio(
        self,
        item_sets: List[ItemSet],
        title: Optional[str] = None,
        show_plot: bool = True,
        max_sets: int = 50,
        save_path: Optional[str] = None
    ) -> None:
        """绘制每个项集的价值重量比分布"""
        if not MATPLOTLIB_AVAILABLE:
            print("错误: matplotlib 未安装，无法绘制图表")
            return

        if not item_sets:
            print("警告: 没有数据可绘制")
            return

        plt.figure(figsize=self.style.figsize_ratio)

        # 收集数据
        set_ids = []
        ratios = [[], [], []]  # [物品1比率列表, 物品2比率列表, 物品3比率列表]

        for item_set in item_sets[:max_sets]:
            set_ids.append(item_set.id)
            for i, item in enumerate(item_set.items):
                ratios[i].append(item.ratio)

        x = range(len(set_ids))
        width = 0.25

        # 绘制柱状图
        colors = ['skyblue', 'lightcoral', 'gold']
        labels = [TextHelper.get_text('item1'), TextHelper.get_text('item2'), TextHelper.get_text('item3')]
        edgecolors = [None, None, 'black']

        for i in range(3):
            positions = [pos + (i - 1) * width for pos in x]
            plt.bar(
                positions, ratios[i], width,
                label=labels[i], alpha=0.7, color=colors[i], edgecolor=edgecolors[i]
            )

        plt.xlabel(TextHelper.get_text('set_id'), fontsize=self.style.label_fontsize)
        plt.ylabel(TextHelper.get_text('value_weight_ratio'), fontsize=self.style.label_fontsize)

        if title is None:
            title = TextHelper.get_text('ratio_title')
        plt.title(title, fontsize=self.style.title_fontsize, fontweight=self.style.title_fontweight)

        plt.legend()
        plt.grid(True, alpha=self.style.grid_alpha, axis='y')

        self._save_and_show(plt.gcf(), save_path, show_plot)

    @staticmethod
    def _add_bar_labels(bars, ax) -> None:
        """为柱状图添加数值标签"""
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2., height,
                f'{int(height)}', ha='center', va='bottom', fontsize=8
            )

    @staticmethod
    def _save_and_show(fig, save_path: Optional[str], show_plot: bool) -> None:
        """保存并显示图表"""
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            fig.savefig(save_path, dpi=300, bbox_inches='tight',
                        facecolor='white', edgecolor='none')
            print(f"图表已保存到: {save_path}")

        if show_plot:
            plt.show()
        else:
            plt.close(fig)


# ==================== 向后兼容的函数 ====================

# 创建全局实例用于向后兼容
_default_visualizer = Visualizer() if MATPLOTLIB_AVAILABLE else None

def setup_plot_for_chinese() -> bool:
    """设置绘图支持中文的辅助函数（向后兼容）"""
    if not MATPLOTLIB_AVAILABLE:
        return False
    return FontConfig.setup()


def plot_scatter(item_sets: List[ItemSet], **kwargs):
    """
    向后兼容的散点图函数

    Args:
        item_sets: 项集列表（必需）
        **kwargs: 其他参数传递给 Visualizer.plot_scatter
    """
    if not MATPLOTLIB_AVAILABLE:
        print("错误: matplotlib 未安装，无法绘制图表")
        return
    return _default_visualizer.plot_scatter(item_sets, **kwargs)


def plot_item_sets_comparison(item_sets: List[ItemSet], **kwargs):
    """向后兼容的对比图函数"""
    if not MATPLOTLIB_AVAILABLE:
        print("错误: matplotlib 未安装，无法绘制图表")
        return
    return _default_visualizer.plot_item_sets_comparison(item_sets, **kwargs)


def plot_value_weight_ratio(item_sets: List[ItemSet], **kwargs):
    """向后兼容的比率图函数"""
    if not MATPLOTLIB_AVAILABLE:
        print("错误: matplotlib 未安装，无法绘制图表")
        return
    return _default_visualizer.plot_value_weight_ratio(item_sets, **kwargs)