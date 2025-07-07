import arrow
import re
from holidays import Korea

# 공휴일 입력
holidays = Korea(years=[2025])

# 마감 키워드가 포함된 문장에서만 마감일을 추가
DEADLINE_KEYWORDS = ["신청", "접수", "지원", "마감", "등록"]

def contains_deadline_keyword(text: str) -> bool:
    return any(kw in text for kw in DEADLINE_KEYWORDS)

# 평일 기준 N일 전 날짜 계산 함수
def subtract_business_days(date: arrow.Arrow, days: int, holidays: set = set()) -> arrow.Arrow:
    count = 0
    while count < days:
        date = date.shift(days=-1)
        date_str = date.format('YYYY-MM-DD')
        if date.weekday() < 5 and date_str not in holidays:
            count += 1
    return date

# 상대 날짜 문자열 → 절대 날짜로 변환 (그리고 마감일 계산)
def parse_relative_dates(text: str, tz: str = 'Asia/Seoul') -> str:
    now = arrow.now(tz)
    weekday_kr = ["월", "화", "수", "목", "금", "토", "일"]
    add_deadline = contains_deadline_keyword(text)  

    patterns = {
        r"오늘": now,
        r"어제": now.shift(days=-1),
        r"그제": now.shift(days=-2),
        r"내일": now.shift(days=+1),
        r"모레": now.shift(days=+2),
        r"이번\s*주\s*월요일": now.floor('week').shift(days=0),
        r"이번\s*주\s*화요일": now.floor('week').shift(days=1),
        r"이번\s*주\s*수요일": now.floor('week').shift(days=2),
        r"이번\s*주\s*목요일": now.floor('week').shift(days=3),
        r"이번\s*주\s*금요일": now.floor('week').shift(days=4),
        r"이번\s*주\s*토요일": now.floor('week').shift(days=5),
        r"이번\s*주\s*일요일": now.floor('week').shift(days=6),
        r"다음\s*주\s*월요일": now.floor('week').shift(weeks=+1, days=0),
        r"다음\s*주\s*화요일": now.floor('week').shift(weeks=+1, days=1),
        r"다음\s*주\s*수요일": now.floor('week').shift(weeks=+1, days=2),
        r"다음\s*주\s*목요일": now.floor('week').shift(weeks=+1, days=3),
        r"다음\s*주\s*금요일": now.floor('week').shift(weeks=+1, days=4),
        r"다음\s*주\s*토요일": now.floor('week').shift(weeks=+1, days=5),
        r"다음\s*주\s*일요일": now.floor('week').shift(weeks=+1, days=6),
    }

    for pattern, date in patterns.items():
        target_date = date.format('YYYY-MM-DD')
        target_weekday = weekday_kr[date.weekday()]
        replacement = f"{target_date} ({target_weekday})"

        if add_deadline:
            deadline_date = subtract_business_days(date, 3, holidays)
            deadline_fmt = deadline_date.format('YYYY-MM-DD')
            deadline_weekday = weekday_kr[deadline_date.weekday()]
            replacement += f" (신청 마감: {deadline_fmt} ({deadline_weekday}))"

        text = re.sub(pattern, replacement, text)

    # 특정 날짜 인식 (예 : 6월 5일)
    date_patterns = re.findall(r"(?:(\d{4})년\s*)?(\d{1,2})월\s*(\d{1,2})일", text)

    for match in date_patterns:
        year = int(match[0]) if match[0] else now.year
        month = int(match[1])
        day = int(match[2])
        try:
            date = arrow.get(f"{year}-{month:02d}-{day:02d}")
            target = date.format('YYYY-MM-DD')
            weekday = weekday_kr[date.weekday()]
            replacement = f"{target} ({weekday})"

            if add_deadline:
                deadline = subtract_business_days(date, 3, holidays)
                deadline_fmt = deadline.format('YYYY-MM-DD')
                deadline_weekday = weekday_kr[deadline.weekday()]
                replacement += f" (신청 마감: {deadline_fmt} ({deadline_weekday}))"

            original = f"{match[0]+'년 ' if match[0] else ''}{month}월 {day}일"
            text = text.replace(original, replacement)
        except Exception:
            continue

    return text