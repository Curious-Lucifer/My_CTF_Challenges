#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/fs.h>
#include <linux/uaccess.h>
#include <linux/proc_fs.h>
#include <linux/slab.h>
#include <linux/io.h>


#define GET_PHYSICAL _IO('G', 0)
#define PEEK_PHYSICAL _IO('P', 0)
#define WRITE_TO_ADDRESS _IO('W', 0)
#define WRITE_NOTE _IO('W', 1)
#define PROTECT_ADDRESS_START 0xffffffff00000000


MODULE_LICENSE("GPL");
MODULE_AUTHOR("Curious");


int PEEKED = 0;
int WRITTEN_TO_ADDRESS = 0;
int WRITTEN_NOTE = 0;


struct PeekPhysicalData {
    void *phyaddr;
    unsigned long peeksize;
    void *peekdata;
};

struct WriteToAddrData {
    void *target;
    void *src;
    unsigned long size;
};

struct WriteNoteData {
    void *src;
    unsigned long size;
};

long get_physical(void *ptr) {
    unsigned long long addr;
    if (copy_from_user(&addr, ptr, 8)) return -EFAULT;

    addr = virt_to_phys(addr);

    return copy_to_user(ptr, &addr, 8);
}

long peek_physical(struct PeekPhysicalData *ptr) {
    struct PeekPhysicalData data;
    if (copy_from_user(&data, ptr, sizeof(struct PeekPhysicalData))) return -EFAULT;

    void *virtaddr = ioremap(data.phyaddr, data.peeksize);
    if (!virtaddr) return -EFAULT;

    return copy_to_user(data.peekdata, virtaddr, data.peeksize);
}

long write_to_address(struct WriteToAddrData *ptr) {
    struct WriteToAddrData data;
    if (copy_from_user(&data, ptr, sizeof(struct WriteToAddrData))) return -EFAULT;

    if (data.target > PROTECT_ADDRESS_START) return -EFAULT;
    if (data.size > 0x60) return -EFAULT;

    return copy_from_user(data.target, data.src, data.size);
}

long write_note(struct WriteNoteData *ptr) {
    char note[0x60] = {0};
    struct WriteNoteData data;
    if (copy_from_user(&data, ptr, sizeof(struct WriteNoteData))) return -EFAULT;

    if (data.size > 0x68) return -EFAULT;

    return copy_from_user(&note, data.src, data.size);
}


static int device_open(struct inode *inode, struct file *filp) {
    return 0;
}

static int device_release(struct inode *inode, struct file *filp) {
    return 0;
}

static ssize_t device_read(struct file *filp, char *buf, size_t len, loff_t *offset) {
    return -EINVAL;
}

static ssize_t device_write(struct file *filp, const char *buf, size_t len, loff_t *offset) {
    return -EINVAL;
}

static long device_ioctl(struct file *filp, unsigned int ioctl_num, unsigned long ioctl_param) {
    long retval = 0;

    switch (ioctl_num) {
        case GET_PHYSICAL: 
            retval = get_physical(ioctl_param);
            break;
        case PEEK_PHYSICAL: 
            if (PEEKED) {
                retval = -EINVAL;
            } else {
                retval = peek_physical(ioctl_param);
                PEEKED = 1;
            }
            break;
        case WRITE_TO_ADDRESS: 
            if (WRITTEN_TO_ADDRESS) {
                retval = -EINVAL;
            } else {
                retval = write_to_address(ioctl_param);
                WRITTEN_TO_ADDRESS = 1;
            }
            break;
        case WRITE_NOTE: 
            if (WRITTEN_NOTE) {
                retval = -EINVAL;
            } else {
                retval = write_note(ioctl_param);
                WRITTEN_NOTE = 1;
            }
            break;
        default:
            retval = -EINVAL;
    }

    return retval;
}


static struct file_operations fops = {
    .read = device_read, 
    .write = device_write, 
    .unlocked_ioctl = device_ioctl,
    .open = device_open, 
    .release = device_release
};

struct proc_dir_entry *proc_entry = NULL;


int init_module(void) {
    proc_entry = proc_create("EBH", 0666, NULL, &fops);
    return 0;
}

void cleanup_module(void) {
    if (proc_entry) proc_remove(proc_entry);
}