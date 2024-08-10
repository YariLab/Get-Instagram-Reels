import os
import re
import requests
import time
import urllib.request
from multiprocessing.pool import ThreadPool


# set up your data below

url = "https://www.instagram.com/api/v1/feed/user/***/username/?count=12"
headers = {}
cookies_array = []

cookies = { "cookie": "" }
for cookie in cookies_array:
  space = ' ' if cookies["cookie"] != '' else ''
  cookies["cookie"] = cookies["cookie"] + space + cookie

headers.update(cookies)

#======================================================= Stage 1 ==============================================================================

start = time.time()

try:
  response = requests.get(url, headers=headers).json()
  user_pk_id = response["user"]["pk_id"]
  items = []

  def hyper_loop(res_items):
    for item in res_items:
        try:
          if item["media_type"] == 2:
            items.append(
              {
                "code": item["code"],
                "link": item["video_versions"][0]["url"]
              }
            )
        except KeyError:
          pass

  hyper_loop(response["items"])

  while True:
    next_max_id = response["next_max_id"] if "next_max_id" in response else ''
    if next_max_id != '':
      next_url = f'https://www.instagram.com/api/v1/feed/user/{user_pk_id}/?count=12&max_id={next_max_id}'
      response = requests.get(next_url, headers=headers).json()
      hyper_loop(response["items"])
    else:
      break

except KeyError:
  pass

print(f'Response time: {round(time.time() - start, 2)} sec')
print(f'Count of reels: {len(items)}')
items.reverse()

#=================================================== Stage 2 ====================================================================================

count = 50
count_stop = 200
path = "E:/reels/"

listdir = os.listdir(path)

def zero_lead(reels_count, count):
      max_len = len(str(reels_count - 1)) + 1
      return str(count).rjust(max_len, '0')

def download_reel(item):
  try:
    link = item["link"]
    global count
    if count < count_stop:
      pattern = re.compile("\d+_" + item["code"] + ".mp4")
      for filepath in listdir:
        if pattern.match(filepath):
          return
        
      count = count + 1 if link is not None else count
      filename = zero_lead(len(items), count) + "_" + item["code"] + ".mp4" if item["code"] != "" or None else "reel_" + count + ".mp4"
      start_download = time.time()
      urllib.request.urlretrieve(link, path + filename)
      return f'Reel [{filename}] downloaded by: {round(time.time() - start_download, 2)} sec'
    pass
  except KeyError:
    pass

results = ThreadPool(4).imap_unordered(download_reel, items)
for msg in results:
   print(msg) if msg is not None else ''

print(f'Script executed time: {round(time.time() - start, 2)} sec')

