# PINOUT FOR THE RASPI
#
# (Pin  1) 3V3     is used for all sensors
# (Pin  3) GPIO 2  is used as SDA Motion and BMP280
# (Pin  5) GPIO 3  is used as SCL Motion and BMP280
# (Pin  7) GPIO 4  is used as Serial DHT22
# (Pin  9) GND     is used for all sensors
# (Pin 11) GPIO 17 is used as Binary for Rain
# (Pin 13) GPIO 27 is used as Binary for Light
# (Pin 15) ---
# (Pin 17) 3v3     is used for all Relais-Switches
# (Pin 19) GPIO 10 is used for open Relais
# (Pin 21) GPIO 9  is used for close Relais
# (Pin 23) ---
# (Pin 25) GND     is used for all Relais-Switches
# (Pin 27) ---
# (Pin 29) ---
# (Pin 31) GPIO 6  is used for Binary Bump 1
# (Pin 33) GPIO 13 is used for Binary Bump 2
# (Pin 35) GPIO 29 is used for Binary Bump 3
# (Pin 37) GPIO 26 is used for Binary Bump 4
# (Pin 39) GND


from gpiozero import OutputDevice, Button
from signal import pause
from sys import argv, exit
from time import sleep


def main():
    def print_bumps():
        print(bump_1.value, bump_2.value, bump_3.value, bump_4.value)

    bump_1 = Button(6)
    bump_2 = Button(13)
    bump_3 = Button(19)
    bump_4 = Button(26)

    if argv[1].lower() == "open":
        active_bumps = (bump_1, bump_2)
        relais = OutputDevice(10, initial_value=True)

    elif argv[1].lower() == "close":
        active_bumps = (bump_3, bump_4)
        relais = OutputDevice(9, initial_value=True)

    else:
        print(f"Unintelligible nonsense >> {" ".join(argv)}")

    if not any([bump.is_pressed for bump in active_bumps]):
        print(relais.value)
        # sleep(0.2)
        relais.value = 0

        while not bump_1.value and not bump_2.value:
            sleep(0.1)

        relais.value = 1
        # sleep(0.2)
        relais.close

    else:
        print("Bump sensors are activated")
        print_bumps()

    print("Bump sensor(s) activated. Shutting down motor")
    print_bumps()

    bump_1.close()
    bump_2.close()
    bump_3.close()
    bump_4.close()


if __name__ == "__main__":
    main()
