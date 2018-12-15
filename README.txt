pts-setfsid: Tools to set UUID and label on filesystems
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
pts-setfsid is a set of Python scripts which can set UUID and label on
filesystems. These scripts can also be used to create fake filesystem
headers which blkid recognizes with UUID and label.

Supported filesystems:

* XFS (by set_xfs_id.py): Label is at most 12 bytes, UUID and label are
  in 0x0...0xa0. This is useful to add a fake XFS headers to an ext2, ext3
  or ext4 filesystem, because those filesystems ignore everything in
  0x0..0x400.
* JFS (by set_jfs_id.py): Label is at most 16 bytes, UUID and label are
  in 0x8000..0x80a8.

Other filesystem considered
~~~~~~~~~~~~~~~~~~~~~~~~~~~
This is based on what
busybox-1.21.1/util-linux/volume_id/*.c supports.

Filesystems with UUID:

* xfs.c: (0x0..0x200, 12-byte label)
* jfs.c: 0x8000...0x8200 (16-byte label)
* ext.c (ext2, ext3, ext4): 0x400..0x600
* exfat.c: 0x0...0x6f... (has label and uuid in root directory, low offset)
* linux_raid.c: (end of device, no label)
* btrfs.c: (0x10000..0x10200, 256-byte label)
* reiserfs.c: (0x10000..0x10200 or 0x2000..0x2200, 16-byte label)
* linux_swap.c: (0x0..0x1000 or 0x0..0x2000 or 0x0..0x4000, 16-byte label)
* ocfs2.c: (0x2000..0x2200, 64-byte label)
* nilfs.c: (0x400..0x4f8, 80-byte label)
* ntfs.c: (0x0..0x200.., 8-byte UUID only, label later in the root directory)
* luks.c: (0x0..0x200, no label)

Filesystems without UUID:

* iso9660.c: 0x8000..0x10000
* hfs.c: 0x400..0x600.. (has MD5 UUID)
* fat.c: 0x0..0x200... (tries to read volume label from root dir, 32-bit UUID)
* cramfs.c: 0x0..0x200
* udf.c: 0x8000..0x8200...
* sysv.c: 0x200..0x400...
* squashfs.c: 0x0..0x200
* romfs.c: 0x0..0x200

__END__
