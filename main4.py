import pygame
import sys
import time
import cv2
import mediapipe as mp
import csv
import numpy as np
import os

# _____________________초기 설정_______________
mp_pose = mp.solutions.pose.Pose()
clock = pygame.time.Clock()
pygame.font.init()
font = pygame.font.SysFont("arial", 50)

# 화면 설정
display_width = 1600
display_height = 900
pygame.display.set_caption("BaBilCo")
gameDisplay = pygame.display.set_mode((display_width, display_height))

# 배경 이미지 설정
mainBackgroundImg = pygame.image.load("C:\\capston\\배경\\메인화면배경.jpg")
mainBackgroundImg = pygame.transform.scale(mainBackgroundImg, (display_width, display_height))

motionCapture_BackImg = pygame.image.load("C:\\capston\\배경\\동작인식화면.jpg")
motionCapture_BackImg = pygame.transform.scale(motionCapture_BackImg, (display_width, display_height))

# 객체 이미지 설정

#버튼 사이즈
buttonSize_width = 250
buttonSize_height = 120

# 이미지 로드
def load_image(img_path, size):
    img = pygame.image.load(img_path)
    img = pygame.transform.scale(img, size)
    return img

# 최초 실행 시 이미지 로드
startButtonImg = load_image("C:\\capston\\객체\\start버튼.png", (buttonSize_width, buttonSize_height))
exitButtonImg = load_image("C:\\capston\\객체\\exit버튼.png", (buttonSize_width - 25, buttonSize_height - 25))
continueButtonImg = load_image("C:\\capston\\객체\\continue버튼.png", (buttonSize_width + 100, buttonSize_height))
howplayButtonImg = load_image("C:\capston\객체\howplay버튼.png", (buttonSize_width + 100, buttonSize_height - 25))
namingBoxImg = load_image("C:\capston\객체\네이밍칸.png", (700, 200))
nextButtonImg = load_image("C:\\capston\\객체\\next버튼.png", (200, 100))
promptImg = load_image("C:\capston\객체\prompt.png", (750, 400))


namingBox_x = display_width / 2  - 60
namingBox_y = display_height / 2 + 40
promptX = 720
promptY = 130
# ___________________________ 클래스 ________________________________________

# 버튼 클래스
class Button:
    def __init__(self, img_in, x, y, width, height, img_act, x_act, y_act, action=None):
        self.img_in = img_in
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.img_act = img_act
        self.x_act = x_act
        self.y_act = y_act
        self.action = action
        self.click = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if self.x <= mouse_pos[0] <= self.x + self.width and self.y <= mouse_pos[1] <= self.y + self.height:
                self.click = True
                if self.action:
                    self.action()

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        if self.x <= mouse_pos[0] <= self.x + self.width and self.y <= mouse_pos[1] <= self.y + self.height:
            surface.blit(self.img_act, (self.x_act, self.y_act))
        else:
            surface.blit(self.img_in, (self.x, self.y))


# ______________________________ 수행 함수 ________________________________

# 종료
def quitgame():
    pygame.quit()
    sys.exit()


