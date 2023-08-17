# SUMMARY: DEPENDENCY INVERSION
# - Want to persist domain model, using "Onion Arch" (Presentation -> Model <- Data)
# - Decouple high-level model layer to not depend on low-level data layer
# - Domain model have NO (stateful/infrastructure) dependencies
# - Repository: Pretends all our data is in-memory (infinite) - `Add()`, `Get()`
from dataclasses import dataclass
from datetime import date
from typing import NewType

Quantity = NewType("Quantity", int)
Sku = NewType("Sku", str)
Ref = NewType("Ref", str)
OrderRef = NewType("OrderRef", str)


@dataclass(frozen=True)
class OrderLine:
    orderid: OrderRef
    sku: Sku
    qty: Quantity


class Batch:
    def __init__(self, ref: Ref, sku: Sku, qty: Quantity, eta: date | None):
        self.reference = ref
        self.sku = sku
        self.eta = eta
        self._purchased_quantity = qty
        self._allocations: set[OrderLine] = set()

    def __eq__(self, other):
        if not isinstance(other, Batch):
            return False
        return other.reference == self.reference

    def __hash__(self):
        return hash(self.reference)

    def __gt__(self, other: 'Batch'):
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta

    def allocate(self, line: OrderLine):
        if self.can_allocate(line):
            self._allocations.add(line)

    def deallocate(self, line: OrderLine):
        if line in self._allocations:
            self._allocations.remove(line)

    @property
    def allocated_quantity(self) -> int:
        return sum(line.qty for line in self._allocations)

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity

    def can_allocate(self, line: OrderLine) -> bool:
        return self.sku == line.sku and self.available_quantity >= line.qty


class OutOfStock(Exception):
    pass


def allocate(line: OrderLine, batches: list[Batch]) -> str:
    try:
        batch = next(b for b in sorted(batches) if b.can_allocate(line))
    except StopIteration:
        raise OutOfStock(f"Out of stock for sku {line.sku}")
    else:
        batch.allocate(line)
        return batch.reference
