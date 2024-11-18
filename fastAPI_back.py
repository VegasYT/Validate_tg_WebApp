
def validate_init_data(init_data: str, bot_token: str) -> bool:
    """
    Валидация init data на основе алгоритма Telegram Mini Apps.
    """
    # Разбираем init_data в словарь
    parsed_data = {k: v for k, v in (pair.split('=') for pair in init_data.split('&'))}

    # Извлекаем hash для сравнения
    init_hash = parsed_data.pop("hash", None)
    if not init_hash:
        raise HTTPException(status_code=400, detail="Missing 'hash' in init data")

    # Декодируем значения (URL-decoding)
    decoded_data = {k: urllib.parse.unquote_plus(v) for k, v in parsed_data.items()}

    # Проверяем срок действия auth_date
    auth_date = int(decoded_data.get("auth_date", 0))
    if time.time() - auth_date > 13600:  # Срок действия
        raise HTTPException(status_code=401, detail="Auth date is expired")

    # Создаем список "ключ=значение" пар, исключая hash
    data_check_string = "\n".join(f"{key}={decoded_data[key]}" for key in sorted(decoded_data))

    # Генерируем ключ HMAC-SHA256 с использованием строки "WebAppData" и токена
    secret_key = hmac.new(
        key="WebAppData".encode("utf-8"),
        msg=bot_token.encode("utf-8"),
        digestmod=sha256
    ).digest()

    # Вычисляем подпись
    computed_hash = hmac.new(
        key=secret_key,
        msg=data_check_string.encode("utf-8"),
        digestmod=sha256
    ).hexdigest()

    # Сравниваем вычисленный hash с переданным
    return computed_hash == init_hash

@app.post("/validate")
async def validate_init_data_endpoint(authorization: str = Header(...)):
    """
    Проверяет подпись init data, переданные в заголовке Authorization.
    """
    # Проверяем формат заголовка Authorization
    try:
        auth_type, auth_data = authorization.split(" ", 1)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid Authorization header format")

    if auth_type != "tma":
        raise HTTPException(status_code=400, detail="Unsupported authorization type")

    # Валидация init data
    if not validate_init_data(auth_data, API_TOKEN):
        raise HTTPException(status_code=401, detail="Invalid init data signature")

    # Разбираем строку user, которая должна быть в формате JSON
    try:
        parsed_data = {k: v for k, v in (pair.split('=') for pair in auth_data.split('&'))}
        user_data = parsed_data.get("user")
        if not user_data:
            raise HTTPException(status_code=400, detail="Missing user data in init data")

        # Декодируем и парсим данные пользователя
        user = json.loads(urllib.parse.unquote_plus(user_data))
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid user data format")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing user data: {str(e)}")

    # Возвращаем данные о пользователе
    return {"status": "success", "user": user}
