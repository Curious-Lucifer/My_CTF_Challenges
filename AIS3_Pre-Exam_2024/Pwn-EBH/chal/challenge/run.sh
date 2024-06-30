#!/bin/bash

/usr/bin/qemu-system-x86_64 \
    -kernel /home/user/challenge/bzImage \
    -initrd /home/user/challenge/initramfs.cpio.gz \
	-fsdev local,security_model=passthrough,id=fsdev0,path=/home/user/web/uploads/$1 \
	-device virtio-9p-pci,id=fs0,fsdev=fsdev0,mount_tag=hostshare \
    -cpu kvm64,+smep,+smap \
    -nographic \
    -monitor none \
    -append "console=ttyS0 nokaslr oops=panic panic=1" \
    -no-reboot &

QEMU_PID=$!
sleep 85
if ps -p $QEMU_PID > /dev/null; then
    sudo kill -9 $QEMU_PID
fi
