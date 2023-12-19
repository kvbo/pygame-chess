from functools import wraps
from time import time

def warp(val, max_len):
  if val < max_len:
    return val

  return val % max_len

def timing(f):
  @wraps(f)
  def wrap(*args, **kw):
    ts = time()
    result = f(*args, **kw)
    te = time()
    print('func:%r took: %2.10f sec' % \
      (f.__name__, te-ts))
    return result
  return wrap