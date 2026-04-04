# Utilities

Helper scripts for managing the Spain Eclipse Sites project.

## download_google_maps_thumbnails.py

Downloads Google Maps Static API thumbnails for all sites to use on GitHub Pages without exposing your API key.

### Setup

1. Install required package:
```bash
pip install python-dotenv
```

2. Create a `.env` file in the project root (copy from `.env.example`):
```bash
cp .env.example .env
```

3. Add your Google Maps API key to `.env`:
```
GOOGLE_MAPS_API_KEY=your_actual_api_key_here
```

### Usage

```bash
python3 utilities/download_google_maps_thumbnails.py
```

This will:
- Download satellite map thumbnails for all sites
- Save them to `data/google_maps_thumbnails/`
- Skip any thumbnails that already exist
- Show a summary of downloaded/skipped/failed images

### After Downloading

1. Review the downloaded images
2. Commit them to the repository:
```bash
git add data/google_maps_thumbnails/
git commit -m "Add Google Maps thumbnails"
git push
```

3. Update `gh-pages/site-details.js` to use local thumbnails instead of API calls

### Notes

- The `.env` file is gitignored and will never be committed
- Only the generated images are committed to GitHub Pages
- Your API key stays secure on your local machine
- You can set API restrictions in Google Cloud Console to limit usage to your domain

## apply_brochure_mappings.py

Applies brochure file mappings from `data/brochure_mappings.json` to the main CSV file.

See the main README for usage details.