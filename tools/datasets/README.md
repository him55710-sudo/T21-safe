# Dataset tools

이 디렉터리의 도구는 RUO 연구에서 **작은 공개 샘플과 메타데이터만** 다룬다. 전체 데이터셋 다운로드, credential 우회, 환자 원시 데이터의 Git 저장은 지원하지 않는다. 모든 명령은 사용자가 `--sample` 또는 `--limit`을 명시해야 실행된다.

## 예시

```bash
python tools/datasets/verify_dataset_registry.py --limit 20
python tools/datasets/inspect_vitaldb.py --limit 3
python tools/datasets/inspect_wfdb_record.py --sample /outside/repo/100.hea --limit 8
python tools/datasets/download_open_sample.py \
  --dataset-id bidmc-ppg-resp \
  --sample https://physionet.org/files/bidmc/1.0.0/bidmc01.hea \
  --limit 65536 \
  --output /outside/repo/t21-samples/bidmc01.hea
python tools/datasets/generate_data_manifest.py \
  --sample /outside/repo/t21-samples \
  --limit 10 \
  --source https://physionet.org/content/bidmc/1.0.0/ \
  --version 1.0.0 \
  --license "Open Data Commons Attribution License 1.0"
```

`download_open_sample.py`는 공식 PhysioNet/VitalDB HTTPS host와 레지스트리의 `OPEN` 자료만 허용하며, Git checkout 내부 대상은 거부한다. 제한 자료는 원 기관의 승인·교육·DUA 절차를 이용해야 한다.

## 테스트

```bash
python -m unittest discover -s tools/datasets/tests -v
```

fixture는 synthetic text/bytes만 사용하며 실제 환자 자료를 포함하지 않는다.

