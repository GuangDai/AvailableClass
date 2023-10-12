import requests
import matplotlib.pyplot as plt
import os
from telegram import Bot
import random
from datetime import datetime, timedelta, timezone

time_data = ["08:00-08:45", "08:50-09:35", "09:50-10:35",
             "10:40-11:25", "11:30-12:15", "13:00-13:45",
             "13:50-14:35", "14:45-15:30", "15:40-16:25",
             "16:35-17:20", "17:25-18:10", "18:30-19:15",
             "19:20-20:05", "20:10-20:55"]
# 填入你的 Telegram Bot 的访问令牌
TOKEN = os.getenv('TELEGRAM_TOKEN')
chatId = os.getenv('CHAT_ID')

# 创建 Telegram Bot 实例
bot = Bot(TOKEN)


# 用于发送文件的函数
import os

def send_image(file_path, chat_id):
    # 确保文件存在
    if not os.path.exists(file_path):
        return False

    # 发送文件
    with open(file_path, 'rb') as file:
        bot.send_document(chat_id, file)  # 假设 `bot.send_document` 也是同步方法

    return True


def get_current_time_in_utc8():
    # 获取当前UTC时间
    utc_time = datetime.utcnow()

    # 将UTC时间转换为UTC+8时间
    utc8_time = utc_time + timedelta(hours=8)

    return utc8_time


def find_time_interval_index():
    # 获取当前UTC+8时间
    current_time = get_current_time_in_utc8()

    # 提取时间部分 (HH:MM)
    current_time_str = current_time.strftime('%H:%M')

    # 遍历时间数据
    for i in range(len(time_data)):
        start_time, end_time = time_data[i].split('-')
        if start_time <= current_time_str <= end_time:
            return i

        if i + 1 < len(time_data) and current_time_str < time_data[i + 1].split('-')[0]:
            return i + 1

    if current_time_str < time_data[0].split('-')[0]:
        return 0
    else:
        return -1


def min_cost_with_path(n, colors):
    m = max(len(c) for c in colors)  # 最大的颜色数量
    INF = float('inf')

    # 初始化 dp 和 path 数组
    dp = [[INF] * m for _ in range(n)]
    path = [[-1] * m for _ in range(n)]
    for j in range(len(colors[0])):
        dp[0][j] = 0

    # 动态规划
    for i in range(1, n):
        for j in range(len(colors[i])):
            for k in range(len(colors[i - 1])):
                cost = calculate_cost(colors[i][j], colors[i - 1][k])
                # cost = 1 if colors[i][j] != colors[i - 1][k] else 0
                if dp[i][j] > dp[i - 1][k] + cost:
                    dp[i][j] = dp[i - 1][k] + cost
                    path[i][j] = k

    # 找到最小的 cost 和对应的颜色
    min_cost = min(dp[-1])
    min_index = dp[-1].index(min_cost)

    # 回溯找到整个路径
    color_path = [0] * n
    color_path[-1] = colors[-1][min_index]
    for i in range(n - 1, 0, -1):
        min_index = path[i][min_index]
        color_path[i - 1] = colors[i - 1][min_index]

    return min_cost, color_path


def second_best_solution_with_exclusion(n, colors, excluded_path):
    m = max(len(c) for c in colors)
    INF = float('inf')

    # 初始化 dp 和 path 数组
    dp = [[INF] * m for _ in range(n)]
    path = [[-1] * m for _ in range(n)]

    for j in range(len(colors[0])):
        dp[0][j] = 0

    # 动态规划找到最优解
    for i in range(1, n):
        for j in range(len(colors[i])):
            for k in range(len(colors[i - 1])):
                cost = calculate_cost(colors[i][j], colors[i - 1][k])

                # cost = 1 if colors[i][j] != colors[i - 1][k] else 0
                if dp[i][j] > dp[i - 1][k] + cost:
                    dp[i][j] = dp[i - 1][k] + cost
                    path[i][j] = k

    # 回溯找到最优路径
    best_cost = min(dp[-1])
    best_index = dp[-1].index(best_cost)
    best_path = [0] * n
    best_path[-1] = colors[-1][best_index]
    for i in range(n - 1, 0, -1):
        best_index = path[i][best_index]
        best_path[i - 1] = colors[i - 1][best_index]

    # 如果最优路径是��允许的路径，设置其cost为无穷大
    if best_path in excluded_path:
        best_cost = INF

    # 对于每一步，尝试改变一个颜色选择
    second_best_cost = INF
    second_best_path = None
    for i in range(n):
        for j in colors[i]:
            if j != best_path[i]:
                temp_path = best_path.copy()
                temp_path[i] = j
                temp_cost = sum(calculate_cost(temp_path[k], temp_path[k - 1]) for k in range(1, n) if
                                temp_path[k] != temp_path[k - 1])
                # 如果这个路径是不允许的路径，设置其cost为无穷大
                if temp_path in excluded_path:
                    temp_cost = INF
                if temp_cost < second_best_cost:
                    second_best_cost = temp_cost
                    second_best_path = temp_path

    return second_best_cost, second_best_path


