#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib.request
import os
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

class Eastmoney():
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.time, self.money_7, self.money = self.get_percentage()

    @staticmethod
    def getabstrs(a, b, strs):# a|str|b
        if a == '':
            return strs[:strs.find(b)]
        elif b == '':
            return strs[strs.find(a) + len(a):]
        else:
            strs = strs[strs.find(a) + len(a):]
            return strs[:strs.find(b)]

    @staticmethod
    def gethtml(url, headers):
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            return response.read().decode('utf-8')

    @staticmethod
    def headers(referer=None, cookie=None):
        # a reasonable UA
        ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'
        headers = {'User-Agent': ua}
        if referer is not None:
            headers.update({'Referer': referer})
        if cookie is not None:
            headers.update({'Cookie': cookie})
        return headers

    def main_url(self):
        return 'http://fund.eastmoney.com/%s.html' % self.id
        
    def get_percentage(self):
        html = self.gethtml(self.main_url(), self.headers(referer='http://fund.eastmoney.com/'))
        #记录时间 #七日年化 #万份收益
        return self.getabstrs('class="fix_date">', '<', html), \
            self.getabstrs('ui-font-middle ui-color-red ui-num">', '%<', html) , \
            self.getabstrs('class="fix_dwjz  bold ui-color-red">', '<', html)

def main():
    def mail_is_ok(my_sender, my_pass, to_users, my_message):
        try:
            msg=MIMEText(my_message, 'plain', 'utf-8')
            msg['From']=formataddr(['noreply', 'noreply@mail.com']) # 括号里的对应发件人邮箱昵称、发件人邮箱账号
            msg['To']=formataddr(['someone', 'someone@mail.com'])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
            msg['Subject']="基金七日年化报告"  # 邮件的主题，也可以说是标题
            server=smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器，端口是465
            server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
            server.sendmail(my_sender, to_users, msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
            server.quit() # 关闭连接
        except Exception:
            return False
        return True

    def eastmoneySort(data):
        eastmoney = [Eastmoney(id,name) for (id,name) in data]
        eastmoney.sort(key=lambda x:x.money_7,reverse=True)#由大到小,降序输出
        #for element in eastmoney:
        #    print(element.name,":",element.money_7)
        return eastmoney

    def is_change(new_id_list): # 优化为ini配置文件
        if os.access('eastmoney.ini', os.F_OK):
            with open('eastmoney.ini',"r", encoding="utf-8") as f:
                old_id_list = f.read()
                if old_id_list == new_id_list:
                    return False
                else:
                    return True
        else:
            return True

    data = [
        ('180008', '支付宝(余额宝)-银华货币A'),
        ('000638', '微信(零钱通)-富国富钱包货币'),
        ('000569', '京东(小金库)-鹏华增值宝货币'),
        ('000588', '招商银行(朝朝盈)-招商招钱宝货币A'),
        #('000644', '招商银行-招商招金宝货币A'),
        #('000730', '招商银行-博时现金宝货币A'),
        ('000397', '腾讯(腾讯腾安)-汇添富全额宝货币'),
        #('003536', '腾讯(腾讯腾安)-浦银安盛日日丰货币D'),
    ]
    data_list = eastmoneySort(data)
    new_id_list = ''
    for x in data_list:
        new_id_list += x.id
    if is_change(new_id_list):
        print('Need Change!!!')
        with open('eastmoney.ini', "w", encoding="utf-8") as f:
	        f.write(new_id_list)
        i = 0
        massage = '现在基金七日年化收益率排列出现变化！！！'
        for x in data_list:
            i+=1
            massage+='\n\n第%d为:\n%s%s\n|七日年化:%s%s||万份收益:%s|' % (i, x.name, x.time, x.money_7, '%', x.money)
        #print(massage)
        if mail_is_ok('***@qq.com', '***', ['***@qq.com'], massage):
            print("邮件发送成功!!!")
        else:
            print("邮件发送失败???")
    else:
        print('All Ok!!!')

if __name__ == '__main__':
    main()
