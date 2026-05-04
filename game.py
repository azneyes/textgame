import os
import pickle
from datetime import datetime
from typing import Dict, List

from data import DIFFICULTY_COST, ITEMS, build_places
from models import Player, Quest


class Game:
    def __init__(self, event_file="events.pkl"):

        self.event_file = event_file
        self.events, self.answers = self.load_events(event_file)
        self.places = build_places(self.events)
        self.player = Player()
        self.difficulty = "보통"
        self.running = True
        self.inputs: List[str] = []
        self.outputs: List[str] = []
        self.input_count = 0
        self.output_count = 0

    def load_events(self, filename):

        try:
            with open(filename, "rb") as f:
                data = pickle.load(f)
            return data.get("events", {}), data.get("answers", {})
        
        except FileNotFoundError:
            return {}, {}

    def log_output(self, text: str):

        self.output_count += 1
        numbered = f"[{self.output_count}] {text}"
        self.outputs.append(numbered)
        print(numbered)

    def get_input(self, prompt="입력: "):

        value = input(prompt).strip()
        self.input_count += 1
        self.inputs.append(f"[{self.input_count}] 입력: {value}")
        return value

    def start(self):

        self.log_output("송도 생활을 마치고 신촌에 처음 도착했다. 연대앞 버스정류장이다.")

        while self.running:
            command = self.get_input()
            self.handle_command(command)

        self.write_logs()

    def write_logs(self):

        with open("player_input.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(self.inputs))

        with open("game_output.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(self.outputs))

    def handle_command(self, command: str):

        if command in ["동", "서", "남", "북"]:
            self.move(command)
        elif command == "상태":
            self.log_output(self.player.print_status(self.places, self.difficulty))
        elif command == "가방":
            self.open_bag()
        elif command == "구매":
            self.buy()
        elif command == "판매":
            self.sell()
        elif command == "임무":
            self.quest_interaction()
        elif command == "임무목록":
            self.print_quests()
        elif command == "난이도":
            self.change_difficulty()
        elif command == "저장":
            self.save_game()
        elif command == "불러오기":
            self.load_game()
        elif command in ["종료", "exit", "quit"]:
            self.log_output("게임을 종료합니다.")
            self.running = False
        else:
            self.log_output("알 수 없는 입력입니다.")

    def describe_place(self):
        
        place = self.places[self.player.location]
        message = f"{place.name}에 도착했다."

        if place.event_info:
            message += f" {place.event_info}"

        tags = place.interaction_tags()
        if tags:
            message += " [" + ", ".join(tags) + "]"

        return message

    def move(self, direction):

        hp_cost = DIFFICULTY_COST[self.difficulty]
        moved, error = self.player.move(direction, self.places, hp_cost)

        if not moved:
            self.log_output(error)
            return
        
        self.log_output(self.describe_place())

    def open_bag(self):

        if not self.player.bag:
            self.log_output("가방이 비어있습니다.")
            return
        
        items = list(self.player.bag.items())
        bag_text = ", ".join([f"{name} x{count}" for name, count in items])
        self.log_output(f"가방을 엽니다 [{bag_text}]")
        choice = self.get_input("사용할 물건 이름 또는 번호 입력, 종료: ")

        if choice == "종료":
            self.log_output("가방을 닫습니다.")
            return
        
        item_name = None
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(items):
                item_name = items[idx][0]

        elif choice in self.player.bag:
            item_name = choice

        if not item_name:
            self.log_output("잘못된 선택입니다.")
            return
        
        self.player.remove_item(item_name)
        self.player.hp += ITEMS[item_name].hp_restore
        self.log_output(f"{item_name}를 사용했습니다. HP={self.player.hp:g}")

    def buy(self):
        place = self.places[self.player.location]

        if not place.buy_items:
            self.log_output("이 장소에서는 구매할 수 없습니다.")
            return
        
        while True:
            lines = ["무엇을 구매하시겠습니까?"]
            item_names = list(place.buy_items.keys())

            for i, name in enumerate(item_names, 1):
                price = place.buy_items[name]
                lines.append(f"{i}) {name}: {price}원, HP가 {ITEMS[name].hp_restore:g}만큼 증가한다.")

            lines.append(f"{len(item_names)+1}) 종료")
            self.log_output("\n".join(lines))
            choice = self.get_input()

            if choice == str(len(item_names) + 1) or choice == "종료":
                self.log_output("구매를 종료합니다.")
                break

            if not choice.isdigit() or not (1 <= int(choice) <= len(item_names)):
                self.log_output("잘못된 선택입니다.")
                continue

            item = item_names[int(choice) - 1]
            price = place.buy_items[item]

            if self.player.money < price:
                self.log_output(f"{item} 구매를 실패했다. 계좌 잔액이 부족하다.")
                continue

            self.player.money -= price
            self.player.add_item(item)
            self.log_output(f"{item}를 구매해서 가방에 넣었다. 계좌 잔액 = {self.player.money}원")

    def sell(self):
        place = self.places[self.player.location]

        if not place.sell_items:
            self.log_output("이 장소에서는 판매할 수 없습니다.")
            return
        
        while True:
            sellable = [item for item in self.player.bag if item in place.sell_items and self.player.bag[item] > 0]

            if not sellable:
                self.log_output("팔 것이 없어서 종료합니다.")
                break

            lines = ["무엇을 판매하시겠습니까?"]
            for i, item in enumerate(sellable, 1):
                lines.append(f"{i}) {item} x{self.player.bag[item]}")

            lines.append(f"{len(sellable)+1}) 종료")
            self.log_output("\n".join(lines))
            choice = self.get_input()

            if choice == str(len(sellable) + 1) or choice == "종료":
                self.log_output("판매를 종료합니다.")
                break

            if not choice.isdigit() or not (1 <= int(choice) <= len(sellable)):
                self.log_output("잘못된 선택입니다.")
                continue

            item = sellable[int(choice) - 1]
            self.player.remove_item(item)
            self.player.money += place.sell_items[item]
            self.log_output(f"{item}를 판매해서 {place.sell_items[item]}원을 벌었다. 계좌 잔액 = {self.player.money}원")

    def quest_interaction(self):

        loc = self.player.location
        if loc == "정문":
            name = "독수리상 방문"

            if name not in self.player.quests and name not in self.player.completed_quests:
                self.player.quests[name] = Quest(name, "학교에서 어떤 일들이 일어나고있는지 소식들이 모이는 독수리상에서 알아보자.")
                self.log_output("학교에서 어떤 일들이 일어나고있는지 소식들이 모이는 독수리상에서 알아보자.\n[임무목록]에 임무가 추가되었습니다.")

            else:
                self.log_output("이미 받은 임무입니다.")

        elif loc == "독수리상":

            if "독수리상 방문" in self.player.quests:

                del self.player.quests["독수리상 방문"]
                self.player.completed_quests.append("독수리상 방문")
                self.log_output("다음의 임무가 해결되었다! [학교에서 어떤 일들이 일어나고있는지 소식들이 모이는 독수리상에서 알아보자.]")
            self.add_investigation_quests()

        elif loc == "본관":
            self.report_quest("교내 부조리 수사")

        elif loc == "세브란스":
            self.report_quest("교내 위생사건 수사")

        elif loc == "이윤재관":
            self.final_report()

        else:
            self.log_output("이 장소에는 임무가 없습니다.")

    def add_investigation_quests(self):

        added = []
        quests = {
            "교내 부조리 수사": ("교내 어딘가에서 부조리가 일어나고있다. 이동하고 상호작용을 해서 부조리를 찾아서 본관에 보고하라.", "본관"),
            "교내 위생사건 수사": ("학생들이 단체로 식중독에 걸렸다. 이동하고 상호작용을 해서 위생사건의 원인을 찾아서 세브란스에 보고하라.", "세브란스"),
        }
        for name, (desc, report_place) in quests.items():
            
            if name not in self.player.quests and name not in self.player.completed_quests:
                self.player.quests[name] = Quest(name, desc, report_place)
                added.append(f"{name} - {desc}")

        if added:

            self.log_output("\n".join(added))

        else:
            self.log_output("새로 받을 임무가 없습니다.")

    def report_quest(self, quest_name):
        
        if quest_name not in self.player.quests:
            self.log_output("해결할 대상이 없습니다.")
            return
        
        question = "교내 어디에 부조리가 있나?" if quest_name == "교내 부조리 수사" else "교내 어디에 식중독 원인이 있나?"
        self.log_output(question)
        answer = self.get_input()
        correct = self.answers.get(quest_name)

        if answer == correct:
            del self.player.quests[quest_name]
            self.player.completed_quests.append(quest_name)
            self.log_output(f"다음의 임무가 해결되었다! [{quest_name}]\n수업들으러 이윤재관 가야지!")

        else:
            self.log_output("정답이 아닙니다. 더 조사해보자.")

    def final_report(self):

        has_bad = "교내 부조리 수사" in self.player.completed_quests
        has_food = "교내 위생사건 수사" in self.player.completed_quests

        if has_bad and has_food:
            self.log_output("부조리와 식중독 수사를 완료했구나! 수업은 이걸로 끝입니다. 또 만나요~")
            self.running = False

        elif has_bad:
            self.log_output("부조리 수사를 완료했구나! 식중독 원인도 찾아주세요~")

        elif has_food:
            self.log_output("식중독 수사를 완료했구나! 부조리도 찾아주세요~")
            
        else:
            self.log_output("아직 임무를 완료하지 않았습니다. 독수리상에서 임무를 받고 해결하세요.")

    def print_quests(self):

        if not self.player.quests:
            self.log_output("현재 가지고 있는 임무가 없습니다.")
            return
        
        text = "\n".join([f"{q.name} - {q.description}" for q in self.player.quests.values()])
        self.log_output(text)

    def change_difficulty(self):

        self.log_output("현재 난이도: " + self.difficulty + "\n난이도를 선택하세요: 쉬움, 보통, 어려움")
        choice = self.get_input()

        if choice in DIFFICULTY_COST:
            self.difficulty = choice
            self.log_output(f"난이도가 {choice}으로 변경되었습니다.")

        else:
            self.log_output("잘못된 난이도입니다.")

    def save_game(self):

        filename = self.get_input("저장할 파일명: ") or "save.pkl"
        data = {
            "player": self.player,
            "difficulty": self.difficulty,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "input_count": self.input_count,
            "output_count": self.output_count,
            "saved_at": datetime.now().isoformat(),
        }
        with open(filename, "wb") as f:
            pickle.dump(data, f)
        self.log_output(f"{filename}에 저장했습니다.")

    def load_game(self):

        files = [f for f in os.listdir(".") if f.endswith(".pkl") and f != self.event_file]

        if files:
            self.log_output("저장된 파일:\n" + "\n".join([f"{i+1}) {name}" for i, name in enumerate(files)]))
        choice = self.get_input("불러올 파일 번호 또는 경로: ")
        filename = None

        if choice.isdigit() and files and 1 <= int(choice) <= len(files):
            filename = files[int(choice) - 1]

        else:
            filename = choice
            
        try:
            with open(filename, "rb") as f:
                data = pickle.load(f)
            self.player = data["player"]
            self.difficulty = data["difficulty"]
            self.inputs = data.get("inputs", self.inputs)
            self.outputs = data.get("outputs", self.outputs)
            self.input_count = data.get("input_count", self.input_count)
            self.output_count = data.get("output_count", self.output_count)
            self.log_output(f"{filename}을 불러왔습니다.")
        except Exception as e:
            self.log_output(f"불러오기에 실패했습니다: {e}")
