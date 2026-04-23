
import requests
import pandas as pd

# Словник: ключ (як написано в CRM) -> значення (як в Meta API)
campaign_mapping = {
    'search - курс data analytics - eu': 'google',
    'search - курс data analytics - ua': 'google',
    'search - курсы python - eu (new)': 'google',
    'da_test': 'meta',
    'eu_v2': 'facebook'
}


def normalize_strings(series):
    return series.astype(str).str.strip().str.lower()


def advertising_comparison():
    sheet_id = '1kl2T5EdV7fjG9c6BjMJCRqhXuX1Igjigu3yvNOMLlSw'
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    table_sheet = pd.read_csv(url)

    # Вибираємо потрібні колонки
    df_crm = table_sheet[['ID', 'utm_campaign.1', 'utm_source.1']].dropna().copy()

    # Створюємо ключ з кампанії
    df_crm['key_raw'] = normalize_strings(df_crm['utm_campaign.1'])

    # Застосовуємо словник
    df_crm['mapped_name'] = df_crm['key_raw'].map(campaign_mapping)

    # Якщо назви немає в словнику, беремо значення з utm_source.1
    df_crm['mapped_name'] = df_crm['mapped_name'].fillna(normalize_strings(df_crm['utm_source.1']))

    return df_crm


def read_ads_api():
    account_id = '26308003548893972'
    access_token = 'EAFZCUaUv68bQBRNExWKGVlsAN90oDJWgmqcGpoTOhTvLqzW2GaRdTjtRDWkm4Lkw6dncwhNQfFJ81z13LHKy2UlenuBjKyueHkrKkqIoZBO0qd44IDyivTKZAWDCq96Tmcn8vf1Dzj6AhJcCLNVxziZAMvD7FoYesI9cc5LJwbZCrhkzCMfxbHBZCe6iH620gaOhZBcyd6ZC5YwWlYAL4ToAbEVvaqjt7xqFVAd5'
    url = f'https://graph.facebook.com/v19.0/act_{account_id}/campaigns'
    params = {'fields': 'name, daily_budget', 'access_token': access_token}

    response = requests.get(url, params=params)
    data = response.json()
    df_ads = pd.DataFrame(data['data'])

    # Перетворення бюджету
    df_ads['daily_budget'] = pd.to_numeric(df_ads['daily_budget'], errors='coerce')
    df_ads['name_norm'] = normalize_strings(df_ads['name'])
    return df_ads


# --- Виконання ---
df_crm = advertising_comparison()
df_ads = read_ads_api()

# Групуємо ліди
crm_grouped = df_crm.groupby('mapped_name').agg({'ID': 'count'}).reset_index()
crm_grouped.rename(columns={'ID': 'leads_count', 'mapped_name': 'name_norm'}, inplace=True)

# Об'єднуємо
result = crm_grouped.merge(df_ads, on='name_norm', how='left')

# Розрахунок CPL
result['cpl'] = result['daily_budget'] / result['leads_count']

# --- СОРТУВАННЯ ВІД БІЛЬШОГО ДО МЕНШОГО ---
result = result.sort_values(by='leads_count', ascending=False)

# Вивід результату
print(result[['name', 'leads_count', 'daily_budget', 'cpl']])

