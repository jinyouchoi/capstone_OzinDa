import cv2
import mediapipe as mp
import numpy as np
import time
from dtw import dtw

cv2.namedWindow("Window", cv2.WINDOW_NORMAL)
cv2.namedWindow("Camera", cv2.WINDOW_NORMAL)

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

cap = cv2.VideoCapture(0)

countdown = 5
while countdown > 0:
    print(f"{countdown}초 후 동작을 인식하겠습니다.")
    time.sleep(1)
    countdown -= 1

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    start = time.time()
    motion = [] #비교할 첫번 째 모션 -> 정지된 캡처 이미지
    while time.time()-start < 5:
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = pose.process(frame_rgb) # MediaPipe 라이브러리에서 제공하는 Pose 모델을 사용하여 입력 이미지에서 사람의 동작을 감지하고 관절 위치를 추출

        if results.pose_landmarks is not None: #pose_landmarks 속성에 포즈 관절 위치 정보 저
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
             #관절 위치 정보를 리스트에 저장 : motion
            motion.append([lmk.x*w for lmk in results.pose_landmarks.landmark] + [lmk.y*h for lmk in results.pose_landmarks.landmark])

        cv2.imshow("Camera", frame)
        if cv2.waitKey(1) == ord('q'):
            break

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    start = time.time()
    count = 0
    while True:
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = pose.process(frame_rgb)
        if results.pose_landmarks is not None:
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            #실시간 현재 관절 위치 정보 리스트에 저장 : curr_motion
            curr_motion = [lmk.x*w for lmk in results.pose_landmarks.landmark] + [lmk.y*h for lmk in results.pose_landmarks.landmark] 

            if len(curr_motion) > 0 and len(motion) > 0:
                # dtw로 유사도 검증 : motion 리스트 vs curr_motion 리스트 
                d, _, _, _ = dtw(np.array(motion), np.array([curr_motion]), dist=lambda x, y: np.linalg.norm(x - y, ord=1))
                # 일정 유사도 이하이면 동일한 것으로 취급 
                if d < 13:#줄일수록 빡빡함
                    count += 1

                # 카운트 횟수 출력
                cv2.putText(frame, f"Count: {count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

            motion = [curr_motion]

        cv2.imshow("Camera", frame)
        if cv2.waitKey(1) == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
