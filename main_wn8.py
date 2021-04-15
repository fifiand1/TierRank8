# -*- coding:utf-8 -*-
import json
import os

import matplotlib.pyplot as plt
import pandas as pd
import requests
from bs4 import BeautifulSoup

from enum import Enum


class RankType(Enum):
    # 为序列值指定value值
    All = 1
    GoldOnly = 2
    SilverOnly = 3


realm = 'ru'
type_color = {
    'LT': 'green',
    'MT': '#fff447',
    'HT': '#737373',
    'SPG': 'red',
    'TD': '#0a8fff'
}
wn8_color = {
    'dred': '#BAAAAD',
    'red': '#f11919',
    'orange': '#ff8a00',
    'yellow': '#e6df27',
    'green': '#77e812',
    'dgreen': '#459300',
    'blue': '#2ae4ff',
    'dblue': '#00a0b8',
    'purple': '#c64cff',
    'dpurple': '#8225ad'
}


def init():
    url = 'https://wotlabs.net/' + realm + '/tankStats'
    txtfile = realm + 'html_wn8.txt'
    jsonfile = realm + 'json_wn8.txt'
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
        data = soup.select('#serverTankStats > tbody')[0]
        for tr in data:
            try:
                tds = tr.find_all('td')
                is_gold = len(tds[0].contents) == 3
                data_list.append({
                    'Nation': tds[1].contents[0].strip(),
                    'Gold': is_gold,
                    'Type': tds[2].contents[0].strip(),
                    'Name': tds[0].contents[1].strip(),
                    'Level': int(tds[3].contents[0].strip()),
                    'WinRateColor': tds[7].attrs.get('class')[0],
                    'WinRate': float(tds[7].contents[0].strip().strip('%')) / 100.0,
                    'WN8Color': tds[8].attrs.get('class')[0],
                    'WN8': int(tds[8].contents[0].strip())
                })
            except AttributeError as e:
                print('except:', e)

        f = open(jsonfile, 'w', encoding='utf8')
        f.write(json.dumps(data_list))
        f.close()
        print("save json successfully")
    else:
        f = open(jsonfile, 'r', encoding='utf8')
        false = False
        true = True
        data_list = eval(f.read())
        f.close()
        print("read json from local")

    return data_list


def rank(list, rank=[8], is_gold=RankType.All, paichu=None, tank_type=None):
    if tank_type is None:
        tank_type = ['LT', 'MT', 'HT', 'TD', 'SPG']
    if paichu is None:
        paichu = ['Chimera']
    filtered = []
    for item in list:
        if item.get('WN8') >= 1000 \
                and item.get('WinRate') >= 0.5 \
                and item.get('Level') in rank \
                and item.get('Type') in tank_type \
                and item.get('Name') not in paichu:
            if is_gold == RankType.GoldOnly:
                if item.get('Gold'):
                    filtered.append(item)
            if is_gold == RankType.SilverOnly:
                if not item.get('Gold'):
                    filtered.append(item)
            else:
                filtered.append(item)

    tank_gold_type = '_All'
    if is_gold == RankType.GoldOnly:
        tank_gold_type = '_G'
    if is_gold == RankType.SilverOnly:
        tank_gold_type = '_S'

    title = realm.upper() + ' Level ' + str(rank) + ' ' + '_'.join(tank_type) + tank_gold_type

    df = pd.DataFrame(filtered)
    df.to_excel(title + '_wn8.xlsx', index=False)

    rate = []
    damage = []
    name = []
    color = []
    edge_color = []

    for item in filtered:
        rate.append(item.get('WinRate'))
        d = item.get('WN8')
        damage.append(d)
        name.append(item.get('Name'))
        color.append(wn8_color.get(item.get('WN8Color')))
        edge_color.append(type_color.get(item.get('Type')))

    # plt.style.use('seaborn')
    fig = plt.figure(figsize=(20, 60))
    # pltfig(fig)
    s = [n ** 2 / 1000 for n in damage]

    # y 的值归一化到[0, 1]
    # 因为 y 大到一定程度超过临界数值后颜色就会饱和不变(不使用循环colormap)。
    norm = plt.Normalize(min(rate), max(rate))
    # matplotlib.colors.Normalize 对象，可以作为参数传入到绘图方法里
    # 也可给其传入数值直接计算归一化的结果
    norm_y = norm(rate)

    plt.scatter(rate, damage, c=edge_color, s=s, linewidths=5, edgecolor=color, cmap='rainbow_r', alpha=1)
    # cbar = plt.colorbar()

    for i in range(len(name)):
        plt.annotate(
            # str(damage[i])+'\n'+
            name[i] + str('★' if filtered[i].get('Gold') else ''), xy=(rate[i], damage[i]),
            xytext=(-5, -5), textcoords='offset points')  # 这里xy是需要标记的坐标，xytext是对应的标签坐标

    plt.xlim(min(rate) - 0.01, max(rate) + 0.01)
    plt.ylim(int(min(damage) / 100) * 100, int(max(damage) / 100) * 100 + 100)  # 10
    plt.xlabel("Win Rate", fontdict={'size': 16})
    plt.ylabel("WN8 Rate", fontdict={'size': 16})
    plt.title(title + ' WN8 Rank List', fontdict={'size': 20})
    # plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    # plt.text(x=0.5, y=damage_max / 2, s="葛炮未来", fontsize=100,
    #          color="gray", alpha=0.6)
    plt.grid(axis="x", which="major")
    plt.savefig(title + '_wn8.png')
    # a = [np.linspace(0, 1, 1600)] * 5000
    # fig.figimage(a, cmap=plt.get_cmap('rainbow_r'), alpha=0.2)
    # plt.show()


