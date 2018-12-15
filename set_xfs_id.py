#! /bin/sh
# by pts@fazekas.hu at Sat Dec 15 13:19:17 CET 2018

""":" # set_xfs_id.py: Set UUID and label on XFS filesystems.

type python2.7 >/dev/null 2>&1 && exec python2.7 -- "$0" ${1+"$@"}
type python2.6 >/dev/null 2>&1 && exec python2.6 -- "$0" ${1+"$@"}
type python2.5 >/dev/null 2>&1 && exec python2.5 -- "$0" ${1+"$@"}
type python2.4 >/dev/null 2>&1 && exec python2.4 -- "$0" ${1+"$@"}
exec python -- ${1+"$@"}; exit 1

This script need Python 2.4, 2.5, 2.6 or 2.7. Python 3.x won't work.

Typical usage: sudo set_xfs_id.py /dev/sd... new mylabel

The UUID and label set works with busybox blkid (1.21.1) and util-linux
blkid (2.20,1, 2.29.2, 2.33), even if there was no XFS filesystem on the
device.

The device must be at least 1025 bytes long for util-linux blkid,
and at least 592 bytes for busybox blkid.

It's safe to run this tool on an existing filesystem, even if it's mounted
read-write.
"""

import array
import sys


def generate_random_uuid():
  try:
    import os
    uuid_bin = os.urandom(16)
    if len(uuid_bin) != 16:
      raise ValueError
  except (ImportError, AttributeError, TypeError, ValueError, OSError):
    try:
      import uuid
      uuid_bin = uuid.uuid1().bytes
      if len(uuid_bin) != 16:
        raise ValueError
    except (ImportError, ValueError):
      import random
      uuid_bin = ''.join(chr(random.randrange(0, 255)) for _ in xrange(16))
      if len(uuid_bin) != 16:
        raise ValueError
  if not isinstance(uuid_bin, str):
    raise RuntimeError
  return uuid_bin


def set_xfs_uuid_and_label(filename, uuid, label):
  bytearray()
  if len(label) > 12:
    raise ValueError('Volume label too long.')
  label += '\0' * (12 - len(label))
  if uuid in ('random', 'rnd', 'new'):
    uuid_bin = generate_random_uuid()
  else:
    uuid = uuid.replace('-', '')
    if len(uuid) != 32:
      raise ValueError('Need 32 hex digits for UUID.')
    uuid_bin = uuid.decode('hex')
  if len(uuid_bin) != 16:
    raise ValueError('UUID must be 16 bytes long.')

  f = open(filename, 'r+')
  # TODO(pts): Check that size of the file is at least 1025 bytes,
  # because util-linux blkid requires this.
  try:
    old_data = f.read(160)
    if len(old_data) != 160:
      raise IOError('Volume too short.')
    # We could use a bytearray (from Python 2.6), but we want Python 2.4
    # compatibility.
    b = array.array('c', old_data)
    def set_b(i, j, x):
      x = array.array('c', x)
      assert len(x) == j - i
      b[i : j] = x
    label +=  '\0' * (12 - len(label))
    if b[:4].tostring() == 'XFSB':
      # If XFS filesystem detected, don't modify anything else.
      f.seek(32)
      f.write(uuid_bin[:32])
      f.seek(108)
      f.write(label[:12])
    else:
      set_b(32, 48, uuid_bin)  # UUID.
      set_b(108, 120, label)  # Label.
      # Only modify other headers if XFS fileystem was not detected.
      set_b(0, 4, 'XFSB')  # XFS_SB_MAGIC.
      # We need to set these so that util-linux blkid will recognize it as XFS.
      set_b(4, 24, '\0' * 20)  # blocksize = dblocks = rblocks = 0.
      set_b(128, 160, '\0' * 32)  # icount = ifree = fdblocks = frextents = 0.
      set_b(88, 88 + 4, '\0\0\0\1')  # agcount = 1.
      set_b(102, 102 + 2, '\2\0')  # sectsize = 512.
      set_b(121, 121 + 1, '\x09')  # sectlog = 9.
      set_b(4, 4 + 4, '\0\1\0\0')  # blocksize = 65535.
      set_b(120, 120 + 1, '\x10')  # blocklog = 16.
      set_b(104, 104 + 2, '\1\0')  # inodesize = 256.
      set_b(122, 122 + 1, '\x08')  # inodelog = 8.
      set_b(123, 123 + 1, '\x08')  # inoplog = blocklog - inodelog  # 8.
      set_b(80, 80 + 4, '\0\0\0\1')  # rextsize = 1.
      set_b(8, 8 + 8, '\0\0\0\0\0\0\0\x40')  # dblocks = 64.
      set_b(84, 84 + 4, '\0\0\0\x40')  #  agblocks = 64.
      set_b(127, 127 + 1, '\1')  # imax_pct = 1.
      assert len(b) == 160
      f.seek(0)
      f.write(b.tostring())
  finally:
    f.close()


def main(argv):
  if len(argv) != 4:
    print >>sys.stderr, 'Usage: %s <device> <new-uuid> <new-label>' % (
        sys.argv[0])
    sys.exit(1)
  filename, uuid, label = sys.argv[1 : 4]
  set_xfs_uuid_and_label(filename, uuid, label)


if __name__ == '__main__':
  sys.exit(main(sys.argv))
