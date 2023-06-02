import pygame
import sys
import time
import cv2
import mediapipe as mp
import csv
import numpy as np
import os
import json
import pandas as pd
import glob


# _____________________초기 설정_______________
mp_pose = mp.solutions.pose.Pose()
clock = pygame.time.Clock()
pygame.font.init()
font = pygame.font.SysFont("neo둥근모pro", 40)
font_countdown = pygame.font.SysFont("neo둥근모pro", 200)

answer_name_index = [] # 문제에 포함되는 모션들의 이름만 저장.

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

setQuestion_BackImg = pygame.image.load("C:\capston\배경\문제출제화면.jpg")
setQuestion_BackImg = pygame.transform.scale(setQuestion_BackImg, (display_width, display_height))

levelSelect_BackImg = pygame.image.load("C:\\capston\\배경\\레벨선택화면.jpg")
levelSelect_BackImg = pygame.transform.scale(levelSelect_BackImg, (display_width, display_height))

blackImg = pygame.image.load("C:\capston\배경\검정화면.jpg")
blackImg = pygame.transform.scale(blackImg, (display_width, display_height))

# 이미지의 알파 채널 활성화
blackImg = blackImg.convert_alpha()

# 투명하게 만들기
blackImg.set_alpha(180) #255로 할수록 불투명


# 객체 이미지 설정

# 버튼 사이즈
buttonSize_width = 250
buttonSize_height = 120

how_many_level = 2 #레벨이 총 몇개 있는가? -> 총 6레벨이지만, 우선 2로..

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
prob_promptImg = load_image("C:\capston\객체\prob_prompt.png", (750, 710))

level_complete= load_image("C:\\capston\\객체\\levelComplete.png", (600,700))
nextLevel = load_image("C:\\capston\\객체\\nextLevel.png", (370,100))

level1 = load_image("C:\\capston\\객체\\레벨1.png", (150, 150))
level2 = load_image("C:\\capston\\객체\\레벨2.png", (150, 150))
level3 = load_image("C:\\capston\\객체\\레벨3.png", (150, 150))
level4 = load_image("C:\\capston\\객체\\레벨4.png", (150, 150))
level5 = load_image("C:\\capston\\객체\\레벨5.png", (150, 150))
level6 = load_image("C:\\capston\\객체\\레벨6.png", (150, 150))

full_heartImg = load_image("C:\\capston\\객체\\full_heart.png", (50, 50))
empty_heartImg = load_image("C:\\capston\\객체\\empty_heart.png", (50, 50))

level_fail= load_image("C:\\capston\\객체\\failLevel.png", (600, 700))

# 관련 변수
namingBox_x = display_width / 2 - 60
namingBox_y = display_height / 2 + 40
promptX = 720
promptY = 130

prob_motion_info = {0: None, 1: None, 2: None } #문제에 입력된 동작이름
prob_motion_proc = [] #문제에 입력된 동작의 번호로 표기 -> 순서

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

    def enter_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
            mouse_pos = pygame.mouse.get_pos()
            keys = pygame.key.get_pressed()

            if (self.x <= mouse_pos[0] <= self.x + self.width and self.y <= mouse_pos[1] <= self.y + self.height) or \
                    keys[pygame.K_RETURN]:
                self.click = True
                if self.action:
                    self.action()

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        if self.x <= mouse_pos[0] <= self.x + self.width and self.y <= mouse_pos[1] <= self.y + self.height:
            surface.blit(self.img_act, (self.x_act, self.y_act))
        else:
            surface.blit(self.img_in, (self.x, self.y))


class Button2:
    def __init__(self, img_in, x, y, width, height, img_act, x_act, y_act, nameList, level_num, action=None):
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
        self.level_num = level_num
        self.nameList = nameList

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if self.x <= mouse_pos[0] <= self.x + self.width and self.y <= mouse_pos[1] <= self.y + self.height:
                self.click = True
                if self.action:
                    self.action(self.nameList, self.level_num)

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

