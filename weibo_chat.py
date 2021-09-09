import datetime

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait

import requests

INDEX_FILE = './chat.txt'

HEADER = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36 Edg/93.0.961.38',
    'Referer': 'https://api.weibo.com/chat/'
}


def download_file(s, url, local_filename):
    with s.get(url, stream=True, headers=HEADER) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename


def parse_message(s, message_json, file_handle):
    message_time = message['created_at']
    message_author = message['sender_screen_name']
    message_text = message['text']

    if len(message_time) != 0:
        t = datetime.datetime.strptime(message_time, "%a %b %d %H:%M:%S %z %Y")
        message_time = t.strftime("%Y-%m-%d %H:%M:%S")

    if message_text == '分享视频' and 'ext_text' in message:
        for fid in list(set(message['att_ids'])):
            attachment_url = f'https://upload.api.weibo.com/2/mss/msget?source=209678993&fid={fid}'
            local_filename = message_time + ' ' + str(fid) + '.mp4'
            local_filename = local_filename.replace(':', '-')
            download_file(s, attachment_url, local_filename)

    if message_text == '分享图片' and 'ext_text' in message:
        for fid in list(set(message['att_ids'])):
            attachment_url = f'https://upload.api.weibo.com/2/mss/msget?source=209678993&fid={fid}'
            local_filename = message_time + ' ' + str(fid) + '.jpg'
            local_filename = local_filename.replace(':', '-')
            download_file(s, attachment_url, local_filename)

    if message_text == '分享语音' and 'ext_text' in message:
        for fid in list(set(message['att_ids'])):
            attachment_url = f'https://api.weibo.com/amrdata/{fid}?source=209678993'
            local_filename = message_time + ' ' + str(fid) + '.mp3'
            local_filename = local_filename.replace(':', '-')
            download_file(s, attachment_url, local_filename)

    f.write(message_time + ' ' + message_author + ' ' + message_text + '\n')


if __name__ == '__main__':
    with open(INDEX_FILE, 'w', encoding='utf8') as f:
        with webdriver.Chrome() as driver:
            driver.maximize_window()

            driver.get('https://weibo.com/')
            print('去手动登录微博')

            WebDriverWait(
                driver, 1e5
            ).until(lambda d: d.find_elements_by_class_name(
                'woo-box-flex.woo-box-alignCenter.woo-box-justifyCenter.Ctrls_item_3KzNH.Ctrls_avatarItem_3LrJN'
            ))  # 寻找登入标记

            driver.get('https://api.weibo.com/chat/')  # 转跳页面
            # 等待页面加载
            WebDriverWait(driver,
                          20).until(lambda d: d.find_elements_by_class_name(
                              'sessionlist.relative.flex.align-items_c'))

            chats = driver.find_elements_by_class_name(
                'sessionlist.relative.flex.align-items_c')

            # 把你要获取的对话放在左侧列表的最上面
            target = chats[0]

            uid = target.find_element_by_class_name(
                'name.fff.nowrap.font14').find_elements_by_tag_name(
                    'span')[1].get_attribute('innerHTML')

            cookies = driver.get_cookies()

            s = requests.Session()
            for cookie in cookies:
                s.cookies.set(cookie['name'], cookie['value'])

            maxid = 0

            while True:
                url = f'https://api.weibo.com/webim/2/direct_messages/conversation.json?convert_emoji=1&count=15&max_id={maxid}&uid={uid}&is_include_group=0&source=209678993'

                r = s.get(url, headers=HEADER)

                messages = r.json()
                if len(messages['direct_messages']
                       ) == 0 and messages['total_number'] == 0:
                    break

                for message in messages['direct_messages']:
                    parse_message(s, message, f)

                if len(messages['direct_messages']) != 0:
                    maxid = messages['direct_messages'][-1]['id'] - 1
                else:
                    break
