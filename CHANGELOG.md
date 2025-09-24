# Changelog

All notable changes to the ThomasNet JSON Scraper project will be documented in this file.



## [1.1.0] - 2025-09-24

### Added
- Interactive login verification system with `check` and `done` commands
- Progress saving functionality that creates temporary CSV files after each page
- Enhanced error reporting that shows lead count before failures
- Safe browser cleanup with connection error handling
- `save_leads_to_csv()` helper function for reliable data persistence

### Fixed
- **Critical**: CSV files now preserve all scraped leads even when script crashes or times out
- Login detection timing optimized (60 seconds during manual login, 2 seconds for regular checks)
- Browser connection timeout errors during script termination
- Data loss when HTTP connection errors occur during scraping
- Login verification process now gives adequate time for manual authentication

### Changed
- Moved leads list initialization outside try block to ensure accessibility during error handling
- Improved error handling in main execution flow
- Enhanced login detection with additional checks for login page indicators
- Better user feedback during login verification process

### Technical Details
- Login verification attempts increased from 3 to 5 with longer wait times
- Added fallback error handling for `driver.quit()` operations
- Implemented automatic progress checkpoints every 25 leads (1 page)
- Enhanced `is_logged_in()` function with parameterized wait times

## [1.0.0] - 2025-09-20

### Added
- Initial release of ThomasNet JSON Scraper
- Basic scraping functionality for ThomasNet supplier search results
- Duplicate detection using previous CSV data
- Manual login handling for ThomasNet authentication
- Chrome profile management with separate Selenium profile
- CSV export with customizable columns
- JSON hash-based page change detection
- Automatic pagination support
- Random delay implementation for rate limiting

### Features
- Scrapes company name, address, and phone number
- Supports any ThomasNet supplier search URL
- Avoids duplicate leads across multiple runs
- Timestamped CSV output files
- Configurable maximum lead limits
- Chrome browser automation with anti-detection measures