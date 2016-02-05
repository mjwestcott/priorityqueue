"""
priorityqueue.py

Priority Queue Implementation with a O(log n) Remove Method

This file implements min- amd max-oriented priority queues based on binary
heaps. I found the need for a priority queue with a O(log n) remove method.
This can't be achieved with any of Python's built in collections including
the heapq module, so I built my own. The heap is arranged according to a given
key function.

Usage:
    >>> from priorityqueue import MinHeapPriorityQueue
    >>> items = [4, 0, 1, 3, 2]
    >>> pq = MinHeapPriorityQueue(items)
    >>> pq.pop()
    0

    A priority queue accepts an optional key function.
    >>> items = ['yy', 'ttttttt', 'z', 'wwww', 'uuuuuu', 'vvvvv', 'xxx']
    >>> pq = MinHeapPriorityQueue(items, key=len)
    >>> pq.pop()
    'z'
    >>> pq.pop()
    'yy'

    Internally, the queue is a list of tokens of type 'Locator', which contain
    the priority value, the item itself, and its current index in the heap.
    The index field is updated whenever the heap is modified. This is what
    allows us to remove in O(log n). Appending an item returns it's Locator.
    >>> token = pq.append('a')
    >>> token
    Locator(value=1, item='a', index=0)
    >>> pq.remove(token)
    'a'

    If we want to be able to remove any item in the list we can maintain an
    auxiliary dictionary mapping items to their Locators. Here's a simple
    example with unique items:
    >>> items = [12, 46, 89, 101, 72, 81]
    >>> pq = MinHeapPriorityQueue()
    >>> locs = {}
    >>> for item in items:
    ...    locs[item] = pq.append(item)
    >>> locs[46]
    Locator(value=46, item=46, index=1)
    >>> pq.remove(locs[46])
    46

    Iterating with 'for item in pq' or iter() will produce the items, not the
    Locator instances used in the internal representation. The items will be
    generated in sorted order.
    >>> items = [3, 1, 0, 2, 4]
    >>> pq = MinHeapPriorityQueue(items)
    >>> for item in pq:
    ...     print(item)
    0
    1
    2
    3
    4
"""
# Inspired by:
#   - AdaptableHeapPriorityQueue in 'Data Structures and Algorithms in Python'
#   - the Go Standard library's heap package
#   - Python's heapq module
#   - Raymond Hettinger's SortedCollection on ActiveState
#   - Peter Norvig's PriorityQueue in the Python AIMA repo

