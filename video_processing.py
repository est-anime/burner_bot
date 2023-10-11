import ffmpeg

input_video = 'input_video.mp4'
subtitle_file = 'subtitle.srt'
output_video = 'output_video.mp4'

ffmpeg.input(input_video).output(output_video, vf='subtitles=' + subtitle_file).run()
