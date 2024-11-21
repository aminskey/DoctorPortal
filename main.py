import torch
import pygame
import json
import cv2

from pygame.locals import *
from text import Text
from PIL import Image
from pyimagesearch.lenet import CNN, all_transforms, class_dict
from os import listdir
from os.path import isfile, isdir
from patient import Patient
from simpleImage import SimpleImage

docname = "Nik Alveis"
name = "M e d   H U B"

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption(name.replace(' ',''))

clock = pygame.time.Clock()

dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = CNN(4)
model.load_state_dict(torch.load("output/cnn_model_stdict.pth", weights_only=True, map_location=dev))
model = model.to(dev)

fnt = pygame.font.Font("assets/Flexi_IBM_VGA_True.ttf", 100)
smallFont = pygame.font.Font("assets/Flexi_IBM_VGA_True.ttf", 25)
fnt2 = pygame.font.Font("assets/Flexi_IBM_VGA_True.ttf", 30)
subFont = pygame.font.Font("assets/Flexi_IBM_VGA_True.ttf", 50)

files = []
patientsList = []

BLACK = (0, 0, 0)
BG = (125, 125, 125)
SHADOW = (95, 95, 95)
SHADOW2 = (65, 65, 65)
WHITE = (200, 200, 200)

with open("./data/stats.csv", "r") as f:
    c, i = f.read().split(",")
    correct, total = int(c), int(i)

