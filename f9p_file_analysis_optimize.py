#!/usr/bin/python
# coding=utf-8

import sys
import os
import time
import datetime
import re
import image_draw
import glob
import numpy as np
import matplotlib.pyplot as plt
import csv


# 解析数据获取并生成中间文件
class f9p_file(object):
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False

    def __init__(self,folder_path,output_file,rate_ms):
        self.folder = folder_path
        self.path = os.path.join(folder_path, '*.log')
        self.frame = glob.glob(self.path)

        for frame in self.frame:
           self.get_f9p_keydata(frame,output_file,rate_ms)

    def get_f9p_keydata(self,input_file, output_url, rate_ms):
        # 判断输入文件是否存在
        if not os.path.exists(input_file):
            print("f9p 输入文件不存在！ 文件名：" + input_file)
            sys.exit(0)

        # 判断输出路径是否存在
        if not os.path.exists(output_url):
            print("f9p 输出路径不存在！ 路径：" + output_url)
            sys.exit(0)

            # 获取解析文件的路径以及文件名
        name = input_file.split('\\')[-1]
        filename = name.split('.')[0]
        # dirname, basename = os.path.split(os.path.realpath(input_file))
        # basenameList = basename.split(".")
        # filename = basenameList[0]

        # 设置解析结果输出的文件
        f9p_data_File_name = os.path.join(output_url, str(filename) + "_data.csv")

        if os.path.exists(f9p_data_File_name): os.remove(f9p_data_File_name)
        # f9p_data_File = open(f9p_data_File_name, 'w+')

        # 变量初始化
        latFlag = 0
        lonFlag = 0
        altFlag = 0
        seqFlag = 0
        strLineData=[]
        linenum = 0
        str_dealover_ts_us = ""

        # 逐行读取数据，进行帧率解析
        sourceFile = open(input_file, 'r')
        while True:
            line = sourceFile.readline()
            if line:
                linenum = linenum + 1
            else:
                break

            strData = str(line)

            # 获取数据解析后的时间戳
            keyPos = "Please input JIRA:"
            if keyPos in strData:
                nextline 
                listData = strData.split(": ")
                str_dealover_sec = str(listData[1]).strip()
            keyPos = "    nsecs:"
            if keyPos in strData:
                listData = strData.split(": ")
                if (len(str(listData[1].strip())) < 9):
                    strMSecTemp = str(listData[1]).strip().rjust(9, '0')  # ns数据长度不足9位，前面用0补齐
                else:
                    strMSecTemp = str(listData[1]).strip()
                str_dealover_msec = str(strMSecTemp[0:6]).strip()
                str_dealover_ts_us = str_dealover_sec + str_dealover_msec  # s与ms字符串拼接成16位时间戳

            # 获取数据发生时的时间戳
            keyPos = "  timestamp_us:"
            if keyPos in strData:
                listData = strData.split(": ")
                str_sensor_ts_us = str(str(listData[1])[0:16]).replace('\n', '').strip()  # 去换行、去空格

            # 获取position_global的纬度
            keyPos = "    lat:"
            if keyPos in strData and latFlag == 0:
                latFlag = 1
                listData = strData.split(": ")
                str_LatWdTemp = str(listData[1]).strip()
                str_LatWdTemp = str(float(str_LatWdTemp) * 57.295779513)
                if float(str_LatWdTemp) < 0:
                    str_LatWd = str(str_LatWdTemp).ljust(15, '0')
                else:
                    str_LatWd = " " + str(str_LatWdTemp).ljust(14, '0')

            # 获取position_global的经度
            keyPos = "    lon:"
            if keyPos in strData and lonFlag == 0:
                lonFlag = 1
                listData = strData.split(": ")
                str_lonJdTemp = str(listData[1]).strip()
                str_lonJdTemp = str(float(str_lonJdTemp) * 57.295779513)
                if float(str_lonJdTemp) < 0:
                    str_LonJd = str(str_lonJdTemp).ljust(14, '0')
                else:
                    str_LonJd = " " + str(str_lonJdTemp).ljust(13, '0')

            # 获取position_global的高程
            keyPos = "    alt:"
            if keyPos in strData and altFlag == 0:
                altFlag = 1
                listData = strData.split(": ")
                str_altGdTemp = str(listData[1]).strip()
                if float(str_altGdTemp) < 0:
                    str_AltGC = str(str_altGdTemp).ljust(8, '0')
                else:
                    str_AltGC = " " + str(str_altGdTemp).ljust(7, '0')

            # 获取status
            keyPos = "    status:"
            if keyPos in strData:
                listData = strData.split(": ")
                str_starSts = str(listData[1]).strip()

            # 获取sat_num
            keyPos = "    sat_num:"
            if keyPos in strData:
                listData = strData.split(": ")
                str_sat_num = str(listData[1]).strip()

            # 获取speed
            keyPos = "    speed:"
            if keyPos in strData:
                listData = strData.split(": ")
                str_speed = str(listData[1]).strip()

            keyPos = "---"
            if keyPos in strData:
                # 关键数据获取后的信息拼接
                time_gap = str(int(str_dealover_ts_us) - int(str_sensor_ts_us))
                strLineData.append([str_dealover_ts_us,str_sensor_ts_us,time_gap,str_LatWd,str_LonJd,str_AltGC,str_starSts,str_sat_num,str_speed])
                # print([str_dealover_ts_us,str_sensor_ts_us,time_gap,str_LatWd,str_LonJd,str_AltGC,str_starSts,str_sat_num,str_speed])
                # 解析数据中间文件生成
                # flag标志复位
                latFlag = 0
                lonFlag = 0
                altFlag = 0
                seqFlag = 0
        sourceFile.close()
        with open(f9p_data_File_name, 'a+', encoding="utf8", newline="") as csvfile:
            myWriter = csv.writer(csvfile)
            myWriter.writerows(strLineData)
        self.f9p_data_analysis(f9p_data_File_name, output_url, rate_ms,filename)

    def f9p_data_analysis(self,input_file, output_url, rate_ms,filename):
        f9p_data_File = open(input_file, 'r')

        # 设置数据匹配关键字
        cntData = 0

        dealover_tsdiff_arr = []
        dealover_tsdiff = 0.0
        dealover_tsdiff_Min = 10000000.0
        dealover_tsdiff_Max = -10000000.0
        dealover_tsdiff_Sum = 0
        dealover_tsdiff_Avg = 0.0
        dealover_tsdiff_normal_Min = 10000000.0
        dealover_tsdiff_normal_Max = -10000000.0
        dealover_tsdiff_normal_Sum = 0
        dealover_tsdiff_normal_Avg = 0.0
        dealover_tsdiff_normal_Cnt = 0
        dealover_tsdiff_lossFrames = 0
        dealover_tsdiff_exinfo = ""
        dealover_startTime = 0
        dealover_endTime = 0

        sensor_tsdiff_arr = []
        sensor_tsdiff = 0.0
        sensor_tsdiff_Min = 10000000.0
        sensor_tsdiff_Max = -10000000.0
        sensor_tsdiff_Sum = 0
        sensor_tsdiff_Avg = 0.0
        sensor_tsdiff_normal_Min = 10000000.0
        sensor_tsdiff_normal_Max = -10000000.0
        sensor_tsdiff_normal_Sum = 0
        sensor_tsdiff_normal_Avg = 0.0
        sensor_tsdiff_normal_Cnt = 0
        sensor_tsdiff_lossFrames = 0
        sensor_tsdiff_exinfo = ""
        sensor_startTime = 0
        sensor_endTime = 0

        delayArr = []
        delay = 0
        delayMin = 10000
        delayMax = -10000
        delaySum = 0
        delayAvg = 0.0
        delay_exinfo = ""

        gpsLatArr = []
        gpsLonArr = []

        gpsAltArr = []
        gpsAlt = 0.0
        gpsAltMin = 10000.0
        gpsAltMax = -10000.0
        gpsAltSum = 0
        gpsAltAvg = 0.0
        gpsAlt_exinfo = ""

        starStsArr = []
        starSts = 0
        starStsMin = 10000.0
        starStsMax = -10000.0
        starStsSum = 0
        starStsAvg = 0.0
        starSts0Cnt = 0
        starSts1Cnt = 0
        starSts2Cnt = 0
        starSts3Cnt = 0
        starSts4Cnt = 0
        starSts5Cnt = 0
        starStsxCnt = 0
        starSts_exinfo = ""

        satNumArr = []
        satNum = 0
        satNumMin = 10000
        satNumMax = -10000
        satNumSum = 0
        satNumAvg = 0.0
        satNum_exinfo = ""

        speedArr = []
        speed = 0
        speedMin = 10000
        speedMax = -10000
        speedSum = 0
        speedyAvg = 0.0
        speed_exinfo = ""

        # 逐行读取数据，进行帧率解析
        lines = f9p_data_File.readlines()

        for line in lines:
            strData = str(line)
            cntData = cntData + 1
            # strDatalen = len(strData)
            strData = strData.split(',')

            '''1616067178365895    1616067178366034    139     31.42265260000     120.634662800     14.2800     48133'''
            # 获取数据解析后的时间戳(us)
            new_dealover_ts = float(strData[0])
            if cntData == 1:
                dealover_startTime = new_dealover_ts
            else:
                dealover_endTime = new_dealover_ts
                dealover_tsdiff = (new_dealover_ts - old_dealover_ts) / 1000
                dealover_tsdiff_arr.append(dealover_tsdiff)
                if (dealover_tsdiff > dealover_tsdiff_Max):    dealover_tsdiff_Max = dealover_tsdiff
                if (dealover_tsdiff < dealover_tsdiff_Min):    dealover_tsdiff_Min = dealover_tsdiff
                dealover_tsdiff_Sum = dealover_tsdiff_Sum + dealover_tsdiff
                # 不含丢帧的帧率最大值/最小值
                if (dealover_tsdiff <= (rate_ms + rate_ms * 0.8)):  # and dealover_tsdiff >= (rate_ms - rate_ms*0.5)):
                    dealover_tsdiff_normal_Cnt = dealover_tsdiff_normal_Cnt + 1
                    if dealover_tsdiff > dealover_tsdiff_normal_Max: dealover_tsdiff_normal_Max = dealover_tsdiff
                    if dealover_tsdiff < dealover_tsdiff_normal_Min: dealover_tsdiff_normal_Min = dealover_tsdiff
                    dealover_tsdiff_normal_Sum = dealover_tsdiff_normal_Sum + dealover_tsdiff
                else:
                    error_cnt = cntData - dealover_tsdiff_normal_Cnt
                    bjTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(new_dealover_ts / 1000000))
                    print("[--处理后] 帧率异常，当前时间：" + str(new_dealover_ts) + " 北京时间：" + str(bjTime) + "; 当前帧计数:" + str(
                        cntData) + "; 丢帧次数:" + str(error_cnt) + "; 本次异常差值ms：" + str(dealover_tsdiff) + "; 丢帧数：" + str(
                        int(dealover_tsdiff / rate_ms + 0.5) - 1) + "\n")
                    dealover_tsdiff_lossFrames = dealover_tsdiff_lossFrames + int(dealover_tsdiff / rate_ms + 0.5) - 1

            old_dealover_ts = new_dealover_ts

            # 获取数据发生时的时间戳
            new_sensor_ts = float(strData[1])
            if cntData == 1:
                sensor_startTime = new_sensor_ts
            else:
                sensor_endTime = new_sensor_ts
                sensor_tsdiff = (new_sensor_ts - old_sensor_ts) / 1000
                sensor_tsdiff_arr.append(sensor_tsdiff)
                if (sensor_tsdiff > sensor_tsdiff_Max):    sensor_tsdiff_Max = sensor_tsdiff
                if (sensor_tsdiff < sensor_tsdiff_Min):    sensor_tsdiff_Min = sensor_tsdiff
                sensor_tsdiff_Sum = sensor_tsdiff_Sum + sensor_tsdiff
                # 不含丢帧的帧率最大值/最小值
                if (sensor_tsdiff <= (rate_ms + rate_ms * 0.8)):  # and sensor_tsdiff >= (rate_ms - rate_ms*0.1)):
                    sensor_tsdiff_normal_Cnt = sensor_tsdiff_normal_Cnt + 1
                    if sensor_tsdiff > sensor_tsdiff_normal_Max: sensor_tsdiff_normal_Max = sensor_tsdiff
                    if sensor_tsdiff < sensor_tsdiff_normal_Min: sensor_tsdiff_normal_Min = sensor_tsdiff
                    sensor_tsdiff_normal_Sum = sensor_tsdiff_normal_Sum + sensor_tsdiff
                else:
                    error_cnt = cntData - sensor_tsdiff_normal_Cnt
                    bjTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(new_sensor_ts / 1000000))
                    print("[++原数据] 帧率异常，当前时间：" + str(new_sensor_ts) + " 北京时间：" + str(bjTime) + "; 当前帧计数:" + str(
                        cntData) + "; 丢帧次数:" + str(error_cnt) + "; 本次异常差值ms：" + str(sensor_tsdiff) + "; 丢帧数：" + str(
                        int(sensor_tsdiff / rate_ms + 0.5) - 1) + "\n")
                    sensor_tsdiff_lossFrames = sensor_tsdiff_lossFrames + int(sensor_tsdiff / rate_ms + 0.5) - 1
            old_sensor_ts = new_sensor_ts

            # 获取延迟时间ms
            delay = float(strData[2]) / 1000
            delayArr.append(delay)
            if (delay > delayMax):    delayMax = delay
            if (delay < delayMin):    delayMin = delay
            delaySum = delaySum + delay

            # 获取经纬度
            gpsLatArr.append(float(strData[3]))
            gpsLonArr.append(float(strData[4]))

            # 获取高度
            gpsAlt = float(strData[5])
            gpsAltArr.append(gpsAlt)
            if (gpsAlt > gpsAltMax):    gpsAltMax = gpsAlt
            if (gpsAlt < gpsAltMin):    gpsAltMin = gpsAlt
            gpsAltSum = gpsAltSum + gpsAlt

            # 获取固Ins-D状态， 0初始化， 1单点定位， 2码差分， 3无效PPS， 4固定解， 5浮点解， 6正在估算 7，人工输入固定值， 8模拟模式， 9WAAS差分
            starSts = int(strData[6])
            starStsArr.append(starSts)
            if (starSts == 0):
                starSts0Cnt = starSts0Cnt + 1
            elif (starSts == 1):
                starSts1Cnt = starSts1Cnt + 1
            elif (starSts == 2):
                starSts2Cnt = starSts2Cnt + 1
            elif (starSts == 3):
                starSts3Cnt = starSts3Cnt + 1
            elif (starSts == 4):
                starSts4Cnt = starSts4Cnt + 1
            elif (starSts == 5):
                starSts5Cnt = starSts5Cnt + 1
            else:
                starStsxCnt = starStsxCnt + 1
            if (starSts > starStsMax):    starStsMax = starSts
            if (starSts < starStsMin):    starStsMin = starSts
            starStsSum = starStsSum + starSts
            # 其他信息整合
            starSts_exinfo = " E0: " + str(round(starSts0Cnt / cntData * 100, 2)) + "%;   "
            starSts_exinfo += "E1: " + str(round(starSts1Cnt / cntData * 100, 2)) + "%;   "
            starSts_exinfo += "E2: " + str(round(starSts2Cnt / cntData * 100, 2)) + "%;   "
            starSts_exinfo += "E3: " + str(round(starSts3Cnt / cntData * 100, 2)) + "%;   "
            starSts_exinfo += "E4: " + str(round(starSts4Cnt / cntData * 100, 2)) + "%;   "
            starSts_exinfo += "E5: " + str(round(starSts5Cnt / cntData * 100, 2)) + "%\n"

            # 获取搜星数
            satNum = int(strData[7])
            satNumArr.append(satNum)
            if (satNum > satNumMax):    satNumMax = satNum
            if (satNum < satNumMin):    satNumMin = satNum
            satNumSum = satNumSum + satNum

            # 获取速度 str_speed
            speed = float(strData[8])
            speedArr.append(speed)
            if (speed > speedMax):    speedMax = speed
            if (speed < speedMin):    speedMin = speed
            speedSum = speedSum + speed

        # 计算平均值
        dealover_tsdiff_Avg = round(dealover_tsdiff_Sum / (cntData - 1), 3)
        dealover_tsdiff_normal_Avg = round(dealover_tsdiff_normal_Sum / (dealover_tsdiff_normal_Cnt - 1), 3)
        sensor_tsdiff_Avg = round(sensor_tsdiff_Sum / (cntData - 1), 3)
        sensor_tsdiff_normal_Avg = round(sensor_tsdiff_normal_Sum / (sensor_tsdiff_normal_Cnt - 1), 3)
        delayAvg = round(delaySum / cntData, 1)
        gpsAltAvg = round(gpsAltSum / cntData, 3)
        starStsAvg = round(starStsSum / cntData, 1)
        satNumAvg = round(satNumSum / cntData, 1)
        speedAvg = round(speedSum / cntData, 2)

        # 设定扩展信息
        dealover_tsdiff_exinfo += " start_time: " + time.strftime('%Y-%m-%d %H:%M:%S',
                                                                  time.localtime(dealover_startTime / 1000000))
        dealover_tsdiff_exinfo += ";  dur_time(hr): " + str(
            round((dealover_endTime - dealover_startTime) / 3600000000, 2)) + "  ; rate(ms): " + str(rate_ms)
        dealover_tsdiff_exinfo += ";  normalFrame(min/max/avg-ms): " + str(dealover_tsdiff_normal_Min) + "/" + str(
            dealover_tsdiff_normal_Max) + "/" + str(dealover_tsdiff_normal_Avg) + "\n"
        dealover_tsdiff_exinfo += " total_frames: " + str(cntData)
        dealover_tsdiff_exinfo += ";  loss_times: " + str(cntData - 1 - dealover_tsdiff_normal_Cnt)
        dealover_tsdiff_exinfo += ";  loss_frames: " + str(dealover_tsdiff_lossFrames)
        dealover_tsdiff_exinfo += ";  loss_per: " + str(
            round((cntData - 1 - dealover_tsdiff_normal_Cnt) / (cntData - 1) * 10000, 4)) + "/10000\n"
        # 设定扩展信息
        sensor_tsdiff_exinfo += " start_time: " + time.strftime('%Y-%m-%d %H:%M:%S',
                                                                time.localtime(sensor_startTime / 1000000))
        sensor_tsdiff_exinfo += ";  dur_time(hr): " + str(
            round((sensor_endTime - sensor_startTime) / 3600000000, 2)) + "  ; rate(ms): " + str(rate_ms)
        sensor_tsdiff_exinfo += ";  normalFrame(min/max/avg-ms): " + str(sensor_tsdiff_normal_Min) + "/" + str(
            sensor_tsdiff_normal_Max) + "/" + str(sensor_tsdiff_normal_Avg) + "\n"
        sensor_tsdiff_exinfo += " total_frames: " + str(cntData)
        sensor_tsdiff_exinfo += ";  loss_times: " + str(cntData - 1 - sensor_tsdiff_normal_Cnt)
        sensor_tsdiff_exinfo += ";  loss_frames: " + str(sensor_tsdiff_lossFrames)
        sensor_tsdiff_exinfo += ";  loss_per: " + str(
            round((cntData - 1 - sensor_tsdiff_normal_Cnt) / (cntData - 1) * 10000, 4)) + "/10000\n"

        # 关闭数据源文件
        f9p_data_File.close()

        # 数据波线图
        # single_data_draw(data_arr, data_cnt, data_max, data_min, data_avg, data_info, extend_info, output_path)
        image_draw.single_data_draw(dealover_tsdiff_arr, cntData - 1, dealover_tsdiff_Max, dealover_tsdiff_Min,
                                    dealover_tsdiff_Avg, "01-{:s}-Dealover-ts(ms)".format(filename), dealover_tsdiff_exinfo, output_url)
        image_draw.single_data_draw(sensor_tsdiff_arr, cntData - 1, sensor_tsdiff_Max, sensor_tsdiff_Min, sensor_tsdiff_Avg,
                                    "02-{:s}-Sensor-ts(ms)".format(filename), sensor_tsdiff_exinfo, output_url)
        image_draw.single_data_draw(delayArr, cntData, delayMax, delayMin, delayAvg, "03-{:s}-Delay(ms)".format(filename), delay_exinfo,
                                    output_url)
        image_draw.single_data_draw(starStsArr, cntData, starStsMax, starStsMin, starStsAvg, "04-{:s}-StarSts".format(filename),
                                    starSts_exinfo, output_url)
        image_draw.single_data_draw(gpsAltArr, cntData, gpsAltMax, gpsAltMin, gpsAltAvg, "05-{:s}-GpsAlt".format(filename), gpsAlt_exinfo,
                                    output_url)
        image_draw.single_data_draw(satNumArr, cntData, satNumMax, satNumMin, satNumAvg, "06-{:s}-satNum".format(filename), satNum_exinfo,
                                    output_url)
        image_draw.single_data_draw(speedArr, cntData, speedMax, speedMin, speedAvg, "07-{:s}-speed".format(filename), speed_exinfo,
                                    output_url)
        image_draw.map_data_draw(gpsLatArr, gpsLonArr, starStsArr, "08-{:s}-Map".format(filename), starSts_exinfo, output_url)

        image_draw.google_map_draw(gpsLatArr, gpsLonArr, starStsArr, "09-{:s}-Map".format(filename), starSts_exinfo, output_url)


if __name__ == '__main__':
    file_name = r'C:\Users\liuxiang\Desktop\yace-log\f9p'
    out_put = r'C:\Users\liuxiang\Desktop\output_new'
    rate_ms = 125
    # filename = 'f9pname'
    start_time = time.time()
    print(start_time)
    f9p_class = f9p_file(file_name,out_put,rate_ms) #创建一个对象
    # f9p_class.f9p_data_analysis(file_name,out_put,rate_ms,filename)
    end_time = time.time()
    print(end_time)
    time_interval = end_time - start_time
    print(time_interval)


