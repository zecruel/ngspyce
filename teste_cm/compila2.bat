@echo off
rem inicializa as principais variaveis
rem -------------------------------------------------------------
set path=%path%;E:\documentos\prog\mingw\bin
set incl=E:/documentos/prog/python/ngspyce/share/ngspice/include
set cmpp=E:\documentos\prog\python\ngspyce\bin\cmpp.exe
set pasta=%cd%
set link=gcc -m32 -shared dlmain.o

rem Compila o cabecalho do CM
rem -------------------------------------------------------------
cd %pasta%\teste\
%cmpp% -lst

rem Compila cada subdiretorio por meio de subrotina
rem -------------------------------------------------------------
for /d %%g in (*) do (call :subrotina %%g)

rem Compila o template do CM
rem -------------------------------------------------------------
cd ..
gcc -m32 -c -I%incl% -Iteste dlmain.c -o dlmain.o

rem linka tudo numa shared library
rem -------------------------------------------------------------
%link% -o teste.cm

echo ------------  FIM -------------------------------------------
rem -------------------------------------------------------------
pause
goto :eof
rem -------------------------------------------------------------

rem subrotina de compilacao
rem -------------------------------------------------------------
:subrotina
cd %1
echo %1
set link=%link% teste\%1\ifspec.o
set link=%link% teste\%1\cfunc.o
%cmpp% -ifs
%cmpp% -mod
gcc -m32 -c -I%incl% -l%incl% cfunc.c -o cfunc.o
gcc -m32 -c -I%incl% -l%incl% ifspec.c -o ifspec.o
cd ..
goto :eof