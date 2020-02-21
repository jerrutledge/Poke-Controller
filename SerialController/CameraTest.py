import numpy as np
import cv2
import pytesseract
from pytesseract import Output
from pprint import pprint

cap = cv2.VideoCapture(0)

while(True):
	# Capture frame-by-frame
	ret, frame = cap.read()

	# Our operations on the frame come here
	bw = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	bw = bw[70:250, 430:-1]
	# bw = cv2.threshold(bw, 250, 255, cv2.THRESH_OTSU)[1]
	# bw = cv2.bitwise_not(bw)

	# Output OCR of frame
	# Define config parameters.
	# '-l eng'  for using the English language
	# '--oem 1' for using LSTM OCR Engine
	config = ('-l eng digits')
	
	# Run tesseract OCR on image
	data = pytesseract.image_to_data(bw, config=config, output_type=Output.DICT)
	print("\n".join(data['text']))
	n_boxes = len(data['text'])
	for i in range(n_boxes):
		if int(data['conf'][i]) > 60:
			(x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
			bw = cv2.rectangle(bw, (x, y), (x + w, y + h), (0, 255, 0), 2)




	# Display the resulting frame
	cv2.imshow('frame',bw)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()