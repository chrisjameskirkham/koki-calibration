THINGS := glib-2.0 opencv
CFLAGS += `pkg-config --cflags $(THINGS)`
LDFLAGS += `pkg-config --libs $(THINGS)` -lkoki

all: dist_at_focal_length

dist_at_focal_length: dist_at_focal_length.c
	$(CC) $(CFLAGS) $< -o $@ $(LDFLAGS)

clean:
	rm -rf dist_at_focal_length
