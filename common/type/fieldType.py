from django_enumfield import enum


class Status(enum.Enum):
    ACTIVE = 1      # 활성
    PAUSE = 2       # 일시정지
    WITHDRAW = 3    # 탈퇴

    # INACTIVE = 1  # 비활성
    # INVITATION = 2  # 초대
    # APV_STANDBY = 3  # 인증 대기

    PUBLIC = 10
    PRIVATE = 11

    DELETE_READY = 99  # 삭제예정 상태 (임시처리용 플래그값)

    @classmethod
    def get_value(cls, value):
        for item in cls:
            if item.name == value:
                val = item.value
                break
        return val


class Language(enum.EnumField):
    KR = 'kr'
    JP = 'jp'
    EN = 'en'

    @classmethod
    def get_value(cls, value):
        for item in cls:
            if item.name == value:
                val = item.value
                break
        return val


class WaterMarkType(enum.EnumField):
    NONE = 'none'  # 미사용
    IMG = 'img'  # 이미지
    TXT = 'txt'  # 텍스트


class UserType(enum.Enum):
    ADMIN = 0
    USER = 1


class GroupAuth(enum.Enum):
    ADMIN = 0
    BASIC = 1
    SHARE = 2
    CUSTOM = 3


class NoticeType(enum.Enum):
    SITE = 0
    ENV = 1

    @classmethod
    def get_value(cls, value):
        for item in cls:
            if item.name == value:
                val = item.value
                break
        return val


class AdminType(enum.Enum):
    SITE = 0
    ENV = 1
    ROOM = 2
    ENV_ROOM = 3
    RESALE = 4
    ROOT = 9

    @classmethod
    def get_value(cls, value):
        for item in cls:
            if item.name == value:
                val = item.value
                break
        return val


class FactorType(enum.Enum):
    NONE = 0
    LOGIN = 1
    NEWIP = 2

    @classmethod
    def get_value(cls, value):
        for item in cls:
            if item.name == value:
                val = item.value
                break
        return val


class SendType(enum.Enum):
    IMMEDIATELY = 0
    DAILY = 1
    WEEK = 2


class AdminLinkType(enum.Enum):
    SITE = 0
    ENV = 1
    ENV_ROOM = 2
    ROOM = 3
    PW_RESET = 4

    @classmethod
    def get_value(cls, value):
        for item in cls:
            if item.name == value:
                val = item.value
                break
        return val


class LinkType(enum.Enum):
    RESET_PWD = 0
    SHARE = 1
    INVITE_ROOM = 2
    MOVE = 3


class SystemLogStatus(enum.Enum):
    COMPLETE = 0
    FAIL = 99


class SystemLogProcessType(enum.Enum):
    DOWNLOAD = 0
    UPLOAD = 1
    OCR = 2
