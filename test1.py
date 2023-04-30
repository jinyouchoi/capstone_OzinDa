import cv2
import mediapipe as mp
import pygame
import time

# 파이게임 초기화
pygame.init()

# 화면 크기 설정
screen_width = 640
screen_height = 480
screen = pygame.display.set_mode((screen_width, screen_height))

# 미디어 파이프 초기화
mp_holistic = mp.solutions.holistic
holistic = mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# 카운트 다운 변수 초기화
count = 5

# 카운트 다운 시작 시간 기록
start_time = time.time()

# 게임 루프
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # 검정색 화면에 하얀색으로 카운트 다운 텍스트 출력
    screen.fill((0, 0, 0))
    if count > 0:
        elapsed_time = time.time() - start_time
        if elapsed_time >= 1:
            count -= 1
            start_time = time.time()
        if count == 0:
            pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(screen_width // 2 - 50, screen_height // 2 - 50, 100, 100))
        else:
            font = pygame.font.Font(None, 100)
            text = font.render(f"{count}", True, (255, 255, 255))
            screen.blit(text, (screen_width // 2 - 50, screen_height // 2 - 50))

    # 5초 후 "동작을 인식 중입니다!" 텍스트 출력
    elif count == 0:
        elapsed_time = time.time() - start_time
        if elapsed_time >= 5:
            screen.fill((0, 0, 0))
            font = pygame.font.Font(None, 50)
            text = font.render("motion capture now!", True, (255, 255, 255))
            screen.blit(text, (10, 10))

            # 카메라로부터 영상 프레임 읽기
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # 미디어 파이프를 이용하여 키 포인트 추출
            results = holistic.process(frame)
            if results.pose_landmarks:
                # 키 포인트 좌표 추출
                for landmark in results.pose_landmarks.landmark:
                    cx, cy = int(landmark.x * screen_width), int(landmark.y * screen_height)
                    cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)

                # 추출한 키 포인트를 화면에 출력
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                frame = cv2.resize(frame, (screen_width, screen_height))
                frame = pygame.surfarray.make_surface(frame)
                screen.blit(frame, (0, 50))

            # "모션 이름 짓기" 버튼 출력
            pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(screen_width - 150, screen_height - 50, 150, 50))
            font = pygame.font.Font(None, 25)
            text = font.render("naming", True, (0, 0, 0))
            screen.blit(text, (screen_width - 150 + 25, screen_height - 50 + 15))

            # 화면 업데이트
            pygame.display.flip()

    # 화면 업데이트
    pygame.display.flip()
