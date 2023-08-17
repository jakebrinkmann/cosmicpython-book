# SUMMARY: DOMAIN MODELING: 
#       - Most likely to change and closest to business (ubiquitous terms from biz jargon)
#       - Make it easy to understand and modify!
#       - Distinguish `Entities` (unique identity) from `Value Objects` (immutable data)
#       - Let verbs be functions (no need for BazFactory when `get_baz()` will do
from dataclasses import dataclass
from datetime import date
from typing import NewType

Quantity = NewType("Quantity", int)
Sku = NewType("Sku", str)  # Stock-Keeping-Unit == Product Code
Ref = NewType("Ref", str)
OrderRef = NewType("OrderRef", str)
# NOTE: a bit much, but could prevent passing a `Sku` where a `Ref` is expected


@dataclass(frozen=True)
class OrderLine:
    orderid: OrderRef
    sku: Sku
    qty: Quantity


# NOTE: Make this _Value Object_ immutable, it is not identified by an ID,
#       it is an object identified only by its data (no long-lived identity)
#       (several OrderLine will have the same orderid)
#
#       _Value Equality_ == Two OrderLine with same orderid+sku+qty are equal


# NOTE: probably don't need a "domain model" for operations this trivial.
#       Sticking rigidly to principles of encapsulation and careful layering
#       will help us avoid a ball of mud.
class Batch:
    # NOTE: _Entity_: domain object that has a long-lived (persistent) identity
    #       change values but are still same thing.
    def __init__(self, ref: Ref, sku: Sku, qty: Quantity, eta: date | None):
        self.reference = ref
        self.sku = sku
        self.eta = eta
        self._purchased_quantity = qty
        self._allocations: set[OrderLine] = set()

    def __eq__(self, other):
        # dunder-E-Q
        if not isinstance(other, Batch):
            return False
        return other.reference == self.reference

    def __hash__(self):
        # based on attribute(s) that define entity unique identity over time
        # - controls how added to sets or used as dict keys
        # - try to make attr read-only
        # - shouldn't modify __hash__ w/o modifying __eq__
        return hash(self.reference)  # or `None` if it is not hashable

    def __gt__(self, other: 'Batch'):  # TODO: how to type-hint self
        # ability to use `sorted()` on our list of batches is nice
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta

    def allocate(self, line: OrderLine):
        # if self.available_quantity >= line.qty:
        #     self.available_quantity -= line.qty
        #
        # NOTE: Opting to keep track of more state and
        #   calculate available_qty on-the-fly.
        #
        #   This allows the deallocation to know which lines
        #   have been allocated. Also is idempotent.
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


# NOTE: take care in naming in the ubiquitous
#       language, just like entities, value objects, and services:
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
