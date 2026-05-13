# Tersine mühendislik kaynakları

Bu dosyadaki tablolar ve iddialar **[11-command-map.md](11-command-map.md)** içindeki kanıt seviyesi sözlüğünü kullanır: `verified` · `observed` · `inferred` · `hypothesis` · `unsafe`.

## `dec_software/witmodSdk.dll.c`

- **Ne değildir (sert sınır):** Bu dosya **üretim kaynak kodu değildir**; tersine mühendislik / decompile çıktısıdır, derleyici veya satıcı tarafından sağlanan resmi kaynak değildir. Dağıtım amacı “çalıştırılabilir SDK” değil; **yalnızca referans hammaddesi** ve hedefli arama için.
- **Kaynak:** Windows tarafı `witmodSdk.dll` (veya eşdeğeri) decompile çıktısı (**observed** — dosyanın kendisi).
- **Kullanım amacı:** Sabit stringler, fonksiyon isimleri, `HidD_SetFeature` / `HidD_GetFeature` gibi Win32 çağrıları, desteklenen VID/PID listeleri ve olası komut yapıları için **ipucu madenciliği**.
- **Sınırlar:** Otomatik decompile isimleri (`FUN_...`, `DAT_...`) anlamsızdır; her iddia **cihaz veya USB capture ile doğrulanmalıdır** (`verified` hedefi).
- **Boyut:** Çok büyük; tam tarama yerine hedefli arama önerilir.

## SDK yazım sarmalayıcısı (Windows)

DLL tarafında HID çıkışı **`WriteFile`** ile **sabit uzunluk `0x40` (64)** bayt output report olarak gönderildiği yollar **observed** edilebilir. Bu, macOS’taki PyPI `hid.Device.write(bytes)` yolunun “aynı Win32 çağrısı” olduğu anlamına gelmez; sadece **64 baytlık rapor taşıma** beklentisinin SDK’da da geçerli olduğuna dair bağlam sağlar.

## Şu ana kadar kodda “kilitlemiş” olduğumuz bilgiler (kanıt etiketli)

- **VID/PID:** `0x0416` / `0x7372` — **verified** (W75 ile denendi; entegrasyon / manuel).
- **Enumeration önceliği:** `usage_page == 0xFF1B` adayları önce — **verified** (test edilen macOS + W75 donanımında RGB’nin çalıştığı yol); başka VID/PID veya revizyonlarda farklı olabilir → ürün ailesi genellemesi **hypothesis** değil, **cihaz başına doğrulama** ister.
- **64 bayt rapor**, report id **`0x01`**, aydınlatma internal komut **`0x07`**, belirli ofsetlerde mod/hız/parlaklık/RGB — **verified** (golden + cihaz).
- **CRC-16/XMODEM** (`0x1021`), kapsam ve endianness — **verified** yalnızca “legacy + cihaz kabulü + golden” anlamında; DLL içinde ayrı fonksiyon olarak izole kanıt **henüz yok** (bkz. [03-wraith-protocol.md](03-wraith-protocol.md) CRC bölümü).

## SDK command remap tablosu (özet)

Tam tablo ve risk sütunu: **[11-command-map.md](11-command-map.md)**. Özet: selector `0x06` / `0x6A` → internal `0x07` lighting (**observed** normalizasyon, **verified** Python yolu `0x07` + `0x01`).

## Firmware, update ve kalıcı yazım

**Firmware güncelleme**, **bootloader** veya **kalıcı profil / EEPROM benzeri** yazım yolları **bu repoda kasıtlı olarak scope dışıdır** ve **unsafe** kabul edilir: yanlış bayt cihazı brick edebilir veya garanti dışı bırakabilir. DLL içinde ilgili izler görülse bile CLI/API üzerinden **expose edilmez** ve “deneme” yapılmaz.

## Güvenlik kuralı

**Bilinmeyen command id’ler fuzz edilmez.** Rastgele veya sıralı deneme yapılmaz. Firmware/update, profile write veya kalıcı ayar yazdığı düşünülen yollar bu repoda **expose edilmez**.

## Yeni command doğrulama checklist’i

Her yeni komut için:

1. DLL veya USB capture kanıtı (**observed** minimum).
2. Payload offset açıklaması (dokümantasyon).
3. Golden packet (hex) + birim test.
4. Mümkünse cihazlı manuel doğrulama notu (**verified**).
5. [11-command-map.md](11-command-map.md) tablosu + risk sütunu güncellemesi.
6. İlgili protokol dokümanında kanıt seviyesi etiketi.

## Henüz kilitlemediğimiz (bilerek)

- **Actuation / Rapid Trigger** komut byte’ları ve payload ofsetleri — `analog.py` bilinçli olarak `NotImplementedError` (**unsafe** veya **unknown** riski bilinene kadar dokunulmaz).
- **Feature report vs output report** ayrımı Windows’ta net olabilir; macOS’ta `write` ile gidilen yol şimdilik pratikte yeterli (**verified** yalnızca mevcut RGB yolu için); diğer komutlar için ayrı doğrulama gerekir.

## Önerilen sonraki RE adımları (koda yazılmamış plan)

1. USB capture (Windows’ta resmi yazılım komutları tetiklenirken) veya DLL içinde komut `0x07` dışı sabitlerin iz sürülmesi — **observed** üretimi.
2. Her yeni komut için yukarıdaki checklist — **verified** hedefi.
3. Komut sözlüğü: **[11-command-map.md](11-command-map.md)** tek tablo kaynağı olarak genişletilir.
