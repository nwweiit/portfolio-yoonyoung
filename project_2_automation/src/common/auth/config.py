import os
from dotenv import load_dotenv, find_dotenv


dotenv_path = find_dotenv(usecwd=True)

if dotenv_path:
    load_dotenv(dotenv_path=dotenv_path)
 


ZONE_ID = os.getenv("ZONE_ID")
BASE_URL = os.getenv("BASE_URL")
ECI_ACCESS_TOKEN = os.getenv("ECI_ACCESS_TOKEN")


if not ZONE_ID:
    raise EnvironmentError(
        "❌ ZONE_ID 환경변수가 설정되지 않았습니다!\n"
        f"발견된 .env 파일: {dotenv_path or '없음'}\n"
        "해결 방법:\n"
        "1. project_root/.env 파일이 존재하는지 확인\n"
        "2. ZONE_ID=your-value 형식으로 작성했는지 확인"
    )

if not ECI_ACCESS_TOKEN:
    raise EnvironmentError(
        "❌ ECI_ACCESS_TOKEN 환경변수가 설정되지 않았습니다!\n"
        ".env 파일을 확인하세요."
    )
