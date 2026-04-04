# Deploy to GitHub Pages - Step by Step Guide

Follow these steps to deploy your Spain Eclipse Sites viewer to GitHub Pages.

## Prerequisites

- Git repository already exists on GitHub
- You have push access to the repository
- Python 3 installed locally

## Step 1: Update .gitignore

Currently, the `data/` directory is ignored. You need to allow it for GitHub Pages.

**Option A: Allow all data files (Recommended)**
```bash
# Edit .gitignore and comment out or remove this line:
# data/

# Or replace it with more specific ignores:
data/*.kml
data/.cache/
```

**Option B: Use the provided GitHub Pages .gitignore**
```bash
cp .gitignore.gh-pages .gitignore
```

## Step 2: Generate All Data

Run the data pipeline to generate all necessary files:

```bash
# Generate site data and download all images
python3 generate_eclipse_site_data.py

# This creates:
# - data/eclipse_site_data.csv (site data)
# - data/igme_images/ (cached IGME photos)
# - data/horizons/ (horizon profile images)
# - data/scrape/shademap_snapshots/ (sun/shadow visualizations)
# - data/scrape/eclipsefan_horizons/ (horizon views)
# - data/scrape/ign_profiles/ (eclipse profiles)
# - data/brochures/ (PDF brochures)
```

## Step 3: Add API Keys (Optional)

If you want to use Google Maps or Mapbox features:

1. Edit `config.json`:
```json
{
  "google_maps_api_key": "YOUR_GOOGLE_MAPS_KEY",
  "mapbox_api_key": "YOUR_MAPBOX_KEY"
}
```

2. **IMPORTANT**: If adding real keys, add `config.json` to `.gitignore`:
```bash
echo "config.json" >> .gitignore
```

3. Create a public version without keys:
```bash
cp config.json config.json.example
# Edit config.json.example to remove real keys
```

## Step 4: Commit Data Files

```bash
# Check what will be added
git status

# Add the data directory
git add data/

# Add other necessary files
git add index.html config.json static/ readme.html credits.html

# Commit
git commit -m "Add generated data for GitHub Pages deployment"
```

## Step 5: Push to GitHub

```bash
# Push to your main branch
git push origin main
```

## Step 6: Enable GitHub Pages

1. Go to your repository on GitHub: `https://github.com/YOUR_USERNAME/spain-eclipse-sites`

2. Click **Settings** (top right)

3. Scroll down to **Pages** section (left sidebar)

4. Under **Source**:
   - Select branch: `main` (or `master`)
   - Select folder: `/ (root)`
   - Click **Save**

5. Wait 1-2 minutes for deployment

6. Your site will be available at:
   ```
   https://YOUR_USERNAME.github.io/spain-eclipse-sites/
   ```

## Step 7: Verify Deployment

Visit your GitHub Pages URL and check:
- [ ] Sites load in the sidebar
- [ ] Clicking a site shows details
- [ ] Images display correctly
- [ ] About/Resources/Help buttons work
- [ ] Favorites and notes features work

## Troubleshooting

### Site Not Loading

**Check GitHub Actions:**
1. Go to **Actions** tab in your repository
2. Look for any failed builds
3. Click on the failed build to see error details

**Common Issues:**
- Build still in progress (wait a few minutes)
- Branch name mismatch (check Settings > Pages)
- Files not committed (check `git status`)

### Images Not Loading

**Check browser console (F12):**
- Look for 404 errors
- Verify image paths match your directory structure

**Fix:**
```bash
# Ensure all images are committed
git add data/igme_images/ data/scrape/
git commit -m "Add missing images"
git push
```

### CSV Not Loading

**Check:**
- `data/eclipse_site_data.csv` exists
- File is committed to git
- No CORS errors in browser console

**Fix:**
```bash
git add data/eclipse_site_data.csv
git commit -m "Add site data CSV"
git push
```

### API Keys Not Working

**For public repositories:**
- Never commit real API keys
- Use environment variables or GitHub Secrets
- Or accept limited functionality without keys

**For private repositories:**
- You can commit keys to `config.json`
- Still recommended to use Secrets for production

## Updating the Site

When you need to update data or add new sites:

```bash
# 1. Update data locally
python3 generate_eclipse_site_data.py

# 2. Commit changes
git add data/
git commit -m "Update site data"

# 3. Push to GitHub
git push origin main

# 4. GitHub Pages will automatically rebuild (1-2 minutes)
```

## Custom Domain (Optional)

To use a custom domain like `eclipse-sites.example.com`:

1. In repository Settings > Pages
2. Enter your custom domain
3. Add DNS records at your domain provider:
   ```
   Type: CNAME
   Name: eclipse-sites (or @)
   Value: YOUR_USERNAME.github.io
   ```

## Performance Tips

1. **Optimize Images:**
   ```bash
   # Install imagemagick
   brew install imagemagick  # macOS
   
   # Resize large images
   find data/igme_images -name "*.jpg" -exec mogrify -resize 1200x1200\> {} \;
   ```

2. **Enable Caching:**
   - GitHub Pages automatically caches static files
   - No additional configuration needed

3. **Monitor Usage:**
   - GitHub Pages has soft limits (100GB bandwidth/month)
   - Check repository Insights > Traffic

## Security Notes

- ✅ Site uses HTTPS automatically
- ✅ No server-side code (static files only)
- ⚠️ Don't commit API keys to public repos
- ⚠️ Be careful with sensitive site data

## Need Help?

- Check [GITHUB_PAGES.md](GITHUB_PAGES.md) for technical details
- Review [README.md](README.md) for project overview
- Open an issue on GitHub if you encounter problems

---

**Quick Command Summary:**
```bash
# 1. Allow data directory
nano .gitignore  # Remove or comment out "data/"

# 2. Generate data
python3 generate_eclipse_site_data.py

# 3. Commit and push
git add data/ index.html config.json
git commit -m "Deploy to GitHub Pages"
git push origin main

# 4. Enable Pages in GitHub Settings > Pages
# 5. Visit https://YOUR_USERNAME.github.io/spain-eclipse-sites/