import os

all_inputs = []

def get_input(prompt):
    user_input = input(prompt)
    all_inputs.append(user_input)
    return user_input

settings = {}

while True:
    diff = get_input("난이도를 선택하세요 (쉬움, 보통, 어려움): ")
    if diff in ["쉬움", "보통", "어려움"]:
        settings["난이도"] = diff
        break
    else:
        print("잘못된 입력입니다. '쉬움', '보통', '어려움' 중에서 입력해주세요.")
map_data = [
    ["", "", "", "", "새천년관", "이윤재관"],
    ["백양관", "백양로5", "대강당", "음악관", "알렌관", "ABMRC"],
    ["중앙도서관", "독수리상", "학생회관", "루스채플", "재활병원", "치과대학"],
    ["체육관", "백양로3", "공터2", "광혜원", "어린이병원", "세브란스병원"],
    ["공학관", "백양로2", "백주년기념관", "안과병원", "제중관", ""],
    ["공학원", "백양로1", "공터1", "암병원", "의과대학", ""],
    ["연대앞 버스정류장", "정문", "스타벅스", "세브란스병원 버스정류장", "", ""]
]

row, col = 6, 0
hp = 10
account_balance = 50000
inventory = []
current_time = "11시"

while True:
    print("\n1. 상태 \n 2. 위치 \n 3. 시간 \n 4. 수업 \n 5. 이동 \n 6. 난이도 변경 \n 7. 가방 \n 8. 종료 \n 9. 저장 \n 10. 불러오기")
    answer = get_input("Please select your option: ")
    
    if answer == "1" or answer == "상태":
        print("당신의 상태는 '배고픔'입니다.")
        print(f"현재 게임 난이도: {settings['난이도']}")
        
        status_choice = get_input("어떤 상태를 확인하시겠습니까? (1. 계좌, 2. HP): ")
        if status_choice == "1" or status_choice == "계좌":
            print(f"● 계좌의 잔액: {account_balance}원")
        elif status_choice == "2" or status_choice.upper() == "HP":
            print(f"● HP: {hp}")
        else:
            print("잘못된 입력입니다.")
            
    elif answer == "7" or answer == "가방":
        if not inventory:
            print("가방이 비어있습니다.")
        else:
            print("가방에 들어있는 물건들:")
            for i, item in enumerate(inventory):
                print(f"{i+1}. {item}")
            choice = get_input("사용할 물건의 이름 또는 번호를 입력하세요 (취소: 엔터): ")
            if choice:
                usable_item = None
                if choice.isdigit() and 1 <= int(choice) <= len(inventory):
                    usable_item = inventory[int(choice)-1]
                elif choice in inventory:
                    usable_item = choice
                
                if usable_item:
                    print(f"'{usable_item}'을(를) 사용했습니다.")
                    inventory.remove(usable_item)
                    if usable_item == "두쫀쿠":
                        hp += 25
                        print(f"HP가 25 증가했습니다! (현재 HP: {hp})")
                    elif usable_item == "카페라떼":
                        hp += 25
                        print(f"HP가 25 증가했습니다! (현재 HP: {hp})")
                else:
                    print("가방에 없는 물건이거나 잘못된 입력입니다.")
    elif answer == "2" or answer == "위치":
        print(f"당신의 위치는 '{map_data[row][col]}'입니다.")
    elif answer == "3" or answer == "시간":
        print(f"당신의 시간은 '{current_time}'입니다.")
    elif answer == "4":
        print("당신의 수업은 1시 이윤재관 511호에 있습니다.")
    elif answer == "5":
        while True:
            direction = get_input("이동할 방향을 입력하세요 (동, 서, 남, 북) 또는 '그만'을 입력하여 돌아가기: ")
            
            if direction == "그만":
                break
                
            new_row, new_col = row, col
            
            if direction == "북":
                new_row -= 1
            elif direction == "남":
                new_row += 1
            elif direction == "동":
                new_col += 1
            elif direction == "서":
                new_col -= 1
            else:
                print("동, 서, 남, 북 중에서 입력해주세요.")
                continue
                
            if 0 <= new_row < len(map_data) and 0 <= new_col < len(map_data[0]) and map_data[new_row][new_col] != "":
                row, col = new_row, new_col
                hp -= 1
                curr_place = map_data[row][col]
                print(f"[{curr_place}] (으)로 이동했습니다. (HP 1 감소, 현재 HP: {hp})")
                
                if curr_place == "학생회관":
                    print("학생회관에 도착했습니다. 이곳에서는 물건을 구매할 수 있습니다.")
                    while True:
                        buy_choice = get_input("무엇을 구매하시겠습니까? (1. 두쫀쿠(5000원), 2. 카페라떼(2500원), 3. 나가기): ")
                        if buy_choice == "1" or buy_choice == "두쫀쿠":
                            if account_balance >= 5000:
                                account_balance -= 5000
                                inventory.append("두쫀쿠")
                                print("두쫀쿠를 구매하여 가방에 넣었습니다. (잔액: 5000원 차감)")
                            else:
                                print("잔액이 부족합니다.")
                        elif buy_choice == "2" or buy_choice == "카페라떼":
                            if account_balance >= 2500:
                                account_balance -= 2500
                                inventory.append("카페라떼")
                                print("카페라떼를 구매하여 가방에 넣었습니다. (잔액: 2500원 차감)")
                            else:
                                print("잔액이 부족합니다.")
                        elif buy_choice == "3" or buy_choice == "나가기":
                            print("학생회관 매점을 나옵니다.")
                            break
                        else:
                            print("잘못된 입력입니다.")
            else:
                print("그 방향은 막혔어.")
    elif answer == "6":
        diff = get_input("변경할 난이도를 선택하세요 (쉬움, 보통, 어려움): ")
        if diff in ["쉬움", "보통", "어려움"]:
            settings["난이도"] = diff
            print(f"난이도가 '{diff}'(으)로 변경되었습니다.")
        else:
            print("잘못된 입력입니다. 변경되지 않았습니다.")
    elif answer == "8" or answer == "종료":
        print("게임을 종료합니다.")
        break
    elif answer == "9" or answer == "저장":
        with open("save_file.txt", "w", encoding="utf-8") as f:
            f.write(f"● 주인공의 상태\n")
            f.write(f"  ○ HP: {hp}\n")
            f.write(f"  ○ 계좌 잔액: {account_balance}원\n")
            if inventory:
                f.write(f"  ○ 가방: {', '.join(inventory)}\n")
            else:
                f.write(f"  ○ 가방: 비어있음\n")
            f.write(f"● 주인공의 위치: {map_data[row][col]}\n")
            f.write(f"● 현재 시각: {current_time}\n")
            f.write(f"● 난이도: {settings['난이도']}\n")
            f.write(f"● 현재까지의 모든 입력: {all_inputs}\n")
        print("게임이 저장되었습니다.")
    elif answer == "10" or answer == "불러오기":
        files = [f for f in os.listdir('.') if os.path.isfile(f)]
        print("현재 폴더의 파일 목록:")
        for i, filename in enumerate(files):
            print(f"{i+1}. {filename}")
        
        load_inp = get_input("불러올 파일의 번호를 선택하거나, 경로를 직접 입력하세요: ")
        
        if load_inp.isdigit() and 1 <= int(load_inp) <= len(files):
            target_file = files[int(load_inp)-1]
        else:
            target_file = load_inp
            
        if os.path.exists(target_file) and os.path.isfile(target_file):
            with open(target_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                
            for line in lines:
                line = line.strip()
                if line.startswith("○ HP:"):
                    hp = int(line.replace("○ HP:", "").strip())
                elif line.startswith("○ 계좌 잔액:"):
                    account_balance = int(line.replace("○ 계좌 잔액:", "").replace("원", "").strip())
                elif line.startswith("○ 가방:"):
                    items_str = line.replace("○ 가방:", "").strip()
                    if items_str == "비어있음":
                        inventory = []
                    else:
                        inventory = [i.strip() for i in items_str.split(",")]
                elif line.startswith("● 주인공의 위치:"):
                    loc = line.replace("● 주인공의 위치:", "").strip()
                    for r in range(len(map_data)):
                        for c in range(len(map_data[r])):
                            if map_data[r][c] == loc:
                                row, col = r, c
                elif line.startswith("● 현재 시각:"):
                    current_time = line.replace("● 현재 시각:", "").strip()
                elif line.startswith("● 난이도:"):
                    settings["난이도"] = line.replace("● 난이도:", "").strip()
            print(f"'{target_file}' 파일에서 데이터를 성공적으로 불러왔습니다.")
        else:
            print("파일을 찾을 수 없습니다.")
    else:
        print("잘못된 입력입니다.")