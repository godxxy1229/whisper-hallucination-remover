# HallucinationRemover

[![버전](https://img.shields.io/badge/version-0.0.1-blue.svg)](https://github.com/godxxy1229/whisper-hallucination-remover)

Whisper 계열 STT 결과에 섞여 들어오는 환각 텍스트를 정규식으로 걸러내는 후처리 모듈입니다.

## 주요 기능

Whisper가 무음 구간이나 배경 소리를 텍스트로 잘못 인식하는 경우가 있습니다. `はい`, `시청자 여러분`, `Thank you for watching.` 같은 것들이 대표적입니다.

이 모듈은 그런 환각 텍스트를 정규식 기반으로 정리합니다.

- `stopwords` 목록에 있는 문자열 제거
- 허용된 언어의 문자만 남기고 나머지 제거
- 반복 패턴, 엔딩 문구, URL, 감탄사 반복, 문장부호 정리

외부 패키지 없이 Python 표준 라이브러리(`re`)만 씁니다.

> 환각을 줄이는 더 근본적인 방법은 VAD, 무음 제거, 구간 분할 같은 **전처리**입니다. 이 모듈은 그런 처리가 어렵거나 부족할 때 마지막 단계에서 한 번 더 걸러주는 용도로 보시면 됩니다.

## 설치

파일 하나짜리입니다. 프로젝트 디렉터리에 넣으면 끝입니다.

```text
your_project/
├─ hallucination_remover.py
└─ main.py
```

## 빠른 시작

```python
from hallucination_remover import HallucinationRemover

remover = HallucinationRemover()
text = "안녕하세요 はい hello 시청자 여러분"

cleaned = remover.remove_hallucinations(text)
print(cleaned)  # 안녕하세요 hello
```

## API

### `HallucinationRemover(stopwords=None, allowed_languages=None)`

| 매개변수 | 타입 | 기본값 | 설명 |
| --- | --- | --- | --- |
| `stopwords` | `list[str] \| None` | `None` → 기본 STOPWORDS 사용 | 제거할 문자열 목록. 대소문자 구분 없이 부분 문자열로 제거합니다. |
| `allowed_languages` | `list[str] \| None` | `None` → `['korean', 'english']` | 남길 언어 목록. |

`None`과 빈 리스트 `[]` 모두 기본값으로 동작합니다. 즉 `allowed_languages=None`이든 `allowed_languages=[]`이든 결과는 같습니다.

### `remove_hallucinations(text)`

문자열 하나를 받아서 정리된 문자열을 돌려줍니다.

- `""`, `"   "` 같은 빈 문자열은 그대로 반환
- 정리 후 결과가 완전히 비어버리면, 원문에서 첫 단어 하나를 살려서 반환하는 보호 로직이 있음

### 언어 토큰

`allowed_languages`에 쓸 수 있는 토큰은 아래 네 가지입니다.

| 토큰 | 문자 범위 |
| --- | --- |
| `korean` | `가-힣`, `ㄱ-ㅎ`, `ㅏ-ㅣ` |
| `english` | `a-zA-Z` |
| `japanese` | 히라가나, 가타카나, CJK 일부 |
| `cyrillic` | `А-Яа-я` |

언어 감지기가 아니라 문자 범위 기반 필터입니다. 문장의 의미는 보지 않습니다.

### 기본 STOPWORDS

```python
STOPWORDS = [
    "はい",
    "ㅎ",
    "핳",
    "Oh,",
    "good.",
    "시청자 여러분",
]
```

`stopwords`에 직접 리스트를 넘기면 이 기본 목록은 **무시**됩니다. 합쳐지는 게 아니라 통째로 교체됩니다.

## 예제

### 기본 사용

```python
remover = HallucinationRemover()
print(remover.remove_hallucinations("안녕하세요 はい hello 시청자 여러분"))
# 안녕하세요 hello
```

### 한국어만 남기기

```python
remover = HallucinationRemover(allowed_languages=["korean"])
print(remover.remove_hallucinations("안녕하세요 hello はい 감사합니다"))
# 안녕하세요
```

### stopwords 직접 지정

```python
remover = HallucinationRemover(stopwords=["테스트"])
print(remover.remove_hallucinations("테스트 문장입니다 테스트 hello"))
# 문장입니다 hello
```

`stopwords=["테스트"]`를 넘기면 기본 STOPWORDS(`はい`, `시청자 여러분` 등)는 적용되지 않습니다.

### 엔딩 문구 제거

```python
remover = HallucinationRemover()
print(remover.remove_hallucinations("여기까지 시청해주셔서 감사합니다."))
# 여기까지
```

## 알아두어야 할 점

완벽한 정제기가 아닙니다. 아래 같은 경우가 생길 수 있습니다.

- **반복 제거가 안 되는 경우**: `안녕하세요 안녕하세요 안녕하세요`가 그대로 남을 수 있습니다.
- **공백이 사라지는 경우**: `고추장 고추장 고추장 넣어주세요` → `고추장넣어주세요`처럼 단어가 붙을 수 있습니다.
- **감탄사 처리에서 붙는 경우**: `아 아 아 오늘 시작합니다` → `아오늘 시작합니다`, `와 와 와 진짜네요` → `와진짜네요`
- **엔딩 문구가 일부 남는 경우**: `Thank you for watching.` → `for watching`이 남습니다.
- **보호 로직 부작용**: `allowed_languages=["korean"]`이어도 결과가 비면 영어 단어가 살아남을 수 있습니다. `hello`만 넣으면 결과가 `hello`가 됩니다.
- **URL 잔여물**: 한국어만 허용해도 `https://example.com`에서 `://` 같은 기호가 남을 수 있습니다.
- **부분 문자열 치환**: `stopwords` 제거가 단어 경계 기준이 아니라서, 의도하지 않은 부분이 함께 잘릴 수 있습니다.

샘플 결과를 직접 확인하면서 쓰는 게 안전합니다.

## 권장 사용법

- Whisper 출력을 바로 이 모듈에 넣지 말고, 먼저 샘플 몇 개로 결과를 확인하세요.
- 도메인(방송, 강의, 상담 등)에 맞게 `stopwords`를 조정하세요.
- VAD나 무음 제거가 가능하면 먼저 적용하고, 이 모듈은 마지막 단계에서만 쓰세요.
