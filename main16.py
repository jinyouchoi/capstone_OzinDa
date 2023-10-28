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

how_many_level = 6 #레벨이 총 몇개 있는가? -> 총 6레벨이지만, 우선 2로..

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
nextLevel = load_image("C:\\capston\\객체\\nextLevel.png", (340,100))

level_fail= load_image("C:\\capston\\객체\\failLevel.png", (600, 700))
retry = load_image("C:\\capston\\객체\\retry.png", (340, 100))

level1 = load_image("C:\\capston\\객체\\레벨1.png", (150, 150))
level2 = load_image("C:\\capston\\객체\\레벨2.png", (150, 150))
level2_lock = load_image("C:\\capston\\객체\\레벨2_lock.png", (150, 150))
level3 = load_image("C:\\capston\\객체\\레벨3.png", (150, 150))
level3_lock = load_image("C:\\capston\\객체\\레벨3_lock.png", (150, 150))
level4 = load_image("C:\\capston\\객체\\레벨4.png", (150, 150))
level4_lock = load_image("C:\\capston\\객체\\레벨4_lock.png", (150, 150))
level5 = load_image("C:\\capston\\객체\\레벨5.png", (150, 150))
level5_lock = load_image("C:\\capston\\객체\\레벨5_lock.png", (150, 150))
level6 = load_image("C:\\capston\\객체\\레벨6.png", (150, 150))
level6_lock = load_image("C:\\capston\\객체\\레벨6_lock.png", (150, 150))

selectLevel = load_image("C:\\capston\\객체\\selectLevel.png",(100,100))

submit = load_image(("C:\\capston\\객체\\submit.png"),(200,100))
show_motion = load_image(("C:\\capston\\객체\\showMotion.png"),(200,100))
motionhint_img = load_image(("C:\\capston\\객체\\motionhint.png"),(1000,800))

full_heartImg = load_image("C:\\capston\\객체\\full_heart.png", (70, 70))
empty_heartImg = load_image("C:\\capston\\객체\\empty_heart.png", (70, 70))

warning_barImg = load_image("C:\\capston\\객체\\warning_bar.png", (450, 60))
# 투명화
warning_barImg = warning_barImg.convert_alpha()
warning_barImg.set_alpha(180) #255로 할수록 불투명

no_warning_barImg = warning_barImg.convert_alpha()
no_warning_barImg.set_alpha(0) #255로 할수록 불투명

warning_textImg = load_image("C:\\capston\\객체\\warning_text.png", (450, 70))
warning_coninue_text = load_image("C:\\capston\\객체\\warning_coninue_text.png", (730, 70))


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

            if (self.x <= mouse_pos[0] <= self.x + self.width and self.y <= mouse_pos[1] <= self.y + self.height) or keys[pygame.K_RETURN]:
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
    level_up_list = [True] + [False] * (how_many_level - 1)
    def __init__(self, img_in, x, y, width, height, img_act, move_item, nameList, level_num, action=None):
        self.img_in = img_in
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.img_act = img_act
        self.move_item = move_item
        self.action = action
        self.click = False
        self.level_num = level_num
        self.nameList = nameList
        self.now_img = img_in

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if self.x <= mouse_pos[0] <= self.x + self.width and self.y <= mouse_pos[1] <= self.y + self.height:
                self.click = True
                if self.level_up_list[self.level_num]:
                    self.action(self.nameList, self.level_num)

    def update(self,surface):
        if self.level_up_list[self.level_num] == True:
            self.now_img = self.img_act
            self.draw(surface)
        else:
            self.move_item = 0
            self.now_img = self.img_in
            self.draw(surface)


    def draw(self,surface):
        mouse_pos = pygame.mouse.get_pos()
        if self.x <= mouse_pos[0] <= self.x + self.width and self.y <= mouse_pos[1] <= self.y + self.height:
            surface.blit(self.now_img, (self.x + self.move_item, self.y+ self.move_item))
        else:
            surface.blit(self.now_img, (self.x, self.y))

