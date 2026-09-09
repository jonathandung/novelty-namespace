@echo off
pushd %~dp0
if "%SPHINXBUILD%" == "" set SPHINXBUILD=sphinx-build
if "%1" == "" %SPHINXBUILD% -M help source build %SPHINXOPTS% %O%
%SPHINXBUILD% >nul 2>nul
if errorlevel 9009 (
	echo.Command 'sphinx-build' not found. Make sure you have Sphinx installed,
	echo.then set the SPHINXBUILD environment variable to point to the full path
	echo.of the 'sphinx-build' executable. Alternatively you may add the Sphinx
	echo.directory to PATH.
	echo.
	echo.If you don't have Sphinx installed, visit
    echo.https://www.sphinx-doc.org/en/master/usage/installation.html.
	exit /b 1
)
%SPHINXBUILD% -M %1 source build %SPHINXOPTS% %O%
popd
