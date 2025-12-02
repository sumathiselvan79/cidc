@echo off
echo ========================================================
echo Push to GitHub Helper
echo ========================================================
echo.
echo 1. Go to https://github.com/new
echo 2. Create a new repository (e.g., "pdf-form-filler")
echo 3. Do NOT initialize with README, .gitignore, or License
echo 4. Copy the repository URL (e.g., https://github.com/username/repo.git)
echo.
set /p REPO_URL="Paste your GitHub Repository URL here: "

if "%REPO_URL%"=="" goto error

echo.
echo Adding remote origin...
git remote add origin %REPO_URL%

echo.
echo Renaming branch to main...
git branch -M main

echo.
echo Pushing to GitHub...
git push -u origin main

echo.
echo Done!
pause
exit

:error
echo Error: No URL provided.
pause
