#!/usr/bin/env python
import asyncio
import sys
import RPi.GPIO as GPIO
import time
import pika
import json
import threading
import math

gpiochannel1 = [0, 5, 6, 13, 19, 26]
# pin 5 and 6 acceleration
# pin 13 and 19 acceleration
# pin 22 and 26 are the PWM control pins

gpiochannel2 = [17, 27, 22, 10, 9, 11]
# pin 27 and 22 acceleration
# pin 10 and 9 acceleration
# pin 17 and 11 are the PWM control pins

# for board setting
GPIO.setmode(GPIO.BCM)

# setup to pin mode
for i in gpiochannel1:
    GPIO.setup(i, GPIO.OUT)
for i in gpiochannel2:
    GPIO.setup(i, GPIO.OUT)

# rgb in pwm mode in a list
motorDriver1_1 = GPIO.PWM(26, 100)
motorDriver1_2 = GPIO.PWM(0, 100)
motorDriver2_1 = GPIO.PWM(17, 100)
motorDriver2_2 = GPIO.PWM(11, 100)

# ultrasonic points
# front
FTRIG = 21
FECHO = 20
# back
BTRIG = 16
BECHO = 12
MIN_DIST = 0  # Minimum distance to detect an object, in centimeters
MAX_DIST = 15  # Maximum distance to detect an object, in centimeters
UltFront = False
UltBack = False

GPIO.setup(FTRIG, GPIO.OUT)
GPIO.setup(FECHO, GPIO.IN)

GPIO.setup(BTRIG, GPIO.OUT)
GPIO.setup(BECHO, GPIO.IN)

def findPercents(inp, mi, ma, v):
    va = (inp - mi) * 100 / (ma - mi)
    if v == 100:
        va = v - va
    if va > 100:
        return 100
    elif va < 0:
        return 0
    else:
        return int(va)


def AccelerationOperation(rightHand):
    try:
        angle = 0
        acc = 0
        x3 = x4 = 0
        if len(rightHand) > 0:
            x0, x1 = rightHand[0][0], rightHand[12][0]
            y0, y1 = rightHand[0][1], rightHand[12][1]
            x3, x4 = rightHand[3][0], rightHand[4][0]
            acc = findPercents(
                math.hypot(x0-x1, y0-y1), 50, 140, 0)
            # accleration speed start
            motorDriver1_1.start(acc)
            motorDriver1_2.start(acc)
            motorDriver2_1.start(acc)
            motorDriver2_2.start(acc)
            # neutral Acceleration
            if acc > 0:
                angle = abs(math.atan2(y1 - y0, x1 - x0) * 180 / math.pi)

                # left side
                if angle < 60:
                    GPIO.output(13, 0)
                    GPIO.output(19, 1)
                    GPIO.output(5, 1)
                    GPIO.output(6, 0)
                    GPIO.output(27, 1)
                    GPIO.output(22, 0)
                    GPIO.output(10, 0)
                    GPIO.output(9, 1)
                # right side
                elif angle > 120:
                    GPIO.output(13, 1)
                    GPIO.output(19, 0)
                    GPIO.output(5, 0)
                    GPIO.output(6, 1)
                    GPIO.output(27, 0)
                    GPIO.output(22, 1)
                    GPIO.output(10, 1)
                    GPIO.output(9, 0)
                else:
                    if x3 > x4:
                        if UltFront:  # if ultrasonic not true acc happens
                            motorDriver1_1.start(0)
                            motorDriver1_2.start(0)
                            motorDriver2_1.start(0)
                            motorDriver2_2.start(0)
                            GPIO.output(13, 0)
                            GPIO.output(19, 0)
                            GPIO.output(5, 0)
                            GPIO.output(6, 0)
                            GPIO.output(27, 0)
                            GPIO.output(22, 0)
                            GPIO.output(10, 0)
                            GPIO.output(9, 0)
                        else:
                            print("direction front ")
                            GPIO.output(13, 0)
                            GPIO.output(19, 1)
                            GPIO.output(5, 0)
                            GPIO.output(6, 1)
                            GPIO.output(27, 0)
                            GPIO.output(22, 1)
                            GPIO.output(10, 0)
                            GPIO.output(9, 1)
                    else:  # forward Acceleration
                        if UltBack:  # if ultrasonic not true acc happens
                            motorDriver1_1.start(0)
                            motorDriver1_2.start(0)
                            motorDriver2_1.start(0)
                            motorDriver2_2.start(0)
                            GPIO.output(13, 0)
                            GPIO.output(19, 0)
                            GPIO.output(5, 0)
                            GPIO.output(6, 0)
                            GPIO.output(27, 0)
                            GPIO.output(22, 0)
                            GPIO.output(10, 0)
                            GPIO.output(9, 0)
                        else:
                            print("direction Back")
                            GPIO.output(13, 1)
                            GPIO.output(19, 0)
                            GPIO.output(5, 1)
                            GPIO.output(6, 0)
                            GPIO.output(27, 1)
                            GPIO.output(22, 0)
                            GPIO.output(10, 1)
                            GPIO.output(9, 0)

            else:
                motorDriver1_1.start(0)
                motorDriver1_2.start(0)
                motorDriver2_1.start(0)
                motorDriver2_2.start(0)
                GPIO.output(13, 0)
                GPIO.output(19, 0)
                GPIO.output(5, 0)
                GPIO.output(6, 0)
                GPIO.output(27, 0)
                GPIO.output(22, 0)
                GPIO.output(10, 0)
                GPIO.output(9, 0)
            print("Acceleration:", acc)
        else:
            motorDriver1_1.start(0)
            motorDriver1_2.start(0)
            motorDriver2_1.start(0)
            motorDriver2_2.start(0)
            GPIO.output(13, 0)
            GPIO.output(19, 0)
            GPIO.output(5, 0)
            GPIO.output(6, 0)
            GPIO.output(27, 0)
            GPIO.output(22, 0)
            GPIO.output(10, 0)
            GPIO.output(9, 0)
        # carmove true = forward
        #        flase = backward

        # 120 >= left
        # 60 >= right

        channel.basic_publish(exchange='', routing_key='car_data', body=json.dumps(
            {"Speed": acc, "CarDirection": angle, "CarMove": x3 > x4, "UltFront": UltFront,
             "UltFrontData": UltFrontdata, "UltBack": UltBack, "UltBackData": UltBackdata}))

    except KeyboardInterrupt:
        print("Force exit operation")
        motorDriver1_1.start(0)
        motorDriver1_2.start(0)
        motorDriver2_1.start(0)
        motorDriver2_2.start(0)
        GPIO.output(13, 0)
        GPIO.output(19, 0)
        GPIO.output(5, 0)
        GPIO.output(6, 0)
        GPIO.output(27, 0)
        GPIO.output(22, 0)
        GPIO.output(10, 0)
        GPIO.output(9, 0)
        sys.exit()
    except Exception as e:
        print(e)
        sys.exit(1)


