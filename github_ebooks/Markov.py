from collections import deque, defaultdict
from random import choice

class SequenceGenerator:
  def __init__(self, order):
    self.order = order
    self.table = defaultdict(list)

  def addSample(self, sequence):
    st = deque([None] * self.order, self.order)
    len = 0

    for v in sequence:
      self.table[tuple(st)].append(v)
      st.append(v)
      len += 1

    self.table[tuple(st)].append(None)
  
  def addSamples(self, sequences):
    for sequence in sequences:
      self.addSample(sequence)

  def next(self, state):
    return choice(self.table.get(tuple(state), [None]))

  def generate(self, seed=[]):
    left = [None] * max(0, self.order - len(seed))
    right = seed[-self.order:]
    state = deque(left + right, self.order)

    while True:
      nt = self.next(state)
      if nt is None:
        raise StopIteration()

      state.append(nt)
      yield nt

