import simpy
from simulator.core.components.component import Component
from simulator.core.pallets.system_pallet import SystemPallet
from typing import List, Tuple, Optional

class PalletConveyor(Component):
    """
    Used for transporting SystemPallets from point to another.
    Pallet capacity is determined by number of discrete 'action points' (slots).
    Has a fixed operation direction.
    Conceptually acts like a small queue with positions.

    Additional Attributes
    ----------
    start : Tuple[int,int]
        Entry point of the conveyor for pallets.
    end : Tuple[int,int]
        Pallet output from conveyor.
    num_slots : int
        The amount of pallets the conveyor can fit.
    cycle_time : float
        Time in simulation units per movement cycle.
    next_component : int
        Id of the component that receives pallets at the end.
    slots : List[Optional[SystemPallet]]
        List of either 'None' or pallet IDs. Conveyor length == num of slots.
    slot_coords : List[Tuple[float,float]]
        List of each slot coordinate.
    """
    def __init__(self, env: simpy.Environment, conveyor_id: int, name: str,
                 start: Tuple[float, float], end: Tuple[float, float], num_slots: int,
                 cycle_time: float, next_component: List[object]=None):
        super().__init__(env, conveyor_id, name)
        self.start = start
        self.end = end
        self.num_slots = num_slots
        self.cycle_time = cycle_time
        self.slots: List[Optional[SystemPallet]] = [None] * num_slots
        self.next_component = next_component

        def calculate_slots(start: Tuple[float,float], end: Tuple[float,float], num_slots: int) -> List[Tuple[float,float]]:
            """Return evenly spaced slot coordinates"""
            if num_slots == 2:
                return [start, end]
            else:
                x1, y1 = float(start[0]), float(start[1])
                x2, y2 = float(end[0]), float(end[1])

                slots = []
                for i in range(num_slots):
                    t = i / (num_slots - 1)  # normalized 0..1
                    x = x1 + t * (x2 - x1)
                    y = y1 + t * (y2 - y1)
                    slots.append((x, y))

                return slots

        self.slot_coords = calculate_slots(start, end, num_slots)

    def can_load(self) -> bool:
        """Check if first slot is free for loading"""
        return self.slots[0] is None

    def load(self, pallet: SystemPallet):
        """Place pallet at start if free"""
        if self.can_load():
            self.slots[0] = pallet
            pallet.actual_dest = self.slot_coords[0]
            print(f"[{self.env.now}] {self.name}: Loaded {pallet}")

    def shift(self):
        """Shift pallets one slot forward if possible."""
        # If the last slot is occupied the pallet must be unloaded before shifting
        # Try to unload the last slot into downstream
        if self.downstream and self.slots[-1] is not None:
            pallet = self.slots[-1]
            accepted = self.downstream[0].can_load()
            if accepted:
                print(f"[{self.env.now}] {self.component_id}: Passed {pallet} downstream")
                self.slots[-1] = None  # remove pallet if accepted
            else: # Unloading not possible -> shifting not possible
                return

        # Traverse backwards to not overwrite slots
        for i in reversed(range(1, self.num_slots)):
            if self.slots[i] is None and self.slots[i - 1] is not None:
                pallet = self.slots[i - 1]
                pallet.actual_dest = self.slot_coords[i]
                self.slots[i] = self.slots[i - 1]
                self.slots[i - 1] = None


    def run(self):
        """Main conveyor loop."""
        while True:
            yield self.env.timeout(self.cycle_time)
            self.shift()
            self.print_state()

    def print_state(self):
        slots_repr = [p.pallet_id if p else "." for p in self.slots]
        print(f"[{self.env.now}] {self.component_id} slots: {slots_repr}")
