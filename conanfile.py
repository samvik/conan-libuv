#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanException
from find_python import find_python
import os
import platform


class LibuvConan(ConanFile):
    name = "libuv"
    version = "1.15.0"
    description = "Cross-platform asynchronous I/O "
    url = "https://github.com/bincrafters/conan-libuv"
    license = "MIT"
    exports = ["LICENSE.md", "find_python.py"]
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
            if platform.system() == "Windows":
                env_vars = dict()
                if self.settings.compiler == "Visual Studio":
                    env_vars['GYP_MSVS_VERSION'] = {'14': '2015',
                                                    '15': '2017'}.get(str(self.settings.compiler.version))
                with tools.environment_append(env_vars):
                    target_arch = {'x86': 'ia32', 'x86_64': 'x64'}.get(str(self.settings.arch))
                    uv_library = 'shared_library' if self.options.shared else 'static_library'
                    
                    python_bin = find_python("2")
                    self.run('%s gyp_uv.py -f ninja -Dtarget_arch=%s -Duv_library=%s' % (python_bin, target_arch, uv_library))
                    self.run('ninja -C out/%s' % self.settings.build_type)
            else:
                self.run('sh autogen.sh')
                autotools = AutoToolsBuildEnvironment(self)
                
                args=['--disable-static' if self.options.shared else '--disable-shared']
                autotools.configure(args=args)
                
                autotools.make()
                autotools.install()
        

    def package(self):
        if platform.system() == "Windows":
            self.copy(pattern="*.h", dst="include", src=os.path.join(self.root, 'include'))
            bin_dir = os.path.join(self.root, 'out', str(self.settings.build_type))
            if self.settings.os == "Windows":
                if self.options.shared:
                    self.copy(pattern="*.dll", dst="bin", src=bin_dir, keep_path=False)
                self.copy(pattern="*.lib", dst="lib", src=bin_dir, keep_path=False)
            elif str(self.settings.os) in ['Linux', 'Android']:
                if self.options.shared:
                    self.copy(pattern="libuv.so.1", dst="lib", src=os.path.join(bin_dir, "lib"), keep_path=False)
                    lib_dir = os.path.join(self.package_folder, "lib")
                    os.symlink("libuv.so.1", os.path.join(lib_dir, "libuv.so"))
                else:
                    self.copy(pattern="*.a", dst="lib", src=bin_dir, keep_path=False)
            elif str(self.settings.os) in ['Macos', 'iOS', 'watchOS', 'tvOS']:
                if self.options.shared:
                    self.copy(pattern="*.dylib", dst="lib", src=bin_dir, keep_path=False)
                else:
                    self.copy(pattern="*.a", dst="lib", src=bin_dir, keep_path=False)      

    def package_info(self):
        print("Cross compiling: %r" % (tools.cross_building(self.settings)));        
        
        if self.settings.os == "Windows":
            if platform.system() == "Windows":
                self.cpp_info.libs = ['libuv.dll.lib' if self.options.shared else 'libuv']
            else:
                self.cpp_info.libs = tools.collect_libs(self)
            self.cpp_info.libs.extend(["psapi", "ws2_32", "iphlpapi", "userenv"])
        else:
            self.cpp_info.libs = tools.collect_libs(self)
            
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")

