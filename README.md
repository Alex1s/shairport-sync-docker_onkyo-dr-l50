# shairport-sync-docker_onkyo-dr-l50

## Set up the Raspberry Pi
Our goal is to turn the DR-L50 on and off by sending the respecitive IR signals directly to the IR receive wire of the DR-L50. This way we want to avoid the countless error sources in IR transmission.
First we will need to prepair the Raspberry Pi to send IR signals via one of its pins.
For this we make sure that we load the `gpio-ir-tx` overlay by e.g. making sure a line like `dtoverlay=gpio-ir-tx`is found in
the `/boot/config.txt` file and is not commented out by a `#` character. If you just added this line make sure you reboot the pi for the changes to take effect.
For more information about the overlay take a look [here](https://github.com/raspberrypi/firmware/blob/3a232374735c2bc5b7188ba2dfc0cbba8fa30d97/boot/overlays/README#L1279). (This may be outdated at the time you are reading this. So check at the master branch [here](https://github.com/raspberrypi/firmware/blob/master/boot/overlays/README) for the latest documentation of the `gpio-ir-tx` overlay.)
The default pin used for transmission is `18`. You can also use a different pin. For example if you want to use pin `26`change the line in the `/boot/config.txt` to `dtoverlay=gpio-ir-tx,gpio_pin=26`.

Once you rebooted the system a character device named `/dev/lirc0` should appear in your filesystem. To send commands we use the `ir-ctl` command from the ` v4l-utils` package which is pre-installed on all Raspberry Pi OS images as of (08.01.2023). We now run `ir-ctl --scancode=necx:0xD26D04` to send a `necx` message with the scancode `0xD26D04`. See the table below for a list of scancodes relevant for this project.

### Proper arguments for ir-ctl
Important is that we do not modulate our output signal. The IC of the DR-L50 expectes a de-modulated signal! De-modulation is performed by the IR receiver before it is passed to the receivers logic IC. `ir-ctl` offers an argument `--carrier` or short `-c`. This needs to be set zero, so that the output signal is not modulated. In case you get a an error when trying to set the carrier argument to zero i.e. you run `ir-ctl --carrier=0 --scancode=necx:0xD26D04` and get the following output:
```
ir-ctl: cannot parse carrier `0'
Try `ir-ctl --help' or `ir-ctl --usage' for more information.
```
Update your `ir-ctl` binary by updating the `v4l-utils` package. You may need to upgrade Raspbian / Raspberry Pi OS. Old repos only contain the old version of the `v4l-package`. You can check yur `ir-ctl` verion by running `ir-ctl --version`. In my case the version `IR raw version 1.16.3` caused the error when setting `carrier` to zero but when compiling from the latest sources I had version `IR ctl version 1.23.0` and this version did not produce the error.

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
What is the reason? Something related to legacy devices? Or a mistake on my side? We will see ...

## Repeating commands
While the NEC IR standard does specifiy a repeat code to efficiently repeat messages, the remote of the DR-L50 does not use them. It just re-transmitts the entire message. Is it thinkable that the IR remote does not use repeat codes but the receiver does indeed support them?

In any case, the remote space two messages 38.8ms appart. It might be worthwhile to check if a shorter space is still accepted by the receiver.