def extract_digits(num):
    # 获取千位
    thousand = (num // 1000) % 10
    # 获取百位
    hundred = (num // 100) % 10
    # 获取后两位
    last_two = num % 100

    return thousand, hundred, last_two


def calculate_cost(a, b):
    a_building, a_stair, a_room = extract_digits(a)
    b_building, b_stair, b_room = extract_digits(b)
    if a_building == 9 or b_building == 9:
        return 30
    if a_building != b_building:
        return 10 + a_stair + b_stair + 1
    if a_stair == 9 or b_stair == 9:
        return 15
    if a_stair != b_stair:
        return abs(a_stair - b_stair) + 1

    if a_room != b_room:
        return 1
    else:
        return 0


# 示例

def num_to_class(num_list):
    temp_class_list = []
    for i in num_list:
        building, stair, room = extract_digits(i)
        temp_class_list.append(f"{building}-{stair}{str(room).zfill(2)}")
    return temp_class_list


def check_classroom(classrooms_list, exclude_set, num_building, excluded_path):
    n = len(classrooms_list)
    class_list_to_num = []
    for i in class_list:
        temp_list = []
        for j in i:
            temp = int(j.replace("-", ""))
            if temp in exclude_set:
                continue
            if num_building == 4 and ((temp // 1000) % 10) == num_building:
                temp_list.append(temp)
                continue
            elif num_building == 3 and ((temp // 1000) % 10) == num_building:
                temp_list.append(temp)
                continue
            elif num_building == 0:
                temp_list.append(temp)
                continue
        if len(temp_list) == 0:
            temp_list.append(9999)
            temp_list.append(4999)
            temp_list.append(3999)
        class_list_to_num.append(temp_list)
    colors = class_list_to_num
    result = []
    for i in range(300):
        random.shuffle(colors[0])

        min_cost, color_path = min_cost_with_path(n, colors)
        result.append([min_cost, num_to_class(color_path)])

    for i in range(1, 512):
        random.shuffle(colors[0])
        try:
            second_best_cost, color_path = second_best_solution_with_exclusion(n, colors, excluded_path)
            excluded_path.append(color_path)
            result.append([second_best_cost, num_to_class(color_path)])
        except:
            continue
    return result, excluded_path


def remove_duplicates(data):
    seen = set()
    result = []
    for item in data:
        # 将子列表的第二个元素（即另一个列表）转换为元组，因为元组是可哈希的
        t = (item[0], tuple(item[1]))
        if t not in seen:
            seen.add(t)
            result.append(item)
    return result


def draw_table(ax, data, start_col):
    N, M = len(data), len(data[0][1])
    time_data = ["08:00-08:45", "08:50-09:35", "09:50-10:35",
                 "10:40-11:25", "11:30-12:15", "13:00-13:45",
                 "13:50-14:35", "14:45-15:30", "15:40-16:25",
                 "16:35-17:20", "17:25-18:10", "18:30-19:15",
                 "19:20-20:05", "20:10-20:55"][-1 * M:]

    # 设置坐标轴不可见
    ax.axis('off')
    ax.grid('off')

    # 使用table方法创建一个表格
    table_data = [[''] + list(range(start_col, start_col + N))]
    for i in range(M):
        row_data = [time_data[i]]
        for j in range(N):
            row_data.append(data[j][1][i])
        table_data.append(row_data)
    cell_colors = [['#ffffff' for _ in range(N + 1)] for _ in range(M + 1)]
    ax.margins(x=0)
    ax.table(cellText=table_data, cellLoc='center', cellColours=cell_colors, colWidths=[0.1] * (N + 1),
             bbox=[0, 0, 1, 1])
    ax.set_position([0.0, 0.0, 1.0, 1.0])


def generate_image(data, name):
    # 获取数据的维度
    num_blocks = (len(data) + 9) // 10  # 计算需要多少块
    fig, axes = plt.subplots(num_blocks, 1, figsize=(10, 6 * num_blocks))
    plt.tight_layout(h_pad=0.1, w_pad=0.1, pad=0)

    # 如果只有一个块，确保axes是一个列表
    if num_blocks == 1:
        axes = [axes]

    for i, ax in enumerate(axes):
        start_idx = i * 10
        end_idx = start_idx + 10
        draw_table(ax, data[start_idx:end_idx], start_idx + 1)
    plt.margins(x=0)

    plt.subplots_adjust(hspace=0.05)
    # 保存图片
    plt.savefig(f"{name}.png", dpi=300, bbox_inches='tight', pad_inches=0.0)
    plt.show()


def count_empty_classrooms(classrooms_list):
    # 初始化一个字典来统计每个教室的出现次数
    count_dict = {}

    # 遍历每个时间段的空余教室列表
    for classrooms in classrooms_list:
        for classroom in classrooms:
            # 如果教室在字典中，增加其计数
            if classroom in count_dict:
                count_dict[classroom] += 1
            # 否则，初始化其计数为1
            else:
                count_dict[classroom] = 1

    # 从字典中筛选出出现次数大于2的教室
    frequent_classrooms = [classroom for classroom, count in count_dict.items() if count > 2]

    return frequent_classrooms


def get_class():
    r = requests.get("https://ec.jray.xyz/api").json()
    class_dict = r["class_list"]["1"]
    type_map = r["class_list"]["type_map"]
    total_class_list = []
    for time_slot in class_dict:
        class_time_slot = []
        for room, _ in time_slot:
            if ("教3" in room or "教4" in room) and "教室" in type_map[room]:
                class_time_slot.append(room.replace("教", ""))
        total_class_list.append(class_time_slot)
    return total_class_list


if __name__ == "__main__":
    ClassList = get_class()
    frequent_class = count_empty_classrooms(ClassList)
    print("Collect Info Done")
    ExcludeClassroomSet = {4414, 4421}
    for time_index in range(14):
        results = []
        excluded_path = []
        class_list = ClassList[time_index:]
        exclude_classroom_set = ExcludeClassroomSet
        for n_building in [3, 4, 0]:
            temp_result, temp_excluded_path = check_classroom(class_list, exclude_classroom_set, n_building, excluded_path)
            results.extend(temp_result)
            excluded_path.extend(temp_excluded_path)
        sorted_results = sorted(remove_duplicates(results), key=lambda x: x[0], reverse=True)
        sorted_results = list(reversed(sorted_results))[0:min(70, len(sorted_results) - 1)]
        generate_image(sorted_results, f"{time_data[time_index]}")
        send_image(f'./{time_data[time_index]}.png', chatId)
        for exclude_room in frequent_class:
            results = []
            excluded_path = []
            exclude_classroom_set = ExcludeClassroomSet
            exclude_classroom_set.add(int(exclude_room.replace("-","")))
            for n_building in [3, 4, 0]:
                temp_result, temp_excluded_path = check_classroom(class_list, exclude_classroom_set, n_building,
                                                                  excluded_path)
                results.extend(temp_result)
                excluded_path.extend(temp_excluded_path)
            sorted_results = sorted(remove_duplicates(results), key=lambda x: x[0], reverse=True)
            sorted_results = list(reversed(sorted_results))[0:min(30, len(sorted_results) - 1)]
            generate_image(sorted_results, f"{time_data[time_index].split("-")[0].replace(":","-")}_{exclude_room}")
            send_image(f'./{time_data[time_index]}_{exclude_room}.png', chatId)
