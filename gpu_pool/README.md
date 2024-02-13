# 공용 GPU Pool Server
GPU Utilization을 높이기 위한 공융 GPU Pool

# Introduction

다수의 GPU로 모델 학습을 돌리다보면 GPU를 100% 효율적으로 사용하기 어려울 수 있습니다. 따라서 개인의 GPU를 공용 GPU Pool에서 공유하여 GPU 사용성을 올립니다.

## Project Structure

```
gpu_pool
├── logger
├── support
├── utils
├── consumer.py
├── env.py
└── publisher.py
```

- logger : 로거 setup
- support : redis 커넥션 및 List 매커니즘 구현
- utils : 어플리케이션 setup 및 유틸리티 모듈 구현
- consumer.py : redis 메세지 큐로 부터 작업을 할당 받는 모듈
- publisher.py : redis 메세지 큐에 작업을 적재하는 모듈
- env.py : 환경변수 셋팅

## Getting started
- Download the code from GitHub:
```bash
https://github.com/boostcampaitech6/level2-objectdetection-cv-05.git
cd level2-objectdetection-cv-05
```

- Install the python libraries.
```bash
pip install -r requirements.txt
```

- Setup
```bash
cd gpu_pool
python utils/setup.py
```

- Run Consumer as daemon
```bash
nohup python consumer.py &
```

- Start Model Experiments
```bash
python publisehr.py
```

## Local
```
python==3.7.13
cuda 11.4
```

## Requirements
```
redis
torch==1.12.1+cu113
torchvision==0.13.1+cu113
```

# Citation
```
@misc{hee000_2024_code,
  author = {조창희},
  title = {Message-queue-based-learning-server},
  year = {2024},
  publisher = {GitHub},
  howpublished = {https://github.com/hee000/Message-queue-based-learning-server},
  accessed = {2024.01}
}
```
