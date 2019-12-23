import numpy as np
import cv2

cap = cv2.VideoCapture(0)

sigma = 0.33

while(True):
    ret, frame = cap.read()

    grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    med = np.median(grey)
    lower = int(max(0, (1.0 - sigma) * med))
    upper = int(min(255, (1.0 + sigma) * med))
    edges = cv2.Canny(grey, lower, upper) #, True)
    cv2.imshow('frame', frame)
    cv2.imshow('edges', edges)
    if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()

