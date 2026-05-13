# macOS, hidapi ve sık sorunlar

Bu bölüm, geliştirme sırasında **gerçekten karşılaşılan** sorunların özeti ve çözüm mantığıdır. Vendor HID / usage page iddiaları için kanıt etiketleri: [11-command-map.md](11-command-map.md) ve [04-wraith-core.md](04-wraith-core.md).

## Üç ayrı “hid” kavramı

1. **PyPI paketi `hid`** — Python modülü; içinde `ctypes` ile native kütüphaneye bağlanır.
2. **Sistem kütüphanesi `libhidapi` (.dylib)** — Homebrew ile `brew install hidapi` olarak gelir; **Python paketinin içinde taşınmaz**.
3. **macOS IOKit / klavye sürücü yığını** — Tuşların OS’a nasıl girdiği; vendor HID `read()` ile her zaman görünmez.

Karışıklığı önlemek için dokümantasyonda mümkün olduğunca “PyPI `hid`” / “libhidapi” diye ayırıyoruz.

## “brew install hidapi yaptım ama yine yüklenmiyor”

### Sorun A: `LoadLibrary("libhidapi.dylib")` göreli isim

PyPI `hid` modülü import sırasında sırayla şunları dener (özet): Linux `.so` isimleri, sonra `libhidapi-iohidmanager.so*`, en sonda `libhidapi.dylib`. Hepsi **kısa dosya adı** ile `ctypes.cdll.LoadLibrary` çağrılır.

macOS’ta Homebrew genelde kütüphaneyi **`$(brew --prefix hidapi)/lib`** altına koyar; bu dizin **dyld varsayılan arama yolunda olmayabilir**. Sonuç: `brew list hidapi` “kurulu” görünür ama Python `hid` import’u patlar.

### Denenen ve yetersiz kalan: `CDLL("/tam/yol/libhidapi.dylib")` ön yükleme

Aynı process içinde önce tam yolu `CDLL` ile yüklemek, sonraki `LoadLibrary("libhidapi.dylib")` çağrısını **her zaman** çözmeyebilir (kısa isim hâlâ bulunamıyor).

### Uygulanan çözüm: `ctypes.cdll.LoadLibrary` geçici yaması

`import hid` **öncesi** (yalnızca Darwin):

1. `brew --prefix hidapi` ve `Cellar/hidapi/*/lib` + sabit yollarla **aday `.dylib` tam yolları** toplanır.
2. `ctypes.cdll.LoadLibrary` geçici olarak değiştirilir: istek adında `hidapi` geçiyorsa ve yol mutlak değilse, aday tam yollar sırayla denenir.
3. `import hid` biter bitmez (`finally`) orijinal `LoadLibrary` geri yüklenir — global yan etkiyi minimize etmek için.

Bu, dağıtılmış bir “hack” gibi görünse de, **kullanıcı deneyimini** Homebrew + PyPI kombinasyonunda pratik olarak düzeltir; alternatif her kullanıcıya `DYLD_*` anlatmak veya farklı bir Python binding seçmekten daha öngörülebilir.

## “`module 'hid' has no attribute 'device'`”

Eski örnekler ve Cython tabanlı binding’ler **`hid.device()`** kullanıyordu. PyPI **`hid` 1.x** ise **`hid.Device`** sınıfını kullanır; cihaz **`Device(path=...)`** ile açılır.

Core bu API’ye göre güncellendi.

## Tuş olayları neden HID `read` ile gelmiyor?

macOS genelde tuş akışını önce sistem yığınına verir; **belirli** vendor uçlarında veya ikincil koleksiyonlarda `read()` boş kalabilir (**observed** / ortam bağımlı). Bu SDK’nın RGB göndermesini engellemez; sadece “ham tuş sniffer” beklentisini karşılamaz. Aydınlatma için **`usage_page 0xFF1B`** önceliği bu repoda **test edilen W75 + macOS** için geçerlidir; tüm HID uçları için genel kural değildir. O tür tuş dinleme ihtiyaçları farklı API’ler ister ve bu repoda hedeflenmedi.

## İzinler (Gelecek / opsiyonel)

Global tuş dinleme veya erişilebilirlik tabanlı araçlar eklerseniz, macOS **Input Monitoring** / **Accessibility** izinleri gerekebilir. v0.1 RGB gönderimi için zorunlu değildir.
