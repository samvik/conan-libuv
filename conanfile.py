#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanException


class LibuvConan(ConanFile):
    name = "libuv"
    version = "1.15.0"
    description = "Cross-platform asynchronous I/O "
    url = "https://github.com/bincrafters/conan-libuv"
    license = "MIT"
    exports = ["LICENSE.md"]
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    root = name + "-" + version

    def configure(self):
        del self.settings.compiler.libcxx
        if self.settings.compiler == "Visual Studio" and int(str(self.settings.compiler.version)) < 14:
            raise ConanException("Visual Studio >= 14 (2015) is required")

    def source(self):
        source_url = "https://github.com/libuv/libuv"
        tools.get("{0}/archive/v{1}.tar.gz".format(source_url, self.version))

    def build(self):
        with tools.chdir(self.root):
            self.run('sh autogen.sh')
            autotools = AutoToolsBuildEnvironment(self)
            
            args=['--disable-static' if self.options.shared else '--disable-shared']
            autotools.configure(args=args)
            
            autotools.make()
            autotools.install()

    def package(self):
        self.run('tree ' + self.package_folder)

    def package_info(self):
        if self.settings.os == "Windows":
            self.cpp_info.libs = ['libuv.dll.lib' if self.options.shared else 'libuv']
            self.cpp_info.libs.extend(["Psapi", "Ws2_32", "Iphlpapi", "Userenv"])
        else:
            self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")
