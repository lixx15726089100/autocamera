#!/usr/bin/ python3

from __future__ import print_function
import logging
import os
import subprocess
import sys
import gphoto2 as gp
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import datetime
import exifread
from PIL import Image
from PIL import ImageFilter
from PIL import ImageEnhance
from PIL import ImageDraw, ImageFont
import imageio
import time


# 通过邮件将内容和附件发送
def mail_send(title, content, attdir=None, attname='att.jpg', receivers='15726089100@qq.com'):

    sender = 'pythonferry@sina.com'
    password = '258bedef6464bcaf'
    mail_host = 'smtp.sina.com'

    msg = MIMEMultipart()
    msg['Subject'] = title
    msg['From'] = sender
    msg_content = content
    msg.attach(MIMEText(msg_content, 'plain', 'utf-8'))

    if attdir is None:
        pass
    else:
        try:
            att = MIMEApplication(open(attdir, 'rb').read())
            att.add_header('Content-Disposition', 'attachment', filename=attname)
            msg.attach(att)
        except:
            msg_content = '\n' + 'fail to read file' + '\n' + attdir
            msg.attach(MIMEText(msg_content, 'plain', 'utf-8'))

    try:
        s = smtplib.SMTP_SSL(mail_host, 465)
        # s.set_debuglevel(1)
        s.login(sender, password)
        msg['To'] = to = receivers
        s.sendmail(sender, to, msg.as_string())
        print('Mail Success!')
        s.quit()
    except smtplib.SMTPException as e:
        print('Mail failed,%s', )


# 输入存储目录实现突破采集功能，返回信息和图片地址
def capture_oneimage(imagesdir='/home/pi/'):

    # 相机有一定的概率不听话，因此需要重试几次。
    for i in range(1, 12):
        camera = gp.Camera()
        try:
            camera.init()
            print('Capturing image')
            file_path = camera.capture(gp.GP_CAPTURE_IMAGE)
            print('Camera file path: {0}/{1}'.format(file_path.folder, file_path.name))
            target = os.path.join(imagesdir, file_path.name)
            print('Copying image to', target)
            camera_file = camera.file_get(
                file_path.folder, file_path.name, gp.GP_FILE_TYPE_NORMAL)
            camera_file.save(target)
            camera.file_delete(file_path.folder, file_path.name)
            camera.exit()
            msg = 'new image'
            return msg, target
        except:
            msg = 'camera-fail x10'
            target = 'Someting wrong with the Camrea,We have retryed 10 times'
            # 每次相机失败后，延时一小段时间再试
            time.sleep(10)
            if i == 10:
                print(target)
                return msg, target


def image_exif(image):
    f = open(image, 'rb')
    tags = exifread.process_file(f)

    # for tag in tags.keys():
    #     print(tag)
    #     print(tag, tags[tag])

    # print(tags['Image Model'])
    # print(tags['EXIF ExposureTime'])
    # print(tags['EXIF FNumber'])
    # print(tags['EXIF ISOSpeedRatings'])

    camera_marker = str(tags['Image Model']) + '  E:' + str(tags['EXIF ExposureTime']) + '  S:' + str(tags['EXIF FNumber'])\
                     + '  ISO:' + str(tags['EXIF ISOSpeedRatings'])
    # print(camera_marker)
    return camera_marker


