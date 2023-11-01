# empty debuginfo
%global debug_package %nil
%global lz4_version 1.9.2

Name:          lz4-java
Version:       1.7.1
Release:       14%{?dist}
Summary:       LZ4 compression for Java
# GPL:
# src/lz4/
# BSD:
# src/lz4/libs
License:       ASL 2.0 and (BSD and GPLv2+)
# GPLv2+ and BSD for lz4 and xxhash libs that are shared in liblz4-java.so
URL:           https://github.com/lz4/lz4-java
Source0:       https://github.com/lz4/lz4-java/archive/%{version}.tar.gz
Source1:       https://github.com/lz4/lz4/archive/v%{lz4_version}.tar.gz

# lz4-java v1.3.0 introduced usage of sun.misc.Unsafe, which would later become
# depricated in jdk 9 and kept as an unexposed API in later jdk releases.
# lz4-java optionally uses Unsafe to achieve faster compression and decompression,
# however it's implementation is not critical to functionality, and can be removed.
Patch0:        0-remove-unsafe.patch
# After updating mvel to version 2.4.10, MVEL generated classes have formatting issues where
# code after comments are not being formatted with new lines. As a result, including comments
# in the templates results in classes with invalid code following the first comment.
# This patch simply removes comments from the templates so the classes can be generated as expected.
# Related bug: https://github.com/mvel/mvel/issues/152
Patch1:        1-remove-comments-from-templates.patch
# Adds a simple makefile to be run in-place of the cpptasks in the build.xml
Patch2:        2-remove-cpptasks.patch
# some lz4-java tests require randomizedtesting, which is not currently
# shipped or maintained in Fedora; remove those and use system ant-junit to run applicable tests
Patch3:        3-remove-randomizedtesting-tests.patch
# RHSCL: condition doesn't support the nested "javaversion" element
Patch4:        4-remove-javaversion.patch
# RHSCL: build missing lz4 and xxhash libs required for liblz4-java.so
Patch5:        5-build-libs.patch

ExclusiveArch: x86_64

# Build tools
BuildRequires: apache-parent
BuildRequires: ant
BuildRequires: ant-junit
BuildRequires: aqute-bnd
BuildRequires: gcc
BuildRequires: ivy-local
BuildRequires: java-devel
BuildRequires: javapackages-local
BuildRequires: lz4
BuildRequires: mvel
BuildRequires: objectweb-asm
BuildRequires: xerces-j2

Provides: bundled(xxhash) = r37
Provides: bundled(lz4) = 1.9.2

%description
LZ4 compression for Java, based on Yann Collet's work.
This library provides access to two compression methods
that both generate a valid LZ4 stream:

* fast scan (LZ4):
    ° low memory footprint (~ 16 KB),
    ° very fast (fast scan with skipping heuristics in case the
      input looks incompressible),
    ° reasonable compression ratio (depending on the
      redundancy of the input).
* high compression (LZ4 HC):
    ° medium memory footprint (~ 256 KB),
    ° rather slow (~ 10 times slower than LZ4),
    ° good compression ratio (depending on the size and
      the redundancy of the input).

The streams produced by those 2 compression algorithms use the
same compression format, are very fast to decompress and can be
decompressed by the same decompressor instance.

%package javadoc
Summary:       Javadoc for %{name}
BuildArch:     noarch

%description javadoc
This package contains javadoc for %{name}.

%prep
%setup -q -n %{name}-%{version}
%setup -q -T -D -a 1 -n %{name}-%{version}

mv lz4-1.9.2/* src/lz4/

%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1

# Cleanup
find -name '*.dylib' -print -delete
find -name '*.so' -print -delete

%build
    export JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk

ant -Divy.mode=local -Divy.revision=1.7.1 -Divy.pom.version=1.7.1 jar test docs makepom
bnd wrap -p lz4-java.bnd -o dist/lz4-java-%{version}.jar --version %{version} dist/lz4-java.jar

%install
%mvn_artifact dist/lz4-java-%{version}.pom dist/lz4-java-%{version}.jar
%mvn_install -J build/docs

%files -f .mfiles
%doc CHANGES.md README.md

%files javadoc -f .mfiles-javadoc
%license LICENSE.txt

%changelog
* Fri Feb 19 2021 Alex Macdonald <almacdon@redhat.com> 1.7.1-14
- Add ExclusiveArch: x86_64

* Wed Feb 17 2021 Alex Macdonald <almacdon@redhat.com> 1.7.1-13
- Bundle missing xxhash and lz4 components & adjust local Makefile

* Wed Jan 13 2021 Alex Macdonald <almacdon@redhat.com> 1.7.1-12
- remove hardcoded lib directory in the Makefile

* Fri Jan 08 2021 Alex Macdonald <almacdon@redhat.com> 1.7.1-11
- remove hardcoded "amd64" directory path in the Makefile

* Wed Dec 09 2020 Alex Macdonald <almacdon@redhat.com> 1.7.1-10
- remove BuildArch: noarch

* Tue Dec 01 2020 Alex Macdonald <almacdon@redhat.com> 1.7.1-9
- run unit tests on classes that do not require randomizedtesting
- add liblz4-java.so generation step to Makefile
- remove mvn_file macro for lz4

* Thu Nov 19 2020 Alex Macdonald <almacdon@redhat.com> 1.7.1-8
- remove dependency on cpptasks

* Mon Nov 16 2020 Alex Macdonald <almacdon@redhat.com> 1.7.1-7
- cleanup whitespace in the local patch to remove comments from templates
- use system lz4 and xxhash instead of bundling the dependencies

* Tue Oct 06 2020 Alex Macdonald <almacdon@redhat.com> 1.7.1-6
- include patch to strip comments from mvel templates

* Tue Sep 15 2020 Alex Macdonald <almacdon@redhat.com> 1.7.1-5
- add "BuildArch: noarch" to fix rpmlint error: no-binary

* Wed Sep 09 2020 Alex Macdonald <almacdon@redhat.com> 1.7.1-4
- fixed sources to have both lz4-java and lz4

* Wed Aug 05 2020 Alex Macdonald <almacdon@redhat.com> 1.7.1-3
- used commit from Jie Kang's fork of lz4-java to update to upstream 1.7.1
- this prevents tests from running; eliminates the need for randomizedtesting for f33 onward
- remove dependency on bea-stax
- remove all usage of sun.misc.Unsafe

* Tue Aug 04 2020 Alex Macdonald <almacdon@redhat.com> 1.7.1-2
- Included the lz4 submodule inside the lz4-java source tarball

* Thu Jul 30 2020 Alex Macdonald <almacdon@redhat.com> 1.7.1-1
- Update to version 1.7.1

* Wed Jan 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.3.0-13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Wed Jul 24 2019 Fabio Valentini <decathorpe@gmail.com> - 1.3.0-12
- Add BuildRequires: gcc to fix FTBFS issue.

* Fri Feb 01 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.3.0-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.3.0-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Thu Feb 08 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.3.0-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.3.0-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.3.0-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Sun Feb 19 2017 gil cattaneo <puntogil@libero.it> 1.3.0-6
- disable test suite on ppc64

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.3.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Mon Sep 12 2016 gil cattaneo <puntogil@libero.it> 1.3.0-4
- exclude aarch64

* Tue May 03 2016 gil cattaneo <puntogil@libero.it> 1.3.0-3
- fix test suite

* Tue May 03 2016 gil cattaneo <puntogil@libero.it> 1.3.0-2
- unbundle lz4 code (lz4-java issues#74)

* Mon Jul 20 2015 gil cattaneo <puntogil@libero.it> 1.3.0-1
- initial rpm
