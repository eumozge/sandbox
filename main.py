import asyncio
import httpx
import pytest
from fastapi import FastAPI, HTTPException, Request
from fastapi.testclient import TestClient
from http import HTTPStatus
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from contextlib import asynccontextmanager
import logging
from typing import AsyncGenerator

#TODO(config): logging.basicConfig на уровне импорта модуля — побочный эффект при import,
#TODO(config): мешает переиспользованию и тестам. Настраивайте логгер явно в точке входа.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#TODO(arch): приложение создаётся на уровне модуля и переиспользуется и в рантайме, и в тестах (TestClient ниже).
#TODO(arch): нет lifespan для старта/останова пулов БД и httpx-клиента.
app = FastAPI()

#TODO(security): креды БД и токен захардкожены в исходниках. Вынести в pydantic-settings/.env, не коммитить секреты.
DATABASE_URL = "postgresql+asyncpg://user:password@localhost/db"
EXTERNAL_API_URL = "https://external-api.local/process"
EXTERNAL_API_TOKEN = "supersecrettoken"

#TODO(config): echo=True в проде засоряет логи SQL; должно зависеть от окружения.
#TODO(arch): engine/SessionLocal создаются при импорте — требуют доступный PostgreSQL, ломая юнит-тесты без БД.
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()


#TODO(models): аннотации класса (id: int = Column(...)) вводят в заблуждение — значение это Column, не int.
#TODO(models): в SQLAlchemy 2.0 используйте Mapped[int] = mapped_column(...).
#TODO(models): нет unique-индекса на email, нет created_at/table_args.
class User(Base):
    """
    Модель пользователя.
    """

    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String)
    email: str = Column(String)


#TODO(models): Order.user_id объявлен, но нет ForeignKey('users.id') и relationship('User') — связь не работает.
#TODO(models): data = Column(JSON) без аннотации типа, неконсистентно с остальными полями.
class Order(Base):
    """
    Модель заказа.
    """

    __tablename__ = "orders"

    id: int = Column(Integer, primary_key=True)
    external_id: int = Column(Integer)
    user_id: int = Column(Integer)
    description: str = Column(String)
    data = Column(JSON)


#TODO(arch): клиент внешнего API в одном файле/слое с роутами. Вынести в clients/ с интерфейсом (Protocol/ABC) для моков.
class ExternalServiceClient:
    """
    Клиент для вызова внешнего API.
    """

#TODO(clients): нет таймаутов/retry/обработки сетевых ошибок (httpx.Timeout, transport retries).
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.token = token

#TODO(clients): get_order поднимает HTTPException — web-слой внутри клиента (нарушение слоёв).
#TODO(clients): поднимайте доменный Exception (ExternalAPIError), HTTPException маппьте в роуте.
#TODO(clients): новый httpx.AsyncClient на каждый запрос — нет переиспользования пула. Передавайте один клиент через DI/lifespan.
    async def get_order(self, order_id: int) -> dict:
        """
        Получает заказ из внешнего API.
        Возвращает ответ в виде JSON или поднимает исключение HTTPException.
        """
        headers = {"Authorization": f"Bearer {self.token}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/{order_id}", headers=headers)
#TODO(clients): проверка только 200; 201/202 трактуются как ошибка. Используйте raise_for_status() или диапазон 2xx.
            if response.status_code == HTTPStatus.OK:
                return response.json()
            else:
                raise HTTPException(status_code=response.status_code, detail=response.text)

#TODO(clients): ответ process_order не проверяется (нет await/статуса) — ошибки внешнего API молча игнорируются.
#TODO(clients): опять новый AsyncClient без таймаута на запрос.
    async def process_order(self, order_id: int) -> None:
        """
        Вызывает обработку заказа во внешнем API.
        """
        headers = {"Authorization": f"Bearer {self.token}"}
        async with httpx.AsyncClient() as client:
            await client.post(f"{self.base_url}/{order_id}", headers=headers)


#TODO(arch): синглтон-клиент на уровне модуля никогда не закрывается (утечка ресурса). Создавать в lifespan и инджектить в Depends.
external_client = ExternalServiceClient(EXTERNAL_API_URL, EXTERNAL_API_TOKEN)


#TODO(arch): get_session — по сути зависимость БД, но не оформлена как FastAPI Depends и не используется в сигнатуре роута.
@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Контекстный менеджер для асинхронной сессии БД.
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        await session.close()


#TODO(decorator): log_execution — синхронный wrapper вокруг async-функции. Возвращает корутину, но FastAPI
#TODO(decorator): через iscoroutinefunction видит wrapper как обычную функцию -> либо threadpool, либо не awaited корутина -> эндпоинт сломан.
#TODO(decorator): нужен async def wrapper + await, либо поддерживающий декоратор; добавьте functools.wraps (теряются __name__/__doc__/сигнатура).
def log_execution(func):
    """
    Логирует вызов функции.
    """

    def wrapper(*args, **kwargs):
        logger.info(f"Calling {func.__name__}")
        return func(*args, **kwargs)

    return wrapper