class MinHeapPriorityQueue():
    """A locator-based min-oriented priority queue implemented with a binary
    heap, arranged according to a key function.

    Operation                   Running Time
    len(P), P.peek()            O(1)
    P.update(loc, value, item)  O(log n)
    P.append(item)              O(log n)*
    P.pop()                     O(log n)*
    P.remove(loc)               O(log n)*

    *amortized due to occasional resizing of the underlying python list
    """

    def __init__(self, iterable=(), key=lambda x: x):
        self._key = key
        decorated = [(key(item), item) for item in iterable]
        self._pq = [self.Locator(value, item, i) for i, (value, item) in enumerate(decorated)]
        if len(self._pq) > 1:
            self._heapify()

    class Locator:
        """Token for locating an entry of the priority queue."""
        __slots__ = '_value', '_item', '_index'

        def __init__(self, value, item, i):
            self._value = value
            self._item = item
            self._index = i

        def __eq__(self, other):
            return self._value == other._value

        def __lt__(self, other):
            return self._value < other._value

        def __le__(self, other):
            return self._value <= other._value

        def __repr__(self):
            return '{}(value={!r}, item={!r}, index={})'.format(
                self.__class__.__name__,
                self._value,
                self._item,
                self._index
            )

    #------------------------------------------------------------------------------
    # non-public
    def _parent(self, j):
        return (j-1) // 2

    def _left(self, j):
        return 2*j + 1

    def _right(self, j):
        return 2*j + 2

    def _swap(self, i, j):
        """Swap the elements at indices i and j of array."""
        self._pq[i], self._pq[j] = self._pq[j], self._pq[i]
        # Update the indices in the Locator instances.
        self._pq[i]._index = i
        self._pq[j]._index = j

    def _upheap(self, i):
        parent = self._parent(i)
        if i > 0 and self._pq[i] < self._pq[parent]:
            self._swap(i, parent)
            self._upheap(parent)

    def _downheap(self, i):
        n = len(self._pq)
        left, right = self._left(i), self._right(i)
        if left < n:
            child = left
            if right < n and self._pq[right] < self._pq[left]:
                child = right
            if self._pq[child] < self._pq[i]:
                self._swap(i, child)
                self._downheap(child)

    def _fix(self, i):
        self._upheap(i)
        self._downheap(i)

    def _heapify(self):
        start = self._parent(len(self) - 1) # Start at parent of last leaf
        for j in range(start, -1, -1):      # going to and includng the root.
            self._downheap(j)

    #------------------------------------------------------------------------------
    # public
    def append(self, item):
        """Add an item to the heap"""
        token = self.Locator(self._key(item), item, len(self._pq))
        self._pq.append(token)
        self._upheap(len(self._pq) - 1) # Upheap newly added position.
        return token

    def update(self, loc, newval, newitem):
        """Update the priority value and item for the entry identified by Locator loc."""
        j = loc._index
        if not (0 <= j < len(self) and self._pq[j] is loc):
            raise ValueError('Invalid locator')
        loc._value = newval
        loc._item = newitem
        self._fix(j)

    def remove(self, loc):
        """Remove and return the item identified by Locator loc."""
        j = loc._index
        if not (0 <= j < len(self) and self._pq[j] is loc):
            raise ValueError('Invalid locator')
        if j == len(self) - 1:
            self._pq.pop()
        else:
            self._swap(j, len(self) - 1)
            self._pq.pop()
            self._fix(j)
        return loc._item

    def peek(self):
        """Return but do not remove item with minimum priority value."""
        loc = self._pq[0]
        return loc._item

    def pop(self):
        """Remove and return item with minimum priority value."""
        self._swap(0, len(self._pq) - 1)
        loc = self._pq.pop()
        self._downheap(0)
        return loc._item

    @property
    def items(self):
        return [token._item for token in self._pq]

    def __len__(self):
        return len(self._pq)

    def __contains__(self, item):
        return item in self.items

    def __iter__(self):
        return iter(sorted(self.items))

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self._pq)

class MaxHeapPriorityQueue(MinHeapPriorityQueue):
    """A locator-based max-oriented priority queue implemented with a binary
    heap, arranged according to a key function.

    Operation                   Running Time
    len(P), P.peek()            O(1)
    P.update(loc, value, item)  O(log n)
    P.append(item)              O(log n)*
    P.pop()                     O(log n)*
    P.remove(loc)               O(log n)*

    *amortized due to occasional resizing of the underlying python list
    """
    # Override all relevant private methods of MinHeapPriorityQueue
    # with max-oriented versions.
    def _upheap(self, i):
        parent = self._parent(i)
        if i > 0 and self._pq[parent] < self._pq[i]:
            self._swap(i, parent)
            self._upheap(parent)

    def _downheap(self, i):
        n = len(self._pq)
        left, right = self._left(i), self._right(i)
        if left < n:
            child = left
            if right < n and self._pq[left] < self._pq[right]:
                child = right
            if self._pq[i] < self._pq[child]:
                self._swap(i, child)
                self._downheap(child)

    def __iter__(self):
        return iter(sorted(self.items, reverse=True))

