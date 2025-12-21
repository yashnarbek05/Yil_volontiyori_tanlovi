from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import GOOGLE_SHEET_URL, KEYS_PATH, WINNERS_COUNT, OVOZ_BERUVCHI_SHEET_NAME

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

creds = Credentials.from_service_account_file(KEYS_PATH, scopes=SCOPES)

service = build("sheets", "v4", credentials=creds)
sheet = service.spreadsheets()


async def get_values_from_sheet(sheet_name):
    try:
        result = sheet.values().get(
            spreadsheetId=GOOGLE_SHEET_URL,
            range=f"{sheet_name}!A2:D"
        ).execute()

        values = result.get("values", [])

        return values

    except HttpError as err:
        print(f"HTTP Error: {err}")
        return []

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []


async def get_winnerss(sheet_name):

    from collections import Counter
    
    rows = await get_values_from_sheet(sheet_name)

    pairs = [
        (normalize(row[0]), normalize(row[1]))
        for row in rows
    ]

    counter = Counter(pairs)

    most_common = counter.most_common(WINNERS_COUNT)

    winners = []
    for (norm_surname, norm_name), count in most_common:
        for row in rows:
            if normalize(row[0]) == norm_surname and normalize(row[1]) == norm_name:
                winners.append((row[0], row[1], count))
                break  # faqat birinchi mos keladigan satrni olamiz
    return winners


async def is_registreted(user_id):
    
    users = await get_values_from_sheet(OVOZ_BERUVCHI_SHEET_NAME)

    for user in users:
        if str(user_id) == user[0]:
            return True
    
    return False

async def find_user(user_id, sheet_name):
    users = await get_values_from_sheet(sheet_name)

    for i in range (0, len(users)):
        if str(user_id) == users[i][0]:
            return i
    
    return -1



async def add_voter(user_id, contact, guruh, tavsiya):
    index = await find_user(user_id, OVOZ_BERUVCHI_SHEET_NAME)
    
    if index != -1:
        request = service.spreadsheets().values().update(spreadsheetId=GOOGLE_SHEET_URL, range=f'{OVOZ_BERUVCHI_SHEET_NAME}!C{index + 2}:D{index + 2}',
                                                     valueInputOption="RAW",
                                                     body={"values": [[guruh, tavsiya]]})
        response = request.execute()

        return response.get("updatedRows")

    users = await get_values_from_sheet(OVOZ_BERUVCHI_SHEET_NAME)



    request = service.spreadsheets().values().update(spreadsheetId=GOOGLE_SHEET_URL, range=f'{OVOZ_BERUVCHI_SHEET_NAME}!A{len(users) + 2}:D{len(users) + 2}',
                                                     valueInputOption="RAW",
                                                     body={"values": [[user_id, contact, guruh, tavsiya]]})
    response = request.execute()

    return response.get("updatedRows")


async def add_volontiyor_or_tashabbuskor(fullname, voter_id, comment, sheet_name):

    surname, name = fullname.split(" ")[:2]

    users = await get_values_from_sheet(sheet_name)

    request = service.spreadsheets().values().update(spreadsheetId=GOOGLE_SHEET_URL, range=f'{sheet_name}!A{len(users) + 2}:D{len(users) + 2}',
                                                     valueInputOption="RAW",
                                                     body={"values": [[surname, name, voter_id, comment]]})
    response = request.execute()

    return response.get("updatedRows")


def normalize(name: str) -> str:
    import re

    if not name:
        return ""

    # 1. lowercase
    name = name.lower()

    # 2. ' va boshqa belgilarni olib tashlash (faqat harf va bo'sh joy qolsin)
    name = re.sub(r"[^a-z\s]", "", name)

    # 3. ortiqcha bo'sh joylarni tozalash
    name = re.sub(r"\s+", " ", name).strip()

    return name
