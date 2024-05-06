FLAG = THJCC{Th1s_fl4G_i5n'7_fr3E,_bU7_It's_f0r_You!!!}

all: chal $(FLAG)

chal: chal.c
	gcc -no-pie -D_FORTIFY_SOURCE=2 -O2 -g chal.c -o chal -lseccomp

$(FLAG): $(FLAG).c
	gcc -shared "$<" -o "$@".so

