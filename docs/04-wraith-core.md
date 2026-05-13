# wraith_core — bağlantı ve taşıma katmanı

Protokol iddialarında kanıt etiketleri: [11-command-map.md](11-command-map.md).

## `exceptions.py`

| Sınıf | Ne zaman |
|--------|-----------|
| `DeviceNotFound` | VID/PID için uygun HID yolu hiç açılamadı veya cihaz yok. |
| `HidOpenError` | (İleride ayrıntılandırılabilir) Belirli path açılış reddi. |
| `TransportError` | Açık handle beklenmedik şekilde geçersiz / yazılamıyor. |
| `ReconnectFailed` | `max_retries` sınırına ulaşıldı. |
| `HidApiNotAvailable` | PyPI `hid` modülü native `libhidapi` yükleyemedi veya yama sonrası hâlâ başarısız. |

## `connection_manager.py` — `ConnectionManager`

### VID / PID

Varsayılan: **`0x0416:0x7372`** (**verified** — test edilen W75 donanımı). Kurucuda override edilebilir.

### HID aday sırası (macOS deneyimi)

`hid.enumerate` sonuçları içinde:

1. **`usage_page == 0xFF1B`** olanlar önce — **verified** yalnızca “bu repoda test edilen W75 + macOS birleşimi” için; başka ürün, revizyon veya klonlarda aynı `usage_page` her zaman doğru uç olmayabilir — **doğrulanmamış donanımda unknown** kabul edin, genel varsayım yapmayın.
2. Sonra `interface_number > 0` olan diğer adaylar (legacy `w75.py` ile aynı mantık).

**Neden:** `interface_number == 1` ve standart klavye koleksiyonu olan uçlar macOS’ta sıkça `open_path` ile açılamıyor; test donanımında RGB **`0xFF1B`** önceliklendiğinde çalışıyor (**verified** bu kombinasyon için).

### Cihaz API’si: `Device` (küçük harf değil)

PyPI **`hid` 1.x** paketi **`hid.device()` + `open_path()`** sunmuyor; **`hid.Device(path=...)`** kullanıyor. Core buna göre yazıldı.

### Yazma

- **`write(bytes(payload))`:** Eski Cython sürümündeki `write(list)` yerine **bytes**; ctypes tabanlı hid_write ile uyum.

### Kilit

- **`threading.RLock`:** Aynı process içinde eşzamanlı `write`/`connect`/`close` çakışmasını önlemek için.

### Durum

- `disconnected` | `connecting` | `connected`
- İsteğe bağlı `on_state_change` callback.

### Yeniden bağlanma ve backoff

Yazma `OSError` / `ValueError` (ve varsa `hid.HIDException`) sonrası:

1. Handle kapatılır, durum `disconnected`.
2. Bekleme: **0.25 → 0.5 → 1 → 2 → 4 saniye**; bundan sonra **her zaman 4 saniye** (tavan altına dönüş yok).
3. `max_retries: int | None` — `None` sınırsız deneme.

**Neden bu aralıklar:** Aşırı sıkı polling USB yığınını zorlamasın; uzun süre kopuk kalınca yine de makul sürede tekrar denensin.

### `set_rgb`

Tek “iş” yüzeyi: içeride `build_rgb_command` + `_write_with_reconnect`. CLI yalnızca bunu çağırır.

### macOS: `hid` import ve ctypes yaması

Ayrıntılı açıklama [07-macos-hid-and-troubleshooting.md](07-macos-hid-and-troubleshooting.md) dosyasında. Kısacası:

- `import hid` geciktirilir (birim test toplamasında native kütüphane zorunlu olmasın diye).
- Darwin’de `import hid` sırasında `ctypes.cdll.LoadLibrary` geçici yamalanır; kısa isimli `libhidapi*` istekleri Homebrew’den çözülen **tam yola** yönlendirilir.
- Import bitince orijinal `LoadLibrary` geri yüklenir (`finally`).

### `_hid()` önbelleği

Modül bir kez başarıyla yüklendikten sonra tekrar import edilmez; performans ve tutarlılık.