#TODO(bug): порядок декораторов — @log_execution выше @app.post, в FastAPI регистрируется обёртка (см. выше).
#TODO(arch): логирование должно быть в сервисном слое, а не декорировать роут.
@log_execution
@app.post("/submit")
#TODO(api): вместо Pydantic-схемы эндпоинт берёт сырой Request + await request.json() — нет валидации/типизации/OpenAPI.
#TODO(api): эндпоинт ничего не возвращает (None -> 200 пустое тело), нет 201 и тела ответа с id.
async def submit_data(request: Request):
    """
    Приём данных заказа и пользователя.
    """
#TODO(bug): нет обработки ошибок парсинга JSON и отсутствия ключей 'user'/'order' -> KeyError/500.
    data = await request.json()
    user_data = data["user"]
    order_data = data["order"]

#TODO(bug): сессия никогда не коммитится (нет await session.commit()) — user/order не сохраняются.
#TODO(bug): нет flush, поэтому user.id не сгенерирован к моменту линковки заказа.
    async with get_session() as session:
        user = User(name=user_data["name"], email=user_data["email"])
        session.add(user)

#TODO(bug): if get_order(...) проверяет истинность dict — при пустом JSON {} заказ не создастся. Проверяйте успешность вызова, а не payload.
#TODO(bug): при сбое внешнего API get_order поднимет HTTPException внутри транзакции без rollback.
        if await external_client.get_order(order_data["exteranal_id"]):
#TODO(bug): Order(exteranal_id=..., user=user) — нет поля exteranal_id (опечатка, должно быть external_id) и нет параметра user (связь не определена) -> TypeError.
#TODO(typo): exteranal_id — опечатка по всему коду (роут + тесты), должно быть external_id.
            order = Order(
                exteranal_id=order_data["exteranal_id"],
                description=order_data["description"],
                data=order_data["data"],
                user=user,
            )
            session.add(order)

#TODO(bug): order.external_id после создания без flush/commit == None; плюс имя поля external_id, не exteranal_id -> внешний вызов получит None.
#TODO(arch): вызов внешней обработки внутри HTTP-запроса после коммита — нет идемпотентности/повтора при сбое.
            await external_client.process_order(order.external_id)


#TODO(tests): TestClient на уровне модуля использует РЕАЛЬНУЮ БД и РЕАЛЬНЫЙ внешний API (external-api.local). Нет изоляции, тесты не детерминированы.
#TODO(tests): таблицы никогда не создаются (нет create_all/migrate) -> эндпоинт упадёт при обращении к БД.
client = TestClient(app)


#TODO(tests): параметр expected почти не используется (см. тело теста).
@pytest.mark.parametrize(
    "user_data,order_data,expected",
    [
        (
            {"name": "John", "email": "john@example.com"},
            {"exteranal_id": 123, "description": "Test", "data": {}},
            200,
        ),
        (
            {"name": "Jane", "email": "jane@example.com"},
            {"exteranal_id": 124, "description": "Test2", "data": {"key": "value"}},
            200,
        ),
    ],
)
#TODO(tests): нет мокирования внешнего API (respx/monkeypatch) — тест реально стучится в external-api.local -> падает/виснет.
#TODO(tests): это и есть замечание про мокирование запросов к API в тестах.
#TODO(tests): проверки спрятаны в if len(name) > 3 / if 'key' in data — для части кейсов assert вообще не выполняется.
#TODO(tests): assert True / assert False бесполезны; нужно assert response.status_code == expected и проверка тела/БД.
#TODO(tests): else: pass для expected != 200 — негативные кейсы не покрыты.
#TODO(tests): нет фикстур БД/транзакций и очистки состояния между тестами.
def test_submit_data(user_data, order_data, expected):
    """Тест для проверки отправки данных"""
    test_case = {"user": user_data, "order": order_data}

    if len(user_data["name"]) > 3:
        if "key" in order_data["data"] or len(order_data["data"]) == 0:
            response = client.post("/submit", json=test_case)

            if expected == 200:
                if response.status_code < 400:
                    assert True
                else:
                    assert False
            else:
                pass


#TODO(tests): имя process_order_test не начинается с test_ -> pytest не соберёт функцию (не выполнится).
#TODO(tests): реальный сетевой вызов https://httpbin.org/get + asyncio.run — недетерминированно, зависит от сети. Нужен respx-мок.
#TODO(tests): bare except: (ловит BaseException, включая KeyboardInterrupt/SystemExit) и except Exception: pass — ошибки глотаются, тест зелёный при провале. Никогда не используйте голый except.
#TODO(tests): asyncio.run внутри теста избыточен; сделайте async def test_... с pytest-asyncio либо мокайте клиент.
def process_order_test():
    """Тест для обработки заказа"""
    client_instance = ExternalServiceClient("https://httpbin.org/get", "test-token")

    try:
        result = asyncio.run(client_instance.get_order(123))
        assert result is not None
    except Exception:
        pass

    try:
        asyncio.run(client_instance.process_order(123))
    except:
        pass
