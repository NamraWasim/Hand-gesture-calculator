import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector

# Video capture
cap = cv2.VideoCapture(0)
detector = HandDetector(detectionCon=0.8, maxHands=1)

# Calculator buttons
buttons = [
    ['7', '8', '9', '/'],
    ['4', '5', '6', '*'],
    ['1', '2', '3', '-'],
    ['C', '0', '=', '+']
]

# Button dimensions
button_w, button_h = 80, 80
expression = ""

# Pinch detection variables
pinch_counter = 0
pinch_threshold = 25
confirm_frames = 3
button_pressed = False

def draw_buttons(img):
    for i in range(len(buttons)):
        for j in range(len(buttons[i])):
            x = j * button_w + 100
            y = i * button_h + 150
            cv2.rectangle(img, (x, y), (x + button_w, y + button_h), (100, 100, 250), -1)
            cv2.putText(img, buttons[i][j], (x + 30, y + 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.3, (255, 255, 255), 3)

def get_button(x, y):
    for i in range(len(buttons)):
        for j in range(len(buttons[i])):
            bx = j * button_w + 100
            by = i * button_h + 150
            if bx < x < bx + button_w and by < y < by + button_h:
                return buttons[i][j], (bx, by)
    return None, (0, 0)

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img, draw=False)

    draw_buttons(img)

    # Output box
    cv2.rectangle(img, (100, 50), (420, 130), (220, 220, 220), -1)
    cv2.putText(img, expression, (110, 110),
                cv2.FONT_HERSHEY_SIMPLEX, 1.8, (0, 0, 0), 4)

    if hands:
        hand = hands[0]
        lmList = hand["lmList"]

        if lmList:
            x1, y1 = lmList[8][0:2]  # Index
            x2, y2 = lmList[4][0:2]  # Thumb

            # Draw dots
            cv2.circle(img, (x1, y1), 10, (0, 255, 0), cv2.FILLED)
            cv2.circle(img, (x2, y2), 10, (0, 0, 255), cv2.FILLED)

            # Distance between index and thumb
            distance = ((x2 - x1)**2 + (y2 - y1)**2)**0.5

            if distance < pinch_threshold:
                pinch_counter += 1
                if pinch_counter >= confirm_frames and not button_pressed:
                    # Get center point between thumb and index
                    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                    button, (bx, by) = get_button(cx, cy)

                    if button:
                        cv2.rectangle(img, (bx, by), (bx + button_w, by + button_h), (0, 255, 255), 4)
                        if button == "=":
                            try:
                                expression = str(eval(expression))
                            except:
                                expression = "Error"
                        elif button == "C":
                            expression = ""
                        else:
                            expression += button

                        button_pressed = True
                        pinch_counter = 0
            else:
                pinch_counter = 0
                button_pressed = False

    else:
        pinch_counter = 0
        button_pressed = False

    cv2.imshow("Virtual Calculator", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
