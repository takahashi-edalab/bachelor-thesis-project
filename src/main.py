import math
import argparse
from decimal import Decimal
from numpy.random import default_rng
from routing import entities
from src import algos, vis


def get_args():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--seed", "-s", type=int, default=0, help="random seed")
    parser.add_argument(
        "--n_nets", "-n", type=int, default=100, help="the number of nets"
    )
    parser.add_argument(
        "--scenario", "-c", type=int, default=1, choices=[1, 2], help="scenario"
    )
    parser.add_argument("--gap_width", "-w", type=float, default=None, help="gap width")
    parser.add_argument(
        "--gap_interval", "-i", type=float, default=10, help="gap interval"
    )
    args = parser.parse_args()
    return args


def generate_netlist(args) -> list:
    rg = default_rng(args.seed)
    # 各ネットの横幹線の左端と右端をランダムに生成
    minx_maxx_list = rg.random((args.n_nets, 2))

    # ネットの幅の分布が違うシナリオ
    if args.scenario == 1:
        # 単一幅が多いケース(比較的簡単)
        width_prob = {
            1: 0.8,
            2: 0.1,
            3: 0.08,
            4: 0.02,
        }
    elif args.scenario == 2:
        # 太い幅が多いケース(比較的大変？)
        width_prob = {
            1: 0.5,
            2: 0.3,
            3: 0.15,
            4: 0.05,
        }
    else:
        raise ValueError("Invalid Dataset Type")

    # 上記の幅の確率分布に従い生成
    widths = rg.choice(
        list(width_prob.keys()), size=args.n_nets, p=list(width_prob.values())
    )
    # 配線するネット集合を作成
    netlist = entities.NetList()
    for i, ((minx, maxx), width) in enumerate(zip(minx_maxx_list, widths)):
        n = entities.Net(
            name=f"{i}",
            pins=[
                entities.Pin(x=Decimal(f"{minx}"), y=Decimal("0.0")),
                entities.Pin(x=Decimal(f"{maxx}"), y=Decimal("0.0")),
            ],
            width=Decimal(f"{width}"),
        )
        netlist.append(n)
    return netlist


def main():
    args = get_args()
    netlist = generate_netlist(args)
    le_gaps = algos.left_edge(netlist, args)
    # 以下の関数を改良しよう
    proposal_gaps = algos.proposed_algorithm(netlist, args)

    # 結果比較
    print("Input")
    print(f"  - #nets        : {args.n_nets}")
    print(f"  - Density      : {netlist.max_density()}")
    print("Lower Bound")
    if args.gap_width is None:
        # 配線領域が1つの場合
        print(f"  - #gaps used   : {1}")
        print("=" * 30)
        print(f"Left Edge: {le_gaps[0].max_height_range():3}")
        print(f"Proposal: {proposal_gaps[0].max_height_range():3}")

        vis.plot_single_gap(le_gaps[0], proposal_gaps[0])
    else:
        # 配線領域が複数ある場合
        print(
            f"  - #gaps used   : {math.ceil(netlist.max_density() / Decimal(f'{args.gap_width}'))}"
        )
        print("=" * 30)
        print(f"Left Edge: {len(le_gaps):3}")
        print(f"Proposal: {len(proposal_gaps):3}")
        vis.plot_multiple_gaps(le_gaps, proposal_gaps)


if __name__ == "__main__":
    main()
