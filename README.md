# shairport-sync-docker_onkyo-dr-l50

## Set up the Raspberry Pi
Our goal is to turn the DR-L50 on and off by sending the respecitive IR signals directly to the IR receive wire of the DR-L50. This way we want to avoid the countless error sources in IR transmission.
First we will need to prepair the Raspberry Pi to send IR signals via one of its pins.
For this we make sure that we load the `gpio-ir-tx` overlay by e.g. making sure a line like `dtoverlay=gpio-ir-tx`is found in
the `/boot/config.txt` file and is not commented out by a `#` character. If you just added this line make sure you reboot the pi for the changes to take effect.
For more information about the overlay take a look [here](https://github.com/raspberrypi/firmware/blob/3a232374735c2bc5b7188ba2dfc0cbba8fa30d97/boot/overlays/README#L1279). (This may be outdated at the time you are reading this. So check at the master branch [here](https://github.com/raspberrypi/firmware/blob/master/boot/overlays/README) for the latest documentation of the `gpio-ir-tx` overlay.)
The default pin used for transmission is `18`. You can also use a different pin. For example if you want to use pin `26`change the line in the `/boot/config.txt` to `dtoverlay=gpio-ir-tx,gpio_pin=26`.

Once you rebooted the system a character device named `/dev/lirc0` should appear in your filesystem. To send commands we use the `ir-ctl` command from the ` v4l-utils` package which is pre-installed on all Raspberry Pi OS images as of (08.01.2023). We now run `ir-ctl --scancode=necx:0xD26D04` to send a `necx` message with the scancode `0xD26D04`. See the table below for a list of scancodes relevant for this project.

### Sending unmodulated IR signals
Important is that we do not modulate our output signal. The IC of the DR-L50 expectes a de-modulated signal! De-modulation is performed by the IR receiver before it is passed to the receivers logic IC. `ir-ctl` offers an argument `--carrier` or short `-c`.
Now you maybe think, we could simple add the `--carrier=0` to the `ir-ctl` command to get an unmodulated signal. But of course that would be way to easy.
You will get a modulated signal at around 38kHz, just as the NEC [specifications](https://techdocs.altium.com/display/FPGA/NEC%2bInfrared%2bTransmission%2bProtocol) demands it. No matter what you carrier frequency you specify. Why? Take a look at [this](https://github.com/torvalds/linux/blob/e8f60cd7db24f94f2dbed6bec30dd16a68fc0828/drivers/media/rc/lirc_dev.c#L290) if-statement.

Okay, so what do we do now? We will have to convert our scancodes to pulses and spaces, save them to a file and then we can use the `--send` or short `-s` option to send these pulses / spaces. Now the kernel will not overwrite our `--carrier` option.
Do not worry, you will not have to do this by hand. Take a look at the `necx_scancode_to_mode2.py` file in this repo. It takes a scancode as positional argument and outputs corresponding [mode2](https://www.lirc.org/html/mode2.html) file to stdout. Here an example how we can finally send an unmodulated signal:
```
/necx_scancode_to_mode2.py 0xD26D04 > mode.txt
ir-ctl --carrier=0 --send mode.txt
```
If you are too lazy for that use the files I already generated. You can find them in the `mode2` directory. This directory contains files for `power_on`, `power_off`, `volume_up` and `volume_down`.



#### Getting an error when setting `--carrier` to zero?
In case you get a an error when trying to set the carrier argument to zero i.e. you run `ir-ctl --carrier=0 --scancode=necx:0xD26D04` and get the following output:
```
ir-ctl: cannot parse carrier `0'
Try `ir-ctl --help' or `ir-ctl --usage' for more information.
```
Update your `ir-ctl` binary by updating the `v4l-utils` package. You may need to upgrade Raspbian / Raspberry Pi OS. Old repos only contain the old version of the `v4l-package`. You can check yur `ir-ctl` version by running `ir-ctl --version`. In my case the version `IR raw version 1.16.3` produced the error above when setting `carrier` to zero but when upgrading to the latest Rasperry Pi OS I had version `IR ctl version 1.20.0` and this version did not produce the error.

## Relevant decoded commands and other facts about the IR protocol
## Decoded commands
The remote for the receiver uses the NECX protocl.
Thus `ADDRESS#` is NOT required to be the bit-inverted of `ADDRESS` but `COMMAND#` IS required to be the bit inverted of `COMMAND`.
Thus the scancode is 3 bytes wide.

| KEY         | ADDRESS     | ADDRESS# | COMMAND | COMMAND# | Scancode (NECX) |
|--------------|-----------|------------|------------|------------|------------|
| POWER_ON | 0xD2 | 0x6D | 0x04 | 0xFB | 0xD26D04 |
| POWER_OFF | 0xD2 | 0x6C | 0x47 | 0xB8 | 0xD26C47 |
| VOLUME_UP | 0xD2 | 0x6D | 0x02 | 0xFD | 0xD26D02 |
| VOLUME_DOWN | 0xD2 | 0x6D | 0x03 | 0xFC | 0xD26D03 |

Interesting to observe here is that the POWER_OFF key has a slightly different address (a single bit is flipped) than the other three keys.
What is the reason? Something related to legacy devices? In any case it is not a mistake on my side as I tested these scancodes and they work.

## Repeating commands
While the NEC IR standard does specifiy a repeat code to efficiently repeat messages, the remote of the DR-L50 does not use them. It just re-transmitts the entire message. Is it thinkable that the IR remote does not use repeat codes but the receiver does indeed support them? Yes, it is thinkable. But no, it is not reality. The receiver does not support repeat codes. At least following repeat code did not work:
```
space 40000
pulse 9000
space 2250
pulse 56
```

Additionally the remote spaces two messages 38.8ms appart. It might be worthwhile to check if a shorter space is still accepted by the receiver.
It turns out it is not. Actually during my experiments it appears to be the case that for reliable transmission the space needs to be even greater!
I did experiment the following way:

1. Turn the volume to zero by hand
2. Run following command `ir-ctl --gap <insert gap to test here> --send volume_up.mode2 --send volume_up.mode2 --send volume_up.mode2 <... repeat the "send" argument so that the command is sent 80 times in total>` 
3. Check that the volume did indeed increase to MAX (80)

I repeated step 2. and 3. 5 times. What I can tell you is that a gap of 65ms did not work reliable in that experiment and a gap of 70ms did work reliable. But do consider that `n = 5` is not a strong argument in statistics. 

## Avoiding problems with mDNS
When running `shairport-sync` in docker using network mode `host` you might notice following message in the container logs:

```*** WARNING: Detected another IPv4 mDNS stack running on this host. This makes mDNS unreliable and is thus not recommended. ***```

This mDNS stack shairport-sync is talking about is avahi-daemon running in the background per default on the Raspberry Pi OS. Disable it using following command:
```systemctl disable avahi-daemon.service```
