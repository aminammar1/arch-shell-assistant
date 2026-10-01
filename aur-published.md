# Publishing to the AUR

> One-time setup + per-release routine for `arch-shell-assistant`.
> After this, anyone can run `paru -S arch-shell-assistant` (or `yay -S ...`).

## 1. One-time account setup

1. Register at <https://aur.archlinux.org/register>.
2. Make sure you have an SSH key:
   ```bash
   ls ~/.ssh/id_ed25519.pub || ssh-keygen -t ed25519
   ```
3. Print it and paste into AUR → *My Account* → *SSH Public Key* → Update:
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```

## 2. Publish the package

```bash
sudo pacman -S --needed base-devel git
git clone ssh://aur@aur.archlinux.org/arch-shell-assistant.git aur-pkg
cp /home/amine/code-source/alien-x-app/PKGBUILD aur-pkg/
cd aur-pkg
makepkg --printsrcinfo > .SRCINFO
makepkg -si
```

`makepkg -si` test-builds and installs locally — if that succeeds, the
package is good. Then push it:

```bash
git add PKGBUILD .SRCINFO
git commit -m "v0.1.0"
git branch -M master   # AUR expects the master branch
git push -u origin master
```

## 3. Verify

Search `arch-shell-assistant` on <https://aur.archlinux.org> — it shows up
within minutes. Test from a clean state:

```bash
paru -S arch-shell-assistant
```

## 4. Later releases

```bash
# in this GitHub repo: bump pkgver in PKGBUILD, commit, push, tag vX.Y.Z
# in aur-pkg: copy the new PKGBUILD over, then
makepkg --printsrcinfo > .SRCINFO
makepkg -si
git add PKGBUILD .SRCINFO
git commit -m "vX.Y.Z"
git push
```

## Notes

- The custom pacman repo on GitHub Pages (see `README.md`) is independent
  and keeps working as a fallback — both channels can coexist.
- Never move a pushed `v*` tag: the PKGBUILD source is pinned to the tag.