__doc__ += """
>>> import random; random.seed(42)
>>> from priorityqueue import MinHeapPriorityQueue, MaxHeapPriorityQueue

Function to verify the min-heap invariant is true for all elements of pq.
>>> def verify(pq):
...     n = len(pq._pq)
...     for i in range(n):
...         left, right = 2*i + 1, 2*i + 2
...         if left < n:
...             assert pq._pq[i] <= pq._pq[left]
...         if right < n:
...             assert pq._pq[i] <= pq._pq[right]

Function to verify the max-heap invariant is true for all elements of pq.
>>> def verify_max(pq):
...     n = len(pq._pq)
...     for i in range(n):
...         left, right = 2*i + 1, 2*i + 2
...         if left < n:
...             assert pq._pq[i] >= pq._pq[left]
...         if right < n:
...             assert pq._pq[i] >= pq._pq[right]

>>> items = [random.randint(1, 100) for _ in range(10000)]
>>> pq = MinHeapPriorityQueue(items)
>>> verify(pq)
>>> pq = MaxHeapPriorityQueue(items)
>>> verify_max(pq)

Check multiple signs for priority values.
>>> items = list(range(100, -100, -1))
>>> random.shuffle(items)
>>> pq = MinHeapPriorityQueue(items)
>>> verify(pq)
>>> pq = MaxHeapPriorityQueue(items)
>>> verify_max(pq)

Test pop, peek, append, remove, update, __len__, and __contains__ operations.
>>> items = ['jjjjjjjjjj', 'iiiiiiiii', 'hhhhhhhh',
...          'ggggggg', 'ffffff', 'eeeee',
...          'dddd', 'ccc', 'bb', 'a']
>>> pq = MinHeapPriorityQueue(items, key=len)
>>> verify(pq)
>>> pq.pop()
'a'
>>> pq.pop()
'bb'
>>> pq.peek()
'ccc'
>>> pq.pop()
'ccc'
>>> pq.pop()
'dddd'
>>> pq.peek()
'eeeee'
>>> pq.pop()
'eeeee'
>>> _ = pq.append('a')
>>> _ = pq.append('bb')
>>> verify(pq)

>>> pq = MaxHeapPriorityQueue(key=len)
>>> pq.append([1, 2, 3])
Locator(value=3, item=[1, 2, 3], index=0)
>>> pq.append([1, 2, 3, 4, 5, 6])
Locator(value=6, item=[1, 2, 3, 4, 5, 6], index=0)
>>> pq.append([1])
Locator(value=1, item=[1], index=2)
>>> pq.append([1, 2, 3, 4, 5, 6, 7, 8, 9])
Locator(value=9, item=[1, 2, 3, 4, 5, 6, 7, 8, 9], index=0)
>>> len(pq)
4
>>> [1] in pq
True
>>> [1, 2, 3, 4, 5] in pq
False

>>> items = list(range(1, 10001))
>>> random.shuffle(items)
>>> pq = MinHeapPriorityQueue(items)
>>> verify(pq)
>>> len(pq) == 10000
True
>>> for i in range(1, 10001):
...     x = pq.pop()
...     assert x == i

>>> pq = MinHeapPriorityQueue()
>>> locs = {}
>>> for x in items:
...     locs[x] = pq.append(x)
>>> pq.remove(locs[1])
1
>>> pq.remove(locs[2])
2
>>> pq.pop()
3
>>> for i in range(4, 100):
...     _ = pq.remove(locs[i])
>>> pq.pop()
100
>>> verify(pq)
>>> pq.update(locs[999], 1, 'test')
>>> 999 in pq
False
>>> pq.pop()
'test'
>>> 998 in pq
True

Test the items and __repr__ methods.
>>> items = ['a', 'b', 'c']
>>> pq = MinHeapPriorityQueue(items)
>>> pq
MinHeapPriorityQueue([Locator(value='a', item='a', index=0), Locator(value='b', item='b', index=1), Locator(value='c', item='c', index=2)])
>>> pq.items == ['a', 'b', 'c']
True

Check that __iter__ generates items in sorted order.
>>> items = list(range(1000))
>>> pq = MinHeapPriorityQueue(items)
>>> for i, x in enumerate(pq):
...     assert i == x
>>> pq = MaxHeapPriorityQueue(items)
>>> for i, x in enumerate(pq):
...     assert 999 - i == x
"""

if __name__ == "__main__":
    import doctest
    doctest.testmod()
