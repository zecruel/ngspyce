set path=%path%;E:\documentos\prog\mingw\bin
set incl=E:/documentos/prog/python/ngspyce/share/ngspice/include
set cmpp=E:\documentos\prog\python\ngspyce\bin\cmpp.exe
set pasta=%cd%

cd %pasta%\teste\
%cmpp% -lst

cd %pasta%\teste\rms\
%cmpp% -ifs
%cmpp% -mod

cd %pasta%\teste\sma\
%cmpp% -ifs
%cmpp% -mod

cd %pasta%\teste\vi_pq\
%cmpp% -ifs
%cmpp% -mod

cd %pasta%\teste\pfc\
%cmpp% -ifs
%cmpp% -mod

cd %pasta%\teste\scr\
%cmpp% -ifs
%cmpp% -mod

cd %pasta%\teste\rms\
gcc -m32 -c -I%incl% -l%incl% cfunc.c -o cfunc.o
gcc -m32 -c -I%incl% -l%incl% ifspec.c -o ifspec.o


cd %pasta%\teste\sma\
gcc -m32 -c -I%incl% -l%incl% cfunc.c -o cfunc.o
gcc -m32 -c -I%incl% -l%incl% ifspec.c -o ifspec.o

cd %pasta%\teste\vi_pq\
gcc -m32 -c -I%incl% -l%incl% cfunc.c -o cfunc.o
gcc -m32 -c -I%incl% -l%incl% ifspec.c -o ifspec.o

cd %pasta%\teste\pfc\
gcc -m32 -c -I%incl% -l%incl% cfunc.c -o cfunc.o
gcc -m32 -c -I%incl% -l%incl% ifspec.c -o ifspec.o

cd %pasta%\teste\scr\
gcc -m32 -c -I%incl% -l%incl% cfunc.c -o cfunc.o
gcc -m32 -c -I%incl% -l%incl% ifspec.c -o ifspec.o

cd %pasta%
gcc -m32 -c -I%incl% -Iteste dlmain.c -o dlmain.o

gcc -m32 -shared dlmain.o teste\rms\ifspec.o teste\rms\cfunc.o teste\sma\ifspec.o teste\sma\cfunc.o teste\vi_pq\ifspec.o teste\vi_pq\cfunc.o teste\pfc\ifspec.o teste\pfc\cfunc.o teste\scr\ifspec.o teste\scr\cfunc.o -o teste.cm
pause