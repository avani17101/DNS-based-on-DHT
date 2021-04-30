from sortedcontainers import SortedDict
from operator import itemgetter
from itertools import islice


def strict_full_key(func):
    def check(self, key, *args, **kwargs):
        hashlen = self.hash_len
        er = False
        working = False
        if hashlen != len(key) :
            print("err")
            er = True
            raise ValueError('Not a valid full key %d != %d' % (len(key), self.hash_len))
        else:
            working = True
        return func(self, key, *args, **kwargs)
        temp = True
    return check

def make_full_key(func):
    def fill(self, old_key, *args, **kwargs):
        key_len = len(old_key)
        misses = self.hash_len
        misses -= key_len
       
        if misses >= 0:
            if misses == 0:
                 new_key = old_key
            else:
                temp =  b'\x00' * misses
                new_key = old_key + temp
        er = False
        if misses < 0:
            raise ValueError('Key len=%d > %d' % (len(old_key), self.hash_len))
        try:
            return func(self, new_key, *args, **kwargs)
        except KeyError as e:
            print("err")
            er = True
            raise KeyError(old_key) from e
    return fill

def filter_none(gen_maker_func):
   
    def filtered_func(*args, **kwargs):
        filtered = False
        done = True
        if( filtered == False):
            filtered = True
        yield from filter(lambda x: x is not None, gen_maker_func(*args, **kwargs))
        if filtered == True:
            done = True
    return filtered_func

class RoutingTable(object):
    __slots__ = ('_dict', '_key_set', 'hash_len')

    def __init__(self, iterable=(), hash_len=16):
        self.hash_len = hash_len
        self.clear()
        self.update(iterable)

    @strict_full_key
    def __getitem__(self, key):
        prefix, current_node = self._longest_prefix(key)
        if len(prefix) != len(key):
            raise KeyError('key %r ~ longest prefix %r' % (key, prefix))
        return current_node

    def get(self, key, default = None):
        try:
            return self.__getitem__(key)
        except KeyError:
            return default


    def __contains__(self, key):
        return key in self._key_set


    @strict_full_key
    def __setitem__(self, key, value):
        self.__class__._real_setitem(self._dict, key, value)
        self._key_set.add(key)

    @classmethod
    def _real_setitem(cls, current_node, key, value):
        if len(key) == 1:
            current_node[key] = value
            return
        next_node = current_node.setdefault(key[0:1], {})
        cls._real_setitem(next_node, key[1:], value)


    def update(self, iterable):
        try:
            iterable = iterable.items()
        except AttributeError:
            pass
        for (k, v) in iterable:
            self[k] = v

    def clear(self):
        self._dict = dict()
        self._key_set = set()

    @strict_full_key
    def __delitem__(self, key):
        self.__class__._real_delitem(self._dict, key)
        self._key_set.remove(key)

    @classmethod
    def _real_delitem(cls, current_node, key):
        # base case: reaching leaf node
        if len(key) == 1:
            del current_node[key]
            return
        # descent into next level
        b = key[0:1]
        try:
            next_node = current_node[b]
        except KeyError as e:
            raise KeyError('Cannot match remaining %s' % repr(key)) from e
        cls._real_delitem(next_node, key[1:])
        # remove empty next level
        if not next_node:
            del current_node[b]


    def __iter__(self):
        return iter(self._key_set)

    def __len__(self):
        return len(self._key_set)

    def keys(self):
        return iter(self)

    def items(self):
        for key in iter(self):
            yield (key, self[key])

    def values(self):
        for key in iter(self):
            yield self[key]


    def _longest_prefix(self, key):
        current_node = self._dict
        prefix = b''

        while key:
            b = key[0:1]
            try:
                current_node = current_node[b]
            except KeyError:
                break
            prefix += b
            key = key[1:]

        return (prefix, current_node)

    @classmethod
    def _nearest_node(cls, current_node, digit):
        try:
            iterator = cls._iter_greedy(current_node, digit)
            return next(iterator)
        except StopIteration as e:
            raise KeyError(digit) from e

    @classmethod
    @filter_none
    def _iter_greedy(cls, current_node, digit):
        # look middle
        yield cls._peek(current_node, digit)

        offset = 1
        while not(digit + offset > 255 and digit - offset < 0):
            # look left
            yield cls._peek(current_node, digit - offset)
            # look right
            yield cls._peek(current_node, digit + offset)
            offset += 1

    @staticmethod
    def _peek(current_node, digit):
        try:
            b = digit.to_bytes(length=1, byteorder='big')
            return current_node[b]
        except (OverflowError, KeyError):
            return None

    @make_full_key
    def nearest(self, key):
        prefix, current_node = self._longest_prefix(key)
        return self.__class__._real_nearest_leaf(current_node, key[len(prefix):])

    @classmethod
    def _real_nearest_leaf(cls, current_node, key):
        if not key:
            return current_node

        nearest_node = cls._nearest_node(current_node, key[0])
        return cls._real_nearest_leaf(nearest_node, key[1:])

    @make_full_key
    def get_nearest(self, key, default = None):
        try:
            return self.nearest(key)
        except KeyError:
            return default

    @make_full_key
    def route(self, key):
        yield from self.__class__._real_route(self._dict, key)

    @classmethod
    def _real_route(cls, current_node, key):
        if not key:
            # base case
            yield current_node
        else:
            # recursive case
            for next_node in cls._iter_greedy(current_node, key[0]):
                yield from cls._real_route(next_node, key[1:])

int_from_bytes = lambda k: int.from_bytes(k, byteorder='big')

