"""
example.py

An Example Use of priorityqueue.py: Solving the 'Skyline' Problem

For a description of the problem: https://uva.onlinejudge.org/external/1/p105.pdf

Our strategy is as follows. We want to scan the horizon left to right. If at
any point the maximum height of a building at the current x coordinate changes,
we should make a note of that (x, height) pair.

In order to achieve this, we can first make a list of all x coordinates where a
building start or ends. These are the significant x values. In fact, we want to
map these x values to the list of buildings that start or end there.

Then we can loop through these x values. For each one:
    - If we are at an x coordinate where a building starts we will append its
      height to a list.
    - If we are at an x coordinate where a buildings ends we will remove its
      height from the list.
    - Look up the max from the heights list, and if it is different
      from the last height we found, then make note of a new (x, height) pair.

The data structure holding the heights was described as a list. But note that
we are performing max(), append(), and remove() operations on it. A Python list
will take O(n), O(1) and O(n) time respectively. We can do better using a
heap-based data structure which operates in O(1), O(log n), and O(log n) time
respectively.

Since we are looping over two x values for each building and performing O(log n)
operations each time, the algorithm described above will run in O(n log n) where
n is the number of buildings. The naive implementation using a list will run in
O(n**2).
"""
from collections import namedtuple, defaultdict
from priorityqueue import MaxHeapPriorityQueue

def skyline(buildings):
    Building = namedtuple("Building", ["left", "height", "right"])
    bs = set(Building(*b) for b in buildings) # remove duplicates

    xs = defaultdict(list) # mapping x values to the buildings which start or end there
    for b in bs:
        xs[b.left].append(b)
        xs[b.right].append(b)

    # a max-heap of buildings, used to find which has the max height at a given x value
    pq = MaxHeapPriorityQueue(key=lambda x: x.height)
    # an auxiliary data structure to help find the location of items in pq
    locs = {}

    floor = Building(0, 0, max(b.right for b in bs))
    locs[floor] = pq.append(floor)

    res = [(0, 0)] # implicit starting coordinates
    for x in sorted(xs):               # scan horizon left to right over significant x values
        for b in xs[x]:                # for each building at that x value
            if x == b.left:            # b starts there,
                locs[b] = pq.append(b) # so add it to pq
            elif x == b.right:         # b ends there,
                pq.remove(locs[b])     # so remove it from pq
                del locs[b]            # and from locs
        ans = x, pq.peek().height
        prev = res[-1]        # check whether ans is needed to uniquely describe the skyline
        if prev[1] != ans[1]: # a change in height,
            res.append(ans)   # so add to the results
    return res[1:] # remove implicit starting coordinates

if __name__ == '__main__':
    # check solution to original UVa problem
    INPUT = [(1,11,5),(2,6,7),(3,13,9),(12,7,16),(14,3,25),(19,18,22),(23,13,29),(24,4,28)]
    OUTPUT = [(1,11),(3,13),(9,0),(12,7),(16,3),(19,18),(22,3),(23,13),(29,0)]
    assert skyline(INPUT) == OUTPUT

    # benchmark against much larger problem sets
    import random; random.seed(42)
    from timeit import default_timer as timer
    def buildings(n):
        START = 0
        END = 100000
        MAX_HEIGHT = 100000
        for _ in range(n):
            l = random.randint(START, END-1)
            h = random.randint(1, MAX_HEIGHT)
            r = random.randint(l+1, END)
            yield (l, h, r)
    print("Skyline Benchmark Results")
    ns = [1000, 2000, 4000, 8000, 16000, 32000, 64000, 128000, 256000]
    for n in ns:
        bs = buildings(n)
        start = timer()
        skyline(bs)
        end = timer()
        print("n={}, time={:0.3f}s".format(n, end - start))
