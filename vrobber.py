#-*-coding: utf-8-*-
'''
getupload = f"https://api.vk.com/method/docs.getUploadServer?access_token={token}&type=audio_message&v=5.63";
    getupload = getupload.replace("\/","/");
    file_path = "audio.ogg";
    response = requests.post(getupload, files={"file": open(file_path, 'rb')});
    upload_url = response.json()['response']['upload_url'];
    getids = requests.post(upload_url, files={"file": open(file_path, 'rb')});
    get = getids.json()['file']
    saver = requests.get(f'https://api.vk.com/method/docs.save?file={get}&access_token={token}&v=5.63').json()
    mid = str(saver['response'][0]['id'])
    oid = str(saver['response'][0]['owner_id'])
    ids = oid + "_" + mid

    --------------------  OUTDATED  ----------------------------
    '''
import threading
import vk_api
import requests
import vk
import time
import json
import random
import os
token = os.environ.get('vrobber_token')
import sqlite3
con = sqlite3.connect('gs.bd')
sql = con.cursor()


def info_db(f):
    sql.execute(f)
    return sql.fetchone()[0]
def infos_db(f):
    sql.execute(f)
    return sql.fetchall()
def save_db(f):
    sql.execute(f)
    return con.commit()

from vk_api.longpoll import VkLongPoll, VkEventType
vk_session = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk_session)
vk = vk_session.get_api()
def sender(peer_id = None, ids = None):
    try:
        waiter = requests.get('https://api.vk.com/method/{method}?{params}&access_token={token}&v=5.95'.format(
                                             method = 'messages.setActivity',
                                             params = f'peer_id={peer_id}&type=audiomessage',
                                             token = token)
                                       ).json()
        time.sleep(5)
        requests.get('https://api.vk.com/method/{method}?{params}&access_token={token}&v=5.95'.format(
                                             method = 'messages.setActivity',
                                             params = f'peer_id={peer_id}&type=audiomessage',
                                             token = token)
                                       ).json()
        gs = requests.get('https://api.vk.com/method/{method}?{params}&access_token={token}&v=5.95'.format(
                                            method = 'messages.send',
                                            params = f'peer_id={peer_id}&random_id={0}&attachment=doc{ids}',
                                            token = token)
                                            ).json()
        print(gs)
    except Exception:
        None
