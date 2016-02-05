priorityqueue.py

Priority Queue Implementation with a O(log n) Remove Method

This project implements min- amd max-oriented priority queues based on binary
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
