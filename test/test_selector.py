from downloader.analyzer import YTDLPAnalyzer
from downloader.selector import FormatSelector

url = "https://www.youtube.com/watch?v=e9ZupmL9BcM"

info = YTDLPAnalyzer().analyze(url)

selector = FormatSelector(info)

print("=" * 60)

print("Available Codecs")

print(selector.codecs())

print()

print("Available Resolutions")

print(selector.resolutions())

print()

print("Best Overall")

print(selector.best())

print()

print("Best AV1")

print(selector.best_av1())

print()

print("Best VP9")

print(selector.best_vp9())

print()

print("Best H264")

print(selector.best_h264())