#!/usr/bin/env python3
"""
    read a wav file and convert it into a series of
    high/low time values as a representation for beat lengths.
    Once that information is extracted create an html file to vibrate to that pattern
"""
import argparse
import soundfile as sf


def convert_wav(wav_filename):
    """

    :param wav_file: a string representation of the path to a wav file for conversion
    :return pulses: an array containing alternating pulse values for vibrations in seconds
    """

    # use soundfile.read to get the sample rate and data values from a wav file
    data, sample_rate = sf.read(wav_filename, dtype='float32')

    # set up constants to use when sorting the data by high and low pulse trains
    pulses = []
    i = 0
    # because the sample rate is the amount of sample per second we
    # will set the range of data that we average to 1 millisecond's worth of samples
    # or 1 / 100 seconds
    avg_range = int(sample_rate / 100)
    active = False

    # create pulses for the entirety of the data length
    while i < len(data):
        # by using a bool that changes every time a high or low pulse train is completed
        # we can ensure the program won't get caught in a loop of constantly trying to
        # get into the high or low pulse train loops and breaking
        if active:
            # reset some variables that will be used for the duration of the loop
            avg_value = 0
            timer = 0
            while True:
                # add a failsafe in case the loop isn't broken before hitting the end of the data
                if i == len(data):
                    break

                # take a chunk of data pieces and average them as sound files will have many high/low shifts
                # but for a vibration pulse train we are more interested in the overall average high or low
                # values for multiple milliseconds
                for x in range(avg_range):
                    try:
                        avg_value += abs(data[i+x][0])
                    except IndexError:
                        avg_range = x
                        break
                avg_value /= avg_range

                # based on manual review of the audio graph it was determined that at an amplitude of about 0.05
                # the audio samples hit what would be the "audible" level or the equivalency of a beat
                # if the average of a millisecond falls below this when finding the length of a high pulse
                # break the loop and switch to finding the length of a low pulse, otherwise add to the timer
                # and overall data found and continue
                if abs(avg_value) < 0.05:
                    break
                else:
                    timer += avg_range
                    i += avg_range

            # once the loop is broken to switch to finding a low pulse add the length
            # of time for the high to an array
            pulses.append(int((timer / sample_rate)*1000))
            active = False

        elif not active:

            # the same thing happens here as what would happen in the loop to find the high pulse time
            # except to find low pulse time
            avg_value = 0
            timer = 0
            while True:
                if i == len(data):
                    break
                for x in range(avg_range):
                    try:
                        avg_value += abs(data[i + x][0])
                    except IndexError:
                        avg_range = x
                        break
                avg_value /= avg_range
                if abs(avg_value) >= 0.05:
                    break
                else:
                    timer += avg_range
                    i += avg_range
            pulses.append(int((timer / sample_rate)*1000))
            active = True

    return pulses


def create_html(html_filename, pulse_train):
    """
    create a basic html file containing a picture that when clicked will
    vibrate based on the wav file named when running the script

    :param html_filename: the name of an html file that you want to create
    :param pulse_train: the previously created pulse train to control vibration lengths
    :return: null
    """

    with open(html_filename, 'w') as html:
        html_open = \
        """
        <!DOCTYPE html>
        <html>
            <head>
                <title>Page Title</title>
            </head>
            <body>
    
                <img onclick="vibrate();" src="https://pbs.twimg.com/media/CojtXEVWgAAAL1_.jpg">
    
            </body>

            <script>

                function vibrate(){
        """

        html_script = "navigator.vibrate({});".format(pulse_train)

        html_close = \
        """
                        console.log("VIBRATE");
                }
            </script>
        </html>
        """
        html.write(html_open)
        html.write(html_script)
        html.write(html_close)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('wav_filename', help='audio file to be played back')
    parser.add_argument('html_filename', help='the name given to the html file created by this script')
    args = parser.parse_args()

    pulse_train = convert_wav(args.wav_filename)
    pulse_train.pop(0)
    create_html(args.html_filename, pulse_train)

