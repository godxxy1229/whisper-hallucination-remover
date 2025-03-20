# ver 0.0.1

import re

# 제거할 특정 단어/구문 리스트
STOPWORDS = [
    "はい", "ㅎ", "핳", "Oh,", "good.", "시청자 여러분"
]

class HallucinationRemover:
    def __init__(self, stopwords=None, allowed_languages=None):
        """
        환각 제거 처리기 초기화
        
        Args:
            stopwords (list, optional): 제거할 특정 단어/구문 목록
            allowed_languages (list, optional): 유지할 언어 목록
                                                ['korean']: 한국어만 허용
                                                ['korean', 'english']: 한국어와 영어 허용
                                                None: 모든 언어 허용
        """
        self.stopwords = stopwords or STOPWORDS
        # 기본값은 한국어와 영어만 허용
        self.allowed_languages = allowed_languages or ['korean', 'english']
        # 내부 처리용 플래그
        # self.keep_only_korean = 'korean' in self.allowed_languages and len(self.allowed_languages) == 1
        
    def remove_hallucinations(self, text):
        """
        Whisper STT 모델에서 발생하는 환각(hallucinations)을 제거하는 함수
        
        Args:
            text (str): 원본 텍스트
            
        Returns:
            str: 환각이 제거된 텍스트
        """
        if not text or len(text.strip()) == 0:
            return text
        
        # 원본 텍스트 저장
        original_text = text
        
        # 1. 언어 필터링 (허용된 언어들만 유지)
        if self.allowed_languages:
            text = self._filter_languages(text, self.allowed_languages)
        
        # 2. STOPWORDS 처리 (사용자가 제공한 특정 단어/구문 제거)
        for word in self.stopwords:
            # 대소문자 구분 없이, 단어 경계에 관계없이 제거
            pattern = re.compile(re.escape(word), re.IGNORECASE)
            text = pattern.sub('', text)
        
        # 3. 연속 반복 패턴 감지 및 제거
        text = self._remove_repeating_patterns(text)
        
        # 4. 단일 문자/기호 반복 제거
        text = self._remove_repeating_single_chars(text)
        
        # 5. 다국어 끝맺음 구문 및 자막 관련 문구 제거
        text = self._remove_ending_phrases(text)
        
        # 6. 연속적인 감탄/반응 제거 (3회 이상)
        text = self._remove_repeating_reactions(text)
        
        # 7. 의성어/의태어 반복 제거
        text = self._remove_repeating_onomatopoeia(text)
        
        # 8. 자음 또는 모음이 비정상적으로 연속 배치된 경우 (한글 관련)
        text = self._remove_nonsense_korean(text)
        
        # 9. 다국어 혼합 문장에서 매우 짧은 구문들 제거
        text = self._clean_mixed_language_phrases(text)
        
        # 10. 특정 음식 이름 반복 패턴 제거
        text = self._remove_food_repetitions(text)
        
        # 11. 환각 제거 후 남은 특수문자 정리
        text = self._clean_remaining_punctuation(text)
        
        # 12. 최종 정리 (여러 공백 제거, 문장 정리)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # 13. 환각 제거로 텍스트가 크게 줄어들었다면 검증
        if len(text) < len(original_text) * 0.1 and len(text.strip()) == 0:
            # 완전히 빈 결과가 되는 것 방지, 최소한의 내용 보존
            words = original_text.split()
            if words:
                # 우선 순위에 따라 단어 선택
                for lang in self.allowed_languages:
                    word = self._get_first_word_by_language(words, lang)
                    if word:
                        return word
                # 아무 언어도 찾지 못했다면 첫 번째 단어 반환
                return words[0]
        
        return text
    
    def _filter_languages(self, text, allowed_languages):
        """
        허용된 언어만 유지하고 나머지는 제거
        
        Args:
            text (str): 원본 텍스트
            allowed_languages (list): 허용할 언어 리스트 ['korean', 'english']
            
        Returns:
            str: 필터링된 텍스트
        """
        # 언어별 문자 패턴
        language_patterns = {
            'korean': r'[가-힣ㄱ-ㅎㅏ-ㅣ]',  # 한국어
            'english': r'[a-zA-Z]',          # 영어
            'japanese': r'[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff]',  # 일본어
            'cyrillic': r'[А-Яа-я]'          # 키릴 문자
        }
        
        # 허용되지 않은 언어에 대한 패턴 생성
        disallowed_patterns = []
        for lang, pattern in language_patterns.items():
            if lang not in allowed_languages:
                disallowed_patterns.append(pattern)
        
        if not disallowed_patterns:
            return text  # 모든 언어가 허용되거나 설정 없는 경우
        
        # 허용되지 않은 문자들을 공백으로 대체
        combined_pattern = '|'.join(f'({p})' for p in disallowed_patterns)
        return re.sub(combined_pattern, '', text)
    
    def _get_first_word_by_language(self, words, language):
        """
        특정 언어에 해당하는 첫 번째 단어 반환
        """
        language_patterns = {
            'korean': r'[가-힣ㄱ-ㅎㅏ-ㅣ]',  # 한국어
            'english': r'[a-zA-Z]',          # 영어
            'japanese': r'[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff]',  # 일본어
            'cyrillic': r'[А-Яа-я]'          # 키릴 문자
        }
        
        pattern = language_patterns.get(language)
        if not pattern:
            return None
            
        for word in words:
            if re.search(pattern, word):
                return word
        return None
    
    def _filter_non_korean(self, text):
        """한국어만 유지하고 다른 언어는 제거 - 이전 버전과의 호환성"""
        return self._filter_languages(text, ['korean'])
    
    def _clean_mixed_language_phrases(self, text):
        """다국어 혼합 문장에서 매우 짧은 구문들 제거"""
        # 허용된 언어만 유지하는 경우 간소화된 처리
        if len(self.allowed_languages) == 1:
            return text
            
        # 언어 그룹화를 위한 패턴들
        patterns = {
            'english': r'[a-zA-Z\'".!?,:;()]+(?:\s+[a-zA-Z\'".!?,:;()]+)*',  # 영어
            'korean': r'[가-힣ㄱ-ㅎㅏ-ㅣ\'".!?,:;()]+(?:\s+[가-힣ㄱ-ㅎㅏ-ㅣ\'".!?,:;()]+)*',  # 한국어
            'japanese': r'[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\'".!?,:;()]+(?:\s+[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\'".!?,:;()]+)*',  # 일본어
            'cyrillic': r'[А-Яа-я\'".!?,:;()]+(?:\s+[А-Яа-я\'".!?,:;()]+)*'  # 키릴 문자
        }

        # 원본 텍스트를 단어 그룹으로 분할
        chunks = []
        remaining = text
        
        while remaining:
            match_found = False
            for lang, pattern in patterns.items():
                match = re.match(pattern, remaining.lstrip())
                if match:
                    matched_text = match.group(0)
                    start_pos = remaining.find(matched_text)
                    # 선행 공백이 있으면 포함
                    prefix = remaining[:start_pos]
                    if prefix:
                        chunks.append((None, prefix))
                    
                    # 단어 수 계산 (간단히 공백으로 분리)
                    word_count = len(matched_text.split())
                    
                    # 허용된 언어인 경우 무조건 유지
                    if lang in self.allowed_languages:
                        chunks.append((lang, matched_text, False))  # 유지
                    # 허용되지 않은 언어는 필터링 후보
                    else:
                        # 매우 짧은 구문(1-2단어)이면서 총 길이가 짧은 경우 필터링
                        if word_count <= 2 and len(matched_text) < 10:
                            chunks.append((lang, matched_text, True))  # 필터링 후보
                        else:
                            chunks.append((lang, matched_text, False))  # 유지
                        
                    remaining = remaining[start_pos + len(matched_text):]
                    match_found = True
                    break
            
            # 어떤 패턴에도 매치되지 않으면 한 글자씩 처리
            if not match_found and remaining:
                chunks.append((None, remaining[0]))
                remaining = remaining[1:]
        
        # 언어 변화가 많은 짧은 구문들 필터링
        filtered_chunks = []
        prev_lang = None
        
        for i, chunk_info in enumerate(chunks):
            if len(chunk_info) == 2:  # (None, text) 형식의 경우
                lang, chunk_text = chunk_info
                filtered_chunks.append(chunk_text)
                prev_lang = lang
            else:  # (lang, text, filter_candidate) 형식
                lang, chunk_text, filter_candidate = chunk_info
                
                # 허용된 언어면 무조건 유지
                if lang in self.allowed_languages:
                    filtered_chunks.append(chunk_text)
                    prev_lang = lang
                    continue
                
                # 필터링 후보이면서 언어 전환점에 있는 경우
                if filter_candidate and lang != prev_lang:
                    # 앞뒤 언어도 확인해 전환점인지 확인
                    next_lang = None
                    for j in range(i+1, len(chunks)):
                        if len(chunks[j]) > 2 and chunks[j][0]:
                            next_lang = chunks[j][0]
                            break
                    
                    # 언어 전환점에 있는 짧은 구문은 제거
                    if prev_lang and next_lang and lang != next_lang and prev_lang != lang:
                        continue
                
                filtered_chunks.append(chunk_text)
                prev_lang = lang
        
        return ''.join(filtered_chunks)
        
    def _remove_repeating_patterns(self, text):
        """연속 반복 패턴 감지 및 제거"""
        def replace_repeating_patterns(match):
            pattern = match.group(1)
            return pattern.strip()
        
        # 1. 공백으로 구분된 패턴 반복 처리
        for word_count in range(1, 7):
            # 유니코드 호환성 개선
            pattern = r'((?:[^\s]+(?:\s+[^\s]+){0,' + str(word_count-1) + r'}\s*)\s*)\1{2,}'
            text = re.sub(pattern, replace_repeating_patterns, text, flags=re.UNICODE)
        
        # 2. 공백 없이 붙어있는 단어 반복 패턴 처리 (한글 특화)
        # 2-1. 한글 단어(2-6글자) 반복
        for char_count in range(2, 7):
            pattern = fr'([\uAC00-\uD7A3]{{{char_count}}})(\1){2,}'
            text = re.sub(pattern, r'\1', text, flags=re.UNICODE)
        
        # 3. 부분 반복 패턴 (예: "연합당연합당연합")
        # 2글자 이상의 연속된 텍스트가 반복되는 경우 탐지
        repetitive_patterns = re.findall(r'([\uAC00-\uD7A3]{2,})(\1)+', text, flags=re.UNICODE)
        for pattern_tuple in repetitive_patterns:
            if pattern_tuple and len(pattern_tuple) > 0:
                pattern = pattern_tuple[0]
                if len(pattern) >= 2:  # 2글자 이상인 경우만
                    # 해당 패턴의 반복을 제거
                    repeat_pattern = fr'({re.escape(pattern)})\1+'
                    text = re.sub(repeat_pattern, r'\1', text)
        
        return text
    
    def _remove_repeating_single_chars(self, text):
        """단일 문자/기호 반복 제거"""
        # 예: "Q. Q. Q. Q." 또는 "아.. 아.. 아.."
        single_char_pattern = r'(\b\w\b\W*)\s*(\1\s*){2,}'
        return re.sub(single_char_pattern, r'\1 ', text)
    
    def _remove_ending_phrases(self, text):
        """다국어 끝맺음 구문 및 자막 관련 문구 제거"""
        ending_phrases = [
            r'시청해주셔서 감사합니다\.?',
            r'Thank you\.?',
            r'Gracias\.?',
            r'ご視聴ありがとうございました\.?',
            r'お疲れ様でした\.?',
            r'おやすみなさい\.?',
            r'お待ちしております\.?',
            r'Vielen Dank\.?',
            r'Abertura\.?',
            r'Продолжение следует\.?',
            r'Dzień dobry\.?',
            r'다음 주에 만나요\.?',
            r'다음주에 만나요\.?',
            r'이 시각 세계였습니다\.?',
            r'자막 제공 .{1,15}',
            r'字幕提供\.?',
            r'한글자막 by .{1,15}',
            r'감사합니다\.?',
            r'광고를 포함하고 있습니다\.?',
            r'Субтитры сделал .{1,15}',
            r'Thank you for watching\.?',
            r'Thanks for watching\.?',
            r'The end\.?',
            r'sub by .{1,15}',
            r'visit .{1,15}',
            r'中文字幕志愿者 .{1,15}',
            r'社群提供的字幕 .{1,15}',
            r'中文字幕 .{1,15}',
            r'Like and subscribe\.?',
            r'\b(?:https?:\/\/)?(?:www\.)?[a-zA-Z0-9.-]+\.(com|net|org|gov|edu|mil|co|io|tv|biz|info|onion|onion\.sh)\b'
        ]
        
        ending_pattern = '|'.join(ending_phrases)
        return re.sub(ending_pattern, '', text)
    
    def _remove_repeating_reactions(self, text):
        """연속적인 감탄/반응 제거"""
        reaction_pattern = r'(\b(?:Oh|Ah|아|어|오|음|에|예|네)\b[\s,.?!]*)(?:\s*\1){2,}'
        return re.sub(reaction_pattern, r'\1', text)
    
    def _remove_repeating_onomatopoeia(self, text):
        """의성어/의태어 반복 제거"""
        onomatopoeia_pattern = r'([ㄱ-ㅎㅏ-ㅣ가-힣a-zA-Z]{1,2}[!,.?]*)(?:\s*\1){2,}'
        return re.sub(onomatopoeia_pattern, r'\1', text)
    
    def _remove_nonsense_korean(self, text):
        """자음 또는 모음이 비정상적으로 연속 배치된 경우"""
        nonsense_korean = r'([ㄱ-ㅎㅏ-ㅣ]{2,})'
        return re.sub(nonsense_korean, '', text)
    
    def _remove_food_repetitions(self, text):
        """특정 음식 이름 반복 패턴 제거"""
        food_pattern = r'(고추장|고춧가루|청양고추|한\s*병)(?:\s*\1){2,}'
        return re.sub(food_pattern, r'\1', text)
        
    def _clean_remaining_punctuation(self, text):
        """
        환각 제거 후 남은 특수문자들 정리
        
        1. 공백으로 구분된 마침표나 쉼표 제거 (예: ". . . .")
        2. 중복된 문장 부호 정리 (예: ",," -> ",")
        3. 줄임표 표준화 (예: "...." -> "...")
        """
        # 1. 공백으로 분리된 마침표, 쉼표 처리
        # 예: ". . . ." 또는 ", , ,"와 같은 패턴 제거
        text = re.sub(r'(?:\s*[.,]\s*){2,}', '...', text)
        
        # 2. 문장 시작이나 끝에 있는 불필요한 특수문자 제거
        text = re.sub(r'^[.,\s]+', '', text)
        text = re.sub(r'[.,\s]+$', '', text)
        
        # 3. 중복된 문장 부호 정리 (연속 2개까지는 허용, 3개 이상은 표준화)
        # 단, 줄임표(...)는 보존
        text = re.sub(r'\.{4,}', '...', text)  # 4개 이상 마침표는 줄임표(...)로 표준화
        text = re.sub(r'[,]{2,}', ',', text)   # 연속된 쉼표는 1개로
        text = re.sub(r'[!]{3,}', '!!', text)  # 3개 이상 느낌표는 2개로
        text = re.sub(r'[?]{3,}', '??', text)  # 3개 이상 물음표는 2개로
        
        # 4. 공백 앞뒤로 특수문자가 있는 경우 공백 제거
        # 예: "단어 , 다른 단어" -> "단어, 다른 단어"
        text = re.sub(r'\s+([.,!?])', r'\1', text)
        
        # 5. 문장 부호 뒤에 공백이 없는 경우 공백 추가
        # 예: "안녕하세요.다음" -> "안녕하세요. 다음"
        text = re.sub(r'([.,!?])([가-힣a-zA-Z0-9])', r'\1 \2', text)
        
        return text