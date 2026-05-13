# wraith_protocol — paket açıklaması

Bu dosyadaki protokol iddiaları **[11-command-map.md](11-command-map.md)** ile aynı kanıt seviyesi sözlüğünü kullanır: `verified` · `observed` · `inferred` · `hypothesis` · `unsafe`.

## Genel rol

USB’den bağımsız, **deterministik bayt üretimi**: CRC, rapor uzunluğu, RGB komutu. Burada **dosya veya soket yok**; yan etkisiz fonksiyonlar.

## `crc.py`

- **Ne yapar:** CRC-16 **XMODEM**, polinom `0x1021`, başlangıç 0.
- **Neden saf Python:** `crcmod` bağımlılığı kaldırıldı; tek uygulama ve kurulum sadeleşti.
- **Dürüst kanıt hikâyesi (verified — cihaz kabulü + golden, SDK izolasyonu yok):** Bu repodaki CRC fonksiyonu, Windows DLL içinde **tek başına izole edilip “şu C fonksiyonunun birebir kopyasıdır” diye kanıtlanmadı**. Eşdeğerlik şu zincirle sabitlendi: **legacy prototip** (`w75.py` + `crcmod`) ile üretilen paket → **cihazın kabul ettiği** çıktı (pratik doğrulama) → refaktör sonrası **aynı parametrelerle aynı baytlar** (`tests/test_crc.py`, `tests/test_lighting.py` golden). Yani doğruluk “SDK kaynak kodundan türetilmiş matematik kanıtı” değil; **davranışsal regresyon + donanım kabulü** kanıtıdır. Polinom ve endianness için DLL içi arama ileride **observed** ile güçlendirilebilir.
- **`digest(data: bytes) -> int`:** Ham bayt dizisi üzerinde CRC.
- **`append_crc(buf: bytearray)`:** CRC kapsamı **report ID hariç** `buf[1:]` üzerinden hesaplanır; sonuç **big-endian** iki bayt olarak eklenir (**inferred** / legacy ile uyumlu kural; golden ile kilitli).

## `packet.py`

- **`REPORT_SIZE = 64`**, **`REPORT_ID = 0x01`** (**verified** — golden ve entegrasyon yolu).
- **`make_packet(payload)`:** `payload` tam **62 bayt** olmalı (CRC öncesi). CRC eklendikten sonra 64 bayt döner.
- **CRC girdi uzunluğu:** `payload[1:]` → **61 bayt** (byte indeksleri 1…60 dahil). Yani son iki bayt (CRC) hariç, report ID’den sonra kalan “gövde”nin tamamı.

## SDK command normalization

Windows SDK içinde bazı **command selector** baytları **internal command id**’ye normalize edilir (**observed** — `witmodSdk.dll.c` / sarmalayıcı akışı).

| Selector | Alternative selector | Internal command |
|----------|----------------------|------------------|
| `0x06` | `0x6A` | `0x07` |

Python v0.1 yolu doğrudan internal komut **`0x07`** ve report id **`0x01`** üretir; bu, çalışan **legacy RGB paketleri** ve golden test ile uyumludur (**verified**). SDK normalizasyon tablosu RE referansı olarak tutulur; ayrıntılı tablo: [11-command-map.md](11-command-map.md).

## Report id `0x06` (“col06”) notu

Bazı Windows SDK yollarında **report id `0x06`** veya buna karşılık gelen selector kullanımı **observed** olarak görülebilir. Bu repodaki **varsayılan üretim yolu** report id **`0x01`** ve `build_rgb_command` düzenidir; **`0x06` varsayılan Python yolu değildir**.

## `lighting.py`

- **`build_rgb_command(mode, speed, brightness, r, g, b, direction=0) -> bytes`**
- Byte düzeni (özet) — **verified** (golden + cihaz):

| İndeks | Anlam |
|--------|--------|
| 0 | Report ID `0x01` |
| 1 | Komut `0x07` (ışıklandırma) |
| 2–5 | `00 00 00 0E` (legacy ile aynı) |
| 6 | mode |
| 7 | speed |
| 8 | brightness |
| 9–11 | R, G, B |
| 12 | direction |
| 13–59 | sıfır dolgu |
| 60–61 | CRC (BE) |

- **Neden `struct.pack` ile 2–5:** Okunabilirlik; değerler sabit.

### Golden RGB paket (birim test ile kilitli)

Aşağıdaki hex, **`build_rgb_command(0, 3, 5, 255, 0, 255, 0)`** çıktısıdır — yani `tests/test_lighting.py` içindeki `_GOLDEN` ile birebir; parametreler eski `w75.py` ilk `send_command` demosuyla aynı seçilmiştir (**verified**).

```text
01070000000e000305ff00ff00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001ac1
```

Üretim çağrı zinciri (özet): `pytest` → `test_build_rgb_command_default_demo_vector` → `build_rgb_command(...)` → `make_packet` / CRC. Entegrasyon tarafında aynı baytlar `ConnectionManager.set_rgb` → core içi `build_rgb_command` ile üretilir; ayrıntı: [06-testing-and-ci.md](06-testing-and-ci.md).

## `analog.py`

- **Şu an:** Sadece fonksiyon imzaları ve `NotImplementedError("Pending RE: command bytes unverified")`.
- **Neden dosya var:** Gelecekteki analog/RT paketleri için yer tutucu; RE tamamlanana kadar **yanlış komut üretmemek** bilinçli tercih.
- **`wraith_protocol/__init__.py` içinde export yok:** Dış API’yi kirletmemek; “kullanıma hazır” sandığı yanlış beklentiyi önlemek. **Kök README:** `analog` modülü **public API değildir**.

## `wraith_protocol/__init__.py`

Dışa açılanlar: CRC, `make_packet`, `build_rgb_command`, sabitler. **Analog fonksiyonları listelenmez.**
