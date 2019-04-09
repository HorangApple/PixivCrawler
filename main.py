from bs4 import BeautifulSoup as bs
import requests
import shutil
from os import path, makedirs
from PIL import Image

################### method ###################
def downloadImages (imagesAddressList, url, number, modeName):
    num=0
    filelist=[]
    headers = {
        "Referer":url
    }
    print("다운로드 중...")
    # make 'images' folder
    if not(path.isdir('.\\images')):
        makedirs(path.join('.\\images'))
        
    # get images
    for i in imagesAddressList :
        response = requests.get(i, headers=headers, stream=True)
        name = f'{number}_{modeName}_{num}.jpg'
        filelist.append(name)
        with open(f'.\\images\\'+name, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        num+=1
    print("다운로드 완료")
    return filelist

def convertBigImageAddress (imagesAddressList):
    print('큰 이미지로 다운로드합니다')
    result=[]
    for i in imagesAddressList:
        result.append(((i.replace("img-master","img-original")).replace("_master1200","")))
    return result

def calculateSize(filelist):
    size_x =[]
    size_y =[]
    for file in filelist:
        image = Image.open(".\\images\\"+file)
        size_x.append(image.size[0])
        size_y.append(image.size[1])
    return [size_x,size_y]

def makeMerge (size,filelist, number, modeName):
    x, y = size
    maxX = max(x)
    endY = sum(y)
    size = (maxX,endY)
    positionY = 0
    images = []
    print("이미지를 병합 중...")
    for i in filelist:
        images.append(Image.open(".\\images\\"+i))
    
    with Image.new('RGB',size,(255,255,255)) as canvas :
        for i, x_, y_ in zip(images, x, y) :
            if x_ == maxX :
                canvas.paste(i, box=(0,positionY))
            else :
                canvas.paste(i, box=(int((maxX-x_)*1/2),positionY))
            positionY += y_
        canvas.save(f'.\\images\\{number}_{modeName}_merge.jpg')
    for i in images:
        i.close()
    print("이미지 병합 완료")
    
################### main ###################

inp = input("여러 이미지가 있는 pixiv 주소를 입력해주십시오 : ")
mode = input("큰 이미지로 다운로드하시겠습니까? (y/n) : ")
merge = input("이미지를 병합하시겠습니까? (y/n) : ")
if inp[41:49] != 'mode=manga' :
    url = inp.replace('mode=medium', 'mode=manga')
number = url.replace('https://www.pixiv.net/member_illust.php?mode=manga&illust_id=', '')

imagesAddressList = []
modeName = ""
# parsing html 
response = requests.get(url).text
soup = bs(response, 'html.parser')

# get image address
i=1
while True :
    selectedImage = soup.select_one(f'#main > section > div:nth-of-type({i}) > img')
    if selectedImage != None:
        imagesAddressList.append(str(selectedImage).split()[5][10:-1])
        i+=1
    else :
        print(f'총 {i-1}장 검색됨')
        break

# behave options #1 big size
if mode == 'y' or mode == 'Y' :
    modeName = 'big'
    imagesAddressList = convertBigImageAddress(imagesAddressList)[:]
else :
    modeName = 'small'
    print('작은 이미지로 다운로드합니다')
filelist = downloadImages (imagesAddressList, url, number, modeName)

# behave options #2 merge images
if merge == 'y' or merge == 'Y' :
    size = calculateSize(filelist)
    makeMerge (size, filelist, number, modeName)