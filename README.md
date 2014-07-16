go-build
========

Build scripts for Ethereum Go.

### OS X
Install all build dependencies.

* brew install go gmp readline
* npm install -g appdmg
* go get -u github.com/ethereum/go-ethereum/ethereal
* Open build.py and edit the (macdeployqt) paths.
* [Download the dmg-background images](https://dl.dropboxusercontent.com/u/374/Ethereum/ethereal-images.zip). (Not added to Git because of filesize)
* python build.py

If everything went ok you should now have a Ethereal.dmg file in your current folder.

### Windows

Install all build dependencies.

* Golang, 1.2 or higher 32bit
* Install Git and Mercurial
* Mingw32
* Use mingw32-get to install gmp packages
* Install QT5-mingw32 (5.2.1 at the moment of writing)
* Add mingw32 to PATH
* Install pkg-config somewhere in your PATH, you can find the executable with needed DLLs on the web or install GTK, it comes bundled with it.
* NSIS

After all these things have been satisfied do a go get -u github.com/ethereum/go-ethereum/ethereal.

Once the compilation is completed you can create a setup binary. Edit build.bat and change qtPath and mingwPath to the paths of your installed versions. After right-click the nsi file and select "Compile NSIS Script". If everything went well you should now have a windows-setup file.


#### Gotcha's

Now it will be a miracle if the windows build works in one go. So here are some things that can go wrong

*Problem*
```
qopenglversionfunctions.h:785:43: error: expected unqualified-id before ')' token
     void (QOPENGLF_APIENTRYP MemoryBarrier)(GLbitfield barriers);
```

See [this ticket](https://github.com/go-qml/qml/issues/56) for a couple of solutions.

*Problem*
pkg-config might whine about the config path. Setup an environment value `PKG_CONFIG_PATH` and set it to `C:\Qt\Qt5.2.1\5.2.1\mingw48_32\lib\pkgconfig`. Adopted to your QT version.

If there are any build problems please create an issue because I have four A4's full of scribbled notes of other problems. :)
