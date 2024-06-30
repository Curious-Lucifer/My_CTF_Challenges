obj-m = EBH.o
KERNEL_VERSION=5.4

EXTRA_CFLAGS += -fno-stack-protector

all: 
	make -C ../linux-$(KERNEL_VERSION) M=$(PWD) modules

clean: 
	make -C ../linux-$(KERNEL_VERSION) M=$(PWD) clean
