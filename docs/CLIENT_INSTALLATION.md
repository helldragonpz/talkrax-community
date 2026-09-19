# Install and use Talkrax

Always use [official downloads](https://talkrax.com/downloads). The page reads
the real release manifest; platform builds can have different release numbers.

## Linux installer
For an x86-64 Ubuntu desktop or a compatible Debian-package system:

1. Download the file ending in `linux-x64.deb`.
2. Open it with your desktop's software/package installer and choose **Install**.
3. Launch **Talkrax** from the application menu as your normal desktop user.
4. Register or sign in. Finish email verification if the server requires it.
5. Open Settings, choose your microphone, camera and speakers, and test them.

The package installs application files under `/opt/talkrax`, adds the application
menu entry and declares its native library dependencies. The desktop supplies
the audio service, secure keyring and screen-cast portal. It does not need
administrator privileges to run.

Build 35 was checked with a clean Ubuntu 22.04 package installation. Other
distributions and physical devices still need testing. A `.deb` is not a Fedora,
Arch, Flatpak or Snap package.

To update, download and open the newer installer. Existing account data is
preserved. To uninstall, remove Talkrax in your software manager; removing the
package does not erase your personal account data or remote account.

## Linux portable archive
Download the `linux-x64.tar.gz` archive, extract the entire directory and open
`Talkrax`. Keep `lib` and `data` beside the executable. Use your normal desktop
session. The archive does not install missing runtime libraries or menu entries.

## Windows
The currently published Windows release is a portable ZIP. Extract the entire
archive, then open `Talkrax.exe`. Keep all DLLs and the `data` directory beside it.
Do not copy only the executable. A guided installer is in preparation; it is not
yet a downloadable verified release.

Allow microphone/camera access for desktop apps in Windows privacy settings
when you want to use those devices. A system privacy setting and a device
selected inside Talkrax are separate controls.

## Connect to another server
Linux build 34 and later include **Change server** on the sign-in page.
The new Windows implementation is not part of the older public Windows build.

1. Obtain the HTTPS server address from its operator.
2. Select **Change server**, enter the address and choose **Review server**.
3. Read the returned operator identity and policy links.
4. Choose **Use server**, then register or sign in on that server.

Accounts and stored sessions are separate for each server origin. Selecting an
independent server does not transfer your official account, messages, purchases
or tokens. An operator's statement is not a Talkrax endorsement.

A compatible independently deployed server is required; this repository does
not yet provide an accepted public server package.

## Media troubleshooting
Build 35 fixes an upstream regression that returned no native audio devices.
A microphone or camera that is absent, disconnected, in use elsewhere or denied
by system policy can still be unavailable.

Linux audio requires a working desktop PulseAudio endpoint, including
PipeWire's PulseAudio compatibility service. Wayland screen sharing also depends
on the desktop portal and its consent picker. The release test received real
screen frames on X11; it did not establish Wayland or external-network acceptance.

Refresh the device list after reconnecting a device. Camera and microphone
tests use the selected device. A server can separately restrict screen sharing,
video or publishing permissions.

## File verification
The [release manifest](https://talkrax.com/releases/release-manifest.json) lists
each file's exact name, size, version and SHA-256 digest. Checksums detect changed
or incomplete files; they do not replace a trusted download source or operating
system signature verification.
