from functools import wraps
from time import time
from typing import List, Tuple
import math
from lib import constants


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


def normalize(pos: Tuple, to_pos=False):
  left = math.floor(pos[0] / constants.SQUARE_WIDTH) 
  top =math.floor(pos[1] / constants.SQUARE_HEIGHT) 
  
  if not to_pos:
    left *= constants.SQUARE_WIDTH
    top *= constants.SQUARE_HEIGHT
    
  return (left, top)