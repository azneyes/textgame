from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Item:
    name: str
    hp_restore: float


@dataclass
class Quest:
    name: str
    description: str
    report_place: Optional[str] = None
    completed: bool = False


@dataclass
class Place:
    name: str
    neighbors: Dict[str, Optional[str]] = field(default_factory=dict)
    buy_items: Dict[str, int] = field(default_factory=dict)
    sell_items: Dict[str, int] = field(default_factory=dict)
    has_quest: bool = False
    event_info: Optional[str] = None

    def interaction_tags(self) -> List[str]:
        
        tags = []
        if self.buy_items:
            tags.append("구매")
        if self.sell_items:
            tags.append("판매")
        if self.has_quest:
            tags.append("임무")
        return tags


@dataclass
class Player:

    location: str = "연대앞 버스정류장"
    hp: float = 10
    money: int = 10000
    bag: Dict[str, int] = field(default_factory=dict)
    quests: Dict[str, Quest] = field(default_factory=dict)
    completed_quests: List[str] = field(default_factory=list)

    def add_item(self, item_name: str, count: int = 1):
        self.bag[item_name] = self.bag.get(item_name, 0) + count

    def remove_item(self, item_name: str, count: int = 1) -> bool:

        if self.bag.get(item_name, 0) < count:
            return False
        
        self.bag[item_name] -= count
        if self.bag[item_name] <= 0:
            del self.bag[item_name]
        return True

    def move(self, direction: str, places: Dict[str, Place], hp_cost: float):

        current = places[self.location]
        next_place = current.neighbors.get(direction)
        if not next_place:
            return False, "그 방향은 막혔어."
        
        self.location = next_place
        self.hp -= hp_cost
        return True, None

    def print_status(self, places: Dict[str, Place], difficulty: str) -> str:

        place = places[self.location]
        east = place.neighbors.get("동") or "막힘"
        west = place.neighbors.get("서") or "막힘"
        south = place.neighbors.get("남") or "막힘"
        north = place.neighbors.get("북") or "막힘"

        return (
            f"계좌의 잔액 = {self.money:,}원\n"
            f"HP = {self.hp:g}\n"
            f"현재위치 = {self.location}\n"
            f"난이도 = {difficulty}\n"
            f"동서남북 = {east}, {west}, {south}, {north}"
        )
