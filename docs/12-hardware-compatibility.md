# Donanım uyumluluğu ve `wraith debug` (macOS)

## Neden var?

Bu proje **belgelendirilmemiş satıcı HID** üzerinden çalışır. macOS’ta aynı VID/PID altında **birden fazla HID arayüzü** (klavye, satıcı kontrol vb.) görülebilir. Sorun bildirirken “cihaz görünmüyor” tek başına yetersizdir.

`wraith debug enumerate` ve `wraith debug probe` komutları:

- Cihazın **HID olarak listelenip listelenmediğini**,
- **Hangi path’lerin açılabildiğini**,
- Bu SDK’nın RGB için kullandığı **sıralama (önce `usage_page 0xFF1B`)** ile **hangi adayın seçileceğini**,
- **Tek bir doğrulanmış RGB paketi** göndermek isteyenler için (yalnızca `--test-rgb --confirm` ile)

güvenli, **firmware / profil / bilinmeyen komut denemesi olmadan** raporlar.

## macOS’ta nasıl çalıştırılır?

Önce [README.md](../README.md) ve [07-macos-hid-and-troubleshooting.md](07-macos-hid-and-troubleshooting.md) içindeki **hidapi** kurulum notlarına uyun.

```bash
wraith debug enumerate
wraith debug enumerate --json

wraith debug probe
wraith debug probe --json
```

Sadece **bilinçli bir test** için (tek seferlik, projede kullanılan **aynı** `set_rgb` yolu):

```bash
wraith debug probe --test-rgb --confirm
```

`--test-rgb` **tek başına** veya `--confirm` eksikken **hiçbir HID yazımı yapılmaz**.

## Bilinen iyi çıktı örneği (known-good)

Başarılı bir `wraith debug probe --test-rgb --confirm --json` çalıştırmasından türetilmiş, **path alanları redakte** edilmiş referans dosya:

[examples/debug-probe-test-rgb-confirm.known-good.json](examples/debug-probe-test-rgb-confirm.known-good.json)

Beklenen özellikler (özet): `vendor_usage_page_found: true`, `rgb_test.status: "ok"`, `selected_candidate.candidate_role: "vendor_control_candidate"`, `usage_page` değeri `65307` (onaltılık `0xFF1B`). Gerçek makinede `path` ve `open_error` metinleri farklı olabilir.

## Issue açarken ne eklenmeli?

Aşağıdakileri mümkünse ekleyin (ayrıntı: [CONTRIBUTING.md](../CONTRIBUTING.md)):

- `wraith debug enumerate --json` çıktısı
- `wraith debug probe --json` çıktısı
- macOS sürümü, klavye modeli, mümkünse firmware bilgisi

## Kapsam sınırları (bilinçli)

- Bu sürüm **RGB / lighting odaklıdır**; analog, rapid trigger, SOCD, profil yazımı veya firmware güncelleme **yoktur ve probe ile taranmaz**.
- Firmware sürümleri revizyonlar arasında değişebilir; [README.md](../README.md) içindeki **uyumluluk tablosu** güncellenebilir bir özetdir.
- `candidate_role` etiketleri **raporlama** içindir; `keyboard_candidate` RGB yolunda **tercih edilmez** (`ConnectionManager` sırası: önce `0xFF1B`, sonra `interface_number > 0` yedekleri).

## Güvenlik

- Bilinmeyen komut **fuzzing** yoktur.
- Probe varsayılan modda **yazma yapmaz**.
- `--test-rgb --confirm` yalnızca `ConnectionManager.set_rgb` ile **tek** bilinen statik renk paketini gönderir.
