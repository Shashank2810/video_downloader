from downloader.analyzer import YTDLPAnalyzer

analyzer = YTDLPAnalyzer()

info = analyzer.analyze(
    "https://www.youtube.com/watch?v=e9ZupmL9BcM"
)

print()

print(info.title)

print()

print("BEST VIDEO")

print(info.best_video)

print()

print("VIDEO STREAMS")

for f in info.video_formats:

    print(
        f.resolution,
        f.video_codec,
        f.format_id,
    )

print()

print("AUDIO STREAMS")

for f in info.audio_formats:

    print(
        f.audio_codec,
        f.format_id,
    )

print()

print("COMBINED")

for f in info.combined_formats:

    print(
        f.resolution,
        f.video_codec,
        f.audio_codec,
    )