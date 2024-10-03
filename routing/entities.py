from decimal import Decimal
from dataclasses import dataclass, field
from functools import cached_property
from collections import defaultdict, UserList
import bisect


@dataclass(frozen=True, order=True)
class Pin:
    x: Decimal
    y: Decimal

    def __repr__(self) -> str:
        return f"Pin: ({self.x}, {self.y})"

    def dict(self) -> dict:
        return dict(x=str(self.x), y=str(self.y))


@dataclass(frozen=True, order=True)
class Net:
    name: str
    pins: list[Pin] = field(default_factory=list, compare=False)
    width: Decimal = field(default=None, compare=False)

    @property
    def x(self) -> list[Decimal]:
        return [p.x for p in self.pins]

    @property
    def y(self) -> list[Decimal]:
        return [p.y for p in self.pins]

    @property
    def n_pins(self) -> int:
        return len(self.pins)

    @cached_property
    def minx(self) -> Decimal:
        return min([p.x for p in self.pins])

    @cached_property
    def maxx(self) -> Decimal:
        return max([p.x for p in self.pins])

    @cached_property
    def miny(self) -> Decimal:
        return min([p.y for p in self.pins])

    @cached_property
    def mid_bottom_y(self) -> Decimal:
        n_pins = len(self.pins)
        sorted_pins = sorted(self.pins, key=lambda p: p.y)
        mid_btm_y = 0
        if not n_pins % 2 == 0:
            bu = n_pins // 2 + 1
            m = sorted_pins[bu - 1]
            mid_btm_y = m.y
        else:
            b = n_pins // 2
            bottom_pin = sorted_pins[b - 1]
            mid_btm_y = bottom_pin.y
        return mid_btm_y

    @cached_property
    def mid_upper_y(self) -> Decimal:
        n_pins = len(self.pins)
        sorted_pins = sorted(self.pins, key=lambda p: p.y)
        mid_up_y = 0
        if not n_pins % 2 == 0:
            bu = n_pins // 2 + 1
            m = sorted_pins[bu - 1]
            mid_up_y = m.y
        else:
            u = n_pins // 2 + 1
            upper_pin = sorted_pins[u - 1]
            mid_up_y = upper_pin.y
        return mid_up_y

    @cached_property
    def midy(self) -> Decimal:
        mid_y = (self.mid_bottom_y + self.mid_upper_y) / 2
        return mid_y

    @cached_property
    def maxy(self) -> Decimal:
        return max([p.y for p in self.pins])

    @property
    def horizontal_wirelength(self) -> Decimal:
        return self.maxx - self.minx

    def vertical_wirelength(self, given_midy=None) -> Decimal:
        if given_midy is None:
            given_midy = self.midy

        ans = 0
        for p in self.pins:
            ans += abs(p.y - given_midy)
        return ans

    def __repr__(self) -> str:
        return self.name


