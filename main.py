# -*- coding:utf-8 -*-
import json
import os

import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup


def init():
    url = 'https://play4stats.com/wot/asia/top/server/?lang=en'
    txtfile = 'html.txt'
    jsonfile = 'json.txt'
    # print(strhtml.text)
    strhtml = ''

    if not os.path.exists(txtfile):
        strhtml = requests.get(url).text  # Get方式获取网页数据
        f = open(txtfile, 'w', encoding='utf8')
        f.write(strhtml)
        f.close()
        print("save html successfully")
    else:
        f = open(txtfile, 'r', encoding='utf8')
        strhtml = f.read()
        f.close()
        print("read html from local")

    data_list = []
    if not os.path.exists(jsonfile):

        soup = BeautifulSoup(strhtml, 'html.parser')
        data = soup.select('#content > section > div.table_wrapper > table > tbody')[0]
        for tr in data:
            tds = tr.find_all('td')
            data_list.append({
                'Nation': tds[0].contents[1].contents[0].strip(),
                'Type': tds[2].contents[0].strip(),
                'Name': tds[3].contents[0].strip(),
                'Level': int(tds[4].contents[0].strip()),
                'WinRate': float(tds[7].contents[0].strip().strip('%')) / 100.0,
                'AvgDamage': int(float(tds[9].contents[1].contents[0].strip()))
            })

        f = open(jsonfile, 'w', encoding='utf8')
        f.write(json.dumps(data_list))
        f.close()
        print("save json successfully")
    else:
        f = open(jsonfile, 'r', encoding='utf8')
        data_list = eval(f.read())
        f.close()
        print("read json from local")

    return data_list


def rank(list, rank=8):
    filted = []
    for item in list:
        if item.get('WinRate') >= 0.5:
            if rank == item.get('Level'):
                filted.append(item)
    # df = pd.DataFrame(filted)
    # df.to_excel(str(rank) + '.xlsx', index=False)

    rate = []
    damage = []
    name = []
    color = []
    type_color = {
        'Light Tank': 'green',
        'Medium Tank': 'yellow',
        'Heavy Tank': 'grey',
        'SPG': 'red',
        'Tank Destroyer': 'blue'
    }
    for item in filted:
        rate.append(item.get('WinRate'))
        d = item.get('AvgDamage')
        damage.append(d)
        name.append(item.get('Name'))
        color.append(type_color.get(item.get('Type')))

    # plt.style.use('seaborn')
    fig = plt.figure(figsize=(10, 50))
    # pltfig(fig)
    s = [n ** 2 / 1000 for n in damage]

    # y 的值归一化到[0, 1]
    # 因为 y 大到一定程度超过临界数值后颜色就会饱和不变(不使用循环colormap)。
    norm = plt.Normalize(min(rate), max(rate))
    # matplotlib.colors.Normalize 对象，可以作为参数传入到绘图方法里
    # 也可给其传入数值直接计算归一化的结果
    norm_y = norm(rate)

    plt.scatter(rate, damage, c=color, s=s, edgecolor='black', cmap='rainbow_r', alpha=0.9)
    # cbar = plt.colorbar()

    for i in range(len(name)):
        plt.annotate(name[i], xy=(rate[i], damage[i]),
                     xytext=(0, -5), textcoords='offset points')  # 这里xy是需要标记的坐标，xytext是对应的标签坐标

    plt.xlim(0.48, 0.6)
    plt.ylim(int(min(damage) / 100) * 100, int(max(damage) / 100) * 100 + 100)  # 10
    plt.xlabel("Win Rate", fontdict={'size': 16})
    plt.ylabel("Avg Damage", fontdict={'size': 16})
    plt.title('Level ' + str(rank) + ' Rank List', fontdict={'size': 20})
    # plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    # plt.text(x=0.5, y=damage_max / 2, s="葛炮未来", fontsize=100,
    #          color="gray", alpha=0.6)
    plt.grid(axis="x", which="major")
    plt.savefig('fig' + str(rank) + '.png')
    # a = [np.linspace(0, 1, 1600)] * 5000
    # fig.figimage(a, cmap=plt.get_cmap('rainbow_r'), alpha=0.2)
    # plt.show()


if __name__ == '__main__':
    data_list = init()
    rank(data_list, 8)
    rank(data_list, 9)
    rank(data_list, 10)
