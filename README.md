# HallucinationRemover

[![버전](https://img.shields.io/badge/version-0.0.1-blue.svg)](https://github.com/godxxy1229/HallucinationRemover)

STT(Speech-to-Text) 결과에서 발생하는 환각(hallucination) 현상을 제거하기 위한 텍스트 처리 도구입니다. Whisper 등의 STT 모델에서 발생하는 불필요한 텍스트, 반복 패턴, 비정상적인 언어 혼합을 제거합니다.

## 주요 기능

- 불필요한 단어/구문(stopwords) 제거
- 언어 기반 필터링 (한국어/영어 등 특정 언어만 유지)
- 반복되는 패턴 감지 및 제거
- 다국어 혼합 문장 정리
- 특수문자 및 문장 부호 정리

## 설치 방법

- hallucination_remover.py를 프로젝트에 복사하세요.

## 빠른 시작

```python
from hallucination_remover import HallucinationRemover

# 기본 설정으로 초기화 (한국어, 영어만 허용)
remover = HallucinationRemover()

# 텍스트에서 환각 제거
input_text = "안녕하세요 hello hello はい 안녕하세요 안녕하세요"
cleaned_text = remover.remove_hallucinations(input_text)
print(cleaned_text)  # "안녕하세요 hello"
```

## 상세 사용법

### 기본 사용법

```python
from hallucination_remover import HallucinationRemover

# 기본 설정으로 사용
remover = HallucinationRemover()
cleaned_text = remover.remove_hallucinations(input_text)
```

### 사용자 정의 stopwords 설정

```python
# 커스텀 stopwords 설정
custom_stopwords = ["안녕", "hello", "감사합니다"]
remover = HallucinationRemover(stopwords=custom_stopwords)
cleaned_text = remover.remove_hallucinations(input_text)
```

### 허용 언어 설정

```python
# 한국어만 허용
korean_only = HallucinationRemover(allowed_languages=['korean'])

# 한국어와 영어만 허용 (기본값)
kor_eng = HallucinationRemover(allowed_languages=['korean', 'english'])

# 모든 언어 허용
all_lang = HallucinationRemover(allowed_languages=None)
```

### 전체 예제

```python
from hallucination_remover import HallucinationRemover

# 한국어 전용 처리기 생성
remover = HallucinationRemover(
    stopwords=["아", "어", "음", "그", "저기", "시청자 여러분"], 
    allowed_languages=['korean']
)

# 원본 텍스트
original_text = """
안녕하세요 안녕하세요 안녕하세요. 오늘 오늘 오늘은 맛있는 음식을 만들어 볼게요.
はい はい はい. 시청자 여러분, 고추장 고추장 고추장 넣고 잘 섞어주세요.
Hello.. Hello.. ㅎㅎㅎ 맛있겠죠? 아.. 아.. 아..
"""

# 환각 제거
cleaned_text = remover.remove_hallucinations(original_text)
print(cleaned_text)
# 출력: "안녕하세요. 오늘은 맛있는 음식을 만들어 볼게요. 고추장 넣고 잘 섞어주세요. 맛있겠죠?"
```

## 설정 옵션

### HallucinationRemover 클래스 초기화 매개변수

| 매개변수 | 타입 | 기본값 | 설명 |
|---------|-----|-------|------|
| `stopwords` | list | 기본 STOPWORDS | 제거할 특정 단어/구문 목록 |
| `allowed_languages` | list | ['korean', 'english'] | 유지할 언어 목록. 설정된 언어만 결과에 포함 |

### 기본 STOPWORDS

```python
STOPWORDS = [
    "はい", "ㅎ", "핳", "Oh,", "good.", "시청자 여러분"
]
```

## 처리되는 환각 유형

HallucinationRemover는 다음과 같은 유형의 텍스트 환각을 처리합니다:

1. **불필요한 단어/구문**: stopwords 목록에 정의된 단어/구문
2. **연속 반복 패턴**: "안녕하세요 안녕하세요 안녕하세요" → "안녕하세요"
3. **단일 문자/기호 반복**: "Q. Q. Q." → "Q."
4. **다국어 끝맺음 구문**: "Thank you for watching", "시청해주셔서 감사합니다" 등
5. **연속적인 감탄/반응**: "아.. 아.. 아.." → "아.."
6. **의성어/의태어 반복**: 중복된 의성어/의태어 정리
7. **한글 비정상적 패턴**: 자음 또는 모음이 비정상적으로 연속 배치된 경우
8. **다국어 혼합 문장**: 허용된 언어가 아닌 짧은 구문 제거
9. **특수문자 정리**: 중복된 문장 부호나 비정상적으로 배치된 특수문자 정리

## 주의사항

- 기본적으로 한국어와 영어만 허용되며, 다른 언어는 제거됩니다. (변경가능)
- 원본 텍스트의 특성에 따라 결과가 달라질 수 있습니다.
