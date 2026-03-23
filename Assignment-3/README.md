README file

This assignment 3 contains two links to YouTube videos which show output tracking videos based on two input videos. 

https://youtu.be/pWMBlgs7v4I

https://www.youtube.com/watch?v=B35yWWD-X4Y

Additionally,
The link to the Hugging Face repository which contains the .parquet dataset file for the detections is:
https://huggingface.co/datasets/shreyonroy/Assignment3_Parquet_Drone_Detections

There is also a .ipynb file that I attached which contains my code. 
The file is called Shreyon Roy_Assignment 3_Artificial_Intelligence.ipynb

I selected my dataset from Roboflow Universe: https://universe.roboflow.com/drone-litid/drone-detection-ndcez
It contains 927 images of drones and I trained my YOLOv26 model off this after downloading it as a .yaml file. I trained the model for 20 epochs. This ensured that the model would detect the drone properly from the frames of the input videos. I set the resoution size of the training to 640px. Then, I used the frames retrieved from the input videos and I ran my detector on it without saving it and ran it at a confidence threshold of 0.15. I experimented with different confidence thresholds and noticed that some frames where the drone was appearing in the video was not getting detected because it's confidence level in the boundary box was low. So I decided on 0.15 for the confidence threshold. 
For the Kalmar Filter state, I set an X and Y as the center of the boundary box whose coordinates I found by dividing the distances of the boundary box's width and height. I had an X-velocity and Y-velocity. This was the state vector. For the state transition matrix, I used the equation of new-position = old_position + velocity*(change_in_time) and set the dt value = 1.0 which indicates a constant velocity model. This is used in tracker.predict(). For noise paramters, I used these values: kf.P *= 1000. kf.R = 5 kf.Q = 0.1 where P = 1000 is the initial covariance, R = 5 is the measurement noise for evlauating jitters in YOLOv26's detection. Q = 0.1 is the process noise which records the imperfections in the movement of the drone like inertia. 

In my code's for loop, the tracker.predict() is called on every frame but the tracker.update(z) when YOLO detects the actual drone in the frame. In the filter, the update and predict work together when a drone is detected. If there is a missed detection, the update call is skipped and the line is drawn based on the last known velocity. Therefore, this prevents the green line from breaking or disappearing if the drone is unseen or moving too fast. 
