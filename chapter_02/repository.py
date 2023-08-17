import abc
# TODO: alternative is to use PEP-544 Protocols

import model
# ^^^^^^^^^^ ORM should import the model, not the other way around


########## the _port_ is the _interface_ between the app and what we abstract away

# NOTE: ABC showing Interface of repository abstraction
#       But, could duck-type with anything allowing `add(thing), get(id)`
#
#       > "What do we get for this?  And what does it cost us?"
#       COST: increased number of moving parts (and ongoing maintenance)
class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, batch: model.Batch):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, reference: model.Ref) -> model.Batch:
        raise NotImplementedError

########## the _adapter_ is the _implementation_ behind that interface

# self-imposed simplicity stops us from coupling our domain model to the database.
#
# Also, nice thing about Abstraction: changes here dont affect the rest of the application
# However, can be a "WTF factor" layer of indirection
class SqlAlchemyRepository(AbstractRepository):

    def __init__(self, session):
        self.session = session

    def add(self, batch: model.Batch):
        # self.session.execute('INSERT INTO ??
        self.session.add(batch)

    def get(self, reference: model.Ref):
        # self.session.execute('SELECT ??
        return self.session.query(model.Batch).filter_by(reference=reference).one()

    def list(self):
        return self.session.query(model.Batch).all()


# In tests, simple fake repository using a set
# TIP: if it's hard to fake, the abstraction is too complicated
class FakeRepository(AbstractRepository):

    def __init__(self, batches):
        self._batches = set(batches)

    def add(self, batch):
        self._batches.add(batch)

    def get(self, reference):
        return next(b for b in self._batches if b.reference == reference)

    def list(self):
        return list(self._batches)
