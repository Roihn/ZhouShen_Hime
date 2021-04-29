
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PyQt5.QtCore import QCoreApplication
import os
import re
from asstm import *

from hime_ui2_0 import Ui_MainWindow





required_type = 'Default'
biaodian = {'。。。': '...', '。': ' ', '‘': '「', '’': '」', '・・・': '...', '···': '...',
        '“': '「', '”': '」', '、': ' ', '~': '～', '!': '！', '?': '？', '　': ' ', '【': '「', '】': '」'}      # 默认要替换的标点
emend_mark = ["xx","??","？？"]
output_header = """
####################################################################
##########################真的晒字幕组###############################
####################################################################
########################专用*对话轴*审轴姬###########################
####################################################################\n\n
"""
def open_dict():
    with open('punctuation.txt', 'r', encoding='utf-8') as fx:
        lin = fx.readlines()
    for i in range(len(lin)):
        lin[i] = lin[i].replace('\n', '')
    test_dict = {}
    new_dict = {}
    for i in lin:
        tmp_dict = eval(i)
        print(tmp_dict)
        for key, value in tmp_dict.items():
            test_dict[key] = value
        new_dict[test_dict['Wrong Punctuation']] = test_dict['Correct Punctuation']
    return new_dict

def write_dict():
    bd2 = []
    for key, value in biaodian.items():
        tmp = {}
        tmp['Wrong Punctuation'] = key
        tmp['Correct Punctuation'] = value
        bd2.append(tmp)
    with open('biaodian.txt', 'w', encoding='utf-8') as fx:
        for i in bd2:
            fx.write(str(i))
            fx.write('\n')