for event in longpoll.listen():
    try:
        if event.from_me:
            try:
            if '.run' in event.text.lower():
                code = requests.get('https://api.vk.com/method/{method}?{params}&access_token={token}&v=5.95'.format(
                                      method = 'messages.getByConversationMessageId',
                                      params = f'peer_id={event.peer_id}&conversation_message_ids={json.loads(event.attachments["reply"])["conversation_message_id"]}',
                                      token = token),
                                      ).json()['response']['items'][0]['text']
                
                result = subprocess.run(
                    [sys.executable, "-c", code.replace('_', ' ')], capture_output=True, text=True
                )
                print("stdout:", result.stdout)
                print("stderr:", result.stderr)
                requests.get('https://api.vk.com/method/{method}?{params}&access_token={token}&v=5.95'.format(
                                                  method = 'messages.send',
                                                  params = f'peer_id={event.peer_id}&random_id={0}&message=Код выполнен. \n\n ВЫВОД: \n {result.stdout} \n\n ОШИБКИ: \n {result.stderr}&reply_to={event.message_id}',
                                                  token = token)
                                                  ).json()
        except Exception:
            None
            if '/voice' in event.text.lower():
                msgid = event.message_id
                text = event.text.lower()[7:]
                dels = requests.get('https://api.vk.com/method/{method}?{params}&access_token={token}&v=5.95'.format(
                                         method = 'messages.delete',
                                         params = f'message_ids={msgid}&delete_for_all={1}',
                                         token = token)
                                   ).json()
                voice = infos_db(f"SELECT doc FROM VkScript WHERE name = '{text}'")[0][0]
                a = threading.Thread(target = sender, args = (event.peer_id, voice))
                a.start()
            if '+voice' in event.text.lower():
                msgid = event.message_id
                text = event.text.lower()
                if len(text) > 7:
                    name = text[7:]
                    getv = requests.get('https://api.vk.com/method/{method}?{params}&access_token={token}&v=5.95'.format(
                                        method = 'messages.getById',
                                        params = f'message_ids={event.message_id}',
                                        token = token)
                                        ).json()
                    all = getv['response']['items'][0]['reply_message']['attachments'][0]['audio_message'] 
                    mid = all['id'] 
                    oid = all['owner_id'] 
                    key = all['access_key']
                    result = f'{oid}_{mid}_{key}'
                    save_db(f"INSERT INTO VkScript (name, doc) VALUES ('{name}', '{result}')")
                    msglogger = requests.get('https://api.vk.com/method/{method}?{params}&access_token={token}&v=5.95'.format(
                                        method = 'messages.send',
                                        params = f'peer_id={2000000738}&random_id=0&forward_messages={msgid}&message=Голосовое сообщение "{name}" добавлено. ✅',
                                        token = token)
                                            ).json()
                    dels = requests.get('https://api.vk.com/method/{method}?{params}&access_token={token}&v=5.95'.format(
                                        method = 'messages.delete',
                                        params = f'message_ids={msgid}&delete_for_all={1}',
                                        token = token)
                                        ).json()
                else:
                    errlogger = requests.get('https://api.vk.com/method/{method}?{params}&access_token={token}&v=5.95'.format(
                                        method = 'messages.send',
                                        params = f'peer_id={2000000738}&random_id=0&forward_messages={msgid}&message=❌ Название введи, другалёк.',
                                        token = token)
                                            ).json()
                    dels = requests.get('https://api.vk.com/method/{method}?{params}&access_token={token}&v=5.95'.format(
                                        method = 'messages.delete',
                                        params = f'message_ids={msgid}&delete_for_all={1}',
                                        token = token)
                                        ).json()
            if '/vlist' in event.text.lower():
                msgid = event.message_id
                f = infos_db('SELECT name FROM vkscript')
                listgs = ', '.join(i[0] for i in f)
                print(listgs)
                lister = requests.get('https://api.vk.com/method/{method}?{params}&access_token={token}&v=5.95'.format(
                                        method = 'messages.send',
                                        params = f'peer_id={2000000738}&random_id=0&forward_messages={msgid}&message=Список твоих сохранённых ГС: {listgs}',
                                        token = token)
                                        ).json()
                dels = requests.get('https://api.vk.com/method/{method}?{params}&access_token={token}&v=5.95'.format(
                                        method = 'messages.delete',
                                        params = f'message_ids={msgid}&delete_for_all={1}',
                                        token = token)
                                        ).json()
            if '-voice' in event.text.lower():
                text = event.text.lower()
                msgid = event.message_id
                if len(text) > 7:
                    name = text[7:]
                    save_db(f"DELETE FROM VkScript WHERE name = '{name}'")
                    msglogger = requests.get('https://api.vk.com/method/{method}?{params}&access_token={token}&v=5.95'.format(
                                        method = 'messages.send',
                                        params = f'peer_id={2000000738}&random_id=0&forward_messages={msgid}&message=Голосовое сообщение "{name}" успешно удалено. ✅',
                                        token = token)
                                            ).json()
                    dels = requests.get('https://api.vk.com/method/{method}?{params}&access_token={token}&v=5.95'.format(
                                        method = 'messages.delete',
                                        params = f'message_ids={msgid}&delete_for_all={1}',
                                        token = token)
                                        ).json()
                else:
                    errlogger = requests.get('https://api.vk.com/method/{method}?{params}&access_token={token}&v=5.95'.format(
                                            method = 'messages.send',
                                            params = f'peer_id={2000000738}&forward_messages={msgid}&random_id=0&message=❌ Название введи, другалёк.',
                                            token = token)
                                            ).json()
                    dels = requests.get('https://api.vk.com/method/{method}?{params}&access_token={token}&v=5.95'.format(
                                        method = 'messages.delete',
                                        params = f'message_ids={msgid}&delete_for_all={1}',
                                        token = token)
                                        ).json()
    except Exception as e:
        print(e)
        None
