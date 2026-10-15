# Publishing to GitHub

Replace `YOUR_GITHUB_USER` with your GitHub username.

## 1. Create an empty GitHub repository

On GitHub: **New repository** -> choose the repository name -> do **not** initialize it with a README, .gitignore or license (those files are already here).

Recommended repository names are the directory names used in the examples below.

## 2. Initialize and push

```sh
git init
git add .
git commit -m "Initial Artix/runit port"
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USER/asusctl-runit-artix.git
git push -u origin main
```

If GitHub asks for a password over HTTPS, use a Personal Access Token or authenticate with GitHub CLI.

### GitHub CLI alternative

```sh
gh auth login
gh repo create asusctl-runit-artix --public --source=. --remote=origin --push
```

## 3. Tag the tested release

```sh
git tag -a v1.0.0 -m "First tested Artix/runit release"
git push origin v1.0.0
```

Then open **Releases -> Draft a new release** on GitHub and select `v1.0.0`.

## 4. Later updates

```sh
git add .
git commit -m "Describe the change"
git push
```

Before publishing changes to a PKGBUILD, build and test it on Artix first.
