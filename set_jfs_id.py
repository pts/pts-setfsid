#! /bin/sh
# by pts@fazekas.hu at Wed Oct 26 20:46:49 CEST 2016

""":" # set_xfs_id.py: Set UUID and label on JFS filesystems.

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

The device must be at least 16 * 1024 * 1024 bytes long for util-linux blkid,
and at least 68 * 1024 bytes for busybox blkid.

It's safe to run this tool on an existing filesystem, even if it's mounted
read-write.
"""

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


def set_jfs_uuid_and_label(filename, uuid, label):
  if len(label) > 16:
    raise ValueError('Volume label too long.')
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
  # TODO(pts): Check that size of the file is at least 16 * 1024 * 1024 bytes,
  # because util-linux blkid requires this.
  try:
    f.seek(0x8000)
    old_data = f.read(0xa8)
    if len(old_data) != 0xa8:
      raise IOError('Volume too short.')
    label +=  '\0' * (16 - len(label))
    if old_data[:4] == 'JFS1':
      # If JFS filesystem detected, don't modify anything else.
      f.seek(0x8088)
      f.write(uuid_bin[:32] + label[:16])
      #f.seek(0x8098)
      #f.write(label[:16])
    else:
      data = ''.join((
          'JFS1', old_data[0x4 : 0x10],
          # This is needed by util-linux blkid, it checks some numbers.
          '\1\0\0\0\0\0\0\0\1\0\0\0\0\0',
          old_data[0x1e : 0x88], uuid_bin, label))
      assert len(data) == 0xa8
      f.seek(0x8000)
      f.write(data)
  finally:
    f.close()


def main(argv):
  if len(argv) != 4:
    print >>sys.stderr, 'Usage: %s <device> <new-uuid> <new-label>' % (
        sys.argv[0])
    sys.exit(1)
  filename, uuid, label = sys.argv[1 : 4]
  set_jfs_uuid_and_label(filename, uuid, label)


if __name__ == '__main__':
  sys.exit(main(sys.argv))
