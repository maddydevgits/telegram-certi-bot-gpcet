import telebot
import os
import ast

import boto3
client=boto3.client('s3')

s3_resource = boto3.resource("s3", region_name='us-east-1')
s3_bucket = s3_resource.Bucket('msteam')
data=[]
for obj in s3_bucket.objects.filter(Prefix='maddydev'+"/"):
    # for obj in s3_bucket.objects.all():
    print(f'-- {obj.key}')
    dummy=[]
    dummy.append(obj.key)
    dummy.append('maddydev')
    dummy.append('https://msteam.s3.amazonaws.com/'+obj.key)
    data.append(dummy)
    # print(data)

RollNo=[]
for i in data:
    t=i[0]
    t=t.split('/')
    t=t[1]
    t=t.split('.')
    t=t[0]
    RollNo.append(t)

# print(RollNo)

botToken='5731756178:AAHKmXUH8mSyBcwkzTfZRPWoDvC4pVzi8mU'
incomingBot = telebot.TeleBot(botToken, parse_mode=None) 

@incomingBot.message_handler(commands=['start', 'help'])
def send_welcome(message):
 incomingBot.reply_to(message, "Welcome to Make Skilled Certi Bot,\n do Enter your registered Roll No")

@incomingBot.message_handler(regexp="[a-zA-Z0-9_]")
def handle_message(message):
    #print('dummy',message)
    message=str(message)
    k=ast.literal_eval(message)
    print(k,type(k))
    chat_id=(k['from_user']['id'])
    m=k['text'].upper()
    print(m,chat_id)
    flag=0
    for i in RollNo:
        if(i==m):
            flag=1
            rindex=RollNo.index(m)
            incomingBot.send_message(int(chat_id),'Hey, Hi Buddy\n\nNice meeting you again ' + str(i) + '. \n\nSpecial thanks for participating in our Programme and you can download the certificate from here:\n\n' + data[rindex][2]+'\n\n Keep doing all the great work like what you did in the internship.' + '\n\nThank You \nMake Skilled Team')
    if(flag==0):
        incomingBot.send_message(int(chat_id),'Please provide your registered Roll No')
        pass

incomingBot.polling()