#continue 화면
def continueGame():
    IMAGE_WIDTH = display_width // 3
    IMAGE_HEIGHT = display_height

    # 이미지 불러오기
    image = pygame.image.load("C:\\capston\\객체\\네이밍칸.png").convert_alpha()

    # 이미지 크기 조정
    image = pygame.transform.scale(image, (420, 150))

    # 이미지 파일 경로
    folder_path = "C:\\capston"
    image_files = [file for file in os.listdir(folder_path) if file.startswith("frame_") and file.endswith(".jpg")]

    gameDisplay.blit(motionCapture_BackImg, (0, 0))

    nextButton = Button(nextButtonImg, 1350, 30, nextButtonImg.get_width(), nextButtonImg.get_height(),
                        nextButtonImg, 1350, 30, None)
    nextButton.draw(gameDisplay)
    gameDisplay.blit(image, (140, 650))
    gameDisplay.blit(image, (590, 650))
    gameDisplay.blit(image, (1050, 650))
    check = font.render(" < CHECK YOUR MOTION > ", True, (0, 0, 0))
    gameDisplay.blit(check, (580, 90))

    file_list = []
    for image_file in image_files:
        file_name = image_file.replace("frame_", "").replace(".jpg", "")
        file_list.append(file_name)

    name1 = font.render(file_list[0], True, (255, 255, 255))
    name2 = font.render(file_list[1], True, (255, 255, 255))
    name3 = font.render(file_list[2], True, (255, 255, 255))
    gameDisplay.blit(name1, (220, 690))
    gameDisplay.blit(name2, (670, 690))
    gameDisplay.blit(name3, (1130, 690))

    # 이미지 로드 및 크기 조정
    images = []
    for image_file in image_files:
        image_path = os.path.join(folder_path, image_file)
        image = pygame.image.load(image_path)
        image = pygame.transform.scale(image, (350, 500))
        images.append(image)

    # 이미지 위치 설정
    image_positions = [
        (170, 150),  # 왼쪽 이미지 위치
        (625, 150),  # 가운데 이미지 위치
        (1090, 150),  # 오른쪽 이미지 위치
    ]

    while nextButton.click == False:
        # 이미지 그리기
        for image, position in zip(images, image_positions):
            gameDisplay.blit(image, position)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            nextButton.handle_event(event)
            if nextButton.click == True:
                level_select(file_list)
                pygame.display.update()
        # 화면 업데이트
        pygame.display.flip()

    return


