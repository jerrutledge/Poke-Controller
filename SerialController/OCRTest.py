import numpy as np
import cv2
import pytesseract
from pytesseract import Output
from pprint import pprint


capture_size = (1280, 720)
digits = False

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, capture_size[0])
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, capture_size[1])

while(True):
	# Capture frame-by-frame
	ret, frame = cap.read()

	# Our operations on the frame come here
	bw = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	# pprint(bw)
	# [top:bottom, left:right]
	bw = bw[-248:-70, 258:-258]
	# bw = cv2.threshold(bw, 40, 255, cv2.THRESH_OTSU)[1]
	# bw = cv2.bitwise_not(bw)

	# Output OCR of frame
	# Define config parameters.
	# '-l eng'  for using the English language
	# '--oem 1' for using LSTM OCR Engine
	if digits:
		config = ('-l eng digits')
	else:
		config = ('-l eng --oem 1 --psm 3')
	
	# Run tesseract OCR on image
	data = pytesseract.image_to_data(bw, config=config, output_type=Output.DICT)
	print((" ".join(data['text'])).strip())
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