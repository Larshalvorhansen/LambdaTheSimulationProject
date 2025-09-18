CC ?= cc
CFLAGS := -O2 -Wall -Wextra -std=c11 $(shell pkg-config --cflags raylib)
LDFLAGS := $(shell pkg-config --libs raylib) -lm

all: econ_patch_c

econ_patch_c: main.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

clean:
	rm -f econ_patch_c
