pkgname=asusctl-runit
pkgver=6.5.0
pkgrel=1
pkgdesc='Artix/runit integration for asusctl 6.5.0, including runit-native asus-shutdown'
arch=('x86_64')
url='https://github.com/OpenGamingCollective/asusctl'
license=('MPL-2.0')
depends=('asusctl=6.5.0' 'runit' 'dbus' 'elogind')
makedepends=('cargo' 'python')
optdepends=(
  'rog-control-center=6.5.0: graphical control center'
  'supergfxctl-runit: tested runit service for nvidia-powerd integration'
)
provides=('asusctl-runit-integration=6.5.0')
conflicts=('asusctl-runit-integration')
replaces=('asusctl-runit-integration')
install=asusctl-runit.install
source=(
  "asusctl-${pkgver}.tar.gz::https://github.com/OpenGamingCollective/asusctl/archive/refs/tags/${pkgver}.tar.gz"
  'prepare-asus-shutdown-runit.py'
  'asusd.run'
  'asusd.check'
  'asusd.log.run'
  'asus-shutdown.run'
  'asus-shutdown.finish'
  'asus-shutdown.log.run'
  'asusctl-runit-setup'
  'asusctl-runit-unsetup'
  'README.md'
  'NOTICE.md'
  'LICENSE'
)
sha256sums=(
  'SKIP'
  '9231674cf4aef470210e7279244628c482ca79679f44e0403083168d2982a67c'
  '0ca0292e19c73f8b0a8dfc05cd6868df6b8cb7a47b8622c22b28c66ac21e2b99'
  '4af030174c015b410d39184fd9d94a85e93050f7e8a5ab9437cd753261763a51'
  '0f6fb6f96f0fa41292ca2372f28c3de57e7baf64c01c42bbe822aeeb38df0104'
  'acc4945c2f9fcb47bd4d8f41138046249865d9558e7e9c74c85b777e9a6f7a11'
  '907f411ed3af58fd5a761fc4ae2c2c485b71f5d739b2e107a0c2dfb3dab640a4'
  '9ad97a414ae5f5483847d829a87c9cc6599f3291f35a14dfa0e5643a623dbd18'
  'f3258947c6de9af9bfabfc7afd35fef8a016b44e69af636b3d9553671512ea5b'
  '6f49cdedf37adbfd491dba69c5a68073d0f7deeaba907a68721b3073295e09b0'
  'aac180d177ee2dcefd44cc55507d1aa0c65d3b0f6fd30935d5200e645b5ca087'
  'b8f706951acfe11bc847144301cedfb0eb0b8ce7936a15e2c422507339fba72c'
  'fab3dd6bdab226f1c08630b1dd917e11fcb4ec5e1e020e2c16f83a0a13863e85'
)

prepare() {
  python "${srcdir}/prepare-asus-shutdown-runit.py" "${srcdir}/asusctl-${pkgver}"
}

build() {
  cd "${srcdir}/asusctl-${pkgver}"
  CARGO_TARGET_DIR="${srcdir}/target" \
    cargo build --release --locked -p asus-shutdown
}

check() {
  cd "${srcdir}/asusctl-${pkgver}"
  CARGO_TARGET_DIR="${srcdir}/target" \
    cargo test --release --locked -p asus-shutdown
}

package() {
  install -Dm755 "${srcdir}/target/release/asus-shutdown" \
    "${pkgdir}/usr/bin/asus-shutdown-runit"

  install -Dm755 "${srcdir}/asusd.run" "${pkgdir}/etc/runit/sv/asusd/run"
  install -Dm755 "${srcdir}/asusd.check" "${pkgdir}/etc/runit/sv/asusd/check"
  install -Dm755 "${srcdir}/asusd.log.run" "${pkgdir}/etc/runit/sv/asusd/log/run"

  install -Dm755 "${srcdir}/asus-shutdown.run" \
    "${pkgdir}/etc/runit/sv/asus-shutdown/run"
  install -Dm755 "${srcdir}/asus-shutdown.finish" \
    "${pkgdir}/etc/runit/sv/asus-shutdown/finish"
  install -Dm755 "${srcdir}/asus-shutdown.log.run" \
    "${pkgdir}/etc/runit/sv/asus-shutdown/log/run"

  install -Dm755 "${srcdir}/asusctl-runit-setup" \
    "${pkgdir}/usr/bin/asusctl-runit-setup"
  install -Dm755 "${srcdir}/asusctl-runit-unsetup" \
    "${pkgdir}/usr/bin/asusctl-runit-unsetup"

  install -Dm644 "${srcdir}/LICENSE" \
    "${pkgdir}/usr/share/licenses/${pkgname}/LICENSE"
  install -Dm644 "${srcdir}/README.md" "${pkgdir}/usr/share/doc/${pkgname}/README.md"
  install -Dm644 "${srcdir}/NOTICE.md" "${pkgdir}/usr/share/doc/${pkgname}/NOTICE.md"
  install -d -m755 "${pkgdir}/var/log/asusd" "${pkgdir}/var/log/asus-shutdown"
}