class ChangeImg:
    def __init__(self, orig_img, change_img, x, y, width, height):
        self.orig_img = orig_img
        self.change_img = change_img
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.is_change = False
        self.now_img = orig_img

    def change(self):
        if self.is_change:
            self.now_img = self.change_img
        else:
            self.now_img = self.orig_img

# ______________________________ 수행 함수 ________________________________

# 종료
def quitgame():
    pygame.quit()
    sys.exit()

def error_txt(text) : #2초간 주의 문구를 띄고 리턴~

    warning_bar_text = pygame.image.load("C:\\capston\\객체\\warning_bar.png")
    warning_bar_text = warning_bar_text.convert_alpha()
    warning_bar_text.set_alpha(130)
    width = len(text) * 30 + 80
    height = 70

    warning_text_secounds = 2

    font_warning = pygame.font.SysFont("neo둥근모pro", 40)
    warning_bar_text = pygame.transform.scale(warning_bar_text, (width, height))

    warning_x = display_width/2 - width/2
    warning_y = 50

    while warning_text_secounds > 0.0:
        gameDisplay.blit(warning_bar_text, (warning_x, warning_y))
        text_obj = font_warning.render(text, True, (255, 255, 255))
        gameDisplay.blit(text_obj, (warning_x + 35, warning_y+15))

        warning_text_secounds -= 0.1
        pygame.display.flip()
        clock.tick(10)
    return

#레벨 저장 json으로
def save_level(level):
    data = {"level": level}
    with open("level.json", "w") as file:
        json.dump(data, file)

#레벨을 불러옴
def load_level():
    try:
        with open("level.json", "r") as file:
            data = json.load(file)
            return data.get("level", 0)  # 기본 레벨은 1로 설정
    except FileNotFoundError:
        return 0  # 파일이 없을 경우 기본 레벨은 1로 설정


#continue 화면
def continueGame():
    IMAGE_WIDTH = display_width // 3
    IMAGE_HEIGHT = display_height
    warning_text_secounds = 2.0

    # 이미지 불러오기
    image = pygame.image.load("C:\\capston\\객체\\네이밍칸.png").convert_alpha()

    # 이미지 크기 조정
    image = pygame.transform.scale(image, (420, 150))

    # 이미지 파일 경로
    folder_path = "C:\\capston"

    image_files = [file for file in os.listdir(folder_path) if file.startswith("frame_") and file.endswith(".jpg")]

    #파일이 없는 경우 예외처리.
    if len(image_files) == 0:

        error_txt("저장된 동작이 없으니 START로 만들어 주세요!")
        return

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
    gameDisplay.blit(name1, (200, 705))
    gameDisplay.blit(name2, (650, 705))
    gameDisplay.blit(name3, (1110, 705))

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

                if five_time <= 0.0:
                    five_time = 0.0

                # 카운트 다운 출력
                count_down = font.render('{:.0f}'.format(five_time), True, (255, 255, 255))
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
                    same_name = font.render("앞과 다른 이름을 써주세요.", True, (255, 255, 255))
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


