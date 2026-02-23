README file

This assignment contains three .parquet files. 
One file is named car_exterior_detections_frames.parquet. This contains the object detections from the frame images in the YouTube video provided.
Another file is named car_exterior_detections_query_images_huggingface.parquet. This contains the object detections from the frame images in the Hugging Face dataset for query images.
The next file is named car_exterior_retrieval_query_images.parquet. This contains information about the retrieval output where the query images are mapped to specific contiguous time intervals in the YouTube video.

The link to the Hugging Face repository which contains the .parquet files is:
https://huggingface.co/datasets/shreyonroy/Assignment2_Parquet/tree/main

The detections parquet file for the frames is organized by rows with column names like video_id, frame_index, class_label, bounding_box, and confidence_score.
The detections parquet file for the query images is organized by rows with column names like video_id, query_index, query_timestamp, class_label, bounding_box, and confidence_score. 
The retrieval parquet file is organized by rows with column names like query_index, start_timestamp, end_timestamp, class_label, and number_of_supporting_detections.

There is also a .ipynb file that I attached which contains my code and logic with comments. 
The file is called Shreyon Roy_Assignment 2_Artificial_Intelligence.ipynb.
