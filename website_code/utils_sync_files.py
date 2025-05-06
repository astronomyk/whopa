# seestar_sync.py

from utils_seestar_data_access import crawl_seestar, get_targets_with_recent_fits, sync_fits_files_to_local

ARCHIVE_PATH = "/media/ingo/archive"
HOURS_LOOKBACK = 2  # Sync only files from the last 6 hours

def main():
    print("🔍 Crawling Seestar share...")
    crawl_data = crawl_seestar()
    if not crawl_data:
        print("⚠️  No data returned from crawl.")
        return

    recent_targets = get_targets_with_recent_fits(crawl_data, hours=HOURS_LOOKBACK)
    if not recent_targets:
        print("✅ No new targets with recent FITS files.")
        return

    filtered = {name: crawl_data[name] for name in recent_targets}
    print(f"📁 Syncing: {', '.join(filtered.keys())}")
    sync_fits_files_to_local(filtered, ARCHIVE_PATH)

if __name__ == "__main__":
    main()
