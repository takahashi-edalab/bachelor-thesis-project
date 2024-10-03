from routing import entities
from decimal import Decimal
import matplotlib.pyplot as plt


def plot_single_gap(le_g: entities.Gap, proposal_g: entities.Gap) -> None:
    plt.rcParams["font.size"] = 10
    fig, axs = plt.subplots(2, 1, figsize=(8, 10), dpi=100)

    for i, g in enumerate([le_g, proposal_g]):
        al = []
        for v in g.assignments.values():
            al.extend(v)
        al = list(set(al))
        nl = entities.NetList([a.net for a in g.net2assignment.values()])

        for a in al:
            # left-bottom, right-top
            width = a.net.maxx - a.net.minx
            bottom_height = a.max_height - a.net.width

            rect = plt.Rectangle(
                (a.net.minx, bottom_height),
                width,
                a.net.width,
                linewidth=0.2,
                edgecolor="black",
                facecolor="blue",
            )
            axs[i].add_patch(rect)

            # 最大混雑度
            zones = nl.max_density_zones()
            for z in zones:
                axs[i].axvline(z[0], color="red", linestyle=":", linewidth=10.0)
                axs[i].axvline(z[1], color="red", linestyle=":", linewidth=10.0)

        margin = Decimal("0.01")

        maxy = max(float(le_g.max_height_range()), float(proposal_g.max_height_range()))
        axs[i].set_xlim(min(g.x_coords) - margin, max(g.x_coords) + margin)
        plt.xticks([0, 1])
        axs[i].set_ylim(0, maxy)
        plt.yticks([0, maxy])

    plt.tight_layout()
    plt.show()


# 図のサイズを設定
def plot_multiple_gaps(
    le_gaps: list[entities.Gap], proposal_gaps: list[entities.Gap]
) -> None:
    fig, axs = plt.subplots(2, 1, figsize=(8, 10), dpi=100)

    if len(le_gaps) > len(proposal_gaps):
        gaps = le_gaps
    else:
        gaps = proposal_gaps
    # gap
    for ax in axs:
        for g in gaps:
            miny = g.base_height
            ax.add_patch(
                plt.Rectangle(
                    (0, miny),
                    width=1,
                    height=g.width,
                    color="lightgray",
                )
            )

    # assignment nets
    for gaps, ax in zip([le_gaps, proposal_gaps], axs):
        for g in gaps:
            for a in g.net2assignment.values():
                n = a.net
                miny = g.base_height + a.max_height - n.width
                ax.add_patch(
                    plt.Rectangle(
                        (n.minx, miny),
                        width=n.maxx - n.minx,
                        height=n.width,
                        color="blue",
                    )
                )

    # set axis limit
    sort_gaps = sorted(le_gaps, key=lambda x: x.base_height)
    c = sort_gaps[0]
    minx, maxx = c.x_coords[0], c.x_coords[-1]
    miny, maxy = sort_gaps[0].base_height, sort_gaps[-1].base_height + c.width

    for ax in axs:
        ax.set_xlim(minx, maxx)
        ax.set_ylim(miny, maxy + 10)

    plt.tight_layout()
    plt.show()
