import urllib3
import os
from datetime import datetime

SOURCE = "http://www.bing.com"
STORAGE = "./images/"
LOGFILE = ".logfile"
SET_WALLPAPER = "gsettings set org.gnome.desktop.background picture-uri file://$(\"pwd\")"
mkdir_if_required = "if [ ! -d " + STORAGE + " ]; then\n    mkdir " + STORAGE + "\n    fi"

def get_image_url(baseUrl):
    http = urllib3.PoolManager()
    req = http.request('GET', baseUrl)
    response = str(req.data)

    start = response.find("g_img={")
    end = response.find(".jpg")
    if start < 0 or end < 0:
        return -1

    while response[start] != '/':
        start += 1
    while response[end-1] != '_':
        end -= 1

    image_link = baseUrl + response[start:end] + "1920x1080.jpg"

    return image_link

def get_image_name(url):
    start = 0
    while url.find('/', start + 1) >= 0:
        start = url.find('/', start + 1)
    start = start + 1
    end = url.find('_', start)

    name_tmp = url[start:end]
    name = name_tmp[0]

    for c in name_tmp[1:]:
        if str.isupper(c):
            name = name + "\ " + c
            continue
        name  = name + c
    name = name + ".jpg"
    default_name = url[start:]

    return (default_name, name)

def check_existing_image():
    date = datetime.now().strftime("%Y%m%d")

    if os.path.isfile(LOGFILE):
        with open(LOGFILE, "r") as logfile:
            last_log = logfile.readlines()[-1]
            last_retrieved_on = last_log[:last_log.find(" ")]
            last_retrieved_file = last_log[last_log.find(" ") + 1:].strip()
            last_retrieved_file_without_escape_sequences = ""
            for c in last_retrieved_file:
                if c != '\\':
                    last_retrieved_file_without_escape_sequences += c
            if date == last_retrieved_on and os.path.exists(STORAGE + last_retrieved_file_without_escape_sequences):
                print "You have the latest image."
                os.system(SET_WALLPAPER + STORAGE[1:] + last_retrieved_file)
                print "Reset that image as wallpaper. Exiting..."
                return 0
            elif os.path.exists(STORAGE + last_retrieved_file_without_escape_sequences):
                os.system("rm -f " + STORAGE + last_retrieved_file_without_escape_sequences)

            return 1

def download_image(url):
    try:
        default_name, name = get_image_name(url)
        date = datetime.now().strftime("%Y%m%d")
        os.system("wget " + url)
        os.system("mv " + default_name + " " + STORAGE + date + "-" + name)

        with open(LOGFILE, "a") as logfile:
            logfile.write(date + " " + date + "-" + name + "\n")
        return name
    except:
        print "Error. Exiting..."
        return -1

def set_wallpaper(name):
    date = datetime.now().strftime("%Y%m%d")
    os.system(SET_WALLPAPER + STORAGE[1:] + date + "-" + name)

def main():
    os.system(mkdir_if_required)

    if check_existing_image() == 0:
        return 0

    url = get_image_url(SOURCE)
    if url == -1:
        print "Error obtaining the image URL"
        return -1
    
    name = download_image(url)
    if name == -1:
        return -2

    set_wallpaper(name)

main()
