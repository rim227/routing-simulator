Network Routing Simulator

## 프로젝트 개요
Dijkstra 알고리즘 기반 네트워크 라우팅 시뮬레이터입니다.
링크 비용 변화에 따른 최단 경로 재탐색 과정을 시각화하고
결과를 자동으로 저장하는 시스템입니다.

## 주요 기능
- CSV 기반 네트워크 토폴로지 자동 생성 (노드 12개, 링크 30개)
- Dijkstra 알고리즘으로 최단 경로 계산
- 링크 비용 변화 시나리오 비교 분석
  - 시나리오1: 최단경로 A→B→G→J→L (비용 15.0)
  - 시나리오2: 비용 변경 후 우회경로 A→E→I→L (비용 16.0)
- 라우팅 테이블 CSV 자동 저장
- Matplotlib 기반 경로 시각화 및 PNG 저장

## 사용 기술
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![NetworkX](https://img.shields.io/badge/NetworkX-orange?style=flat)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat&logo=pandas&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-blue?style=flat)

## 실행 방법
```bash
pip install networkx pandas matplotlib
python main.py
```

## 프로젝트 구조
```
routing-simulator/
├── main.py
├── data.csv
└── README.md
```
