noobplatinum@noobplatinum-IdeaPad-Pro-5-14IAH10:~$ uname -a
Linux noobplatinum-IdeaPad-Pro-5-14IAH10 6.14.0-37-generic #37~24.04.1-Ubuntu SMP PREEMPT_DYNAMIC Thu Nov 20 10:25:38 UTC 2 x86_64 x86_64 x86_64 GNU/Linux
noobplatinum@noobplatinum-IdeaPad-Pro-5-14IAH10:~$ lscpu | head
Architecture:                            x86_64
CPU op-mode(s):                          32-bit, 64-bit
Address sizes:                           42 bits physical, 48 bits virtual
Byte Order:                              Little Endian
CPU(s):                                  16
On-line CPU(s) list:                     0-15
Vendor ID:                               GenuineIntel
Model name:                              Intel(R) Core(TM) Ultra 7 255H
CPU family:                              6
Model:                                   197
noobplatinum@noobplatinum-IdeaPad-Pro-5-14IAH10:~$ ls -la /sys/class/powercap/
total 0
drwxr-xr-x  2 root root 0 Jan 20 15:37 .
drwxr-xr-x 87 root root 0 Jan 20 12:53 ..
lrwxrwxrwx  1 root root 0 Jan 20 12:53 intel-rapl -> ../../devices/virtual/powercap/intel-rapl
lrwxrwxrwx  1 root root 0 Jan 20 12:53 intel-rapl:0 -> ../../devices/virtual/powercap/intel-rapl/intel-rapl:0
lrwxrwxrwx  1 root root 0 Jan 20 12:53 intel-rapl:0:0 -> ../../devices/virtual/powercap/intel-rapl/intel-rapl:0/intel-rapl:0:0
lrwxrwxrwx  1 root root 0 Jan 20 12:53 intel-rapl:1 -> ../../devices/virtual/powercap/intel-rapl/intel-rapl:1
lrwxrwxrwx  1 root root 0 Jan 20 12:53 intel-rapl-mmio -> ../../devices/virtual/powercap/intel-rapl-mmio
lrwxrwxrwx  1 root root 0 Jan 20 12:53 intel-rapl-mmio:0 -> ../../devices/virtual/powercap/intel-rapl-mmio/intel-rapl-mmio:0
noobplatinum@noobplatinum-IdeaPad-Pro-5-14IAH10:~$ docker version
Client: Docker Engine - Community
 Version:           29.1.5
 API version:       1.52
 Go version:        go1.25.6
 Git commit:        0e6fee6
 Built:             Fri Jan 16 12:48:47 2026
 OS/Arch:           linux/amd64
 Context:           default

Server: Docker Engine - Community
 Engine:
  Version:          29.1.5
  API version:      1.52 (minimum version 1.44)
  Go version:       go1.25.6
  Git commit:       3b01d64
  Built:            Fri Jan 16 12:48:47 2026
  OS/Arch:          linux/amd64
  Experimental:     false
 containerd:
  Version:          v2.2.1
  GitCommit:        dea7da592f5d1d2b7755e3a161be07f43fad8f75
 runc:
  Version:          1.3.4
  GitCommit:        v1.3.4-0-gd6d73eb8
 docker-init:
  Version:          0.19.0
  GitCommit:        de40ad0
noobplatinum@noobplatinum-IdeaPad-Pro-5-14IAH10:~$ docker image inspect hubblo/scaphandre --format '
> {{.Id}}'

sha256:d4fb656bfee214440c6745cf2fef040b8e88bbdd3df61c4165df01732acffee4