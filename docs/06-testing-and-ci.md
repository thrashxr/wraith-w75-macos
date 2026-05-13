# Test stratejisi

## Varsayılan: `pytest`

`pyproject.toml` → `[tool.pytest.ini_options]`:

- `addopts = "-m \"not integration\""`  
  Böylece **fiziksel cihaz gerektiren** testler normal `pytest` çalıştırmasında **seçilmez** (CI dostu).

## Birim testler

| Dosya | Ne doğrular |
|--------|----------------|
| `test_crc.py` | CRC değeri ve `append_crc` ile golden 64 bayt paketin tutarlılığı. |
| `test_lighting.py` | `build_rgb_command(0,3,5,255,0,255,0)` çıktısının bilinen hex ile birebir eşleşmesi. |

Golden vektör, eski `w75.py` + `crcmod` ile üretilen paketten türetildi; böylece refaktörlerde regresyon yakalanır.

### Golden RGB paketinin kaynağı (**verified** — test dosyası)

- **Üreten çağrı:** `build_rgb_command(0, 3, 5, 255, 0, 255, 0)` — `tests/test_lighting.py` içindeki `test_build_rgb_command_default_demo_vector`.
- **Hex (tek satır):** `01070000000e000305ff00ff00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001ac1`
- **Entegrasyon:** Aynı parametreler `ConnectionManager.set_rgb` üzerinden cihaza gider; birim test yalnızca bayt üretimini assert eder. Ayrıntılı tablo ve kanıt sözlüğü: [03-wraith-protocol.md](03-wraith-protocol.md), [11-command-map.md](11-command-map.md).

## Entegrasyon testi

- **Dosya:** `tests/test_integration.py`
- **İşaret:** `@pytest.mark.integration`
- **Ne yapar:** `ConnectionManager().set_rgb(...)` — gerçek USB ve çalışan hidapi gerekir.
- **`HidApiNotAvailable`:** Ortamda native kütüphane yoksa **`pytest.skip`** — CI’da “kırmızı” değil “atlandı”.
- **`DeviceNotFound`:** Cihaz takılı değilse **`pytest.fail`** — integration bilinçli çalıştırıldığında sorun görünür olsun.

## Integration’ı çalıştırma

```bash
pytest --override-ini "addopts=" -m integration
```

`addopts` geçici olarak boşaltılmalı; aksi halde `-m "not integration"` ile çelişir.

## Neden `examples/` içinde assert yok?

Plan kararı: demo ile otomatik test karışmasın. İkisi aynı dosyada hem “gösteri” hem “assert” olunca bakım zorlaşıyor; ayrı marker’lı test net sınır çizer.