def level_select(nameList):
    level_list = []
    level_up_list = Button2.level_up_list
    current_level = load_level()
    if current_level == how_many_level:
        current_level -= 1
    for i in range(current_level + 1):
        if level_up_list[i] == False:
            level_up_list[i] = True

    print(level_up_list)
    move_motion = 0

    # 레벨 단계별로 나오는 거
    level_1_Button = Button2(level1, 620, 150, level1.get_width(), level1.get_height(), level1, 10, nameList, 0, SetQuestion)
    level_list.append(level_1_Button)
    #여기까지는 기본적을 나와야 하는 상황
    level_2_Button = Button2(level2_lock, 1100, 190, level2_lock.get_width(), level2_lock.get_height(), level2, 10 , nameList, 1, SetQuestion)
    level_list.append(level_2_Button)
    level_3_Button = Button2(level3_lock, 1200, 500, level3_lock.get_width(), level3_lock.get_height(), level3, 10 , nameList, 2, SetQuestion)
    level_list.append(level_3_Button)
    level_4_Button = Button2(level4_lock, 810, 640, level4_lock.get_width(), level4_lock.get_height(), level4, 10 , nameList, 3, SetQuestion)
    level_list.append(level_4_Button)
    level_5_Button = Button2(level5_lock, 420, 530, level5_lock.get_width(), level5_lock.get_height(), level5, 10 , nameList, 4, SetQuestion)
    level_list.append(level_5_Button)
    level_6_Button = Button2(level6_lock, 870, 390, level6_lock.get_width(), level6_lock.get_height(), level6,10 , nameList, 5, SetQuestion)
    level_list.append(level_6_Button)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quitgame()
            for button in level_list:
                button.handle_event(event)

        gameDisplay.blit(levelSelect_BackImg, (0, 0))
        for button in level_list:
           # button.update(gameDisplay)
            button.update(gameDisplay)

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

    text_len_warning = False

    while nextButton.click == False:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            namingBoxButton.handle_event(event)

            if namingBoxButton.click:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        if len(text) > 0 :
                            text = text[:-1]  # 마지막 글자 삭제
                            text_len_warning = False
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
                        gameDisplay.blit(textline, (namingBox_x + 90, namingBox_y + 80))

                    if len(text) < 15:
                        if event.key != pygame.K_RETURN:
                            if event.unicode.isalpha() or event.unicode.isdigit() or event.unicode.isspace():
                                text += event.unicode  # 글자 추가
                                # 작성란에 텍스트 그리기
                                textline = font.render(text, True, (255, 255, 255))
                                gameDisplay.blit(textline, (namingBox_x + 90, namingBox_y + 80))

                    if len(text) >= 15 and text_len_warning == False:
                        error_txt("글자 수는 15 미만으로 해주세요.")
                        text_len_warning = True

                pygame.display.update()
                nextButton.enter_event(event)

    nextButton.click = False
    return text

def motionhint():
    #이미지 파일 경로
    folder_path = "C:\\capston"
    image_files = [file for file in os.listdir(folder_path) if file.startswith("frame_") and file.endswith(".jpg")]

    #힌트 배경 불러오기
    gameDisplay.blit(motionhint_img, (300, 100))

    file_list = []
    for image_file in image_files:
        file_name = image_file.replace("frame_", "").replace(".jpg", "")
        file_list.append(file_name)

    name1 = font.render(file_list[0], True, (0, 0, 0))
    name2 = font.render(file_list[1], True, (0, 0, 0))
    name3 = font.render(file_list[2], True, (0, 0, 0))
    gameDisplay.blit(name1, (420, 650))
    gameDisplay.blit(name2, (690, 650))
    gameDisplay.blit(name3, (960, 650))


    # 이미지 로드 및 크기 조정
    images = []
    for image_file in image_files:
        image_path = os.path.join(folder_path, image_file)
        image = pygame.image.load(image_path)
        image = pygame.transform.scale(image, (210, 360))
        images.append(image)

    # 이미지 위치 설정
    image_positions = [
        (420, 220),  # 왼쪽 이미지 위치
        (690, 220),  # 가운데 이미지 위치
        (960, 220),  # 오른쪽 이미지 위치
    ]

    for image, position in zip(images, image_positions):
        gameDisplay.blit(image, position)

    # 화면 업데이트
    pygame.display.flip()

    return


