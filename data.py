from models import Item, Place

ITEMS = {
    "두쫀쿠": Item("두쫀쿠", 10),
    "카페라떼": Item("카페라떼", 5),
}

DIFFICULTY_COST = {
    "쉬움": 0.5,
    "보통": 1,
    "어려움": 2,
}

# 6-column map from the slides. Empty cells are omitted.
MAP_ROWS = [
    ["종합관", "본관", "경영관", "노천극장", "새천년관", "이윤재관"],
    ["백양관", "백양로5", "대강당", "음악관", "알렌관", "ABMRC"],
    ["중앙도서관", "독수리상", "학생회관", "루스채플", "재활병원", "치과대학"],
    ["체육관", "백양로3", "공터2", "광혜원", "어린이병원", "세브란스"],
    ["공학관", "백양로2", "백주년기념관", "안과병원", "제중관", None],
    ["공학원", "백양로1", "공터1", "암병원", "의과대학", None],
    ["연대앞 버스정류장", "정문", "스타벅스", "세브란스 버스정류장", None, None],
]

BUY_PRICES = {
    "학생회관": {"두쫀쿠": 5000, "카페라떼": 3000},
    "스타벅스": {"두쫀쿠": 4000, "카페라떼": 2000},
    "ABMRC": {"두쫀쿠": 4000, "카페라떼": 2000},
}

HIGH_SELL_PLACES = ["체육관", "공학관", "공학원", "재활병원", "어린이병원", "종합관", "노천극장"]
NORMAL_SELL_PLACES = [
    "중앙도서관", "백양관", "대강당", "백주년기념관", "안과병원", "암병원", "새천년관", "알렌관",
    "제중관", "의과대학", "치과대학", "세브란스", "본관", "경영관"
]


def build_places(events=None):
    places = {}
    coords = {}
    for r, row in enumerate(MAP_ROWS):
        for c, name in enumerate(row):
            if name:
                coords[(r, c)] = name
                places[name] = Place(name=name)

    directions = {"동": (0, 1), "서": (0, -1), "남": (1, 0), "북": (-1, 0)}

    for (r, c), name in coords.items():
        for d, (dr, dc) in directions.items():
            places[name].neighbors[d] = coords.get((r + dr, c + dc))

    for place_name, prices in BUY_PRICES.items():
        places[place_name].buy_items = dict(prices)

    for place_name in HIGH_SELL_PLACES:
        places[place_name].sell_items = {"두쫀쿠": 7000, "카페라떼": 4000}

    for place_name in NORMAL_SELL_PLACES:
        places[place_name].sell_items = {"두쫀쿠": 6000, "카페라떼": 3000}

    for quest_place in ["정문", "독수리상", "본관", "세브란스", "이윤재관"]:
        places[quest_place].has_quest = True

    if events:
        for place_name, info in events.items():
            if place_name in places:
                places[place_name].event_info = info

    return places
