import winsound
import numpy as np
import os
import cv2, pandas
import time
import datetime
import threading


first_frame = None
status_list = [None, None]
times=[]
df=pandas.DataFrame(columns=["Start", "End"])

detection = False
detection_stopped_time = None
timer_strated = False
RECORD_DELAY_TIME = 5


video = cv2.VideoCapture(0)


fourcc = cv2.VideoWriter_fourcc(*'mp4v')

# background substraction
while True:
 check, frame = video.read()
 status = 0
 gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
 gray=cv2.GaussianBlur(gray,(21, 21),0)

 if first_frame is None:
     first_frame=gray
     continue

 delta_frame=cv2.absdiff(first_frame,gray)
 thresh_delta=cv2.threshold(delta_frame, 30, 255, cv2.THRESH_BINARY)[1]
 thresh_delta=cv2.dilate(thresh_delta, None, iterations=2)

 (cnts,_) =cv2.findContours(thresh_delta.copy(),cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# putting rectangles on detected objects
 for contour in cnts:
     if cv2.contourArea(contour) < 10000:
         continue
     status = 1
     (x, y, w, h)=cv2.boundingRect(contour)
     cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0), 3)
     cv2.putText(frame, "Status: {}".format('Movement detected'), (10,20), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2)    

 status_list.append(status)


 # recording and saving the file
 if status == 1 and status != 0:
     if detection:
         timer_strated = False
     else:
         detection = True
         alarm = True
         current_time = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
         out=cv2.VideoWriter(os.path.join('Recordings',f"{current_time}.mp4"), fourcc, 20.0, (640,480))
         print("Recording Started!")
 elif detection:
     if timer_strated:
         if time.time() - detection_stopped_time >= RECORD_DELAY_TIME:
             detection = False
             timer_strated = False
             out.release()
             print('Recording Stoped!')
     else:
         timer_strated = True
         detection_stopped_time = time.time()

 if detection:
     out.write(frame)

# setting alarm if motion is detected
 if status_list[-1]==1 and status_list[-2]==0:
     winsound.PlaySound('alarm.wav', winsound.SND_ASYNC)


     
# adding time to a csv file
 if status_list[-1]==1 and status_list[-2]==0:
     times.append(datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S"))
 if status_list[-1]==0 and status_list[-2]==1:
     times.append(datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S"))

# showing frames
 cv2.imshow("Gray Scale Frame",gray)
 cv2.imshow("Delta Frame",delta_frame)
 cv2.imshow("Threshold Frame",thresh_delta)
 cv2.imshow("SURVELLANCE MODE",frame)

# Breaking the loop
 key=cv2.waitKey(1)
 if key==ord('q'):
     if status ==1:
         times.append(datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S"))
     break

# appending dataframe for time
for i in range(0,len(times),2):
    df=df.append({"Start":times[i],"End":times[i + 1]},ignore_index=True)

# saving entry and exit time of the object to csv file
df.to_csv('Time.Record_{0}.csv'.format(datetime.datetime.now().strftime("%d-%m-%Y")))

# releasing the video capture frame
video.release()
cv2.destroyAllWindows
print (status)