#include <stdio.h>
#include <stdint.h>
#include <assert.h>
#include <cv.h>
#include <highgui.h>
#include <stdlib.h>
#include <linux/videodev2.h>
#include "koki.h"

int main(int argc, const char* argv[])
{

	if (argc < 5){
		printf("USAGE: %s <device> <filename> <width> <height> [<wait>]\n", argv[0]);
		return 1;
	}

	const char *device = argv[1];
	const char *filename = argv[2];
	float width = atof(argv[3]);
	float height = atof(argv[4]);

	int wait = 0;
	if (argc == 6){
		wait = atoi(argv[5]);
	}

	int fd = koki_v4l_open_cam(device);
	struct v4l2_format fmt = koki_v4l_create_YUYV_format(width, height);
	koki_v4l_set_format(fd, fmt);

	int num_buffers = 1;
	koki_buffer_t *buffers;
	buffers = koki_v4l_prepare_buffers(fd, &num_buffers);

	koki_v4l_start_stream(fd);

	if (wait){
		fprintf(stderr, "Press [ENTER] to take photo...\n");
		getchar();
	}

	uint8_t *yuyv = koki_v4l_get_frame_array(fd, buffers);
	IplImage *frame = koki_v4l_YUYV_frame_to_grayscale_image(yuyv, width, height);
	cvSaveImage(filename, frame, 0);

	cvReleaseImage(&frame);
	koki_v4l_stop_stream(fd);

	return 0;
}
