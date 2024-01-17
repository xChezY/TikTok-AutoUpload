import requests, secrets, string, uuid, zlib, json, datetime, re
from requests_auth_aws_sigv4 import AWSSigV4


def generate_random_string(length, underline):
    characters = (
        string.ascii_letters + string.digits + "_"
        if underline
        else string.ascii_letters + string.digits
    )
    random_string = "".join(secrets.choice(characters) for _ in range(length))
    return random_string


def crc32(content):
    prev = 0
    prev = zlib.crc32(content, prev)
    return ("%X" % (prev & 0xFFFFFFFF)).lower().zfill(8)


def print_response(r):
    print(f"{r = }")
    print(f"{r.content = }")


def print_error(url, r):
    print(f"[-] An error occured while reaching {url}")
    print_response(r)


def assert_success(url, r):
    if r.status_code != 200:
        print_error(url, r)
    return r.status_code == 200


def convert_tags(text, session):
    end = 0
    i = -1
    text_extra = []
    
    
    def text_extra_block(start, end, type, hashtag_name, user_id, tag_id):
        return {
            "end": end,
            "hashtag_name": hashtag_name,
            "start": start,
            "tag_id": tag_id,
            "type": type,
            "user_id": user_id
        }
    
    
    def convert(match):
        nonlocal i, end, text_extra
        i += 1
        if match.group(1):
            text_extra.append(text_extra_block(end, end+len(match.group(1))+1, 1, match.group(1), "", str(i)))
            end += len(match.group(1))+1
            return "<h id=\""+ str(i) +"\">#"+match.group(1)+"</h>"
        elif match.group(2):
            url = "https://www.tiktok.com/@"+match.group(2)
            headers = {
            'authority': 'www.tiktok.com',
            'accept': '*/*',
            'accept-language': 'q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6,zh;q=0.5,vi;q=0.4',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }

            r = session.request("GET", url, headers=headers)
            user_id = r.text.split('webapp.user-detail":{"userInfo":{"user":{"id":"')[1].split('"')[0]
            text_extra.append(text_extra_block(end, end+len(match.group(2))+1, 0, "", user_id, str(i)))
            end += len(match.group(2))+1
            return "<m id=\""+ str(i) +"\">@"+match.group(2)+"</m>"
        else:
            end += len(match.group(3))
            return match.group(3)
            
    result = re.sub(r'#(\w+)|@([\w.-]+)|([^#@]+)', convert, text)
    return result, text_extra