# 문제를 출제하고 사용자가 맞추는 화면
def SetQuestion(nameList, num):

    while True:

        global prob_motion_proc
        global prob_motion_info

        not_correct = False #오답인지 아닌지 표시

        nxButton_x = 625
        nxButton_y = 705

        motionCap_cameraX = 150
        motionCap_cameraY = 50

        # 카메라 크기 설정
        CAMERA_WIDTH = 500
        CAMERA_HEIGHT = 700

        heart_y = 800
        heart_width = 100
        heart_height = 100
        retryButton_click = False

        warning_x = CAMERA_WIDTH/2 - warning_barImg.get_width()/2 + motionCap_cameraX

        #level_up 리스트 불러오기
        level_up_list = Button2.level_up_list

        #try_count = 0 # 재도전 횟수

        level = num

    ### 문제마다 반복할 부분!!
        while level <= how_many_level:

            if level ==  how_many_level:
                break
        #for level in range(num, how_many_level):

            if retryButton_click:
                level -= 1 #오답 횟수만큼 빼주기
                print("level: ", level)
                retryButton_click = False

            not_correct = False

            chance = 3
            heart_list = [ChangeImg(full_heartImg, empty_heartImg, 100, heart_y, heart_width, heart_height),
                            ChangeImg(full_heartImg, empty_heartImg, 170, heart_y, heart_width, heart_height),
                            ChangeImg(full_heartImg, empty_heartImg, 240, heart_y, heart_width, heart_height)]

            warning = ChangeImg(no_warning_barImg, warning_barImg, warning_x, 80, warning_barImg.get_width(), warning_barImg.get_height)

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

            submit_button_click = False

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
                    font_code = pygame.font.SysFont("Arial", 40)
                    code_lines = quiz_code.split('\n')
                    y = 100  # 시작 y 좌표
                    for line in code_lines:
                        text_surface = font_code.render(line, True, pygame.Color('white'))
                        gameDisplay.blit(text_surface, (850, y))
                        y += 40

                    count_down = font_countdown.render(str(3 - j), True, (255, 0, 0))
                    gameDisplay.blit(count_down, ((display_width / 2, display_height / 2)))

                    pygame.display.flip()
                    time.sleep(1.5)

                mp_holistic = mp.solutions.holistic.Holistic()

                # 한 문제를 맞췄을 경우 지속적으로 초기화해줘야 함.
                do_that = True
                count_secounds = 3.0
                count_secounds_now = False #3초 세는 것을 시작해라!
                
                warning_text_secounds = 1.0 #경고 문구를 몇 초동안 띄울 것인지

                while limit_time > 0.0:

                    if now_motion_count == to_do_num: #밑에서 +1한걸 위에서 -1 해주는 개념
                        now_motion_count = to_do_num-1

                    # 제한 시간이 떨어질 때 까지, answer_motion에 대한 모든 동작 to_do_num을 채우지 않으면 땡 처리!
                    now_answer_motion_name = prob_motion_info[prob_motion_proc[now_motion_count]] #현재 가져올 정답 번호
                    answer_motion = answer_info('C:/capston/quizData.json', level, nameList, now_answer_motion_name)

                    if do_that == False and now_motion_count < to_do_num:  #정답을 맞췄다는 것임! -> 카운트 넘 1씩 증가해버리기
                        now_motion_count+= 1

                    if now_motion_count == 1:
                        count_secounds_now = True

                    if do_that == False and now_motion_count < to_do_num:  #정답을 맞췄다는 것임!
                        do_that = True
                        count = 0
                        count_secounds_now = True #3초 세는 것을 시작해라

                    gameDisplay.blit(setQuestion_BackImg, (0, 0))
                    gameDisplay.blit(prob_promptImg, (promptX, motionCap_cameraY))

                    # 코드 렌더링
                    font_code = pygame.font.SysFont("Arial", 40)
                    code_lines = quiz_code.split('\n')
                    y = 100  # 시작 y 좌표
                    for line in code_lines:
                        text_surface = font_code.render(line, True, pygame.Color('white'))
                        gameDisplay.blit(text_surface, (850, y))
                        y += 45

                    # 제한 시간을 0.1초씩 감소
                    limit_time -= 0.1

                    if count_secounds_now == True:
                        #2초 세기 시간을 0.1초씩 감소
                        count_secounds -= 0.1

                    if count_secounds < 0.0 and count_secounds_now: # 2초 지났다면, 1번 수행했다면
                        if do_that == True: #정답을 맞추지 못했다는 것
                            chance -= 1 #찬스 감소
                            heart_list[chance].is_change = True
                            heart_list[chance].change()
                            count_secounds = 3.0
                            warning.is_change = True
                            warning.change()


                    if limit_time <= 0.0: #제한 시간 종료 조건
                        limit_time = 0.0
                        not_correct = True #오답처리하도록

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

                    gameDisplay.blit(show_motion, (450, 30))  # showMotion 이미지 그리기
                    gameDisplay.blit(submit, (140, 30))  # submit 이미지 그리기

                    results = pose.process(
                        frame)  # MediaPipe 라이브러리에서 제공하는 Pose 모델을 사용하여 입력 이미지에서 사람의 동작을 감지하고 관절 위치를 추출
                    if results.pose_landmarks:
                        pose_landmarks = results.pose_landmarks.landmark

                        left_landmark_x, left_landmark_y = None, None
                        right_landmark_x, right_landmark_y = None, None

                        # 왼손 처리
                        if pose_landmarks[15].visibility > 0.5:
                            left_landmark_x = int(pose_landmarks[15].x * w)
                            left_landmark_y = int(pose_landmarks[15].y * h)

                        # 오른손 처리
                        if pose_landmarks[16].visibility > 0.5:
                            right_landmark_x = int(pose_landmarks[16].x * w)
                            right_landmark_y = int(pose_landmarks[16].y * h)

                        # 좌표 검사
                        #모션보기 왼손
                        if left_landmark_x is not None and 0 <= left_landmark_y <= 100 and 0 <= left_landmark_x <= 200:
                            motionhint()
                        
                        #모션보기 오른손
                        if right_landmark_x is not None and 0 <= right_landmark_y <= 100 and 0 <= right_landmark_x <= 200:
                            motionhint()

                        #제출하기 왼손
                        if left_landmark_x is not None and 0 <= left_landmark_y <= 100 and 500 <= left_landmark_x <= 700:
                            submit_button_click = True
                            
                        # 제출하기 오른손
                        if right_landmark_x is not None and 0 <= right_landmark_y <= 100 and 500 <= right_landmark_x <= 700:
                            submit_button_click = True

                    
                    #하트 출력
                    for ht in range(3):
                        gameDisplay.blit(heart_list[ht].now_img, (heart_list[ht].x, heart_list[ht].y))

                    if chance <= 0:
                        not_correct = True
                        break

                    #경고 문구 출력
                    gameDisplay.blit(warning.now_img, (warning.x, warning.y))

                    if warning.is_change:
                        gameDisplay.blit(warning_textImg, (warning.x, warning.y))
                        warning_text_secounds -= 0.1


                    if warning_text_secounds < 0.0:
                        warning.is_change = False
                        warning.change()
                        if chance > 0:
                            warning_text_secounds = 1.0

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

                        length_motion = 0
                        for m in range(0, how_many_motion):
                            font_motion2 = pygame.font.SysFont("neo둥근모pro", 45)
                            motion_text = font_motion2.render(prob_motion_info[m] + ": " + str(each_motion[prob_motion_info[m]]), True, (250, 250, 60))

                            if m != 0:
                                gameDisplay.blit(motion_text, (340 + (length_motion* 25), 810))
                            else:
                                gameDisplay.blit(motion_text, (340, 810))

                            length_motion += len(prob_motion_info[m]) + 1


                        pygame.display.flip()


                    if submit_button_click == True:  # 제출하기 클릭
                        if now_motion_count == to_do_num: #정답일 경우
                            if level < how_many_level - 1:
                                level_up_list[level+1] = True # 정답일 경우에는 무조건 다음 레벨이 열리기 때문에 nextButton을 눌러도 변경이 되지 않음
                            save_level(level+1)
                            # cap.release()
                            gameDisplay.blit(blackImg, (0, 0))
                            gameDisplay.blit(level_complete, (520, 100))
                            gameDisplay.blit(nextLevel, (nxButton_x, nxButton_y))
                            gameDisplay.blit(selectLevel,(nxButton_x-100,nxButton_y))
                            nextLevelButton = Button(nextLevel, nxButton_x, nxButton_y, nextLevel.get_width() + 30,
                                                     nextLevel.get_height() + 30,
                                                     nextLevel, nxButton_x, nxButton_y, None)
                            selectLevelButton = Button(selectLevel,nxButton_x-80,nxButton_y,selectLevel.get_width(),
                                                       selectLevel.get_height(),selectLevel,nxButton_x-100,nxButton_y,None)

                            pygame.display.flip()
                            while nextLevel_click == False:
                                for event in pygame.event.get():
                                    nextLevelButton.handle_event(event)
                                    selectLevelButton.handle_event(event)
                                    if event.type == pygame.QUIT:
                                        pygame.quit()
                                        quit()

                                    if nextLevelButton.click:
                                        nextLevel_click = True

                                    if selectLevelButton.click:
                                        level_select(nameList)

                        else: #제출하기 눌렀는데ㅡ 틀린경우
                            not_correct = True
                            break


                    if nextLevel_click:
                        nextLevel_click = False
                        break

                        pygame.display.flip()

                    clock.tick(10)


                #오답화면 처리
                if not_correct:
                    print("odab")
                    #cap.release()
                    gameDisplay.blit(blackImg, (0, 0))
                    gameDisplay.blit(level_fail, (520, 100))

                    gameDisplay.blit(retry, (nxButton_x + 5, nxButton_y))
                    retryButton = Button(retry, nxButton_x + 5, nxButton_y, retry.get_width() + 30, retry.get_height() + 30, retry, nxButton_x + 5, nxButton_y, None)

                    pygame.display.flip()

                    while retryButton_click == False:
                        for event in pygame.event.get():
                            retryButton.handle_event(event)
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                quit()
                            if retryButton.click:
                                retryButton_click = True
                                #try_count += 1 #재도전 횟수

                level += 1
        # 모든 반복을 종료했을 경우
        return


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

