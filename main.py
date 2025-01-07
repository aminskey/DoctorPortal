import torch
import pygame
import json
import cv2

from text import Text
from PIL import Image
from lenet import CNN, all_transforms, class_dict
from os import listdir
from os.path import isfile, isdir
from patient import Patient
from simpleImage import SimpleImage

docname = "Nick Larsen"
name = "M e d   H U B"
companyName = "(c) NeuroSoft Solutions"

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

    cpr = Text("CPR: {}".format(p.cpr), smallFont, (200, 200, 200))
    cpr.rect.topleft = pname.rect.bottomleft

    hgt = Text("Height: {}cm".format(p.height), smallFont, WHITE)
    age = Text(f"Age: {p.age.years}yrs {p.age.months}mts", smallFont, WHITE)

    hgt.rect.topleft = cpr.rect.bottomleft + pygame.math.Vector2(0, 5)
    age.rect.topleft = hgt.rect.bottomleft
    allSprites.add(pname, cpr, hgt, age)

    h2 = Text("Background", subFont, WHITE, shadow=SHADOW)
    h2.rect.midtop = (screen.get_width() - shade.get_width()//2, 5)
    allSprites.add(h2)


    point = pygame.math.Vector2(s + 10, h2.rect.bottomleft[1])
    for head, data in p.bgInfo.items():
        l = Text("{}:".format(head.strip('-').capitalize()), smallFont, WHITE, shadow=BLACK)
        l.rect.topleft = point
        textGrp.add(l)

        point.x = s+20
        point.y += l.rect.height + 5

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
        point.y += l.rect.height+10

    mri = SimpleImage(f"{p.wd}/{p.mri}", (175, 175))
    btn = Text("Press to Diagnose MRI-SCAN", fnt2, SHADOW, clickable=True, shadow=SHADOW2)
    point = (s+10, point.y - 5)
    if not p.diag:
        btn.rect.topleft = point
        mri.rect.topleft = btn.rect.bottomleft

        textGrp.add(btn)
        allSprites.add(mri)
    else:
        lb1 = Text("Diagnosed MRI-Scan", fnt2, WHITE, shadow=BLACK)
        lb2 = Text("Diagnose:", fnt2, WHITE, shadow=SHADOW)
        dinfo = Text(p.dict["diagnose"], fnt2, WHITE)

        lb1.rect.topleft = point
        mri.rect.topleft = lb1.rect.bottomleft
        lb2.rect.topleft = mri.rect.topright + pygame.math.Vector2(5, 0)
        dinfo.rect.topleft = lb2.rect.bottomleft
        allSprites.add(mri, lb1, lb2, dinfo)

    retbtn = Text("Return", subFont, (120, 120, 120), clickable=True)
    retbtn.rect.bottomright = screen.get_size() + pygame.math.Vector2(-10, -10)
    textGrp.add(retbtn)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        if retbtn.clicked:
            return
        if btn.clicked:
            recognize(f"{p.wd}/{p.mri}", p)
            p.diag = True
            p.dict["isdiagnosed"] = True
            showPatient(p)
            return

        textGrp.update()

        screen.fill(BG)
        screen.blit(shade, (screen.get_width() - shade.get_width(), 0))
        textGrp.draw(screen)
        allSprites.draw(screen)

        pygame.display.update()
        clock.tick(30)

def startScreen():
    textGrp = pygame.sprite.Group()

    title = Text(name, fnt, WHITE, (screen.get_width()//2, screen.get_height()//3), shadow=SHADOW)
    logo = SimpleImage("assets/logo-mini.png", (50, 50))
    sub = Text("Staying Connected.", subFont, (100, 100, 100))

    login = Text("Login", subFont, (105, 105, 105), (screen.get_width()//2, screen.get_height() * 2//3), clickable=True)
    login.setClick(mainMenu)

    splash = Text(companyName, smallFont, (110, 110, 110))
    splash.rect.bottomright = screen.get_rect().bottomright

    sub.rect.midtop = title.rect.midbottom
    logo.rect.midright = sub.rect.midleft + pygame.math.Vector2(-10, 0)

    textGrp.add(title, login, logo, sub, splash)


    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        textGrp.update()

        screen.fill(BG)
        textGrp.draw(screen)

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

    title = Text("Welcome", fnt, WHITE, (screen.get_width() * 2//3, screen.get_height()//6), SHADOW2)
    subtitle = Text("Back Dr. {}".format(docname), subFont, WHITE, shadow=SHADOW2)
    t2 = Text("Patients", subFont, WHITE, shadow=SHADOW)

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
            return

        textGrp.update()

        screen.fill(BG)
        screen.blit(splash.image, splash.rect)
        screen.blit(shade, (0, 0))
        textGrp.draw(screen)

        pygame.display.update()
        clock.tick(30)
def recognize(path, p):
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

    retBtn = Text("Return", subFont, SHADOW, clickable=True)
    retBtn.rect.bottomright = screen.get_rect().bottomright + pygame.math.Vector2(-5, -5)

    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN or retBtn.clicked:
                p.diag = True
                p.dict["diagnose"] = label.msg
                return

        retBtn.update()

        screen.fill((0, 0, 0))
        screen.blit(img2, rct)
        screen.blit(label.image, label.rect)
        screen.blit(label2.image, label2.rect)
        screen.blit(retBtn.image, retBtn.rect)

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
    startScreen()