def upload_video(session_id, video_file, title, schedule_time=0, allow_comment=1, allow_duet=0, allow_stitch=0, visibility_type=0, brand_organic_type=0, branded_content_type=0):
    if schedule_time - datetime.datetime.now().timestamp() > 864000:
        print("[-] Can not schedule video in more than 10 days")
        return False
    if len(title) > 2200:
        print("[-] The title has to be less than 2200 characters")
        return False

    session = requests.Session()
    session.cookies.set("sessionid", session_id, domain=".tiktok.com")
    session.cookies.set("tt-target-idc", "useast2a", domain=".tiktok.com")

    # get project_id
    creation_id = generate_random_string(21, True)
    url = f"https://www.tiktok.com/api/v1/web/project/create/?creation_id={creation_id}&type=1&aid=1988"
    r = session.post(url)
    if not assert_success(url, r):
        return False

    # get project_id
    project_id = r.json()["project"]["project_id"]
    url = "https://www.tiktok.com/api/v1/video/upload/auth/?aid=1988"
    r = session.get(url)
    if not assert_success(url, r):
        return False

    # get upload info
    aws_auth = AWSSigV4(
        "vod",
        region="ap-singapore-1",
        aws_access_key_id=r.json()["video_token_v5"]["access_key_id"],
        aws_secret_access_key=r.json()["video_token_v5"]["secret_acess_key"],
        aws_session_token=r.json()["video_token_v5"]["session_token"],
    )
    with open(video_file, "rb") as f:
        video_content = f.read()
    file_size = len(video_content)
    url = f"https://www.tiktok.com/top/v1?Action=ApplyUploadInner&Version=2020-11-19&SpaceName=tiktok&FileType=video&IsInner=1&FileSize={file_size}&s=g158iqx8434"

    r = session.get(url, auth=aws_auth)
    if not assert_success(url, r):
        return False

    # upload chunks
    upload_node = r.json()["Result"]["InnerUploadAddress"]["UploadNodes"][0]
    video_id = upload_node["Vid"]
    store_uri = upload_node["StoreInfos"][0]["StoreUri"]
    video_auth = upload_node["StoreInfos"][0]["Auth"]
    upload_host = upload_node["UploadHost"]
    session_key = upload_node["SessionKey"]
    chunk_size = 5242880
    chunks = []
    i = 0
    while i < file_size:
        chunks.append(video_content[i : i + chunk_size])
        i += chunk_size
    crcs = []
    upload_id = str(uuid.uuid4())
    for i in range(len(chunks)):
        chunk = chunks[i]
        crc = crc32(chunk)
        crcs.append(crc)
        url = f"https://{upload_host}/{store_uri}?partNumber={i+1}&uploadID={upload_id}&phase=transfer"
        headers = {
            "Authorization": video_auth,
            "Content-Type": "application/octet-stream",
            "Content-Disposition": 'attachment; filename="undefined"',
            "Content-Crc32": crc,
        }

        r = session.post(url, headers=headers, data=chunk)

    # finish upload
    url = f"https://{upload_host}/{store_uri}?uploadID={upload_id}&phase=finish&uploadmode=part"
    headers = {
        "Authorization": video_auth,
        "Content-Type": "text/plain;charset=UTF-8",
    }
    data = ",".join([f"{i+1}:{crcs[i]}" for i in range(len(crcs))])

    r = requests.post(url, headers=headers, data=data)
    if not assert_success(url, r):
        return False

    url = f"https://www.tiktok.com/top/v1?Action=CommitUploadInner&Version=2020-11-19&SpaceName=tiktok"
    data = '{"SessionKey":"' + session_key + '","Functions":[{"name":"GetMeta"}]}'

    r = session.post(url, auth=aws_auth, data=data)
    if not assert_success(url, r):
        return False

    # publish video
    url = "https://www.tiktok.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }

    r = session.head(url, headers=headers)
    if not assert_success(url, r):
        return False

    url = "https://www.tiktok.com/api/v1/web/project/post/?aid=1988"
    headers = {"content-type": "application/json"}
    brand = ""
    if brand_organic_type:
        brand += '"brand_organic_type":2001,'
    if branded_content_type:
        brand += '"brand_content_type":2001'
    if brand and brand[-1] == ",":
        brand = brand[:-1]
    markup_text, text_extra = convert_tags(title, session)
    data = json.dumps(
        {
            "upload_param": {
                "video_param": {
                    "text": title,
                    "text_extra": text_extra,
                    "markup_text": markup_text,
                    "poster_delay": 0,
                },
                "visibility_type": visibility_type,
                "allow_comment": allow_comment,
                "allow_duet": allow_duet,
                "allow_stitch": allow_stitch,
                "sound_exemption": 0,
                "geofencing_regions": [],
                "schedule_time": schedule_time,
                "creation_id": creation_id,
                "is_uploaded_in_batch": False,
                "is_enable_playlist": False,
                "is_added_to_playlist": False,
                "tcm_params": '{"commerce_toggle_info":' + brand + "}",
            },
            "project_id": project_id,
            "draft": "",
            "single_upload_param": [],
            "video_id": video_id,
            "creation_id": creation_id,
        }
    )

    r = session.request("POST", url, data=data, headers=headers)
    if r.json()["status_msg"] == "You are posting too fast. Take a rest.":
        print("[-] You are posting too fast, try later again")
        return False

    url = f"https://www.tiktok.com/api/v1/web/project/list/?aid=1988"

    r = session.get(url)
    if not assert_success(url, r):
        return False
    for j in r.json()["infos"]:
        if j["creationID"] == creation_id:
            if j["tasks"][0]["status_msg"] == "Y project task init":
                print("[+] Video got uploaded")
                return True
            print(f"[-] Video could not be uploaded: {j['tasks'][0]['status_msg']}")
            return False
        

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--sessionid", required=True)
    parser.add_argument("-v", "--video", required=True)
    parser.add_argument("-t", "--title", required=True)
    parser.add_argument("-sc", "--schedule", type=int, default=0)
    parser.add_argument("-c", "--comment", type=int, default=1)
    parser.add_argument("-d", "--duet", type=int, default=0)
    parser.add_argument("-st", "--stitch", type=int, default=0)
    parser.add_argument("-vi", "--visibility", type=int, default=0)
    parser.add_argument("-bo", "--brandorganic", type=int, default=0)
    parser.add_argument("-bc", "--brandcontent", type=int, default=0)
    args = parser.parse_args()
    upload_video(args.sessionid, args.video, args.title, args.schedule, args.comment, args.duet, args.stitch, args.visibility, args.brandorganic, args.brandcontent)