import enum


@enum.unique
class Code(enum.IntEnum):
    SUCCESS = 1000  # 성공

    INTERNAL_SERVER_ERROR = -1000   # 서버 에러
    ACCESS_DENIED = -1001           # 접근 권한 없음
    CONNECTION_TIME_OUT = -1002     # 시간 제한
    ACCESS_IS_NOT_FOUND = -1003     # 해당 URL 없음
    SERVER_BAD_REQUEST = -1004
    NO_AUTHORITY = -1005            # 작업 권한 없음

    # USER, PASSWORD, LOGIN
    LOGIN_FAIL = -2000              # 로그인 실패
    WRONG_PASSWORD = -2001          # 비밀번호 틀림
    INACTIVE_USER = -2002           # 비활성인 사용자
    NO_EXIST_USER = -2003           # 사용자 없음
    WRONG_RE_PASSWORD = -2004       # 비밀번호 확인 틀림
    ALREADY_EXIST_USER = -2005      # 이미 존재하는 사용자

    # FILE
    FILE_NOT_EXIST = -5000          # 파일이 존재하지 않음
    EMPTY_FILE = -5001              # 빈 파일
    FAILED_TO_FILE_UPLOAD = -5002   # 파일 업로드 실패

    # IMPROPER
    IMPROPER_PARAMETERS = -7000     # 부적절한 파라미터
    IMPROPER_CODE = -7001           # 부적절한 코드
    IMPROPER_LICENSE_KEY = -7002    # 부적절한 라이선스 키
    IMPROPER_MAIL_LINK = -7003      # 부적절한 메일 링크
    IMPROPER_CSV = -7004            # 부적절한 CSV 파일 양식

    # 미사용 중
    INCOMPLETE_FILE_CONVERSION = -9051
    ALREADY_REMOVE_USER = -9052
    ALREADY_EXPIRED_DATE = -9053
    ALREADY_EXPIRED_FOLDER = -9054
