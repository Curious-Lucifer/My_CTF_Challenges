buf = open('EBH.ko', 'rb').read()

idx = buf.index(b'\x48\x8b\x74\x24\x08\x48\x83\xfa\x60\x77\x15')
buf = buf[:idx] + b'\x48\x8b\x74\x24\x08\x48\x83\xfa\x68\x77\x15' + buf[idx + 11:]

open('EBH.ko', 'wb').write(buf)