if __name__ == '__main__':
    data_list = init()
    # rank(data_list, 8, tank_type=['LT'], is_gold=True)
    # rank(data_list, 8, tank_type=['TD'], is_gold=True)
    # rank(data_list, 8, tank_type=['MT'], is_gold=True)
    # rank(data_list, 8, tank_type=['HT'], is_gold=True)
    # rank(data_list, [8, 9, 10], tank_type=['HT', 'MT', 'TD'], is_gold=False)
    # rank(data_list, [6], tank_type=['LT', 'HT', 'MT', 'TD'], is_gold=False)
    rank(data_list, [7], tank_type=['LT', 'HT', 'MT', 'TD', 'SPG'], is_gold=RankType.All)
    rank(data_list, [8], tank_type=['LT', 'HT', 'MT', 'TD', 'SPG'], is_gold=RankType.All)
    rank(data_list, [9], tank_type=['LT', 'HT', 'MT', 'TD', 'SPG'], is_gold=RankType.All)
    rank(data_list, [10], tank_type=['LT', 'HT', 'MT', 'TD', 'SPG'], is_gold=RankType.All)

    rank(data_list, [8], tank_type=['LT', 'HT', 'MT', 'TD', 'SPG'], is_gold=RankType.GoldOnly)

    rank(data_list, [8], tank_type=['LT', 'HT', 'MT', 'TD', 'SPG'], is_gold=RankType.SilverOnly)
    rank(data_list, [9], tank_type=['LT', 'HT', 'MT', 'TD', 'SPG'], is_gold=RankType.SilverOnly)
    rank(data_list, [10], tank_type=['LT', 'HT', 'MT', 'TD', 'SPG'], is_gold=RankType.SilverOnly)
    #
    # rank(data_list, 6, tank_type=['MT', 'HT'], is_gold=False)
    # rank(data_list, 7, tank_type=['MT', 'HT'], is_gold=False)
    # rank(data_list, 8, tank_type=['TD'], is_gold=False)
    # rank(data_list, 8, tank_type=['LT'], is_gold=False)
    # rank(data_list, 8, tank_type=['MT'], is_gold=False)
    # rank(data_list, 8, tank_type=['HT'], is_gold=False)
    # #
    # rank(data_list, 9, tank_type=['TD'], is_gold=False)
    # rank(data_list, 9, tank_type=['LT'], is_gold=False)
    # rank(data_list, 9, tank_type=['MT'], is_gold=False)
    # rank(data_list, 9, tank_type=['HT'], is_gold=False)
    # #
    # rank(data_list, 10, tank_type=['LT'], is_gold=False)
    # rank(data_list, 10, tank_type=['MT'], is_gold=False)
    # rank(data_list, 10, tank_type=['HT'], is_gold=False)
    # rank(data_list, 10, tank_type=['TD'], is_gold=False)
    # rank(data_list, 10, is_gold=False)
