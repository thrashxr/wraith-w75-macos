# CLI, örnekler ve paketleme

## PyPI / setuptools

- **Proje adı (`name`):** `wraith-w75` — pip’te görünen isim (tire normaldir).
- **Python paketleri:** `wraith_protocol`, `wraith_core`, `wraith_cli`, `wraith_api` — `pyproject.toml` içinde `[tool.setuptools] packages` ile sabit listelenir.
- **Çalışma zamanı bağımlılığı:** `hid>=1.0.0` (PyPI’daki ctypes tabanlı paket).
- **Geliştirici ekstra:** `[project.optional-dependencies] dev` → `pytest`.
- **Konsol scripti:** `[project.scripts]` → `wraith = "wraith_cli.main:main"`  
  Kurulumdan sonra: `wraith --help` (aslında alt komutlar `required=True` olduğu için doğrudan alt komut gerekir).

## `wraith_cli/main.py`

- **Kütüphane:** Yalnızca `wraith_core` (`ConnectionManager`, istisnalar, `diagnostics` alt modülü üzerinden `debug` komutları).
- **Alt komutlar:**
  - `wraith status` — `ensure_connected` + JSON `status()`; cihaz yoksa çıkış kodu 1.
  - `wraith set-color --mode static|breathe --r --g --b` ve isteğe bağlı `--speed`, `--brightness`, `--direction`, `--max-retries`.
  - `wraith debug enumerate [--json]` — varsayılan VID/PID için HID arayüz listesi; `wraith_core.diagnostics`.
  - `wraith debug probe [--json] [--test-rgb --confirm]` — uyumluluk özeti; RGB yazımı yalnızca `--test-rgb` ile birlikte `--confirm` iken (`ConnectionManager.set_rgb`).
- **Mod eşlemesi:** `static` → aydınlatma modu `0`, `breathe` → `1` (eski demo scriptiyle uyumlu başlangıç).
- **Hata yüzeyi:** `HidApiNotAvailable` ve `DeviceNotFound` ayrı ele alınır; diğerleri genel `Error:` ile stderr’e yazılır.

## `examples/w75_demo.py`

- **Amaç:** Eski `w75.py` ana bloktaki gibi birkaç `set_rgb` sırası; eğitim ve manuel regresyon.
- **Kasıtlı olarak assert yok:** “Demo = gösteri”; otomatik doğrulama `tests/` altında.
- **Çalıştırma:** Paket kurulu ortamda `python examples/w75_demo.py` veya `PYTHONPATH=.` ile.

## Faz 2 notu (`wraith_api`)

Şu an yalnızca `__init__.py` içinde kısa açıklama. FastAPI uygulaması eklendiğinde önerilen uçlar (plan): `POST /set-rgb`, `GET /status`; analog uçlar RE sonrası.
