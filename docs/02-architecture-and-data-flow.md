# Mimari ve veri akışı

Protokol byte’ları ve kanıt seviyeleri: [11-command-map.md](11-command-map.md), [03-wraith-protocol.md](03-wraith-protocol.md).

## Katmanlar (zorunlu kural)

```text
wraith_cli  →  wraith_core  →  wraith_protocol  →  USB HID (libhidapi)
```

**CLI, `wraith_protocol` import etmez.** Bunun nedenleri:

1. **Tek yazım kapısı:** `ConnectionManager` içinde `threading.RLock` ile HID `write` seri hale getirilir. CLI doğrudan paket üretseydi, başka bir süreç (ör. ileride API) aynı handle’a yazmaya çalışınca yarış durumu oluşurdu.
2. **Yeniden bağlanma:** Bağlantı kopması, handle geçersizliği gibi durumlar core’da toplanır; üst katman sadece `set_rgb` gibi anlamlı çağrılar yapar.
3. **Test edilebilirlik:** Birim testleri protokolü HID olmadan doğrular; entegrasyon testi core üzerinden gider.

## FastAPI (gelecek) nereye oturur?

Plan: `HTTP istemcisi → wraith_api → wraith_core`. Route handler’lar **`wraith_protocol`’ü doğrudan import etmez** (`lighting`, `crc`, `packet` dahil); yalnızca core’daki `ConnectionManager.set_rgb` benzeri yüzey kullanılır. Böylece HTTP ve CLI aynı güvenlik ve kilit modelini paylaşır.

## `wraith_protocol` ne zaman doğrudan kullanılır?

- **Birim testlerde** (`tests/test_crc.py`, `tests/test_lighting.py`): golden vektörler, CRC doğruluğu.
- **`wraith_core` içinde:** `build_rgb_command` çağrıları `connection_manager` içinden yapılır.

Uygulama kodu (CLI dışı bir servis yazıyorsanız) yine **önce core** kullanmalı; sadece özel deneyler için protokole inebilirsiniz, ama üretim yolunda önerilmez.

## Özet akış (RGB gönderme)

1. Kullanıcı `wraith set-color ...` çalıştırır.
2. `wraith_cli.main` argümanları çözümler (`static` → mod `0`, `breathe` → mod `1`).
3. `ConnectionManager.set_rgb(...)` çağrılır.
4. Core içinde `wraith_protocol.lighting.build_rgb_command` → 64 bayt `bytes`.
5. Core, açılmış `hid.Device` üzerinde `write(bytes)` ile gönderir.
6. Hata durumunda kapanan handle, backoff ile yeniden enumerate + açma denemesi.
