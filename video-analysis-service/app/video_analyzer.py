import cv2
import numpy as np
from datetime import datetime


class VideoAnalyzer:
    def __init__(self, video_path):
        self.video_path = video_path

    def analyze(self):
        """
        Анализирует видео на наличие движения
        Возвращает: (has_movement, movement_percentage, analysis_time)
        """
        start_time = datetime.now()

        cap = cv2.VideoCapture(self.video_path)

        if not cap.isOpened():
            raise Exception("Could not open video file")

        motion_frames = 0
        total_frames = 0
        prev_frame = None

        max_frames = 1000
        frame_skip = 5

        try:
            while True:
                ret, frame = cap.read()
                total_frames += 1

                if not ret or total_frames > max_frames:
                    break

                if total_frames % frame_skip != 0:
                    continue

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.GaussianBlur(gray, (21, 21), 0)

                if prev_frame is None:
                    prev_frame = gray
                    continue

                frame_diff = cv2.absdiff(prev_frame, gray)
                thresh = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)[1]
                thresh = cv2.dilate(thresh, None, iterations=2)
                contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                movement_detected = False
                for contour in contours:
                    if cv2.contourArea(contour) > 500:
                        movement_detected = True
                        break

                if movement_detected:
                    motion_frames += 1

                prev_frame = gray

            analyzed_frames = total_frames // frame_skip
            if analyzed_frames > 0:
                movement_percentage = (motion_frames / analyzed_frames) * 100
            else:
                movement_percentage = 0.0

            has_movement = movement_percentage > 5.0

            analysis_time = (datetime.now() - start_time).total_seconds()

            return has_movement, movement_percentage, analysis_time

        finally:
            cap.release()