def AccessingTheGPIO(handData):
    # print(handData, width, height)
    rightHand = handData["right"]  # right hand for controlling the car
    leftHand = handData["left"]  # left hand for to controllig the RGB led
    print(rightHand)
    # Acceleration threading
    if len(rightHand) > 0:
        AccelerationOperation(rightHand)
        # rightThread = threading.Thread(
        #     target=AccelerationOperation, args=(rightHand, ch)
        # )
        # # after defineing the thread model we need to start the thread
        # rightThread.start()
    else:
        motorDriver1_1.start(0)
        motorDriver1_2.start(0)
        motorDriver2_1.start(0)
        motorDriver2_2.start(0)
        GPIO.output(13, 0)
        GPIO.output(19, 0)
        GPIO.output(5, 0)
        GPIO.output(6, 0)
        GPIO.output(27, 0)
        GPIO.output(22, 0)
        GPIO.output(10, 0)
        GPIO.output(9, 0)

# ultrasonic function


def ObjectDetectFront():
    try:
        while True:
            GPIO.output(FTRIG, False)
            time.sleep(0.0001)
            GPIO.output(FTRIG, True)
            time.sleep(0.00001)
            GPIO.output(FTRIG, False)

            while GPIO.input(FECHO) == 0:
                pulse_start = time.time()

            while GPIO.input(FECHO) == 1:
                pulse_end = time.time()

            pulse_duration = pulse_end - pulse_start

            distance = pulse_duration * 17150

            distance = round(distance, 2)

            global UltFront
            global UltFrontdata

            UltFrontdata = distance

            if distance > MIN_DIST and distance < MAX_DIST:
                # print(f"True {distance}")
                UltFront = True
                # Add code here to indicate the presence of an object (e.g. turn on a buzzer, activate a motor, etc.)
            else:
                # print(f"False {distance}")
                UltFront = False
                # Add code here to indicate the absence of an object (e.g. turn off a buzzer, deactivate a motor, etc.)

    except KeyboardInterrupt:
        # Clean up the GPIO pins when the program is interrupted
        GPIO.cleanup()

# ultrasonic function


def ObjectDetectBack():
    try:
        while True:
            GPIO.output(BTRIG, False)
            time.sleep(0.0001)
            GPIO.output(BTRIG, True)
            time.sleep(0.00001)
            GPIO.output(BTRIG, False)

            while GPIO.input(BECHO) == 0:
                pulse_start = time.time()

            while GPIO.input(BECHO) == 1:
                pulse_end = time.time()

            pulse_duration = pulse_end - pulse_start

            distance = pulse_duration * 17150

            distance = round(distance, 2)

            global UltBack
            global UltBackdata
            UltBackdata = distance

            if distance > MIN_DIST and distance < MAX_DIST:
                # print(f"True {distance}")
                UltBack = True
                # Add code here to indicate the presence of an object (e.g. turn on a buzzer, activate a motor, etc.)
            else:
                # print(f"False {distance}")
                UltBack = False
                # Add code here to indicate the absence of an object (e.g. turn off a buzzer, deactivate a motor, etc.)

    except KeyboardInterrupt:
        # Clean up the GPIO pins when the program is interrupted
        GPIO.cleanup()

# RabbitMQ receiveing data


def callback(ch, method, properties, body):
    data = json.loads(body)
    landmarks = data
    AccessingTheGPIO(landmarks)  # calling the Accessing function

    # Acknowledge that we have received and processed the message
    ch.basic_ack(delivery_tag=method.delivery_tag)

    # print(landmarks)  # Replace this with your own processing code
    # GPIOthread = threading.Thread(
    #     target=AccessingTheGPIO, args=(landmarks, ch))
    # GPIOthread.start()


if __name__ == "__main__":
    cred = pika.PlainCredentials('guest', 'guest')
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='192.168.1.11', port=5672, virtual_host='/', credentials=cred))

    global channel

    channel = connection.channel()

    channel.queue_declare(queue='hand_gesture_data')

    # this threading part for to detect Front ultrasonic
    ultrasonicF = threading.Thread(target=ObjectDetectFront)
    ultrasonicF.start()

    # this threading part for to detect Back ultrasonic
    ultrasonicB = threading.Thread(target=ObjectDetectBack)
    ultrasonicB.start()

    channel.basic_consume(queue='hand_gesture_data',
                          on_message_callback=callback)

    print('Waiting for hand gesture data. To exit press CTRL+C')
    channel.start_consuming()
