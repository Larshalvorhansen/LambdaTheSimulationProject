CC = gcc
CFLAGS = -O2 -Wall -Wextra -std=c11 $(shell pkg-config --cflags portaudio-2.0)
LDFLAGS = $(shell pkg-config --libs portaudio-2.0) -lm
TARGET = tiny_rack
SRC = tiny_rack.c

all: $(TARGET)

$(TARGET): $(SRC)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

clean:
	rm -f $(TARGET)
