"""
数据结构模块
定义Item和ItemSet类，用于表示D{0-1}KP问题的基本元素
"""


class Item:
    """物品类，表示单个可装入背包的物品"""

    def __init__(self, item_id: int, weight: float, value: float, set_id: int):
        """
        初始化物品

        Args:
            item_id: 物品ID
            weight: 物品重量
            value: 物品价值
            set_id: 所属项集ID
        """
        self.id = item_id
        self.weight = weight
        self.value = value
        self.set_id = set_id
        self.ratio = value / weight if weight > 0 else 0  # 价值重量比

    def __repr__(self):
        return f"Item(id={self.id}, w={self.weight}, v={self.value}, set={self.set_id})"


class ItemSet:
    """项集类，包含3个物品，每个项集至多选一个"""

    def __init__(self, set_id: int, items: list):
        """
        初始化项集

        Args:
            set_id: 项集ID
            items: 包含3个物品的列表，顺序为物品1、物品2、物品3
        """
        self.id = set_id
        self.items = items  # 长度为3的列表
        self.selected_item = -1  # -1表示未选，0-2表示选择的物品索引

        # 验证物品3的特性：价值=前两项之和，重量<前两项之和
        self._validate_items()

    def _validate_items(self):
        """验证物品3是否符合D{0-1}KP特性"""
        if len(self.items) != 3:
            raise ValueError(f"项集{self.id}必须包含3个物品")

        item1, item2, item3 = self.items
        # 检查物品3的价值是否为前两项之和
        if abs(item3.value - (item1.value + item2.value)) > 1e-6:
            print(f"警告: 项集{self.id}的物品3价值({item3.value})不等于前两项之和({item1.value + item2.value})")

        # 检查物品3的重量是否小于前两项之和
        if item3.weight >= (item1.weight + item2.weight):
            print(f"警告: 项集{self.id}的物品3重量({item3.weight})不小于前两项之和({item1.weight + item2.weight})")

    def get_third_item_ratio(self) -> float:
        """获取项集第三项的价值重量比，用于排序"""
        return self.items[2].ratio

    def __repr__(self):
        return f"ItemSet(id={self.id}, items={self.items})"