class zhoushen_GUi(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(zhoushen_GUi, self).__init__(parent)
        self.gai_shan_zhou = False
        
        self.setupUi(self)
        self.progressBar.setValue(0)
        # 打开文件
        self.OpenFile.clicked.connect(self.fileopen)
        # 检查要不要连闪轴
        self.radioButton.toggled.connect(lambda :self.rBstate(self.radioButton))
        # 开始锤
        self.StartProgram.clicked.connect(self.kai_shi)

        # 检查并打开符号替换的txt文件
        try:
            self.biaodian = open_dict()
        except FileNotFoundError:
            reply = QMessageBox.question(self, '信息', '没有找到字符替换文件！\n已自动重建',
                QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                write_dict()
                self.biaodian = open_dict()
        except SyntaxError:
            reply = QMessageBox.question(self, '错误', '字符替换文件格式有误！\n是否重建？',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                write_dict()
                self.biaodian = open_dict()
            else:
                os._exit(5)

    def rBstate(self, radioButton):
        if radioButton.isChecked():
            self.textBrowser.append('开启无脑连轴模式！')
            self.gai_shan_zhou = True
        # else:
        #     self.gai_shan_zhou == False

    def fileopen(self):
        self.fileName_path, self.filetype = QFileDialog.getOpenFileName(self,
                "选取文件",
                "./",
                "ASS Files (*.ass)")  #设置文件扩展名过滤,注意用双分号间隔
        if self.fileName_path == '':
            return None
        # 打开文件
        self.textBrowser.append(self.fileName_path)
        self.name = self.fileName_path.split('/')[-1]
        self.path = self.fileName_path[:-len(self.name)]
        with open(self.fileName_path, 'r', encoding='utf-8-sig') as fass:
            self.line, self.header = [], []
            for i in fass.readlines():
                if i[:8] == 'Dialogue':
                    self.line.append(i)
                elif i[:7] == 'Comment':
                    self.line.append(i)
                else:
                    self.header.append(i)
        self.textBrowser.append('ass文件读取成功！')
        self.progress_point = 0
        self.progressBar.setValue(0)

    def kai_shi(self):
        # 读取时间和位置
        self.info_list = []
        for i, l in enumerate(self.line):
            if not re.search(r",fx,",l) and l[:7] != 'Comment':
                entries = l.rstrip().split(',')
                if entries[3] != required_type:
                    continue
                tmp_info_dict = {
                    "start": entries[1],
                    "end": entries[2],
                    "index": i+1
                }
                self.info_list.append(tmp_info_dict)

        # 先检查符号
        self.outlog = output_header
        self.textBrowser.append('##############开始字符检查#################')
        self.outlog += '##############开始字符检查#################\n'
        self.char_check()
        self.textBrowser.append('##############字符检查完毕#################')
        self.outlog += '##############字符检查完毕#################\n\n'

        self.progressBar.setValue(9)
        self.progress_point = 9
        # 开始锤轴啦

        lenth = len(self.info_list)              # 总行数
        ckpt = round(lenth / 90)        # 进度条计数器
        
        # Sort all the lines with required_type based on start time
        self.info_list = sorted(self.info_list, key=lambda info:info['start'])

        # 查行内的闪轴
        self.textBrowser.append('##############开始行内闪轴检查#################')
        self.outlog += '##############开始行内闪轴检查#################\n'
        self.inline_flash_check()
        self.textBrowser.append('##############行内闪轴检查完毕#################')
        self.outlog += '##############行内闪轴检查完毕#################\n\n'
        
        # 查行间的闪轴
        self.textBrowser.append('##############开始行间闪轴检查#################')
        self.outlog += '##############开始行间闪轴检查#################\n'
        self.inter_flash_check()
        self.textBrowser.append('##############行间闪轴检查完毕#################')
        self.outlog += '##############行间闪轴检查完毕#################\n\n'

        # 查行间的重叠
        self.textBrowser.append('##############开始行间重叠检查#################')
        self.outlog += '##############开始行间重叠检查#################\n'
        self.overlap_check()
        self.textBrowser.append('##############行间重叠检查完毕#################')
        self.outlog += '##############行间重叠检查完毕#################\n\n'

        self.progressBar.setValue(100)
        self.textBrowser.append("看完了！")
        self.outlog += '看完了！\n'
        with open(self.path + '改-' + self.name[:-4] + '.txt', 'w', encoding='utf-8') as ft:
            ft.writelines(self.outlog)
        with open(self.path + '改-' + self.name, 'w', encoding='utf-8-sig') as fn:
            fn.writelines(self.header)
            fn.writelines(self.line)
        reply = QMessageBox.question(self, '信息', '锤完了！',
                QMessageBox.Ok)

    def char_check(self):
        """检查字符问题."""
        for i in range(len(self.line)):
            if self.line[i][:7] == 'Comment' or re.search(r",fx,", self.line[i]):      # 跳过注释
                continue
            for mark in emend_mark:
                if mark in self.line[i].split(',')[9]:
                    msg = '第{}行可能翻译没听懂，校对请注意一下————{}'.format(
                        i+1, self.line[i].split(',')[9].replace('\n', ''))
                    self.print_log(msg)
            for key, value in self.biaodian.items():
                if key in self.line[i].split(',')[9]:
                    self.line[i] = self.line[i].replace(key, value)
                    msg = "第{}行轴的{}标点有问题，但是我给你换成了{}".format(i+1, key, value)
                    self.print_log(msg)

    def inline_flash_check(self):
        """检查行内闪轴问题."""
        ckpt = round(len(self.info_list)/10)
        for i in range(len(self.info_list)): 
            if i % ckpt == 0:
                if self.progress_point <= 99:
                    self.progress_point += 1
                    self.progressBar.setValue(self.progress_point)

            # 先锤单行自己的闪轴
            tdelta1 = timedelta(self.info_list[i]['end'], self.info_list[i]['start'])                   # 轴的时间
            if tdelta1 <= 0.49 and tdelta1 > 0:
                tneeded = 0.5 - tdelta1                                   # 算出要加的时间
                if i == len(self.info_list)-1:  # 单独处理最后一行内容
                    tdelta2 = 1
                else:
                    tdelta2 = timedelta(self.info_list[i+1]['start'], self.info_list[i]['end'])   #算出与下一句的时间间隔
                if tdelta2 < 0.001:
                    # 前一个轴是闪轴，但后面有连轴
                    msg = "第{}行轴是闪轴（{}ms），但是它和{}行轴是连轴，所以看着改吧".format(
                                self.info_list[i]['index'], tdelta1*1000, self.info_list[i+1]['index']
                        )
                    self.print_log(msg)
                    continue
                if tdelta2 < tneeded:
                    # 前一个轴是闪轴，但如果拉长到300ms会与下一个轴冲突
                    if self.gai_shan_zhou:
                        msg = "第{}行轴（{}ms）是闪轴，但拉长就会和第{}行轴冲突了，我姑且给你连上了".format(
                            self.info_list[i]['index'], tdelta1*1000, self.info_list[i+1]['index'])
                        self.line[self.info_list[i]['index']-1] = self.line[self.info_list[i]['index']-1].replace(
                            self.line[self.info_list[i]['index']-1].split(',')[2], self.info_list[i+1]['start'])
                        self.info_list[i]['end'] = self.info_list[i+1]['start']
                    else:
                        msg = "第{}行轴（{}ms）是闪轴，但拉长就会和第{}行轴冲突，你自己看着改吧".format(
                            self.info_list[i]['index'], tdelta1*1000, self.info_list[i+1]['index'])
                    self.print_log(msg)
                    continue
                
                # 排除特殊情况后 接下来都是常规的行内闪轴
                if self.gai_shan_zhou:
                    tmp = timeplus(self.info_list[i]['end'], tneeded)
                    msg = "第{}行轴是闪轴（{}ms），但是我给你改好了，以防万一告诉你一下从{}改成了{}".format(
                        self.info_list[i]['index'], tdelta1*1000, self.info_list[i]['end'], tmp)
                    self.line[self.info_list[i]['index']-1] = self.line[self.info_list[i]['index']-1].replace(
                        self.line[self.info_list[i]['index']-1].split(',')[2], tmp)
                    self.info_list[i]['end'] = tmp
                else:
                    msg = "第{}行轴是闪轴（{}ms），请注意一下".format(self.info_list[i]['index'], tdelta1*1000)
                self.print_log(msg)
            i += 1

    def inter_flash_check(self):
        """检查行间闪轴问题."""
        ckpt = round(len(self.info_list)/70)
        for i in range(len(self.info_list)-1): # 无需检查最后一行 
            if i % ckpt == 0:
                if self.progress_point <= 99:
                    self.progress_point += 1
                    self.progressBar.setValue(self.progress_point)
            # 锤行与行之间的闪轴
            tdelta = timedelta(self.info_list[i+1]['start'], self.info_list[i]['end'])                   # 轴的时间
            if tdelta < 0.289 and tdelta > 0: 
                if self.gai_shan_zhou:
                    msg = "第{}行轴和第{}行轴之间是闪轴（{}ms），不过我给你连上了（{}）".format(
                        self.info_list[i]['index'], self.info_list[i+1]['index'], tdelta*1000, self.info_list[i]['start'])
                    self.line[self.info_list[i]['index']-1] = self.line[self.info_list[i]['index']-1].replace(
                                self.line[self.info_list[i]['index']-1].split(',')[2], self.info_list[i+1]['start'])
                    self.info_list[i]['end'] = self.info_list[i+1]['start']
                else:
                    msg = '第{}行轴和第{}行轴之间是闪轴（{}ms），建议连上（{}）'.format(
                        self.info_list[i]['index'], self.info_list[i+1]['index'], tdelta*1000, self.info_list[i]['start']
                    )
                self.print_log(msg)

    def overlap_check(self):
        """检查行间重叠问题."""
        ckpt = round(len(self.info_list)/10)
        for i in range(len(self.info_list)-1): # 无需检查最后一行 
            if i % ckpt == 0:
                if self.progress_point <= 99:
                    self.progress_point += 1
                    self.progressBar.setValue(self.progress_point)

            if self.info_list[i]['end'] > self.info_list[i+1]['start']:
                msg = "第{}行轴与第{}行轴有重叠，请检查（{}）".format(
                    self.info_list[i]['index'], self.info_list[i+1]['index'], self.info_list[i]['start'])
                self.print_log(msg)

    def print_log(self, msg):
        """输出log信息."""
        self.textBrowser.append(msg)
        self.outlog += msg + '\n'

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = zhoushen_GUi()
    window.show()
    sys.exit(app.exec_())