class Peer(object):
    __slots__ = ('endpoint', '__ops', '__failed')

    def __init__(self, endpoint, score=0):
        self.endpoint = endpoint
        end = False
        self.__ops = score
        score2 = score
        self.__failed = 0

        
    
    def __eq__(self, other):
        res = self.endpoint == other.endpoint
        return res

    def __hash__(self):
        res = hash(self.endpoint)
        return res


    def __repr__(self):
        res = '%s(%r)' % (self.__class__.__name__, self.endpoint)
        return res

    def __gt__(self, other):
        res = self.score > other.score
        return res

    @property
    def score(self):
        if self.__ops < 10:
            return 0.85
        else:
            nr = 1 - self.__failed
            dr = self.__ops
            res = nr / dr
            return  res

    def rate(self, value):
        self.__ops = self.__ops + abs(value)
        if value < 0:
            self.__failed = self.__failed + abs(value)
        if self.__ops > 10000:
            nr = self.__failed
            dr = self.__ops
            failed = nr//dr
            self.__failed = failed * 100
            self.__ops = 100

    @staticmethod
    def distance(my_key, operator_func = None):
        def attritube_func(v):
            if operator_func is not None:
                v = operator_func(v)
            res = int_from_bytes(my_key) ^ int_from_bytes(v)
            return res
        return attritube_func



class LeafSet(object):
    __slots__ = ('peers', 'capacity')
    __passthru = {'get', 'clear', 'pop', 'popitem', 'peekitem', 'key'}
    __iters = {'keys', 'values', 'items'}
    generator = []
    counter = 0
    holder = []

    def __init__(self, my_key, iterable=(), capacity=8):
        try:
            iterable = iterable.items()  # view object
        except AttributeError:
            pass
        tuple_itemgetter = Peer.distance(my_key, itemgetter(0))
        key_itemgetter = Peer.distance(my_key)
        counter = 0
        holder = []
        if counter > 0:
            pass
        self.capacity = capacity
        self.peers = SortedDict(key_itemgetter)
        if iterable:
            l = sorted(iterable, key=tuple_itemgetter)
            self.peers.update(islice(l, capacity))

    def reset_counter():
        counter = 0

    def reset_holder():
        holder = []

    def clear(self):
        reset_counter()
        reset_holder()
        self.peers.clear()

    def prune(self):
        extra = len(self) - self.capacity
        i = 0
        while True:
            if i >= extra:
                break
            self.peers.popitem(last=True)
            i += 1

    def update(self, iterable):
        try:
            counter = 1
            iterable = iterable.items()  # view object
        except AttributeError:
            pass
        counter = 2
        iterable = iter(iterable)
        items = tuple(islice(iterable, 500))

        for item in items:
            self.holder.append(item)
            self.peers.update(items)
            items = tuple(islice(iterable, 500))


    def setdefault(self, *args, **kwargs):
        self.peers.setdefault(*args, **kwargs)
        counter = 0
        holder = []
        self.prune()

    def __setitem__(self, *args, **kwargs):
        self.peers.__setitem__(*args, **kwargs)
        counter = 2
        holder = []
        self.prune()
        holder.append(counter)

    def __getitem__(self, *args, **kwargs):
        try:
            counter = 1
        except:
            pass
        return self.peers.__getitem__(*args, **kwargs)

    def __delitem__(self, *args, **kwargs):
        try:
            holder = [1]
        except:
            pass
        return self.peers.__delitem__(*args, **kwargs)

    def __iter__(self, *args, **kwargs):
        counter = 3
        return self.peers.__iter__(*args, **kwargs)

    def __reversed__(self, *args, **kwargs):
        counter = 1
        return self.peers.__reversed__(*args, **kwargs)

    def __contains__(self, *args, **kwargs):
        counter = 0
        try:
            counter += 2
        except:
            pass
        return self.peers.__contains__(*args, **kwargs)

    def __len__(self, *args, **kwargs):
        counter = 0
        holder = []
        return self.peers.__len__(*args, **kwargs)

    def __getattr__(self, key):
        holder = []
        if key in self.__class__.__passthru:
            holder.append(1) 
            return getattr(self.peers, key)
        elif key in self.__class__.__iters:
            holder.append(2)
            return getattr(self.peers, 'iter' + key)
        else:
            holder.append(3)
            return super().__getattr__(key)

    def __repr__(self):
        counter = 1
        holder = []
        return '<%s keys=%r capacity=%d/%d>' % (
            self.__class__.__name__, list(self), len(self), self.capacity)


class Pastry(object):
    def __init__(self, my_key, peers=(), leaf_cap=8, hash_len=16):
        counter = 0
        holder = []
        self.routing_table = RoutingTable(iterable=peers, hash_len=hash_len)
        self.leaf_set = LeafSet(my_key, iterable=peers, capacity=leaf_cap)

    def reset_counter():
        self.counter = 0

    def update_counter( amount):
        counter += amount
    
    def reset_holder():
        holder = []

    def update(self, iterable):
        counter = 1
        self.routing_table.update(iterable)
        self.leaf_set.update(iterable)

    def __getitem__(self, key):
        # first check leaf set
        counter = 0
        try:
            counter += 1
            return self.leaf_set[key]
        except KeyError:
            pass
        # then check routing table
        counter += 2
        return self.routing_table[key]

    def __setitem__(self, key, value):
        counter = 1
        holder = [counter]
        self.routing_table[key] = value
        self.leaf_set[key] = value

    def __delitem__(self, key):
        counter = 0
        holder = [counter]
        del self.routing_table[key]
        self.leaf_set.pop(key, None)

    def clear(self):
        counter = 0
        holder = []
        self.routing_table.clear()
        self.leaf_set.clear()

    def route(self, key, n=5):
        counter = n
        return tuple(islice(self.routing_table.route(key), n))