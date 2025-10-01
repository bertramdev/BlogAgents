# Google Sheets Integration Setup Guide

## Overview
BlogAgents can integrate with Google Sheets to:
- Cache style guides to avoid re-analyzing the same blogs
- Store generated content for review and management
- Track blog source performance statistics
- Provide a collaborative workspace for content teams

## Setup Steps

### 1. Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note your project ID

### 2. Enable APIs
1. Go to "APIs & Services" > "Library"
2. Search for and enable:
   - **Google Sheets API**
   - **Google Drive API**

### 3. Create Service Account
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Fill in:
   - **Name**: BlogAgents Service Account
   - **Description**: Service account for BlogAgents Sheets integration
4. Click "Create and Continue"
5. Skip role assignment (click "Continue" then "Done")

### 4. Generate Service Account Key
1. Click on the created service account
2. Go to "Keys" tab
3. Click "Add Key" > "Create New Key"
4. Choose **JSON** format
5. Download and save the JSON file securely

### 5. Create Google Spreadsheet
1. Go to [Google Sheets](https://sheets.google.com)
2. Create a new blank spreadsheet
3. Name it "BlogAgents Data" (or your preferred name)
4. Copy the **Spreadsheet ID** from the URL:
   - URL: `https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit`
   - ID: `1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms`

### 6. Share Spreadsheet with Service Account
1. Open your spreadsheet
2. Click "Share" in the top right
3. Add the service account email (found in your JSON file as `client_email`)
4. Give it **Editor** permissions
5. Uncheck "Notify people" and click "Share"

### 7. Configure BlogAgents
1. Open BlogAgents app
2. Check "Enable Google Sheets storage"
3. Paste the entire contents of your service account JSON file
4. Enter your Spreadsheet ID
5. Click "Test Sheets Connection"

## What Gets Created
The app will automatically create these sheets in your spreadsheet:

### Style_Guides
- Domain, Last_Updated, Tone, Heading_Style, List_Style, Style_Guide_Text, Analysis_Quality

### Generated_Content
- ID, Topic, Source_Blog, Date_Created, Status, Final_Content, SEO_Score, Word_Count, User_Notes

### Blog_Sources
- Domain, Category, Quality_Rating, Last_Analyzed, Success_Count, Notes

## Security Best Practices
- Store service account JSON securely
- Don't share or commit the JSON file to version control
- Use separate projects for development and production
- Regularly rotate service account keys
- Limit spreadsheet sharing to only necessary users

## Troubleshooting

### Connection Failed
- Verify service account email has Editor access to spreadsheet
- Check that both Sheets API and Drive API are enabled
- Ensure JSON is valid (test at jsonlint.com)

### Permission Errors
- Service account needs Editor permissions on the spreadsheet
- Both Google Sheets API and Google Drive API must be enabled

### Rate Limits
- Google Sheets API has a limit of 300 requests per minute
- For high-volume usage, consider implementing request batching

## Benefits
- **Faster generation**: Cached style guides skip re-analysis
- **Content management**: All generated content stored and searchable
- **Team collaboration**: Multiple users can review and edit content
- **Performance tracking**: See which blog sources work best
- **Data persistence**: No data loss when app restarts
- **Export capabilities**: Use Sheets' built-in export features