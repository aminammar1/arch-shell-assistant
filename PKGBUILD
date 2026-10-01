# Maintainer: Mohamed Amine Ammar <ammar.mohamdamine@gmail.com>
pkgname=arch-shell-assistant
pkgver=0.1.0
pkgrel=1
pkgdesc="Safe plain-language to shell-command agent for Arch Linux: explains, rates risk, confirms before running"
arch=('any')
url="https://github.com/aminammar1/arch-shell-assistant"
license=('MIT')
depends=('python' 'python-openai' 'python-dotenv' 'python-rich')
makedepends=('python-build' 'python-installer' 'python-hatchling')
# After you push tag v$pkgver to GitHub, regenerate sums with: updpkgsums
source=("$pkgname-$pkgver.tar.gz::$url/archive/refs/tags/v$pkgver.tar.gz")
sha256sums=('SKIP')

build() {
  cd "$pkgname-$pkgver"
  python -m build --wheel --no-isolation
}

package() {
  cd "$pkgname-$pkgver"
  python -m installer --destdir="$pkgdir" dist/*.whl
  install -Dm644 README.md "$pkgdir/usr/share/doc/$pkgname/README.md"
  install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}