# 1프레임 캡처
def cameraCapture(iscap):
    nameList = []
    image_list = []  # 캡처한 이미지 넣을 리스트
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

        five_time = 5  # 카운트 다운 횟수

        # 3번 반복
        for i in range(3):

            while five_time > 0.0:
                # 화면을 배경 이미지로 채우기
                gameDisplay.blit(motionCapture_BackImg, (0, 0))
                gameDisplay.blit(namingBoxImg, (namingBox_x, namingBox_y))
                gameDisplay.blit(nextButtonImg, (1200, 700))
                gameDisplay.blit(promptImg, (promptX, promptY))
                nextButton = Button(nextButtonImg, 1200, 700, nextButtonImg.get_width(), nextButtonImg.get_height(),
                                    nextButtonImg, 1200, 700, None)
                nextButton.draw(gameDisplay)

                # 캡처 시작 문구 띄우기
                capture_complete = font.render("5초 후에 자신의 신체 전체를", True, (255, 255, 255))
                gameDisplay.blit(capture_complete, (800, 200))

                capture_complete2 = font.render("카메라에 인식해주세요!", True, (255, 255, 255))
                gameDisplay.blit(capture_complete2, (800, 300))

                # 카메라에서 프레임 읽어오기
                _, image = cap.read()

                # 이미지를 화면 중앙에 맞춰서 출력하기
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                results = mp_holistic.process(image)

                if results.pose_landmarks:
                    mp.solutions.drawing_utils.draw_landmarks(image, results.pose_landmarks,
                                                              mp.solutions.holistic.POSE_CONNECTIONS)

                # 이미지 회전
                image = np.rot90(image)
                image = pygame.surfarray.make_surface(image)
                image = pygame.transform.scale(image, (CAMERA_WIDTH, CAMERA_HEIGHT))

                gameDisplay.blit(image, (motionCap_cameraX, motionCap_cameraY))

                # 제한 시간을 1초씩 감소
                five_time -= 0.1

                # 카운트 다운 출력
                count_down = font.render('time : {:.1f}'.format(five_time), True, (255, 255, 255))
                gameDisplay.blit(count_down, (
                    (motionCap_cameraX - count_down.get_width()) // 2,
                    (motionCap_cameraY - count_down.get_height()) // 2))

                pygame.display.flip()
                clock.tick(10)

            five_time = 5  # 카운트 다운 횟수 초기화

            # 프레임 카운트 초기화
            frame_count = 0

            # 캡쳐할 프레임 수
            capture_count = 1

            # 캡쳐할 프레임 리스트 초기화
            frames = []

            mp_drawing = mp.solutions.drawing_utils
            mp_pose = mp.solutions.pose

            gameDisplay.blit(promptImg, (promptX, promptY))

            pygame.display.flip()

            # mideapipe 모델
            # with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            # 1 프레임 찍기
            while capture_count > 0:
                motion = []  # 비교할 첫번 째 모션

                # 프롬프트 화면 전환
                gameDisplay.blit(promptImg, (promptX, promptY))

                ret, frame = cap.read()
                h, w, _ = frame.shape

                # 이미지를 화면 중앙에 맞춰서 출력하기
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                results = mp_holistic.process(image)

                if results.pose_landmarks:
                    mp.solutions.drawing_utils.draw_landmarks(image, results.pose_landmarks,
                                                              mp.solutions.holistic.POSE_CONNECTIONS)

                # results = pose.process(frame)  # MediaPipe 라이브러리에서 제공하는 Pose 모델을 사용하여 입력 이미지에서 사람의 동작을 감지하고 관절 위치를 추출

                # 프레임 수가 0이면 캡쳐할 프레임 리스트 초기화
                if frame_count == 0:
                    frames = []

                if results.pose_landmarks is not None:
                    mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                    # 캡쳐할 프레임 리스트에 현재 프레임 추가
                    motion.append([lmk.x * w for lmk in results.pose_landmarks.landmark] + [lmk.y * h for lmk in
                                                                                            results.pose_landmarks.landmark])

                # 프레임 카운트 증가
                frame_count += 1

                # 캡쳐할 프레임 수 감소
                capture_count -= 1

                # 카메라에서 프레임 읽어오기
                _, image = cap.read()

                # 이미지를 화면 중앙에 맞춰서 출력하기
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                # 이미지 변환하기
                image = image_change(image)

                # 이미지 리스트에 내 이미지 추가
                image_list.append(image)

                gameDisplay.blit(promptImg, (promptX, promptY))

                # 캡쳐 완료 메시지 출력
                capture_complete3 = font.render("모션 캡쳐 완료!", True, (255, 255, 255))
                gameDisplay.blit(capture_complete3, (800, 200))
                capture_complete4 = font.render("모션에 이름을 붙여주세요", True, (255, 255, 255))
                gameDisplay.blit(capture_complete4, (800, 300))

                # 이미지 출력
                img = pygame.transform.scale(image_list[i], (500, 700))
                gameDisplay.blit(img, (150, 120))

                pygame.display.flip()

            while True:
                csv_filename = naming(nextButton, image_list[i])

                # 파일 이름이 이미 있는 경우 다시 쓰기
                if csv_filename in nameList:
                    gameDisplay.blit(promptImg, (promptX, promptY))
                    same_name = font.render("동일이름이니, 다른 이름을 써주세요.", True, (255, 255, 255))
                    gameDisplay.blit(same_name, (800, 300))
                    gameDisplay.blit(namingBoxImg, (namingBox_x, namingBox_y))
                    pygame.display.flip()
                    continue


                else:
                    # csv 파일로 저장하기
                    with open("frame_{}.csv".format(csv_filename), "w", newline="") as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow(
                            ["frame"] + ["x{}".format(j) for j in range(33)] + ["y{}".format(j) for j in range(33)])
                        writer.writerows(motion)
                    nameList.append(csv_filename)
                    # 이미지를 파일로 저장
                    pygame.image.save(image, "frame_{}.jpg".format(csv_filename))
                    break

        # 종료하기
        cap.release()
        image_check(image_list, namingBoxImg, nameList)
        level_select(nameList)
        return


def image_check(image_list, namingBoxImg, name_list):
    gameDisplay.blit(motionCapture_BackImg, (0, 0))
    nextButton = Button(nextButtonImg, 1350, 30, nextButtonImg.get_width(), nextButtonImg.get_height(),
                        nextButtonImg, 1350, 30, None)
    nextButton.draw(gameDisplay)
    namingBoxImg = pygame.transform.scale(namingBoxImg, (420, 150))
    gameDisplay.blit(namingBoxImg, (140, 650))
    gameDisplay.blit(namingBoxImg, (590, 650))
    gameDisplay.blit(namingBoxImg, (1050, 650))
    check = font.render(" < CHECK YOUR MOTION > ", True, (0, 0, 0))
    gameDisplay.blit(check, (580, 90))

    # 이름 출력
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
    return


###########이미지 변환하기##########################
def image_change(image):
    image = np.rot90(image)
    # image = cv2.flip(image, 0)
    resized_image = cv2.resize(image, (500, 400))
    image = pygame.surfarray.make_surface(resized_image)
    return image


# 레벨을 선택하는 화면
def level_select(nameList):
    level_list = []
    gameDisplay.blit(levelSelect_BackImg, (0, 0))
    # 레벨 단계별로 나오는 거
    level_1_Button = Button2(level1, 65, 550, level1.get_width(), level1.get_height(), level1, 65, 550, nameList, 0, SetQuestion)
    level_list.append(level_1_Button)
    level_2_Button = Button2(level2, 330, 460, level2.get_width(), level2.get_height(), level2, 330, 460, nameList, 1, SetQuestion)
    level_list.append(level_2_Button)
    level_3_Button = Button(level3, 665, 530, level3.get_width(), level3.get_height(), level3, 665, 530, None)
    level_list.append(level_3_Button)
    level_4_Button = Button(level4, 840, 300, level4.get_width(), level4.get_height(), level4, 840, 300, None)
    level_list.append(level_4_Button)
    level_5_Button = Button(level5, 1100, 450, level5.get_width(), level5.get_height(), level5, 1100, 450, None)
    level_list.append(level_5_Button)
    level_6_Button = Button(level6, 1380, 370, level6.get_width(), level6.get_height(), level6, 1380, 370, None)
    level_list.append(level_6_Button)

    while True:
        for button in level_list:
            button.draw(gameDisplay)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quitgame()
            for button in level_list:
                button.handle_event(event)

        pygame.display.update()


###########이미지 3개 띄우기##########
##전역변수 이거는 약간의 수정이 필요할 수도;;
x = 150
y = 150


def display_image(image_list):
    global x, y
    padding = 50
    width = 400
    image_num = len(image_list)
    for i in range(image_num):
        gameDisplay.blit(image_list[i], (x + (width + padding) * i, y))
    pygame.display.flip()

    return


def naming(nextButton, img):
    # 텍스트 입력
    text = ""
    namingBoxButton = Button(namingBoxImg, namingBox_x, namingBox_y, namingBoxImg.get_width(),
                             namingBoxImg.get_height(), namingBoxImg, namingBox_x, namingBox_y, None)
    while nextButton.click == False:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            namingBoxButton.handle_event(event)

            if namingBoxButton.click:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        if len(text) > 0:
                            text = text[:-1]  # 마지막 글자 삭제

                        gameDisplay.blit(motionCapture_BackImg, (0, 0))
                        gameDisplay.blit(namingBoxImg, (namingBox_x, namingBox_y))
                        gameDisplay.blit(nextButtonImg, (1200, 700))
                        gameDisplay.blit(promptImg, (promptX, promptY))
                        nextButton = Button(nextButtonImg, 1200, 700, nextButtonImg.get_width(),
                                            nextButtonImg.get_height(),
                                            nextButtonImg, 1200, 700, None)
                        nextButton.draw(gameDisplay)

                        # 이미지를 화면 중앙에 맞춰서 출력하기
                        img = pygame.transform.scale(img, (500, 700))
                        gameDisplay.blit(img, (150, 120))

                        # 캡쳐 완료 메시지 출력
                        capture_complete3 = font.render("모션 캡쳐 완료!", True, (255, 255, 255))
                        gameDisplay.blit(capture_complete3, (800, 200))
                        capture_complete4 = font.render("모션에 이름을 붙여주세요", True, (255, 255, 255))
                        gameDisplay.blit(capture_complete4, (800, 300))
                        pygame.display.flip()

                        textline = font.render(text, True, (255, 255, 255))
                        gameDisplay.blit(textline, (namingBox_x + 100, namingBox_y + 50))

                    else:
                        if event.key != pygame.K_RETURN:
                            text += event.unicode  # 글자 추가
                            # 작성란에 텍스트 그리기
                            textline = font.render(text, True, (255, 255, 255))
                            gameDisplay.blit(textline, (namingBox_x + 100, namingBox_y + 50))

                pygame.display.update()
                nextButton.enter_event(event)

    nextButton.click = False
    return text


# 문제를 출제하고 사용자가 맞추는 화면
def SetQuestion(nameList, num):

    global prob_motion_proc
    global prob_motion_info

    font_text = pygame.font.SysFont("neo둥근모pro", 40)

    motionCap_cameraX = 150
    motionCap_cameraY = 50

    # 카메라 크기 설정
    CAMERA_WIDTH = 500
    CAMERA_HEIGHT = 700


### 문제마다 반복할 부분!!
    for level in range(num, how_many_level):

        nextLevel_click = False
        pass_OK = False

        mp_drawing = mp.solutions.drawing_utils
        mp_pose = mp.solutions.pose

        each_motion = None # 각 모션이 몇번 수행되었는가 -> {"~": 0, "~": 3........}

        cap = cv2.VideoCapture(0)
        start = time.time()

        cur_motion = []  # 현재 모션을 저장할 변수
        now_motion_count = 0 #현재 to_do_num 중에서 몇개의 모션을 진행했는지 -> max == to_do_num
        now_motion_proc = [] #현재 모션의 순서를 저장!

        motion_count_print = []

        count = 0
        count_set = 6 # count가 이정도 되면 +1로 되도록 한다.
        space = 0

        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            # 코드 가져오기 -> next 문제를 누르게 된다면 가져오게 된다. -> num + 1 해줘야 함.. 문제가 총 6개니까 6번 반복 해야 함.
            quiz_code, limit_time, to_do_num, how_many_motion = add_input_to_quiz('C:/capston/quizData.json', level, nameList)
            #to_do_num : 총 몇번의 동작을 해야 하는가, how_many_motion : 몇개의 동작이 문제에 들어가는가?(문제 속 빈칸이 몇 개인가?)

            each_motion = each_motion_extract(how_many_motion, each_motion) #각 모션이 몇번씩 수행되었는가?

            start_time = time.time()

            clock = pygame.time.Clock()


            for j in range(3):
                # 카운트 다운 출력

                gameDisplay.blit(setQuestion_BackImg, (0, 0))
                gameDisplay.blit(prob_promptImg, (promptX, motionCap_cameraY))
                textline = font.render('제한 시간 : {:.1f}'.format(limit_time), True, (0, 255, 0))
                gameDisplay.blit(textline, (namingBox_x + 100, 700))

                # 코드 렌더링
                code_lines = quiz_code.split('\n')
                line_spacing = 1.0  # 줄 간격 설정
                y = 100  # 시작 y 좌표
                for line in code_lines:
                    text_surface = font.render(line, True, pygame.Color('white'))
                    gameDisplay.blit(text_surface, (850, y))
                    y += 40

                count_down = font_countdown.render(str(3 - j), True, (255, 0, 0))
                gameDisplay.blit(count_down, ((display_width / 2, display_height / 2)))

                pygame.display.flip()
                time.sleep(1.5)

            mp_holistic = mp.solutions.holistic.Holistic()

            # 한 문제를 맞췄을 경우 지속적으로 초기화해줘야 함.
            do_that = True

            while limit_time > 0.0:

                # 제한 시간이 떨어질 때 까지, answer_motion에 대한 모든 동작 to_do_num을 채우지 않으면 땡 처리!
                now_answer_motion_name = prob_motion_info[prob_motion_proc[now_motion_count]] #현재 가져올 정답 번호
                answer_motion = answer_info('C:/capston/quizData.json', level, nameList, now_answer_motion_name)

                if do_that == False:  #정답을 맞췄다는 것임! -> 카운트 넘 1씩 증가해버리기
                    now_motion_count+= 1
                    do_that = True
                    count = 0

                gameDisplay.blit(setQuestion_BackImg, (0, 0))
                gameDisplay.blit(prob_promptImg, (promptX, motionCap_cameraY))

                # 코드 렌더링
                code_lines = quiz_code.split('\n')
                line_spacing = 1.0  # 줄 간격 설정
                y = 100  # 시작 y 좌표
                for line in code_lines:
                    text_surface = font.render(line, True, pygame.Color('white'))
                    gameDisplay.blit(text_surface, (850, y))
                    y += 40

                # 제한 시간을 0.1초씩 감소
                limit_time -= 0.1

                if limit_time <= 0.0:
                    limit_time = 0.0

                textline = font.render('제한 시간 : {:.1f}'.format(limit_time), True, (0, 255,0))
                gameDisplay.blit(textline, (namingBox_x + 100, 700))

                ret, frame = cap.read()

                h, w, _ = frame.shape
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                results = mp_holistic.process(image)

                if results.pose_landmarks:
                    mp.solutions.drawing_utils.draw_landmarks(image, results.pose_landmarks,
                                                              mp.solutions.holistic.POSE_CONNECTIONS)

                # 이미지 회전
                image = np.rot90(image)
                image = pygame.surfarray.make_surface(image)
                image = pygame.transform.scale(image, (CAMERA_WIDTH, CAMERA_HEIGHT))

                gameDisplay.blit(image, (motionCap_cameraX, motionCap_cameraY))

                results = pose.process(frame)  # MediaPipe 라이브러리에서 제공하는 Pose 모델을 사용하여 입력 이미지에서 사람의 동작을 감지하고 관절 위치를 추

                if results.pose_landmarks is not None:
                    mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                    # 실시간 현재 관절 위치 정보 리스트에 저장 : curr_motion
                    # 관절 위치 정보를 리스트에 저장 : motion
                    cur_motion = [lmk.x * w for lmk in results.pose_landmarks.landmark] + [lmk.y * h for lmk in results.pose_landmarks.landmark]

                    if count == count_set and do_that:
                        each_motion[now_answer_motion_name] += 1
                        do_that = False
                        count = 0

                    count = check_motion(count, cur_motion, answer_motion)
                    text_count = font.render(f"Count: {count}", True, (255,0, 0))
                    gameDisplay.blit(text_count, (100, 50))


                    for m in range(0, how_many_motion):
                        motion_text = font.render(prob_motion_info[m] + ": " + str(each_motion[prob_motion_info[m]]), True, (255, 0, 0))
                        gameDisplay.blit(motion_text, (100 + m*250, 800))

                    pygame.display.flip()


                if now_motion_count == to_do_num :
                    cap.release()
                    gameDisplay.blit(blackImg, (0, 0))
                    gameDisplay.blit(level_complete, (520, 100))
                    gameDisplay.blit(nextLevel, (610, 700))
                    nextLevelButton = Button(nextLevel, 610, 700, nextLevel.get_width() + 30, nextLevel.get_height() + 30,
                                          nextLevel, 610, 700, None)

                    pygame.display.flip()

                    while nextLevel_click == False:
                        for event in pygame.event.get():
                            nextLevelButton.handle_event(event)
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                quit()

                            if nextLevelButton.click:
                                nextLevel_click = True


                if nextLevel_click:
                    nextLevel_click = False
                    break

                    pygame.display.flip()

                clock.tick(10)

#현재 문제에 사용되고 있는 각 모션의 정보를 motion 변수들에 넣을 예정!
def each_motion_extract(how_many_motion, each_motion):
    global prob_motion_info

    if how_many_motion == 3:
        each_motion = {prob_motion_info[0]: 0, prob_motion_info[1]: 0, prob_motion_info[2]: 0}

    elif how_many_motion == 2:
        each_motion = {prob_motion_info[0]: 0, prob_motion_info[1]: 0}

    elif how_many_motion == 1:
        each_motion = {prob_motion_info[0]: 0}

    return each_motion

# json 문제 파일 속에 사용자의 모션함수 넣기 -> 문제 번호에 대한 랜덤 완성 문제 code 리턴
def add_input_to_quiz(file_name, problem_index, motion_function_names):  # json 파일, 문제번호(랜덤), 모션함수 이름 리스트

    global prob_motion_proc
    global prob_motion_info

    with open(file_name, 'r') as file:
        data = json.load(file)
        problems = data['problems']  # 문제 배열
        problem = problems[problem_index]  # 문제 배열 속 출제 할 문제를 problem에 넣음

        code = problem['code']  # 출제 코드
        limit_time = int(problem['limit_time'])  # 제한시간
        to_do_num = int(problem['to_do_num']) #총 해야 할 동작의 횟수
        procedure = problem['ans_timeLine']# 행동 순서 0, 1, 1, 2, 3 : 0번 행동 -> 1번 행동 -> 1번 행동 ...

        prob_motion_proc = [int(value) for value in procedure.split(',')]
        how_many_motion = int(problem["how_many_motion"])


        for i, motion_function_name in enumerate(motion_function_names):
            code = code.replace("_____", motion_function_name, 1)  # _____에 사용자 함수를 넣는 과정
            prob_motion_info[i] = motion_function_name

        return code, limit_time, to_do_num, how_many_motion


def answer_info(file_name, problem_index, motion_function_names, now_answer_motion_name):  # 정답 정보 -> answer_moption

    answer_motion = []  # 정답 모션 키 값들이 저장될 공간
    answer_moition_fileName = ''

    with open(file_name, 'r') as file:
        data = json.load(file)
        problems = data['problems']
        problem = problems[problem_index]
        start = 0

        limit_time = problem['limit_time']  # 제한시간

    with open('frame_' + now_answer_motion_name + '.csv') as file2:
        df = pd.read_csv(file2)
        answer_motion = df.iloc[: 33:].values.flatten().tolist()
        print("open:", now_answer_motion_name)

        return answer_motion


def compare_motion(cur_motion, answer_motion):
    print("cur: ", cur_motion)
    print("answer: ", answer_motion)
    """
    비교 함수입니다. 현재 모션과 정답 모션 간의 유사도를 계산합니다.

    Parameters:
        cur_motion (list): 현재 모션의 포즈 정보
        answer_motion (list): 정답 모션의 포즈 정보

    Returns:
        similarity (float): 현재 모션과 정답 모션의 유사도
    """

    # 현재 모션과 정답 모션의 길이를 비교하여 맞춰줌
    min_len = min(len(cur_motion), len(answer_motion))
    cur_motion = cur_motion[:min_len]
    answer_motion = answer_motion[:min_len]

    # 현재 모션과 정답 모션 사이의 코사인 유사도를 계산함
    dot_product = np.dot(cur_motion, answer_motion)
    norm_cur_motion = np.linalg.norm(cur_motion)
    norm_answer_motion = np.linalg.norm(answer_motion)
    similarity = dot_product / (norm_cur_motion * norm_answer_motion) #유사도 검출하는 것

    print(similarity)

    return similarity

def check_motion(count, cur_motion, answer_motion):

    if len(cur_motion) > 0 and len(answer_motion) > 0:

        # cur_motion와 answer_motion의 동작을 비교
        similarity = compare_motion(cur_motion, answer_motion)

        # 유사도가 임계값 미만이면 동일한 것으로 간주 (0~1의 값, 1에 가까울수록 유사)
        temporal = 0.9964

        # 필요에 따라 임계값을 조정
        if np.all(similarity > temporal):
            count += 1

    return count

# 디버깅에 쓰일 마우스 클릭 함수
def mouseClickCheck(event):
    if event.type == pygame.MOUSEBUTTONDOWN:
        mouse_pos = pygame.mouse.get_pos()
        print(mouse_pos[0], mouse_pos[1])


# ______________________________배경 함수______________________________________________________________

def motionCapScreen():
    # 특정 폴더 경로
    folder_path = "C:\\capston"

    # 폴더 내의 모든 CSV 파일 삭제
    csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
    for csv_file in csv_files:
        os.remove(csv_file)

    file_list = os.listdir(folder_path)

    for file_name in file_list:
        if file_name.startswith("frame") and file_name.endswith(".jpg"):
            file_path = os.path.join(folder_path, file_name)
            os.remove(file_path)
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
                            continueButtonImg.get_height(), continueButtonImg, 110, 580, continueGame)
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