#손으로 인식하기
def click_to_hands():

    # 카메라 캡처 객체 생성
    cap = cv2.VideoCapture(0)
    # 카메라에서 프레임 읽어오기
    _, image = cap.read()

    #인식한 좌표값을 리턴해줌

#클릭 했는지 비교
def is_click(hands_X, hands_Y, hands_button):
    if hands_button.x <= hands_X <= hands_button.x + hands_button.width and hands_button.y <= hands_Y <= hands_button.y + hands_button.height:
        hands_button.click = True


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

def delete_level_file():
    file_path = "C:\\capston\\level.json"  # 삭제할 파일의 경로 및 이름
    if os.path.exists(file_path):  # 파일이 존재하는지 확인
        os.remove(file_path)  # 파일 삭제
        print("파일이 삭제되었습니다")


def mainScreen():
    mainS = True
    folder_path = "C:\\capston"

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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if mouse_pos[0] < 100 and mouse_pos[1] < 100:
                    delete_level_file()
                    csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
                    for csv_file in csv_files:
                        os.remove(csv_file)

                    file_list = os.listdir(folder_path)

                    for file_name in file_list:
                        if file_name.startswith("frame") and file_name.endswith(".jpg"):
                            file_path = os.path.join(folder_path, file_name)
                            os.remove(file_path)
            for button in (startButton, exitButton, continueButton, howplayButton):
                button.handle_event(event)

        gameDisplay.blit(mainBackgroundImg, (0, 0))
        transparent = pygame.Color(0, 0, 0, 0)
        rect_surface = pygame.Surface((100, 100), pygame.SRCALPHA)
        rect_surface.fill(transparent)
        gameDisplay.blit(rect_surface, (0, 0))

        for button in (startButton, exitButton, continueButton, howplayButton):
            button.draw(gameDisplay)

        pygame.display.update()

# 메인, 호출
mainScreen()
