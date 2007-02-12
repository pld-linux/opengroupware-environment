# TODO:
# - spec filename vs Name
# - proper user/group creation
Summary:	OGo environment
Summary(pl.UTF-8):   Środowisko Ogo
Name:		ogo-environment
Version:	1.0a
Release:	8
License:	LGPL
Group:		Libraries
URL:		http://www.opengroupware.org/
BuildRequires:	rpmbuild(macros) >= 1.202
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires(post):	/bin/hostname
Requires(post):	some-gnustep-stuff (Defaults command)
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Adds the required user and some configurations.

%description -l pl.UTF-8
Ustawienie wymaganych przez OpenGroupware.org zmiennych, użytkowników
i podstawowej konfiguracji.

%prep

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_var}/lib/opengroupware.org/.libFoundation/Defaults
install -d $RPM_BUILD_ROOT%{_var}/lib/opengroupware.org/documents
install -d $RPM_BUILD_ROOT%{_var}/lib/opengroupware.org/news

%clean
rm -rf $RPM_BUILD_ROOT

%pre
if [ "$1" = "1" ]; then
# TODO: register in uid_gid.db.txt and use %%useradd/%%groupadd macros
	/usr/sbin/groupadd shyrix
	/usr/sbin/useradd -c "OpenGroupware.org User" \
		-s /bin/sh -d %{_var}/lib/opengroupware.org -g skyrix ogo
fi

%post
if [ "$1" = "1" ]; then
	cd %{_sysconfdir}
	ln -s %{_var}/lib/opengroupware.org/.libFoundation opengroupware.org
	## some defaults
# add 'su -s /bin/sh' ?
	su - ogo -c "
	Defaults write NSGlobalDomain LSConnectionDictionary '{hostName=localhost; userName=OGo; password=\"\"; port=5432; databaseName=OGo}'
	Defaults write NSGlobalDomain skyrix_id `hostname`
	Defaults write NSGlobalDomain TimeZoneName GMT
	Defaults write NSGlobalDomain WOHttpAllowHost '( localhost, 127.0.0.1, localhost.localdomain)'
	Defaults write nhsd NGBundlePath '%{prefix}/opengroupware.org-1.0a/conduits'
	"
	## XXX: what about remote database?
	if [ -f %{_var}/lib/pgsql/data/pg_hba.conf ]; then
		if [ "`grep -iE '^host.*all.*all.*127.0.0.1.*trust$' %{_var}/lib/pgsql/data/pg_hba.conf`" ]; then
			echo -en "pg_hba.conf seems to be OK.\n"
		else
			echo -en "pg_hba.conf needs to be edited - please refer to our FAQ\n"
		fi
	fi
	if [ -f %{_var}/lib/pgsql/data/postgresql.conf ]; then
		if [ "`grep -iE '^tcpip_socket.*=.*true$' %{_var}/lib/pgsql/data/postgresql.conf`" ]; then
			echo -en "postgresql.conf seems to be OK.\n"
		else
			echo -en "postgresql.conf needs to be edited - please refer to our FAQ\n"
		fi
	fi
fi

%postun
if [ "$1" = "0" ]; then
	%userremove ogo
	%groupremove skyrix
	if [ -h "/etc/opengroupware.org" ]; then
		rm -f /etc/opengroupware.org
	fi
fi

%files
%defattr(644,root,root,755)
%dir %{_var}/lib/opengroupware.org
%dir %attr(700,ogo,skyrix) %{_var}/lib/opengroupware.org/.libFoundation
%dir %attr(700,ogo,skyrix) %{_var}/lib/opengroupware.org/.libFoundation/Defaults
%dir %attr(700,ogo,skyrix) %{_var}/lib/opengroupware.org/documents
%dir %attr(700,ogo,skyrix) %{_var}/lib/opengroupware.org/news
