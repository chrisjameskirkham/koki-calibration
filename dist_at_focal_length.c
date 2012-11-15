#include <stdio.h>
#include <glib.h>
#include <cv.h>
#include <highgui.h>

#include "koki.h"

int main(int argc, char** argv)
{

	if (argc != 4){
		printf("USAGE: %s <filename> <focal_length> <marker_width>\n", argv[0]);
		return 1;
	}

	const char *filename = argv[1];
	float focal_length = atof(argv[2]);
	float marker_width = atof(argv[3]);

	IplImage *frame = cvLoadImage(filename, CV_LOAD_IMAGE_GRAYSCALE);
	assert(frame != NULL);

	koki_t *koki = koki_new();
	koki_camera_params_t params;

	params.size.x = frame->width;
	params.size.y = frame->height;
	params.principal_point.x = params.size.x / 2;
	params.principal_point.y = params.size.y / 2;
	params.focal_length.x = focal_length;
	params.focal_length.y = focal_length;

	GPtrArray *markers = koki_find_markers(koki, frame, marker_width, &params);

	if (markers->len != 1){
		return 1;
	}

	koki_marker_t *marker;
	marker = g_ptr_array_index(markers, 0);

	printf("%f\n", marker->distance);

	koki_markers_free(markers);
	cvReleaseImage(&frame);

	return 0;

}
