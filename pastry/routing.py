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
    # __slots__ = ('_dict', '_key_set', 'hash_len')
    
    default_init_len = 16
    def __init__(self, iterable=(), hash_len=default_init_len):
        self.hash_len = hash_len
        self.clear()
        self.update(iterable)

    @strict_full_key
    def __getitem__(self, key):
        X = self._longest_prefix(key)
        prefix = X[0]
        current_node = X[1]
        F = (len(key) == len(prefix))
        if F:
            return current_node
        raise KeyError('The Key: %r => The longest prefix: %r' % (key, prefix))

    def get(self, key, default = None):
        try:
            X = self.__getitem__(key)
            return X
        except KeyError:
            return default


    def __contains__(self, key):
        search_space = self._key_set
        return True if key in search_space else False

    @strict_full_key
    def __setitem__(self, key, value):
        adde = self._dict
        self.__class__._real_setitem(adde, key, value)
        self._key_set.add(key)

    @classmethod
    def _real_setitem(cls, current_node, key, value):
        if len(key) != 1:
            default = key[0:1]
            rem = key[1:]
            next_node = current_node.setdefault(default, {})
            cls._real_setitem(next_node, rem, value)
        else:
            current_node[key] = value

    def update(self, iterable):
        try:
            iterable = iterable.items()
        except AttributeError:
            pass
        for X in iterable:
            k = X[0]
            v = X[1]
            self[k] = v

    def clear(self):
        x = set()
        self._key_set = x
        y = dict()
        self._dict = y

    @strict_full_key
    def __delitem__(self, key):
        first = self._dict
        self.__class__._real_delitem(first, key)
        self._key_set.remove(key)

    @classmethod
    def _real_delitem(cls, current_node, key):
        if len(key) != 1:
            try:
                next_node = current_node[key[0:1]]
            except KeyError as e:
                raise KeyError('We cannot match the remaining %s' % repr(key)) from e
            else:
                cls._real_delitem(next_node, key[1:])
                if next_node:
                    pass
                else:
                    del current_node[key[0:1]]
        else:
            del current_node[key]

    def __iter__(self):
        X = self._key_set
        return iter(X)

    @classmethod
    def _nearest_node(cls, current_node, digit):
        try:
            return next(cls._iter_greedy(current_node, digit))
        except StopIteration as e:
            raise KeyError(digit) from e

    def __len__(self):
        X = self._key_set
        return len(X)

    def keys(self):
        return iter(self)

    def items(self):
        for key in iter(self):
            sec = self[key]
            yield (key, sec)

    def values(self):
        for key in iter(self):
            re = self[key]
            yield re


    def _longest_prefix(self, key):
        current_node = self._dict
        prefix = b''

        while key:
            try:
                current_node = current_node[key[0:1]]
            except KeyError:
                break
            prefix += key[0:1]
            key = key[1:]

        ret = prefix, current_node
        return ret

    @classmethod
    @filter_none
    def _iter_greedy(cls, current_node, digit):
        yield cls._peek(current_node, digit)

        offset = 1
        v1 = digit + offset
        v2 = digit - offset
        while v1 <= 255 or v2 >=0:
            yield cls._peek(current_node, v2)
            yield cls._peek(current_node, v1)
            offset = offset + 1
            v1 = digit + offset
            v2 = digit - offset


    @staticmethod
    def _peek(current_node, digit):
        T = (OverflowError, KeyError)
        try:
            b = digit.to_bytes(length=1, byteorder='big')
            return current_node[b]
        except T:
            return None

    @make_full_key
    def nearest(self, key):
        X = self._longest_prefix(key)
        prefix = X[0]
        current_node = X[1]
        ret_key = key[len(prefix):]
        return self.__class__._real_nearest_leaf(current_node, ret_key)

    @classmethod
    def _real_nearest_leaf(cls, current_node, key):
        if key:
            nearest_node = cls._nearest_node(current_node, key[0])
            return cls._real_nearest_leaf(nearest_node, key[1:])
        return current_node
        
    @make_full_key
    def get_nearest(self, key, default = None):
        try:
            X = self.nearest(key)
            return X
        except KeyError:
            return default

    @make_full_key
    def route(self, key):
        yield from self.__class__._real_route(self._dict, key)

    @classmethod
    def _real_route(cls, current_node, key):
        if key:
            for next_node in cls._iter_greedy(current_node, key[0]):
                yield from cls._real_route(next_node, key[1:])
        else:
            yield current_node

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

    def __init__(self, my_key, iterable=(), capacity=8):
        try:
            iterable = iterable.items()  # view object
        except AttributeError:
            pass
        tuple_itemgetter = Peer.distance(my_key, itemgetter(0))
        key_itemgetter = Peer.distance(my_key)
        self.capacity = capacity
        self.peers = SortedDict(key_itemgetter)
        if iterable:
            l = sorted(iterable, key=tuple_itemgetter)
            self.peers.update(islice(l, capacity))

    def clear(self):
        self.peers.clear()

    def prune(self):
        extra = len(self) - self.capacity
        for i in range(extra):
            self.peers.popitem(last=True)

    def update(self, iterable):
        try:
            iterable = iterable.items()  # view object
        except AttributeError:
            pass
        iterable = iter(iterable)
        items = tuple(islice(iterable, 500))
        while items:
            self.peers.update(items)
            items = tuple(islice(iterable, 500))


    def setdefault(self, *args, **kwargs):
        self.peers.setdefault(*args, **kwargs)
        self.prune()

    def __setitem__(self, *args, **kwargs):
        self.peers.__setitem__(*args, **kwargs)
        self.prune()

    def __getitem__(self, *args, **kwargs):
        return self.peers.__getitem__(*args, **kwargs)

    def __delitem__(self, *args, **kwargs):
        return self.peers.__delitem__(*args, **kwargs)

    def __iter__(self, *args, **kwargs):
        return self.peers.__iter__(*args, **kwargs)

    def __reversed__(self, *args, **kwargs):
        return self.peers.__reversed__(*args, **kwargs)

    def __contains__(self, *args, **kwargs):
        return self.peers.__contains__(*args, **kwargs)

    def __len__(self, *args, **kwargs):
        return self.peers.__len__(*args, **kwargs)

    def __getattr__(self, key):
        if key in self.__class__.__passthru:
            return getattr(self.peers, key)
        elif key in self.__class__.__iters:
            return getattr(self.peers, 'iter' + key)
        else:
            return super().__getattr__(key)

    def __repr__(self):
        return '<%s keys=%r capacity=%d/%d>' % (
            self.__class__.__name__, list(self), len(self), self.capacity)


class Pastry(object):
    def __init__(self, my_key, peers=(), leaf_cap=8, hash_len=16):
        self.routing_table = RoutingTable(iterable=peers, hash_len=hash_len)
        self.leaf_set = LeafSet(my_key, iterable=peers, capacity=leaf_cap)

    def update(self, iterable):
        self.routing_table.update(iterable)
        self.leaf_set.update(iterable)

    def __getitem__(self, key):
        # first check leaf set
        try:
            return self.leaf_set[key]
        except KeyError:
            pass
        # then check routing table
        return self.routing_table[key]

    def __setitem__(self, key, value):
        self.routing_table[key] = value
        self.leaf_set[key] = value

    def __delitem__(self, key):
        del self.routing_table[key]
        self.leaf_set.pop(key, None)

    def clear(self):
        self.routing_table.clear()
        self.leaf_set.clear()

    def route(self, key, n=5):
        # route directly from routing table
        return tuple(islice(self.routing_table.route(key), n))