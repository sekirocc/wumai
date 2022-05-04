%define name wumai

Summary: wumai
Name: %{name}
Version: %{version}
Release: %{release}
License: MIT
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: nickelchen0101@gmail.com <UNKNOWN>
Url: http://wumai.com
Source0: %{name}-%{version}.tar.gz

Requires: python2-oslo-utils >= 3.7.0, python-six >= 1.9.0, python2-oslo-config >= 2:3.9.0
Requires: python-flask = 1:0.10.1, python-sqlalchemy = 1.0.11
Requires: python-redis = 2.10.3, python-jsonschema = 2.3.0, python2-PyMySQL = 0.6.7

%description
UNKNOWN

%prep
%setup -n %{name}-%{version} -n %{name}-%{version}

%build
python setup.py build

%install
python setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%pre

%post

%preun

%files -f INSTALLED_FILES
%defattr(-,root,root)
