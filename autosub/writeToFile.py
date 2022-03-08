#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime



def format_seconds(seconds, format=None):
    fmt = '%H:%M:%S,%f' if format == "srt" else '%H:%M:%S.%f'
    return datetime.datetime.fromtimestamp(seconds, tz=datetime.timezone.utc).strftime(fmt)[:-3]
    # -3: cut microseconds to milliseconds



def write_to_file(output_file_handle_dict, inferred_text, line_count, limits, cues):
    """Write the inferred text to SRT file
    Follows a specific format for SRT files

    Args:
        output_file_handle_dict : Mapping of subtitle format (eg, 'srt') to open file_handle
        inferred_text : text to be written
        line_count : subtitle line count
        limits : starting and ending times for text
    """

    for format in output_file_handle_dict.keys():
        from_dur = format_seconds(limits[0], format)
        to_dur = format_seconds(limits[1], format)

        file_handle = output_file_handle_dict[format]
        if format == 'srt':
            file_handle.write(str(line_count) + "\n")
            file_handle.write(from_dur + " --> " + to_dur + "\n")
            file_handle.write(inferred_text + "\n\n")
        elif format == 'vtt':
            file_handle.write(from_dur + " --> " + to_dur + " align:start position:0%\n")
            # Write out WebVTT (Video Timed Text) format, where words may be associated with a timestamp cue so each
            # word can be displayed by the player at a certain point (like YouTube autogenerated subtitles or karaoke
            # song lyrics).
            # Insert an empty line as the first line is for text without a cue
            file_handle.write("\n")
            words = inferred_text.split(" ")
            # The first word in any VTT subtitle from YouTube does not have a cue timing associated with it,
            # presumably because it uses the timestamp of the subtitle line itself as the first cue.
            # This approach is taken here too
            file_handle.write(words[0] + " ")
            cue_timed_text = ""
            for pair in zip(cues[1:], words[1:]):
                timestamp = format_seconds(pair[0], "vtt")
                word = pair[1]
                cue_timed_text += f"<{timestamp}><c> {word}</c>".format(timestamp=timestamp, word=word)

            # Insert the cue timed text
            file_handle.write(cue_timed_text + "\n\n")
        elif format == 'txt':
            file_handle.write(inferred_text + ". ")