# 1프레임 캡처
def cameraCapture(iscap):

    name_list = []

    #캡처한 이미지를 넣을 리스트
    image_list = []

    # 모션캡처화면 속 카메라 위치
    motionCap_cameraX = 150
    motionCap_cameraY = 120

    # 카메라 크기 설정
    CAMERA_WIDTH = 500
    CAMERA_HEIGHT = 700

    if not iscap:
        capture = False

        # 카메라 캡처 객체 생성
        cap = cv2.VideoCapture(0)

        # 관절 추출 모델 생성
        mp_holistic = mp.solutions.holistic.Holistic()

        # 프레임 카운트 변수
        frame_count = 0

        # 캡쳐된 프레임을 저장할 리스트
        frames = []


        # 3번 반복
        for i in range(3):
            # 5초 카운트 다운

            for j in range(5):
                # 화면을 배경 이미지로 채우기
                gameDisplay.blit(motionCapture_BackImg, (0, 0))
                gameDisplay.blit(namingBoxImg, (namingBox_x, namingBox_y))
                gameDisplay.blit(nextButtonImg, (1200, 700))
                gameDisplay.blit(promptImg, (promptX, promptY))
                nextButton = Button(nextButtonImg, 1200, 700, nextButtonImg.get_width(), nextButtonImg.get_height(),
                                    nextButtonImg, 1200, 700, None)
                nextButton.draw(gameDisplay)

                #캡처 시작 문구 띄우기
                capture_complete = font.render("Please take a pose with your", True, (255, 255, 255))
                gameDisplay.blit(capture_complete, (800, 200))

                capture_complete2 = font.render("entire body.", True, (255, 255, 255))
                gameDisplay.blit(capture_complete2, (800, 300))

                # 카메라에서 프레임 읽어오기
                _, image = cap.read()

                # 이미지를 화면 중앙에 맞춰서 출력하기
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


                results = mp_holistic.process(image)

                if results.pose_landmarks:
                    mp.solutions.drawing_utils.draw_landmarks(image, results.pose_landmarks, mp.solutions.holistic.POSE_CONNECTIONS)

                # 이미지 회전
                image = np.rot90(image)
                image = pygame.surfarray.make_surface(image)
                image = pygame.transform.scale(image, (CAMERA_WIDTH, CAMERA_HEIGHT))

                gameDisplay.blit(image, (motionCap_cameraX, motionCap_cameraY))
                


                # 카운트 다운 출력
                count_down = font.render(str(5 - j), True, (255, 255, 255))
                gameDisplay.blit(count_down, ((motionCap_cameraX - count_down.get_width()) // 2, (motionCap_cameraY - count_down.get_height()) // 2))

                pygame.display.flip()
                time.sleep(1)

            # 프레임 카운트 초기화
            frame_count = 0

            # 캡쳐할 프레임 수
            capture_count = 1

            # 캡쳐할 프레임 리스트 초기화
            frames = []

            # 1프레임 찍기
            while capture_count > 0:
                # 프롬프트 화면 전환
                gameDisplay.blit(promptImg, (promptX, promptY))

                # 카메라에서 프레임 읽어오기
                _, image = cap.read()

                # 이미지를 화면 중앙에 맞춰서 출력하기
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                results = mp_holistic.process(image)
                if results.pose_landmarks:
                    mp.solutions.drawing_utils.draw_landmarks(image, results.pose_landmarks,
                                                              mp.solutions.holistic.POSE_CONNECTIONS)

                    # 프레임 수가 0이면 캡쳐할 프레임 리스트 초기화
                    if frame_count == 0:
                        frames = []

                    frames = [frame_count] + [landmark.x * CAMERA_WIDTH for landmark in results.pose_landmarks.landmark] + [
                            landmark.y * CAMERA_HEIGHT for landmark in results.pose_landmarks.landmark]
                    # 캡쳐할 프레임 리스트에 현재 프레임 추가
                    frames.append(image)

                    # 프레임 카운트 증가
                    frame_count += 1

                    # 캡쳐할 프레임 수 감소
                    capture_count -= 1

                    # 캡쳐 완료 메시지 출력
                    capture_complete3 = font.render("Capture Complete.", True, (255, 255, 255))
                    gameDisplay.blit(capture_complete3, (800, 200))
                    capture_complete4 = font.render("Write a name of the motion.", True, (255, 255, 255))
                    gameDisplay.blit(capture_complete4, (800, 300))
                    pygame.display.flip()

                    # 0.5초 대기
                    time.sleep(0.5)

                # 이미지를 BGR로 변환하고 저장하기
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

  #############################이미지 변환하기
                image = image_change(image)

                #이미지 리스트에 내 이미지 추가
                image_list.append(image)



            while True :
                csv_filename = naming(nextButton)

                # 파일 이름이 이미 있는 경우 다시 쓰기
                if csv_filename in name_list:
                    gameDisplay.blit(promptImg, (promptX, promptY))
                    same_name = font.render("Please write another name", True, (255, 255, 255))
                    gameDisplay.blit(same_name, (800, 300))
                    gameDisplay.blit(namingBoxImg, (namingBox_x, namingBox_y))
                    pygame.display.flip()
                    continue

                else:
                    # csv 파일로 저장하기
                    with open("{}.csv".format(csv_filename), "w", newline="") as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow(
                            ["frame"] + ["x{}".format(j) for j in range(33)] + ["y{}".format(j) for j in range(33)])
                        writer.writerow([1])

                    name_list.append(csv_filename)
                    break

    image_check(image_list,namingBoxImg,name_list)
    pygame.display.flip()


def image_check(image_list,namingBoxImg,name_list):
    gameDisplay.blit(motionCapture_BackImg, (0, 0))
    nextButton = Button(nextButtonImg, 1350, 30, nextButtonImg.get_width(), nextButtonImg.get_height(),
                        nextButtonImg, 1350, 30, None)
    nextButton.draw(gameDisplay)
    namingBoxImg = pygame.transform.scale(namingBoxImg,(420,150))
    gameDisplay.blit(namingBoxImg, (140,650))
    gameDisplay.blit(namingBoxImg, (590,650))
    gameDisplay.blit(namingBoxImg, (1050,650))
    check = font.render(" < CHECK YOUR MOTION > ", True, (0,0,0))
    gameDisplay.blit(check,(580,90))

    #이름 출력
    name1 = font.render(name_list[0], True, (255, 255, 255))
    name2 = font.render(name_list[1], True, (255, 255, 255))
    name3 = font.render(name_list[2], True, (255, 255, 255))
    gameDisplay.blit(name1, (220, 690))
    gameDisplay.blit(name2, (670, 690))
    gameDisplay.blit(name3, (1130, 690))

    while nextButton.click == False:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            nextButton.handle_event(event)
        display_image(image_list)
        pygame.display.update()


###########이미지 변환하기##########################
def image_change(image):
    image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    resized_image = cv2.resize(image,(500,400))
    image = pygame.surfarray.make_surface(resized_image)
    return image


###########이미지 3개 띄우기##########3
##전역변수 이거는 약간의 수정이 필요할 수도;;

x = 150
y = 150
def display_image(image_list):
    global x,y
    padding = 50
    width = 400
    image_num = len(image_list)
    for i in range(image_num):
        gameDisplay.blit(image_list[i], (x + (width + padding) * i, y))
    pygame.display.flip()

def naming(nextButton):
    # 텍스트 입력
    text = ""
    namingBoxButton = Button(namingBoxImg, namingBox_x, namingBox_y, namingBoxImg.get_width(), namingBoxImg.get_height(), namingBoxImg, namingBox_x, namingBox_y, None)


    while nextButton.click == False:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            nextButton.handle_event(event)
            namingBoxButton.handle_event(event)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    text = text[:-1]  # 마지막 글자 삭제
                    gameDisplay.blit(namingBoxImg, (namingBox_x, namingBox_y))
                    textline = font.render(text, True, (255, 255, 255))
                    gameDisplay.blit(textline, (namingBox_x + 100, namingBox_y + 50))

                else:
                    text += event.unicode  # 글자 추가

                    # 작성란에 텍스트 그리기
                    textline = font.render(text, True, (255, 255, 255))
                    gameDisplay.blit(textline, (namingBox_x + 100, namingBox_y + 50))

            pygame.display.update()

    nextButton.click = False
    return text

#디버깅에 쓰일 마우스 클릭 함수
def mouseClickCheck(event):
    if event.type == pygame.MOUSEBUTTONDOWN:
        mouse_pos = pygame.mouse.get_pos()
        print(mouse_pos[0], mouse_pos[1])

# ______________________________배경 함수______________________________________________________________

def motionCapScreen():
    motionCapS = True

    isCap = False

    while motionCapS:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quitgame()

        gameDisplay.blit(motionCapture_BackImg, (0, 0))

        # 한번만 호출하여 캡처
        if isCap == False:
            cameraCapture(isCap)

        isCap = True

        pygame.display.flip()


def mainScreen():
    mainS = True

    # 버튼 생성
    startButton = Button(startButtonImg, 1250, 600, startButtonImg.get_width() + 30, startButtonImg.get_height() + 30,
                         startButtonImg, 1260, 590, motionCapScreen)
    exitButton = Button(exitButtonImg, 1260, 720, exitButtonImg.get_width() + 30, exitButtonImg.get_height() + 30,
                        exitButtonImg, 1270, 710, quitgame)
    continueButton = Button(continueButtonImg, 100, 590, continueButtonImg.get_width() + 30,
                            continueButtonImg.get_height(), continueButtonImg, 110, 580)
    howplayButton = Button(howplayButtonImg, 100, 710, howplayButtonImg.get_width() + 30, howplayButtonImg.get_height(),
                           howplayButtonImg, 110, 700)

    while mainS:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quitgame()
            for button in (startButton, exitButton, continueButton, howplayButton):
                button.handle_event(event)

        gameDisplay.blit(mainBackgroundImg, (0, 0))
        for button in (startButton, exitButton, continueButton, howplayButton):
            button.draw(gameDisplay)

        pygame.display.update()


# 메인, 호출

mainScreen()