def image_osd(context, imagefrom, imageto):

    # 由于图片比较大，先截取，再OSD


    im_raw = Image.open(imagefrom)
    im = im_raw.crop((1000,300,3300,2300))

    draw = ImageDraw.Draw(im)
    # 字体选择与widnows区别较大，毕竟这货没界面不要字体，选了‘似曾相识’字体
    fnt = ImageFont.truetype(r'/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 70)
    fnt2 = ImageFont.truetype(r'/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 150)
    cur_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    # 更改照片尺寸会影响分辨率，影响OSD的位置
    # 小字体时间戳的位置
    draw.text((1500, 1900), str(cur_time), fill='black', font=fnt)
    # 大字体dayxx的位置
    draw.text((1000, 50), context, fill='black', font=fnt2)

    im.save(imageto)


# 压缩图片生成gif相关
def image2_gif(image_list, gif_name):
    frames = []
    for image_name in image_list:
        if image_name.endswith('.jpg'):
            print(image_name)
            frames.append(imageio.imread(image_name))
    # Save them as frames into a gif
    imageio.mimsave(gif_name, frames, 'GIF', duration=0.5)
    return


def image2_compress(iamgesfrom='static/', imagesto='images3/'):
    # 生成jpg列表用于生成gif
    dirlist = os.listdir(iamgesfrom)
    dirlist.sort()
    imagelist = []
    imagelistto =[]
    for image in dirlist:
        imagelist.append(iamgesfrom + image)
        imagelistto.append(imagesto + image)
    for image, imageto in zip(imagelist, imagelistto):
        im = Image.open(image)
        # Resize图片大小，入口参数为一个tuple，新的图片大小
        im2 = im.resize((396, 264))
        # 处理后的图片的存储路径，以及存储格式
        im2.save(imageto, 'JPEG')

    print(imagelistto)

    image2_gif(imagelistto, imagesto + 'watch the plant.gif')


def main():
    # sys.path.append('/home/pi/pyprj/cannon5dcaptureandmail/')
    # 需要重新设定工作目录，否则在命令行无法运行
    os.chdir('/home/pi/pyprj/cannon5dcaptureandmail/')
    '''
    # 直接定义起始日期，并转化为datetime对象
    start_day = datetime.datetime.strptime('2020-06-24', "%Y-%m-%d")
    # print(start_day)
    # print(type(start_day))
    # 获取当前日期和时间，日期用于计算和起始日期的差，时间用于image的OSD
    cur_day = datetime.datetime.now()
    # cur_time = datetime.datetime.now().strftime("%Y-%m-%d")
    # print(cur_time)
    dayscount = (cur_day - start_day).days
    # print(dayscount)
    '''

    # 时间缩短测试用例，用3分钟代替1天
    # 直接定义起始日期，并转化为datetime对象
    start_day = datetime.datetime.strptime('2020-07-01 00:00:00', "%Y-%m-%d %H:%M:%S")
    # print(start_day)
    # print(type(start_day))
    # 获取当前日期和时间，日期用于计算和起始日期的差，时间用于image的OSD
    cur_day = datetime.datetime.now()
    # cur_time = datetime.datetime.now().strftime("%Y-%m-%d")
    # print(cur_time)
    dayscount = int((cur_day - start_day).days)
    print(dayscount)

    hourscount = int(datetime.datetime.now().strftime("%H"))
    print(hourscount)

    # time.sleep(100)

    # 采集图像返回参数
    msg, target = capture_oneimage(os.getcwd() + '/images/')
    # 判断是否采集图像成功，不成功就发送警告邮件
    if msg == 'new image':
        # 暂时不用了，提取图片信息功能
        # image_exif("images/IMG_3450.JPG")
        # 每天建立一个文件夹
        path = 'static/day' + (str(dayscount)).zfill(3) + '/'
        if os.path.exists(path):
            pass
        else:
            os.mkdir(path)

        # 加入OSD信息
        osd_str = 'day' + (str(dayscount)).zfill(3) + 'hour' + (str(hourscount)).zfill(2)
        osdimagename = path + osd_str + '.jpg'
        image_osd(osd_str, target, osdimagename)
        title = 'Watch The Plant ' + osd_str

        # 仅仅在规定时间内发送，其余时间，只拍不发
        # 正常发送,发送频率过高，一分钟一次时间一长就会被封号
        # if hourscount == 8 or hourscount == 16:
        #     mail_send(title, msg, osdimagename, (osd_str + '.jpg'), "15726089100@qq.com, 935862737@qq.com")
        #     # mail_send(title, msg, osdimagename, (osd_str + '.jpg'), '935862737@qq.com')

    else:
        # 发送错误信息
        mail_send('ERROR', msg, None, 'att.jpg', '15726089100@qq.com')

    # 每隔10天额外发送一个GIF，但是需要压缩图片,不然生成的gif太大了
    # if (dayscount % 5) == 0:
    #     image2_compress('images2/', 'images3/')
    #     mail_send('Watch The Plant 10days GIF report', 'new GIF every 10days', 'images3/watch the plant.gif', 'watch the plant.gif', "15726089100@qq.com, 935862737@qq.com")
    #     # mail_send('Watch The Plant 10days GIF report', 'new GIF every 10days', 'images3/watch the plant.gif', 'watch the plant.gif', '935862737@qq.com')
    #
    # else:
    #     pass

    return 0


if __name__ == "__main__":
    main()

