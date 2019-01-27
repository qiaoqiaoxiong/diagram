import re


class DataItem:
    def __init__(self):
        self.ticket = ""
        self.act = -1
        self.success = False
        self.msg = ""
        self.cost = .0


class User:
    def __init__(self):
        self.ticket = ""
        self.starting_download_uab = False
        self.download_step = 0
        self.download_success_count = 0
        self.download_failed = False
        self.download_uab_part_time = .0
        self.finish_download_uab = False
        self.download_uab_time = .0
        self.cdn_switch = False

        self.starting_decompress = False
        self.decompress_cost = .0
        self.decompress_20_cost = .0
        self.decompress_step = 0
        self.decompress_finish = False
        self.enter_game = False

    def update(self, data_item):
        if data_item.act == 90:
            self.starting_download_uab = True
            self.download_step += 1
            is_success = int(data_item.msg.split(",")[0])
            if is_success == 1:
                self.download_success_count += 1
                self.download_uab_part_time += data_item.cost
        elif data_item.act == 100:
            self.starting_decompress = True
            self.decompress_step = int(data_item.msg)
            if self.decompress_step == 20:
                self.decompress_20_cost = data_item.cost
        elif data_item.act == 12:
            self.cdn_switch = True
        elif data_item.act == 9:
            if data_item.success:
                self.finish_download_uab = True
                self.download_uab_time = data_item.cost
        elif data_item.act == 14:
            self.enter_game = True
        elif data_item.act == 10:
            self.decompress_cost = data_item.cost
            self.decompress_finish = data_item.success


class DataAnalysis:
    def __init__(self):
        self.data = []
        self.users = {}

    def load_data(self, file):
        f = open(file)  # 返回一个文件对象
        f.readline()  # 调用文件的 readline()方法
        line = f.readline()
        line_num = 1
        while line:
            line_num = line_num + 1
            items = re.findall('"([^"]*)"', line)
            data_item = DataItem()
            data_item.ticket = items[0]
            data_item.act = int(items[8])
            data_item.success = bool(items[9])
            data_item.msg = items[10]
            data_item.cost = float(items[11])
            self.data.append(data_item)

            line = f.readline()

        print("数据总行数:" + str(line_num))
        f.close()

    def user_count(self):
        ticket = set()
        for item in self.data:
            ticket.add(item.ticket)

        return len(ticket)

    def analyze(self):
        for item in self.data:
            if item.ticket in self.users:
                self.users[item.ticket].update(item)
            else:
                user = User()
                user.update(item)
                self.users[item.ticket] = user

    def user_count(self):
        return len(self.users)

    def start_decompress_uab_count(self):
        count = 0
        for user in self.users.values():
            if user.starting_decompress:
                count += 1

        return count

    def start_download_uab_count(self):
        count = 0
        for user in self.users.values():
            if user.starting_download_uab:
                count += 1

        return count

    def quit_on_cdn_switch(self):
        count = 0
        for user in self.users.values():
            if user.cdn_switch and not user.finish_download_uab:
                count += 1

        return count

    def success_cdn_switch(self):
        count = 0
        for user in self.users.values():
            if user.cdn_switch and user.finish_download_uab:
                count += 1

        return count

    def finish_download_uab_count(self):
        count = 0
        for user in self.users.values():
            if user.finish_download_uab:
                count += 1

        return count

    def average_download_uab_time_cost(self):
        count = 0
        time_cost = .0
        min_cost = 1000000000.0
        max_cost = .0
        for user in self.users.values():
            if user.finish_download_uab:
                if user.download_uab_time < 50:
                    continue
                count += 1
                time_cost += user.download_uab_time
                min_cost = min(min_cost, user.download_uab_time)
                max_cost = max(max_cost, user.download_uab_time)

        return time_cost/count, min_cost, max_cost

    def enter_game_count(self):
        count = 0
        for user in self.users.values():
            if user.enter_game:
                count += 1

        return count

    def download_uab_failed(self):
        count = 0
        for user in self.users.values():
            if not user.finish_download_uab:
                count += 1

        return count

    def download_success_count(self, threshold):
        count = 0
        time_cost = 0
        for user in self.users.values():
            if not user.finish_download_uab and user.download_success_count == threshold:
                count += 1
                time_cost += user.download_uab_part_time

        return count, '%.2f' % (time_cost/max(count, 1))

    def download_file_count(self, threshold):
        count = 0
        for user in self.users.values():
            if not user.finish_download_uab and user.download_step <= threshold:
                count += 1

        return count

    def download_file_giveup(self):
        count = 0
        for user in self.users.values():
            if not user.finish_download_uab and user.download_step <= 2 and not user.cdn_switch:
                count += 1

        return count

    def decompress_finish(self):
        count = 0
        for user in self.users.values():
            if user.decompress_finish:
                count += 1

        return count

    def decompress_time(self):
        count = 0
        average_time = 0
        max_time = 0
        min_time = 1000000000
        for user in self.users.values():
            if user.decompress_finish:
                count += 1
                average_time += user.decompress_cost
                min_time = min(min_time, user.decompress_cost)
                max_time = max(max_time, user.decompress_cost)

        return average_time/count, min_time, max_time

    def decompress_20_time(self):
        count = 0
        average_time = 0
        max_time = 0
        min_time = 1000000000
        for user in self.users.values():
            if user.starting_decompress:
                count += 1
                average_time += user.decompress_20_cost
                min_time = min(min_time, user.decompress_20_cost)
                max_time = max(max_time, user.decompress_20_cost)

        return average_time/count, min_time, max_time


if __name__ == '__main__':
    analysis = DataAnalysis()
    analysis.load_data("data.csv")
    analysis.analyze()
    print("进入玩家总数:" + str(analysis.user_count()))
    print("开始下载uab人数:" + str(analysis.start_download_uab_count()))
    print("下载uab完成人数:" + str(analysis.finish_download_uab_count()))
    print("解压到20%成功人数", analysis.start_decompress_uab_count())
    print("解压uab完成人数:", analysis.decompress_finish())
    print("进入游戏人数:" + str(analysis.enter_game_count()))

    print("下载uab失败人数:" + str(analysis.download_uab_failed()))
    print("下载uab成功的玩家平均,最短，最长时间（/s）:" + str(analysis.average_download_uab_time_cost()))

    print("cdn切换失败下载失败人数:" + str(analysis.quit_on_cdn_switch()))
    print("cdn切换成功下载成功人数:" + str(analysis.success_cdn_switch()))
    print("解压uab平均，最短，最长时间（/s）", analysis.decompress_time())
    print("一开始下载uab就流失的玩家（第一个uab都没下完）", analysis.download_file_count(2))
    print("没有发生cdn切换，uab一个都没下载完的玩家", analysis.download_file_giveup())
    print(analysis.decompress_20_time())

    for i in range(0, 60):
        print("流失玩家中成功下载uab个数为" + str(i) + "的人数及下载平均耗时" + str(analysis.download_success_count(i)))

