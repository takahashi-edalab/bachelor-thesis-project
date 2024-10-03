from decimal import Decimal
from routing import entities


def left_edge(netlist: entities.NetList, args) -> list[entities.Gap]:
    gaps = []
    # 各ネットの左端が小さい順に並び替える
    sorted_netlist = sorted(netlist, key=lambda x: x.minx)

    # 未配線ネットがなくなるまで繰り返す
    i = 0
    while sorted_netlist:
        if args.gap_width is None:
            gap_base_height = 0
        else:
            gap_base_height = (i + 1) * args.gap_interval + i * args.gap_width
        gap = entities.Gap(
            sorted_netlist, width=args.gap_width, base_height=gap_base_height
        )
        gaps.append(gap)
        i += 1

        while True:
            # 基準線は最初左に無限大の位置から
            x = Decimal(float("-inf"))
            remove_nets = []
            for n in sorted_netlist:
                # 基準線よりも右側にあり, かつ配線領域内に収まるように配線できる場合には配線
                if x < n.minx and gap.is_assignable(n):
                    gap.assign(n)
                    # 配線したネットの右端に基準線を移動
                    x = n.maxx
                    remove_nets.append(n)

            # 配線できるネットがなかったので, 次の配線領域へ
            if remove_nets == []:
                break

            # 配線したnetは全て削除
            for n in remove_nets:
                sorted_netlist.remove(n)
    return gaps


def proposed_algorithm(netlist: entities.NetList, args) -> list[entities.Gap]:
    """この関数を改良してLeft Edgeに勝とう!!

    Args:
        netlist (entities.Netlist): 入力ネット集合
        args (list[entiites.Gap]): 配線領域幅等の情報がある

    Returns:
        list[entities.Gap]: 配線された配線領域リスト
    """
    # gap = 配線領域
    gaps = []

    # ポイント1: 何を基準に優先して検討する？
    sorted_netlist = sorted(netlist, key=lambda x: x)

    # 未配線ネットがなくなるまで繰り返す
    i = 0
    while sorted_netlist:
        if args.gap_width is None:
            gap_base_height = 0
        else:
            gap_base_height = (i + 1) * args.gap_interval + i * args.gap_width
        gap = entities.Gap(
            sorted_netlist, width=args.gap_width, base_height=gap_base_height
        )
        gaps.append(gap)
        i += 1

        while True:
            # 基準線は最初左に無限大の位置から
            x = Decimal(float("-inf"))
            remove_nets = []
            for n in sorted_netlist:
                # ポイント2:
                # 左から右に単純に配線するだけでいい？
                # 他になにか入力の特徴は使えないか？
                if x < n.minx and gap.is_assignable(n):
                    gap.assign(n)
                    # 配線したネットの右端に基準線を移動
                    x = n.maxx
                    remove_nets.append(n)

            # 配線できるネットがなかったので, 次の配線領域へ
            if remove_nets == []:
                break

            # 配線したnetは全て削除
            for n in remove_nets:
                sorted_netlist.remove(n)
    return gaps