def showPatient(p):

    textGrp = pygame.sprite.Group()
    allSprites = pygame.sprite.Group()

    shade = pygame.Surface((screen.get_width() * 7//12, screen.get_height()))
    shade.fill(BLACK)
    shade.set_alpha(120)

    s = screen.get_width() - shade.get_width()

    img = cv2.imread(f"{p.wd}/{p.img}")
    dst = cv2.copyMakeBorder(img, int(0.05*img.shape[0]), int(0.05*img.shape[0]), int(0.05*img.shape[1]),int(0.05*img.shape[1]), cv2.BORDER_CONSTANT, None, SHADOW2)

    profpic = SimpleImage(f"{p.wd}/{p.img}", (s-50, s - 50))
    profpic.image = pygame.transform.scale(pygame.image.frombuffer(dst.tobytes(), dst.shape[1::-1], "BGR"), (s-50, s - 50))
    profpic.rect.topleft = (25, 25)
    allSprites.add(profpic)

    pname = Text(p.name, fnt2, (200, 200, 200), shadow=SHADOW)
    pname.rect.midtop = profpic.rect.midbottom + pygame.math.Vector2(0, 5)

    cpr = Text(p.cpr, smallFont, (200, 200, 200))
    cpr.rect.midtop = pname.rect.midbottom

    hgt = Text("Height: {}cm".format(p.height), smallFont, WHITE)
    age = Text("Age: {}yrs".format(p.age), smallFont, WHITE)

    hgt.rect.topleft = cpr.rect.bottomleft + pygame.math.Vector2(0, 5)
    age.rect.topleft = hgt.rect.bottomleft
    allSprites.add(pname, cpr, hgt, age)

    h2 = Text("Background", subFont, WHITE, shadow=SHADOW)
    h2.rect.midtop = (screen.get_width() - shade.get_width()//2, 5)
    allSprites.add(h2)


    point = pygame.math.Vector2(s + 10, h2.rect.bottomleft[1] + 10)
    for head, data in p.bgInfo.items():
        l = Text(head.strip('-').capitalize(), smallFont, WHITE, shadow=BLACK)
        l.rect.topleft = point

        point.x += l.rect.width + 10

        textGrp.add(l)

        x = data.split(' ')
        for word in x:
            tmp = Text(word, smallFont, WHITE)

            if point.x + tmp.image.get_width() > screen.get_width() or word == '--nl':
                point = pygame.math.Vector2(s+20, point[1] + tmp.image.get_height())

            if word == '--nl':
                continue

            tmp.rect.topleft = point
            point.x += tmp.rect.width + 10
            textGrp.add(tmp)

        point.x = s+10
        point.y += l.rect.height*2

    btn = Text("Diagnose MRI-SCAN", fnt2, WHITE, shadow=SHADOW, clickable=True)
    btn.setClick(lambda: recognize(f"{p.wd}/{p.mri}"))
    btn.rect.topleft = (s+10, point.y + 10)
    textGrp.add(btn)

    retbtn = Text("Tilbage", subFont, (120, 120, 120), clickable=True)
    retbtn.rect.bottomright = screen.get_size() + pygame.math.Vector2(-10, -10)
    textGrp.add(retbtn)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        if retbtn.clicked:
            return

        textGrp.update()

        screen.fill(BG)
        screen.blit(shade, (screen.get_width() - shade.get_width(), 0))
        textGrp.draw(screen)
        allSprites.draw(screen)

        pygame.display.update()
        clock.tick(30)

def mainMenu():
    l = listdir("./data/Patients")
    textGrp = pygame.sprite.Group()
    pList = []

    shade = pygame.Surface((screen.get_width()//3, screen.get_height()))
    shade.fill(BLACK)
    shade.set_alpha(100)

    splash = Text(name, fnt, (115, 115, 115), screen.get_rect().center)

    title = Text("Velkommen", fnt, WHITE, (screen.get_width() * 2//3, screen.get_height()//6), SHADOW2)
    subtitle = Text("tilbage Dr. {}".format(docname), subFont, WHITE, shadow=SHADOW2)
    t2 = Text("PATIENTER", subFont, WHITE, shadow=SHADOW)

    logOff = Text("Log Off", subFont, (150, 150, 150), clickable=True)
    logOff.rect.bottomleft = screen.get_rect().bottomleft + pygame.math.Vector2(15, -15)

    t2.rect.midtop = (screen.get_width()//6, 5)
    subtitle.rect.midtop = title.rect.midbottom

    textGrp.add(title, subtitle, t2, logOff)
    mountpoint = (15, t2.rect.bottomleft[1])

    k = 0
    for i in l:
        if isfile(f"./data/Patients/{i}"):
            l.remove(i)
        elif isdir(f"./data/Patients/{i}") and isfile(f"./data/Patients/{i}/data.json"):
            with open(f"./data/Patients/{i}/data.json", "r") as f:
                d = json.load(f)
                f.close()

            tmp = Patient(d["patient-data"])
            tmp.wd = f"./data/Patients/{i}"

            print(tmp.name)

            label = Text(tmp.name, fnt2, (150, 150, 150), clickable=True)
            if k <= 0:
                label.rect.topleft = mountpoint
            else:
                label.rect.topleft = pList[k-1].rect.bottomleft + pygame.math.Vector2(0, 10)
            textGrp.add(label)
            pList.append(label)
            patientsList.append(tmp)
            k += 1

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        for btn in pList:
            if pygame.mouse.get_pressed()[0] and btn.rect.collidepoint(pygame.mouse.get_pos()):
                i = pList.index(btn)
                showPatient(patientsList[i])

        if logOff.clicked:
            pygame.quit()
            exit()

        textGrp.update()

        screen.fill(BG)
        screen.blit(splash.image, splash.rect)
        screen.blit(shade, (0, 0))
        textGrp.draw(screen)

        pygame.display.update()
        clock.tick(30)
def recognize(path):
    img = Image.open(path).convert("RGB")
    img_tensor = all_transforms(img).unsqueeze(0)
    img_tensor = img_tensor.to(dev)

    model.eval()

    with torch.no_grad():
        output = model(img_tensor)
        _, predicted = torch.max(output, 1)

    img2 = pygame.transform.scale(pygame.image.fromstring(img.tobytes(), img.size, "RGB"), (screen.get_width() * 3//4, screen.get_height() * 3//4))
    rct = img2.get_rect()

    rct.midtop = screen.get_rect().midtop

    label = Text(f"{class_dict[predicted.item()].upper()}", fnt, (225, 255, 255))
    label.rect.midbottom = (screen.get_width()//2, screen.get_height())

    label2 = Text("{}% ACCURACY".format(int((correct/total)*100)), subFont, (0, 0, 255))
    label2.rect.midbottom = label.rect.midtop

    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == K_RETURN:
                    return

        screen.fill((0, 0, 0))
        screen.blit(img2, rct)
        screen.blit(label.image, label.rect)
        screen.blit(label2.image, label2.rect)

        pygame.display.update()
        clock.tick(30)

def filterFiles(l: list, wd="./data"):
    m = []
    for i in l:
        if isfile(f"{wd}/{i}"):
            if '.' in i and i.split('.')[1] == 'jpeg' or i.split('.')[1] == 'jpg' or i.split('.')[1] == 'png':
                m.append(i)
    return m

if __name__ == "__main__":
    mainMenu()
