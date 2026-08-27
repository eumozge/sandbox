import ctypes

# 1. C hash function signature: hashfunc(PyObject*) -> Py_ssize_t
HASHFUNC = ctypes.CFUNCTYPE(ctypes.c_ssize_t, ctypes.py_object)

# 2. Custom hash function for lists
def list_hash_wrapper(obj):
    try:
        # Convert list to tuple to get a hash of its contents
        return hash(tuple(obj))
    except Exception:
        return 0

# Protect callback from garbage collection
c_hash_callback = HASHFUNC(list_hash_wrapper)

# 3. Extract C hash function address from int.__hash__ descriptor
class WrapperDescriptor(ctypes.Structure):
    _fields_ = [
        ("ob_refcnt", ctypes.c_ssize_t),
        ("ob_type", ctypes.c_void_p),
        ("d_common", ctypes.c_void_p * 4),
        ("d_wrapped", ctypes.c_void_p)
    ]

descr = WrapperDescriptor.from_address(id(int.__hash__))
int_hash_address = descr.d_wrapped

# 4. Dynamically search for the tp_hash field offset in PyTypeObject
type_ptr = ctypes.cast(id(int), ctypes.POINTER(ctypes.c_void_p))

tp_hash_offset = None
for offset in range(50):
    if type_ptr[offset] == int_hash_address:
        tp_hash_offset = offset
        break

if tp_hash_offset is None:
    raise RuntimeError("Failed to find tp_hash offset")

# 5. Patch PyList_Type at the discovered offset
list_ptr = ctypes.cast(id(list), ctypes.POINTER(ctypes.c_void_p))
list_ptr[tp_hash_offset] = ctypes.cast(c_hash_callback, ctypes.c_void_p).value


lst = [1, 2, 3]
print(hash(lst))

t = (1, 2, lst)
s = {t: 1}
print(s)