class NetList(UserList):
    def horizontal_wirelength(self) -> Decimal:
        if self.data == []:
            return 0
        hwl = sum([n.horizontal_wirelength for n in self.data])
        return hwl

    def vertical_wirelength(self) -> Decimal:
        if self.data == []:
            return 0
        vwl = sum([n.vertical_wirelength() for n in self.data])
        return vwl

    def n_pins(self) -> int:
        if self.data == []:
            return 0
        n_p = sum([n.n_pins for n in self.data])
        return n_p

    def sum_height(self, nl: list) -> Decimal:
        total = sum([n.width for n in nl])
        return total

    def max_density(self):
        diff_density = defaultdict(list)
        for n in self.data:
            diff_density[n.minx].append((n, "add"))
            diff_density[n.maxx].append((n, "remove"))

        _max_density = 0
        overlapped_nets = []
        # sort via key
        for k, nl in sorted(diff_density.items(), key=lambda k: k[0]):
            for t in nl:
                net, command = t
                if command == "add":
                    overlapped_nets.append(net)
                else:
                    overlapped_nets.remove(net)

            if overlapped_nets == []:
                continue
            density = self.sum_height(overlapped_nets)
            if command == "add":
                if _max_density < density:
                    _max_density = density
        return _max_density

    def max_density_zones(self) -> list[tuple]:
        diff_density = defaultdict(list)
        for n in self.data:
            diff_density[n.minx].append((n, "add"))
            diff_density[n.maxx].append((n, "remove"))

        max_density = 0
        start_x = None
        zones = []
        overlapped_nets = []
        # sort via key
        for k, nl in sorted(diff_density.items(), key=lambda k: k[0]):
            # print(k)
            for t in nl:
                net, command = t
                if command == "add":
                    overlapped_nets.append(net)
                else:
                    overlapped_nets.remove(net)

            if overlapped_nets == []:
                continue

            density = self.sum_height(overlapped_nets)
            if command == "add":
                if max_density < density:
                    max_density = density
                    start_x = k
                    zones = []
                elif max_density == density:
                    start_x = k
            else:
                if not start_x is None:
                    z = (start_x, k)
                    zones.append(z)
                    start_x = None
        return zones


@dataclass(frozen=True, order=True)
class Assignment:
    net: Net
    max_height: Decimal

    def __repr__(self) -> str:
        return f"{self.net.name}[{self.max_height-self.net.width}, {self.max_height}]"


class Gap:
    def __init__(
        self,
        netlist: list,
        id: int = None,
        width: Decimal = None,
        base_height: float | Decimal = None,
    ):
        self.id = id
        # if None, unlimited
        self.width = width
        if not width is None:
            self.width = Decimal(str(width))
        if not base_height is None:
            self.base_height = Decimal(str(base_height))

        self.x_coords = sorted(set([x for n in netlist for x in n.x]))
        self.assignments = dict([(x, []) for x in self.x_coords])
        self.net2assignment = {}

    def max_height(self, x: Decimal) -> Decimal:
        if self.assignments[x] == []:
            return Decimal("0.0")
        return self.assignments[x][-1].max_height

    def update_max_height(self, height: Decimal, net: Net) -> Decimal:
        updated_height = height + net.width
        return updated_height

    def range_x(self, minx: float, maxx: float) -> list[float]:
        l = bisect.bisect_left(self.x_coords, minx)
        r = bisect.bisect_right(self.x_coords, maxx)
        return self.x_coords[l:r]

    def max_height_range(self, minx: float = None, maxx: float = None) -> Decimal:
        if minx is None:
            minx = float("-inf")
        if maxx is None:
            maxx = float("inf")

        max_h = Decimal("0.0")
        for x in self.range_x(minx, maxx):
            h = self.max_height(x)
            if h > max_h:
                max_h = h
        return max_h

    def is_assignable(self, net: Net, height_limit: Decimal = None) -> bool:
        if height_limit is None:
            height_limit = self.width

        # unlimited capacity
        if height_limit is None:
            return True

        height = self.max_height_range(net.minx, net.maxx)
        new_height = self.update_max_height(height, net)
        return new_height <= height_limit

    def assign(self, net: Net) -> None:
        if not self.is_assignable(net):
            raise ValueError(f"Given Net {net} is not assignable.")

        assign_nets = []
        assign_nets.extend([net])

        new_assignment = []
        last_max_h = self.max_height_range(assign_nets[0].minx, assign_nets[0].maxx)
        for n in assign_nets:
            updated_max_h = self.update_max_height(last_max_h, n)
            assignment = Assignment(n, updated_max_h)
            # register assignment
            self.net2assignment[net.name] = assignment
            new_assignment.append(assignment)
            last_max_h = updated_max_h

        # new assignment does not surpass the max channel hegiht
        for x in self.range_x(net.minx, net.maxx):
            self.assignments[x].extend(new_assignment)
