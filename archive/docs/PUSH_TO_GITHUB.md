# Push Repository to GitHub - Step by Step

## Step 1: Create Repository on GitHub

1. Go to https://github.com/flyingbarron
2. Click the **"+"** button (top right) → **"New repository"**
3. Fill in the details:
   - **Repository name**: `spain-eclipse-sites`
   - **Description**: Spain Eclipse Site Viewer - Interactive map for 2026 total solar eclipse viewing locations
   - **Visibility**: Choose Public or Private
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
4. Click **"Create repository"**

## Step 2: Push Your Code

After creating the repository, GitHub will show you commands. Use these:

### Option A: Using HTTPS (Recommended for first time)

```bash
# The remote is already added, so just push
git push -u origin main
```

You'll be prompted for credentials. Use:
- **Username**: flyingbarron
- **Password**: Your GitHub Personal Access Token (not your password!)

### Option B: Using SSH (If you have SSH keys set up)

```bash
# Change remote to SSH
git remote set-url origin git@github.com:flyingbarron/spain-eclipse-sites.git

# Push
git push -u origin main
```

## Step 3: Get a Personal Access Token (If needed)

If you don't have a Personal Access Token:

1. Go to https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Give it a name: "spain-eclipse-sites"
4. Select scopes:
   - ✅ `repo` (Full control of private repositories)
5. Click **"Generate token"**
6. **COPY THE TOKEN** (you won't see it again!)
7. Use this token as your password when pushing

## Step 4: Verify Upload

After pushing, go to:
```
https://github.com/flyingbarron/spain-eclipse-sites
```

You should see all your files!

## Step 5: Enable GitHub Pages

Now follow the deployment guide in [DEPLOY_TO_GITHUB_PAGES.md](DEPLOY_TO_GITHUB_PAGES.md)

Quick version:
1. Go to repository **Settings** → **Pages**
2. Source: `main` branch, `/ (root)` folder
3. Click **Save**
4. Wait 1-2 minutes
5. Visit: `https://flyingbarron.github.io/spain-eclipse-sites/`

## Troubleshooting

### Authentication Failed

**Problem**: `fatal: could not read Username for 'https://github.com'`

**Solution**: You need to authenticate. Options:

1. **Use GitHub CLI** (easiest):
   ```bash
   # Install GitHub CLI
   brew install gh  # macOS
   
   # Login
   gh auth login
   
   # Push
   git push -u origin main
   ```

2. **Use SSH** (if you have keys):
   ```bash
   git remote set-url origin git@github.com:flyingbarron/spain-eclipse-sites.git
   git push -u origin main
   ```

3. **Use Personal Access Token**:
   - Create token at https://github.com/settings/tokens
   - Use token as password when prompted

### Repository Already Exists

**Problem**: Repository already exists on GitHub

**Solution**:
```bash
# Force push (CAUTION: This overwrites remote)
git push -u origin main --force

# Or, if you want to merge:
git pull origin main --allow-unrelated-histories
git push -u origin main
```

### Wrong Branch Name

**Problem**: Your branch is called `master` not `main`

**Solution**:
```bash
# Rename branch to main
git branch -M main

# Push
git push -u origin main
```

## Current Status

✅ Git repository initialized locally
✅ Remote added: `https://github.com/flyingbarron/spain-eclipse-sites.git`
⏳ Waiting for: Repository to be created on GitHub
⏳ Waiting for: First push to GitHub

## Quick Command Reference

```bash
# Check current status
git status
git remote -v

# Push to GitHub (after creating repo)
git push -u origin main

# If you need to change remote URL
git remote set-url origin NEW_URL

# View commit history
git log --oneline

# Check what will be pushed
git log origin/main..main  # After first push
```

## Next Steps After Pushing

1. ✅ Repository on GitHub
2. Enable GitHub Pages (Settings → Pages)
3. Update .gitignore to allow data/
4. Generate and commit data files
5. Push data files
6. Visit your live site!

---

**Need help?** Check [DEPLOY_TO_GITHUB_PAGES.md](DEPLOY_TO_GITHUB_PAGES.md) for the complete deployment guide.