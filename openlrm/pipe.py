import argparse
import os
import time
import json
import re
import requests
import subprocess as sp
from datetime import timedelta
from requests_toolbelt.multipart.encoder import MultipartEncoder

MODEL_NAME = "openlrm"
PATH_SUFFIX_INPUT = "/input"
PATH_SUFFIX_OUTPUT = "/dumps"

def upload(name, file, id):
    url = "https://zzimkong.ggm.kr/inference/done"
    ply_file = MultipartEncoder(
        fields={
            'file': (f'{name}.ply', open(file, 'rb')),
            'id': str(id)
        }
    )
    headers = {'Content-Type' : ply_file.content_type} # multipart/form-data
    r = requests.post(url, headers=headers, data=ply_file, verify=False)
    return r.status_code

def status(status, message, id):
    url = "https://zzimkong.ggm.kr/inference/status"
    data = {"status": status, "statusMessage": message, "id": id}
    r = requests.post(url, data=data, verify=False)
    print(message) # 디버그 프린트용

def download_from_internet(url, file_name):
    with open(file_name, "wb") as file:
        response = requests.get(url)
        file.write(response.content)

def main(args):
    print(args)
    msg = '업로드 된 가구 이미지를 처리 중입니다.'    # user에게 보여줄 메시지
    status("progress", msg, args.id)

    base = os.getcwd() # 현재 디렉토리를 base로 사용
    print(f"{base}")
    input_dir=f"{base}{PATH_SUFFIX_INPUT}"
    output_dir=f"{base}{PATH_SUFFIX_OUTPUT}"

    #model = args.model
    # TODO: decision 필요
    #     1안) model 인자 사용하여 모델 별 분기해서 실행
    #     2안) model == MODEL_NAME 일 때에만 작동하고 나머지는 거름
    model = 'openlrm-base-obj-1.0' # 일단 hard coding

    print("xxx1xxx")
    print(args)
    print(re.search(r"^(http|https):", args.src))
    print("xxxaxxx")
    if re.search(r"^(http|https):", args.src):
        # 인터넷 데이터 (http 혹은 https)
        data_url = args.src                 # https://zzimkong.ggm.kr/room.png
        data = data_url.split('/')[-1]      # room.png
        name = data.split('.')[0]           # room
        img_path = f"{input_dir}/{data}"
        print("xxx2xxx")
        download_from_internet(data_url, img_path)
    else:
        # 파일 데이터
        data = args.src
        name = data.split('.')[0]
        img_path = f'{input_dir}/{data}'
        print("xxx3xxx")

    print("xxx4xxx")
    inference_start = time.time()
    command = f'python -m lrm.inferrer --model_name {model} --source_image "{img_path}" --export_mesh'
    print(f"{command}")
    s = sp.run(command, capture_output=False, text=True, shell=True)
    print(f"s result: {s.returncode}")
    if s.returncode != 0:
        status("error", "가구 이미지 처리 중 문제가 발생하였습니다.", args.id)
        os.abort()

    print(f"Elapsed time: {timedelta(seconds=time.time() - inference_start)}")

    msg = '가구 이미지가 완료되었습니다! 구성 결과를 서버에 업로드 중입니다.'
    status("progress", msg, args.id)

    print("web server로 전송 중")
    send_start = time.time()
    result = upload(name, f'{output_dir}/{name}.ply', args.id)
    if result == 201:
        print(f"전송 완료. Elapsed time: {timedelta(seconds=time.time() - send_start)}")
        status("progress", "업로드가 완료되었습니다.", args.id)
    else:
        status("error", "구성 결과 업로드 중 문제가 발생하였습니다.", args.id)
        os.abort()

if __name__ == "__main__":
    # ----- Parser -----
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-dc',
        '--config_file',
        dest='config_file',
        type=str,
        default='',
        help='config file',
    )
    parser.add_argument('--id',
                        type=int, 
                        help='(Required) id.')
    parser.add_argument('--src',
                        type=str, 
                        help='(Required) user data name.')
    parser.add_argument('--model',
                        type=str, 
                        help='(Required) model.',
                        default="nerfacto")

    # Parse arguments
    args = parser.parse_args()
    config = json.loads(args.config_file) # dict

    args.id = config["id"]
    args.src = config["src"]
    print(args)
    main(args)